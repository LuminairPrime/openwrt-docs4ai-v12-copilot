---
title: Adding new device support
module: wiki
origin_type: wiki_page
token_count: 2892
source_file: L1-raw/wiki/wiki_page-guide-developer-add-new-device.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_url: https://openwrt.org/docs/guide-developer/add.new.device
language: text
ai_summary: The 'Adding new device support' module provides a comprehensive guide for developers looking to add support for new devices within the OpenWrt ecosystem. It outlines a general approach that includes listing device chips, ensuring access to the bootloader, and verifying hardware components such as flash partitioning and GPIOs. The document also details specific methods for testing GPIOs for LEDs and buttons, including example scripts for automation. Developers are encouraged to refer to related resources for device support policies and platform addition guidelines.
ai_when_to_use: Use this module when you need to add support for a new device that is based on an already supported platform in OpenWrt.
ai_related_topics:
- add.new.platform
- Device support policies / best practices
- hw.hacking.first.steps
- GPIOs
---
# Adding new device support

This article assumes your device is based on a platform already supported by OpenWrt. If you need to add a new platform, see -\>[add.new.platform](/docs/guide-developer/add.new.platform)

If you already solved the puzzle and are looking for device support submission guidelines, check out [Device support policies / best practices](/docs/guide-developer/device-support-policies)

## General Approach

1.  Make a detailed list of chips on the device and find info about support for them. Focus on processor, flash, ethernet and wireless. Some helpful tips are available on [hw.hacking.first.steps](/docs/guide-developer/hw.hacking.first.steps)
2.  Make sure you have working serial console and access to the bootloader.
3.  Prepare and install firmware, watch the bootlog for problems and errors.
4.  Verify flash partitioning, LEDs and buttons.

## GPIOs

Most of devices use [GPIOs](/docs/techref/hardware/port.gpio) for controlling LEDs and buttons. There aren't any generic GPIOs numbers, so OpenWrt has to use device specific mappings. It means we need to find out GPIOs for every controllable LED and button on every supported device.

### GPIO LEDs

If LED is controlled by GPIO, direction has to be set to `out` and we need to know the polarity:

- If LED turns on for value 1, it's active high
- If LED turns on for value 0, it's active low

A single GPIO can be tested in the following way:

    cd /sys/class/gpio
    GPIO=3
    echo $GPIO > export
    echo "out" > gpio$GPIO/direction
    echo 0 > gpio$GPIO/value
    sleep 1s
    echo 1 > gpio$GPIO/value
    sleep 1s
    echo $GPIO > unexport

Of course every GPIO (starting with 0) has to be tested, not only a GPIO 3 as in the example above.

So basically you need to create a table like:

| Color | Name  | GPIO | Polarity    |
|-------|-------|------|-------------|
| Green | Power | 0    | Active high |
| Blue  | WLAN  | 7    | Active high |
| Blue  | USB   | 12   | Active low  |

To speed up testing all GPIOs one by one you can use following bash script. Please note you have to follow LEDs state and console output. If the USB LED turns on and the last console message is `[GPIO12] Trying value 0` it means USB LED uses GPIO 12 and is active low.

``` bash
#!/bin/sh
GPIOCHIP=0
BASE=$(cat /sys/class/gpio/gpiochip${GPIOCHIP}/base)
NGPIO=$(cat /sys/class/gpio/gpiochip${GPIOCHIP}/ngpio)
max=$(($BASE+$NGPIO))
gpio=$BASE
while [ $gpio -lt $max ] ; do
    echo $gpio > /sys/class/gpio/export
    [ -d /sys/class/gpio/gpio${gpio} ] && {
        echo out > /sys/class/gpio/gpio$gpio/direction

        echo "[GPIO$gpio] Trying value 0"
        echo 0 > /sys/class/gpio/gpio$gpio/value
        sleep 3s

        echo "[GPIO$gpio] Trying value 1"
        echo 1 > /sys/class/gpio/gpio$gpio/value
        sleep 3s

        echo $gpio > /sys/class/gpio/unexport
    }
    gpio=$((gpio+1))
done
```

- Save the above content as a file `gpio-test.sh` & then transfer inside router's `/tmp` directory, or copy above content & paste inside `vi` editor in router & save as `gpio-test.sh` file.
- to make it executable, run: `chmod +x /tmp/gpio-test.sh`

### GPIO buttons

In case of GPIO controlled buttons value changes during button press. So the best idea to find out which GPIO is connected to some hardware button is to:

1.  Dump values of all GPIOs
2.  Push button and keep it pushed
3.  Dump values of all GPIOs
4.  Find out which GPIO changed its value

For dumping GPIO values following script can be used:

``` bash
#!/bin/sh
GPIOCHIP=0
BASE=$(cat /sys/class/gpio/gpiochip${GPIOCHIP}/base)
NGPIO=$(cat /sys/class/gpio/gpiochip${GPIOCHIP}/ngpio)
max=$(($BASE+$NGPIO))
gpio=$BASE
while [ $gpio -lt $max ] ; do
    echo $gpio > /sys/class/gpio/export
    [ -d /sys/class/gpio/gpio${gpio} ] && {
        echo in > /sys/class/gpio/gpio${gpio}/direction
        echo "[GPIO${gpio}] value $(cat /sys/class/gpio/gpio${gpio}/value)"
        echo ${gpio} > /sys/class/gpio/unexport
    }
    gpio=$((gpio+1))
done
```

- Save the above content as a file `gpio-dump.sh` & then transfer inside router's `/tmp` directory, or copy above content & paste inside `vi` editor in router & save as `gpio-dump.sh` file
- to make it executable, run: `chmod +x /tmp/gpio-dump.sh`

If GPIO value changes from 1 to 0 while pressing the button, it's active low. Otherwise it's active high.

Example table:

| Name  | GPIO | Polarity   |
|-------|------|------------|
| WPS   | 4    | Active low |
| Reset | 6    | Active low |

### KSEG1ADDR() and accessing NOR flash

For getting MAC addresses, EEPROM and other calibration data for your board, you may need to read from flash in the kernel. In the case of many Atheros chips using NOR flash, done using the KSEG1ADDR() macro which translates the hardware address of the flash to the virtual address for the process context which is executing your init function.

If you are reviewing the code for initializing a board similar to your own and you see this idium: KSEG1ADDR(0x1fff0000), the number at first appears to be magic but it is logical if you understand two things. Firstly, Atheros SoCs using NOR flash wire it to the physical address 0x1f000000 (there are no guarantees about where the flash will be wired for your board but this is a common location). You cannot rely on the address given in the bootloader, you might see 0xbf000000 but this is probably also a virtual address. If your board wires flash to these memory locations, you may obviously access flash using KSEG1ADDR(0x1f000000 + OFFSET_FROM_BEGIN) but in the event that you have to access data which you know will exist at the very end of the flash, you can use a trick to make your code compatible with multiple sizes of flash memory.

Often flash will be mapped to a full 16MB of address space no matter whether it is 4MB, 8MB or 16MB so in this case KSEG1ADDR(0x20000000 - OFFSET_FROM_END) will work for accessing things which you know to be a certain distance from the end of the flash memory. When you see KSEG1ADDR(0x1fff0000), on devices with 4MB or 8MB of flash, it's fair to guess that it's using this trick to reference the flash which resides 64k below the end of the flash (where Atheros Radio Test data is stored).

## Examples

### Brcm63xx Platform

If you have the OEM sourcecode for your [bcm63xx](/docs/techref/hardware/soc/soc.broadcom.bcm63xx) specific device, it may be useful some things for later adding the OpenWrt support:

- Look for your Board Id at `shared/opensource/boardparms/boardparms.c`
- Adapt the `imagetag.c` to create a different tag (see `shared/opensource/inlude/bcm963xx/bcmTag.h` in the GPL tar for the layout)
- Finally xor the whole image with '12345678' (the ascii string, not hex).

(from <https://forum.openwrt.org/viewtopic.php?pid=123105#p123105>)

For creating the OpenWrt firmware your [bcm63xx](/docs/techref/hardware/soc/soc.broadcom.bcm63xx) device, you can follow the following steps:

1.  Obtain the [source and follow the compile procedure](/docs/guide-developer/toolchain/start) with the make menuconfig as last step.
2.  During **menuconfig** select the correct target system.
3.  Next generate the board_bcm963xx.c file for the selected platform with all board parameters execute the following command:
    `make kernel_menuconfig`
4.  Add the board-id to the ./target/linux/brcm63xx/image/Makefile.
    **Example**
    \\# Davolink DV2020
$(call Image/Build/CFE,$(1),DV2020,6348)
    - add the board-id with the parameters to ./build_dir/linux-brcm63xx/linux-2.6.37.4/arch/mips/bcm63xx/boards/board_bcm963xx.c\\ **Example**\\ <code>static struct board_info __initdata board_DV2020 = {
          .name                           = "DV2020",
          .expected_cpu_id                = 0x6348,

          .has_uart0                      = 1,
          .has_pci                        = 1,
          .has_ohci0                      = 1,

          .has_enet0                      = 1,
          .has_enet1                      = 1,
          .enet0 = {
                  .has_phy                = 1,
                  .use_internal_phy       = 1,
          },
          .enet1 = {
                  .force_speed_100        = 1,
                  .force_duplex_full      = 1,
          },

};

static const struct board_info \_\_initdat : : :

      &board_DV2020,

\</code\>

1.  Finish the [compile instructions](/docs/guide-developer/toolchain/start) according the procedure from the make step.

### Ramips Platform

As long as you are adding support for an ramips board with an existing chipset, this is rather straightforward. You need to create a new *board* definition, which will generate an image file specifically for your device and runs device-specific code. Then you write various board-specific hacks to initialize devices and set the correct default configuration.

Your board identifier will be passed in the following sequence:

     (Image Generator puts it in the kernel command line)
              ↓
     (Kernel command line is executed with BOARD=MY_BOARD)
              ↓
     (Kernel code for ramips finds your board and loads machine-specific code)
              ↓
     (/lib/ramips.sh:ramips_board_name() reads the board name from /proc/cpuinfo)
              ↓
     (Several userspace scripts use ramips_board_name() for board-specific setup)

At a minimum, you need to make the following changes to make a basic build, all under target/linux/ramips/:

- Add a new machine image in `image/Makefile`
- Create a new machine file in `arch/mips/ralink/$CHIP/mach-myboard.c` where you register:
  - GPIO pins for LEDs and buttons
  - Port layout for the device (vlan configuration)
  - Flash memory configuration
  - Wifi
  - USB
  - Watchdog timer
  - And anything else specific to your board
- Reference the new machine file in `arch/mips/ralink/$CHIP/{Kconfig,Makefile}`
- Reference the new machine name in `files/arch/mips/include/asm/mach-ralink/machine.h`
- Add your board to `base-files/lib/ramips.sh` for userspace scripts to read the board name

Then you'll want to modify some of these files depending on your board's features:

- `base-files/etc/diag.sh` to set a LED which OpenWRT should blink on bootup
- `base-files/lib/upgrade/platform.sh` to allow sysupgrade to work on your board
- `base-files/etc/uci-defaults/network` to configure default network interface settings, particularly MAC addresses
- `base-files/etc/uci-defaults/leds` if you have configurable LEDs which should default to a behavior, like a WLAN activity LED
- `base-files/etc/hotplug.d/firmware/10-rt2x00-eeprom` to extract the firmware image for the wireless module
- `base-files/lib/preinit/06_set_iface_mac` to set the MAC addresses of any other interfaces

Example commits:

- [Skyline SL-R7205 (rt305x)](https://dev.openwrt.org/changeset/30645)
- [Belkin F5D8235-4 v1 (rt288x)](https://dev.openwrt.org/changeset/29617)
- [Planex DB-WRT01 (MT7620A)](https://dev.openwrt.org/changeset/46918)

## Tips

After add a new board, you may should clean the `tmp` folder first. \<code\> cd trunk rm -rf tmp make menuconfig \</code\>

If you have added a device profile, and it isn't showing up in "make menuconfig" try touching the main target makefile

    touch target/linux/*/Makefile
