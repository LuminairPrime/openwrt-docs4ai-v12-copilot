---
module: wiki
total_token_count: 99226
section_count: 49
is_monolithic: false
is_sharded_part: true
part_number: 1
part_count: 2
generated: '2026-03-27T20:02:56.666251+00:00'
---

# wiki Bundled Reference (Part 1 of 2)

> **Contains:** 49 documents
> **Tokens:** ~99226 (cl100k_base)
> **Index:** [./bundled-reference.md](./bundled-reference.md)

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

---

# Adding new platform support

You can find a list of all currently supported [start](/docs/platforms/start). Maybe there is no need to add a completely new platform, but only a new device, see -\>[add.new.device](/docs/guide-developer/add.new.device).

Linux is now one of the most widespread operating system for embedded devices due to its openess as well as the wide variety of platforms it can run on. Many manufacturer actually use it in firmware you can find on many devices: DVB-T decoders, routers, print servers, DVD players ... Most of the time the stock firmware is not really open to the consumer, even if it uses open source software.

You might be interested in running a Linux based firmware for your router for various reasons: extending the use of a network protocol (such as IPv6), having new features, new piece of software inside, or for security reasons. A fully open-source firmware is de-facto needed for such applications, since you want to be free to use this or that version of a particular reason, be able to correct a particular bug. Few manufacturers do ship their routers with a Sample Development Kit, that would allow you to create your own and custom firmware and most of the time, when they do, you will most likely not be able to complete the firmware creation process.

This is one of the reasons why OpenWrt and other firmware exists: providing a version independent, and tools independent firmware, that can be run on various platforms, known to be running Linux originally.

## Which Operating System does this device run?

There is a lot of methods to ensure your device is running Linux. Some of them do need your router to be unscrewed and open, some can be done by probing the device using its external network interfaces.

### Operating System fingerprinting and port scanning

A large bunch of tools over the Internet exists in order to let you do OS fingerprinting, we will show here an example using *nmap*:

|                                                                      |
|----------------------------------------------------------------------|
| `nmap -P0 -O //IP address//
 Starting Nmap 4.20 ( http://insecure.org ) at 2007-01-08 11:05 CET
 Interesting ports on 192.168.2.1:
 Not shown: 1693 closed ports
 PORT   STATE SERVICE
 22/tcp open  ssh
 23/tcp open  telnet
 53/tcp open  domain
 80/tcp open  http
 MAC Address: 00:13:xx:xx:xx:xx (Cisco-Linksys)
 Device type: broadband router
 Running: Linksys embedded
 OS details: Linksys WRT54GS v4 running OpenWrt w/Linux kernel 2.4.30
 Network Distance: 1 hop`                                              |

The *nmap* utility is able to report whether your device uses a Linux TCP/IP stack, and if so, will show you which Linux kernel version is probably runs. This report is quite reliable and it can make the distinction between BSD and Linux TCP/IP stacks and others.

Using the same tool, you can also do port scanning and service version discovery. For instance, the following command will report which IP-based services are running on the device, and which version of the service is being used:

|                                                                      |
|----------------------------------------------------------------------|
| `nmap -P0 -sV //IP address//
 Starting Nmap 4.20 ( http://insecure.org ) at 2007-01-08 11:06 CET
 Interesting ports on 192.168.2.1:
 Not shown: 1693 closed ports
 PORT   STATE SERVICE VERSION
 22/tcp open  ssh     Dropbear sshd 0.48 (protocol 2.0)
 23/tcp open  telnet  Busybox telnetd
 53/tcp open  domain  ISC Bind dnsmasq-2.35
 80/tcp open  http    OpenWrt BusyBox httpd
 MAC Address: 00:13:xx:xx:xx:xx (Cisco-Linksys)
 Service Info: Device: WAP`                                            |

The web server version, if identified, can be determining in knowing the Operating System. For instance, the BOA web server is typical from devices running an open-source Unix or Unix-like.

### Wireless Communications Fingerprinting

Although this method is not really known and widespread, using a wireless scanner to discover which OS your router or Access Point run can be used. We do not have a clear example of how this could be achieved, but you will have to monitor raw 802.11 frames and compare them to a very similar device running a Linux based firmware.

### Web server security exploits

The Linksys WRT54G was originally hacked by using a "ping bug" discovered in the web interface. This tip has not been fixed for months by Linksys, allowing people to enable the "boot_wait" helper process via the web interface. Many web servers used in firmwares are open source web server, thus allowing the code to be audited to find an exploit. Once you know the web server version that runs on your device, by using nmap -sV or so, you might be interested in using exploits to reach shell access on your device.

### Native Telnet/SSH access

Some firmwares might have restricted or unrestricted Telnet/SSH access, if so, try to log in with the web interface login/password and see if you can type in some commands. This is actually the case for some Broadcom BCM963xx based firmwares such as the one in Neuf/Cegetel ISP routers, Club-Internet ISP CI-Box and many others. Some commands, like cat might be left here and be used to determine the Linux kernel version.

### Analyzing a binary firmware image

You are very likely to find a firmware binary image on the manufacturer website, even if your device runs a proprietary operating system. If so, you can download it and use an hexadecimal editor to find printable words such as vmlinux, linux, ramdisk, mtd and others.

Some Unix tools like `hexdump` or `strings` can be used to analyze the firmware. Below there is an example with a binary firmware found on the Internet:

|                                                                                  |
|----------------------------------------------------------------------------------|
| `hexdump -C <binary image.extension> | less
 00000000  46 49 52 45 32 2e 35 2e  30 00 00 00 00 00 00 00  |FIRE2.5.0.......|
 00000010  00 00 00 00 31 2e 30 2e  30 00 00 00 00 00 00 00  |....1.0.0.......|
 00000020  00 00 00 00 00 00 00 38  00 43 36 29 00 0a e6 dc  |.......8.C6)..??|
 00000030  54 49 44 45 92 89 54 66  1f 8b 08 08 f8 10 68 42  |TIDE..Tf....?.hB|
 00000040  02 03 72 61 6d 64 69 73  6b 00 ec 7d 09 bc d5 d3  |..ramdisk.?}.???|
 00000050  da ff f3 9b f7 39 7b ef  73 f6 19 3b 53 67 ea 44  |???.?9{?s?.;Sg?D|`   |

Scroll over the firmware to find printable words that can be significant.

### Amount of flash memory

Linux can hardly fit in a 2MB flash device, once you have opened the device and located the flash chip, try to find its characteristics on the Internet. If your flash chip is a 2MB or less device, your device is most likely to run a proprietary OS such as WindRiver VxWorks, or a custom manufacturer OS like Zyxel ZynOS.

OpenWrt does not currently run on devices which have 2MB or less of flash memory. This limitation will probably not be worked around since those devices are most of the time micro-routers, or Wireless Access Points, which are not the main OpenWrt target.

### Plugging a serial port

By using a serial port and a level shifter, you may reach the console that is being shown by the device for debugging or flashing purposes. By analyzing the output of this device, you can easily notice if the device uses a Linux kernel or something different.

## Finding and using the manufacturer SDK

Once you are sure your device run a Linux based firmware, you will be able to start hacking on it. If the manufacturer respected the GPL, it will have released a Sample Development Kit with the device.

### GPL violations

Some manufacturers do release a Linux based binary firmware, with no sources at all. The first step before doing anything is to read the license coming with your device, then write them about this lack of Open Source code. If the manufacturer answers you they do not have to release a SDK containing Open Source software, then we recommend you get in touch with the gpl-violations.org community.

You will find below a sample letter that can be sent to the manufacturer:

|                                                                                                               |
|---------------------------------------------------------------------------------------------------------------|
| `Miss, Mister,

 I am using a //device name//, and I cannot find neither on your website nor on the CD-ROM
 the open source software used to build or modify the firmware.

 In conformance to the GPL license, you have to release the following sources:

  * complete toolchain that made the kernel and applications be compiled (gcc, binutils, libc)
  * tools to build a custom firmware (mksquashfs, mkcramfs ...)
  * kernel sources with patches to make it run on this specific hardware, this does not include binary drivers

 Thank you very much in advance for your answer.

 Best regards, //Your Name//`                                                                                   |

### Using the SDK

Once the SDK is available, you are most likely not to be able to build a complete or functional firmware using it, but parts of it, like only the kernel, or only the root filesystem. Most manufacturers do not really care releasing a tool that do work every time you uncompress and use it.

You should anyway be able to use the following components:

- kernel sources with more or less functional patches for your hardware
- binary drivers linked or to be linked with the shipped kernel version
- packages of the toolchain used to compile the whole firmware: gcc, binutils, libc or uClibc
- binary tools to create a valid firmware image

Your work can be divided into the following tasks:

- create a clean patch of the hardware specific part of the Linux kernel
- spot potential kernel GPL violations especially on network stack and USB stack stuff
- make the binary drivers work, until there are open source drivers
- use standard a GNU toolchain to make working executables
- understand and write open source tools to generate a valid firmware image

### Creating a hardware specific kernel patch

Most of the time, the kernel source that comes along with the SDK is not really clean, and is not a standard Linux version, it also has architecture specific fixes backported from the CVS or the git repository of the kernel development trees. Anyway, some parts can be easily isolated and used as a good start to make a vanilla kernel work your hardware.

Some directories are very likely to have local modifications needed to make your hardware be recognized and used under Linux. First of all, you need to find out the linux kernel version that is used by your hardware, this can be found by editing the linux/Makefile file.

|                                 |
|---------------------------------|
| `head -5 linux-2.x.x/Makefile
 VERSION = 2
 PATCHLEVEL = x
 SUBLEVEL = y
 EXTRAVERSION = z
 NAME=A fancy name`               |

So now, you know that you have to download a standard kernel tarball at kernel.org that matches the version being used by your hardware.

Then you can create a diff file between the two trees, especially for the following directories:

|                                                                                                                           |
|---------------------------------------------------------------------------------------------------------------------------|
| `diff -urN linux-2.x.x/arch///sub architecture// linux-2.x.x-modified/arch///sub architecture// > 01-architecture.patch
 diff -urN linux-2.x.x/include/ linux-2.x.x-modified/include > 02-includes.patch
 diff -urN linux-2.x.x/drivers/ linux-2.x.x-modified/drivers > 03-drivers.patch`                                            |

This will constitute a basic set of three patches that are very likely to contain any needed modifications that has been made to the stock Linux kernel to run on your specific device. Of course, the content produced by the diff -urN may not always be relevant, so that you have to clean up those patches to only let the "must have" code into them.

The first patch will contain all the code that is needed by the board to be initialized at startup, as well as processor detection and other boot time specific fixes.

The second patch will contain all useful definitions for that board: addresses, kernel granularity, redefinitions, processor family and features ...

The third patch may contain drivers for: serial console, ethernet NIC, wireless NIC, USB NIC ... Most of the time this patch contains nothing else than "glue" code that has been added to make the binary driver work with the Linux kernel. This code might not be useful if you plan on writing drivers from scratch for this hardware.

### Using the device bootloader

The [bootloader](/docs/techref/bootloader) is the first program that is started right after your device has been powered on. This program, can be more or less sophisticated, some do let you do network booting, USB mass storage booting ... The bootloader is device and architecture specific, some bootloaders were designed to be universal such as RedBoot or [Das U-Boot](/docs/techref/bootloader/uboot) so that you can meet those loaders on totally different platforms and expect them to behave the same way.

If your device runs a proprietary operating system, you are very likely to deal with a proprietary boot loader as well. This may not always be a limitation, some proprietary bootloaders can even have source code available (i.e : Broadcom CFE).

According to the bootloader features, hacking on the device will be more or less easier. It is very probable that the bootloader, even exotic and rare, has a documentation somewhere over the Internet. In order to know what will be possible with your bootloader and the way you are going to hack the device, look over the following features:

- does the bootloader allow [net booting](/inbox/howto/netboot) via [BOOTP](https://en.wikipedia.org/wiki/Bootstrap Protocol)/[PXE](https://en.wikipedia.org/wiki/Preboot Execution Environment)/DHCP/NFS or [TFTP](https://en.wikipedia.org/wiki/Trivial File Transfer Protocol)?
- does the bootloader accept loading [ELF](https://en.wikipedia.org/wiki/Executable and Linkable Format) binaries?
- does the bootloader have a kernel/firmware size limitation?
- does the bootloader expect some magic values to be part of the firmware, or the firmware to be encrypted?
- does the bootloader expect a firmware format to be loaded with?
- are the loaded files executed from RAM or flash?

Net booting is something very convenient, because you will only have to set up network booting servers on your development station, and keep the original firmware on the device till you are sure you can replace it. This also prevents your device from being flashed, and potentially bricked every time you want to test a modification on the kernel/filesystem.

If your device needs to be flashed every time you load a firmware, the bootlader might only accept a specific firmware format to be loaded, so that you will have to understand the firmware format as well.

### Making binary drivers work

As we have explained before, manufacturers do release binary drivers in their GPL tarball. When those drivers are statically linked into the kernel, they become GPL as well, fortunately or unfortunately, most of the drivers are not statically linked. This anyway lets you a chance to dynamically link the driver with the current kernel version, and try to make them work together.

This is one of the most tricky and grey part of the fully open source projects. Some drivers require few modifications to be working with your custom kernel, because they worked with an earlier kernel, and few modifications have been made to the kernel in-between those versions. This is for instance the case with the binary driver of the Broadcom BCM43xx Wireless Chipsets, where only few differences were made to the network interface structures.

Some general principles can be applied no matter which kernel version is used in order to make binary drivers work with your custom kernel:

- turn on kernel debugging features such as:
  - CONFIG_DEBUG_KERNEL
  - CONFIG_DETECT_SOFTLOCKUP
  - CONFIG_DEBUG_KOBJECT
  - CONFIG_KALLSYMS
  - CONFIG_KALLSYMS_ALL
- link binary drivers when possible to the current kernel version
- try to load those binary drivers
- catch the lockups and understand them

Most of the time, loading binary drivers will fail, and generate a kernel oops. You can know the last symbol the binary drivers attempted to use, and see in the kernel headers file, if you do not have to move some structures field before or after that symbol in order to keep compatibily with both the binary driver and the stock kernel drivers.

### Understanding the firmware format

You might want to understand the firmware format, even if you are not yet capable of running a custom firmware on your device, because this is sometimes a blocking part of the flashing process.

A firmware format is most of the time composed of the following fields:

- header, containing a firmware version and additional fields: Vendor, Hardware version ...
- CRC32 checksum on either the whole file or just part of it
- Binary and/or compressed kernel image
- Binary and/or compressed root filesystem image
- potential garbage

Once you have figured out how the firmware format is partitioned, you will have to write your own tool that produces valid firmware binaries. One thing to be very careful here is the endianness of either the machine that produces the binary firmware and the device that will be flashed using this binary firmware.

### Writing a flash map driver

The flash map driver has an important role in making your custom firmware work because it is responsible of mapping the correct flash regions and associated rights to specific parts of the system such as: bootloader, kernel, user filesystem.

Writing your own flash map driver is not really a hard task once you know how your firmware image and flash is structured. You will find below a commented example that covers the case of the device where the bootloader can pass to the kernel its partition plan.

First of all, you need to make your flash map driver be visible in the kernel configuration options, this can be done by editing the file `linux/drivers/mtd/maps/Kconfig`:

|                                                                            |
|----------------------------------------------------------------------------|
| `config MTD_DEVICE_FLASH
         tristate "Device Flash device"
         depends on ARCHITECTURE && DEVICE
         help
          Flash memory access on DEVICE boards. Currently only works with
          Bootloader Foo and Bootloader Bar.`                                |

Then add your source file to the linux/drivers/mtd/maps/Makefile, so that it will be compiled along with the kernel.

|                                                    |
|----------------------------------------------------|
| `obj-$(CONFIG_MTD_DEVICE_FLASH) += device-flash.o` |

You can then write the kernel driver itself, by creating a `linux/drivers/mtd/maps/device-flash.c` C source file.

|                                                                                               |
|-----------------------------------------------------------------------------------------------|
| `// Includes that are required for the flash map driver to know of the prototypes:
 #include <asm/io.h>
 #include <linux/init.h>
 #include <linux/kernel.h>
 #include <linux/mtd/map.h>
 #include <linux/mtd/mtd.h>
 #include <linux/mtd/partitions.h>
 #include <linux/vmalloc.h>

 // Put some flash map definitions here:
 #define WINDOW_ADDR 0x1FC00000  /* Real address of the flash */
 #define WINDOW_SIZE 0x400000    /* Size of flash */
 #define BUSWIDTH 2      /* Buswidth */

 static void __exit device_mtd_cleanup(void);

 static struct mtd_info *device_mtd_info;

 static struct map_info devicd_map = {
     .name = "device",
     .size = WINDOW_SIZE,
     .bankwidth = BUSWIDTH,
     .phys = WINDOW_ADDR,
 };

 static int __init device_mtd_init(void)
 {
     // Display that we found a flash map device
     printk("device: 0x\%08x at 0x\%08x\n", WINDOW_SIZE, WINDOW_ADDR);

     // Remap the device address to a kernel address
     device_map.virt = ioremap(WINDOW_ADDR, WINDOW_SIZE);

     // If impossible to remap, exit with the EIO error
     if (!device_map.virt) {
         printk("device: Failed to ioremap\n");
         return -EIO;
     }
     // Initialize the device map
     simple_map_init(&device_map);

     /* MTD informations are closely linked to the flash map device
        you might also use "jedec_probe" "amd_probe" or "intel_probe" */
     device_mtd_info = do_map_probe("cfi_probe", &device_map);

     if (device_mtd_info) {
         device_mtd_info->owner = THIS_MODULE;

         int parsed_nr_parts = 0;

         // We try here to use the partition schema provided by the bootloader specific code
         if (parsed_nr_parts == 0) {
             int ret =
                 parse_bootloader_partitions(device_mtd_info,
                             &parsed_parts, 0);
             if (ret > 0) {
                 part_type = "BootLoader";
                 parsed_nr_parts = ret;
             }
         }

         add_mtd_partitions(devicd_mtd_info, parsed_parts,
                    parsed_nr_parts);

         return 0;
     }
     iounmap(device_map.virt);

     return -ENXIO;
 }

 // This function will make the driver clean up the MTD device mapping
 static void __exit device_mtd_cleanup(void)
 {
     // If we found a MTD device before
     if (device_mtd_info) {
         // Delete every partitions
         del_mtd_partitions(device_mtd_info);
         // Delete the associated map
         map_destroy(device_mtd_info);
     }

     // If the virtual address is already in use
     if (device_map.virt) {
         // Unmap the physical address to a kernel space address
         iounmap(device_map.virt);

         // Reset the structure field
         device_map.virt = 0;
     }
 }

 // Macros that indicate which function is called on loading/unloading the module
 module_init(device_mtd_init);
 module_exit(device_mtd_cleanup);

 // Macros defining license and author, parameters can be defined here too.
 MODULE_LICENSE("GPL");
 MODULE_AUTHOR("Me, myself and I <memyselfandi@domain.tld>");`                                  |

---

# Adding a new device

A good all-round advice would be to start by looking at recent commits about adding a new device, to see what files where changed and how. Many files try to be as self-explanatory as possible, most of the times just opening them will be enough to understand their function.

## Learn by example

### Search by grep locally

A good method is learn by example, so you can do:

    grep -lri mt300a target/

The result is minimal list of files required to add a new board:

    target/linux/ramips/base-files/etc/board.d/01_leds
    target/linux/ramips/base-files/etc/board.d/02_network
    target/linux/ramips/base-files/lib/upgrade/platform.sh
    target/linux/ramips/base-files/lib/ramips.sh
    target/linux/ramips/dts/GL-MT300A.dts
    target/linux/ramips/image/mt7620.mk

### Search by Git commit

[Browse the source filtered by "add support for"](https://git.openwrt.org/?p=openwrt%2Fopenwrt.git&a=search&h=HEAD&st=commit&s=add+support+for) and checkout the `diff` for newly added device

## Important files

This is a general map of where most important files are located:

### /target/linux/\<arch_name\>/base-files/etc/…

This folder contains files and folders that will be integrated in the firmware’s /etc folder.

These are its subfolders and files:

- **…board.d/** scripts for defining device-specific default hardware, like leds and network interfaces.
- **…hotplug.d/** scripts for defining device-specific actions to be done automatically on hotplugging of devices
- **…init.d/** scripts for defining device-specific actions to be done automatically on boot
- **…uci-defaults/** files for defining device-specific uci configuration items. Used e.g. for config migration after syntax changes.
- **…diag.sh** defines what is the led to use for error codes for each board

*Note that some of these functions are now done in the DTS for the board.*

### /target/linux/\<arch_name\>/base-files/lib/…

This folder contains files and folders that will be integrated in the firmware’s /lib folder.

These are its subfolders and files:

- **…\<arch_name\>.sh** human-readable full board name associated to script-safe board name
- **…preinit/** common \<arch_name\> preinit startup scripts
- **…upgrade/** common \<arch_name\> upgrade scripts

### /target/linux/\<arch_name\>/base-files/sbin

This folder contains files and folders that will be integrated in the firmware’s /sbin folder, usually common \<arch_name\> sbin scripts and tools.

### /target/linux/\<arch_name\>/dts/

Device tree source files, or dts for short.

*Certain architectures have the DTS directory deeper down. ARM devices, for example, typically have it located at `files-X.yy/arch/arm/boot/dts/`*

*If the DTS or DTSI file is already present in upstream Linux, they will usually not be present in the OpenWrt source. Configuring for the target and running `make target/linux/{clean,prepare}` will download and patch Linux, allowing the resulting file to be found in the `build_dir`*

### /target/linux/\<arch_name\>/image/

Configuration needed to build device-specific flashable images.

### /target/linux/\<arch_name\>/\<board_name\>/

Board-specific configuration.

### /target/linux/\<arch_name\>/modules.mk

Arch-specific kernel module config file for menuconfig

### Making new device appear in make menuconfig

After edit the files above, you need to touch the makefiles

    touch target/linux/*/Makefile

## Patches

The patches-\* subdirectories contain the kernel patches applied for every target.
All patches should be named 'NNN-lowercase_shortname.patch' and sorted into the following categories:

**0xx** - upstream backports
**1xx** - code awaiting upstream merge
**2xx** - kernel build / config / header patches
**3xx** - architecture specific patches
**4xx** - mtd related patches (subsystem and drivers)
**5xx** - filesystem related patches
**6xx** - generic network patches
**7xx** - network / phy driver patches
**8xx** - other drivers
**9xx** - uncategorized other patches
 All patches must be written in a way that they are potentially upstreamable, meaning:

1.  they must contain a **proper subject**
2.  they must contain a **proper commit message** explaining what they change
3.  they must contain a **valid Signed-off-by line**

## Testing images

Test firmware images without writing them to flash by using ramdisk images.

In **make menuconfig** select **Target Images** and then you can select the **ramdisk** option.

This will create an image with kernel + initramfs, that will have **initramfs** in the name. The resulting image can be loaded in the device through the bootloader's tftp function and should boot to a prompt without relying on flash/filesystem support.

## Tips and tricks

### Getting a shell on the target device

In order to collect relevant data for a port of OpenWrt to the device of interest one wants shell access. Most devices though do not offer a way to get a shell with telnet or ssh.

#### Abuse Unsanitized User Input

Some router offers ping test or NTP server configuration and may not properly sanitize user input. Try to enter shell script and see if you are lucky. You may need some `javascript` knowledges to disable client-side input validation.

##### Starting telnetd

``` bash
$( /bin/busybox telnetd -l/bin/sh -p23 & )
```

##### Obtain the password hash using HTTP or use `sed` to delete/change the default password if telnet login is required

``` bash
$( cp /etc/shadow /www )
$( cp /etc/passwd /www )
```

Then try to download them to your computer and crack the hash

#### Downgrade to older firmware

Some router may try to download a firmware file (e.g. [TP-Link Archer C2 AC750](/toh/tp-link/archer_c2_ac750)) from specific private IP at the beginning of booting, which allow user to downgrade to older firmware

#### Downgrade by Serial access

Serial access may allow you to enter console mode of u-boot for flashing/loading other firmware. Usually soldering is required. See [Generic flashing over the Serial port](/docs/guide-user/installation/generic.flashing.serial)

#### HTTP Server Vulnerability

Some routers may be running outdated/insecure HTTP server and may be vulnerable to buffer overflow or other attack

#### Netgear

With [netgear-telnetenable](/toh/netgear/telnet.console) many Netgear devices can be opened up for telnet access. Also see [GitHub: insanid/NetgearTelnetEnable](https://github.com/insanid/NetgearTelnetEnable). When such means cannot be used, one could try to flash an image build from the sources published by the vendor with telnetd enabled.

With [nmrpflash](https://github.com/jclehner/nmrpflash) many Netgear devices can be flashed. Devices that are compatible with this tool become effectively unbrickable.

### Collecting relevant data

On [WikiDevi](https://wikidevi.com/wiki/Main_Page) lots of information can be found, e.g. the FCC ID is very useful when searching for documentation, datasheets and internal photo's (to be able to distinguish used chips without having to open the casing).

Typically one can use the following commands:

``` bash
dmesg                          # log buffer might be to small, see note 1.
cat /proc/cmdline
cat /proc/cpuinfo
cat /proc/meminfo
cat /proc/devices
ls /sys/devices/platform
cat /proc/mtd
cat /sys/class/mtd/mtd*/offset # Linux 4.1 and newer, see note 2.
ifconfig -a
ls /sys/class/net
brctl show
cat /sys/kernel/debug/gpio     # GPIO information
```

**Note 1:** Often the log buffer is to small and the earliest messages may be missing from the information retrieved with `dmesg`. If one build a stock image from the sources the vendor has published, a larger buffer size can be set within the kernel config.

**Note 2:** <http://lxr.free-electrons.com/source/Documentation/ABI/testing/sysfs-class-mtd>

Another useful tool for getting information for setting LEDs might be [gpiodump](https://github.com/jclehner/gpiodump-mt7620), a MT7620 GPIOMODE register dumper (RAMIPS).

### Getting collected data from a device

Because of the limited space, common file transfer utilities such as rsync/curl/ssh/scp/ftp/http/tftp may not be available, a stripped down version/applet may be available from busybox.

Assume the router ip is `192.168.0.123`, and the file to be transfer located at `/tmp/important-data.txt`.

#### Use SCP to download

Your ssh server built into the device may have SCP capabilities without an sftp server. It may also only support legacy SCP (requiring the -O option) not scpv2.

i.e.

##### Receiver

    scp -O <source> <dest>

For example:

     scp -O root@192.168.1.1:/tmp/important-data.txt ~/

#### HTTP by `httpd` and `busybox mount`

If the web interface are served from `/www`.

##### Sender

``` bash
mount -o bind /tmp /www
```

##### Receiver

``` bash
wget http://192.168.0.123/important-data.txt
```

#### FTP by `busybox ftpput`

##### Receiver

Setup an FTP server. Add an anonymous account with write permission

``` bash
python -m pyftpdlib -w -p 21
```

##### Sender

``` bash
busybox ftpput 192.168.0.123 important-data.txt /tmp/important-data.txt
```

#### netcat by `busybox nc`

##### Receiver

``` bash
busybox nc -l -p 12345 > important-data.txt
```

##### Sender

``` bash
cat /tmp/important-data.txt | busybox nc 192.168.0.123:12345
```

#### TFTP by `busybox tftp`

##### Receiver

Setup a tftp server

##### Sender

``` bash
busybox tftp -p -l /tmp/important-data.txt -r important-data.txt 192.168.0.123
```

#### Use Curl to upload

Depending on what is compiled into your curl binary if available you may also be able to auth, use ftp/tftp etc. Extracts from curl man page:

    It supports these protocols: DICT, FILE, FTP, FTPS, GOPHER, GOPHERS,
           HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, MQTT, POP3, POP3S, RTMP, RTMPS, RTSP, SCP, SFTP, SMB, SMBS, SMTP, SMTPS, TELNET,  TFTP,  WS
           and WSS. The command is designed to work without user interaction.

           curl  offers  a busload of useful tricks like proxy support, user authentication, FTP upload, HTTP post, SSL connections, cookies,
           file transfer resume and more. As you will see below, the number of features will make your head spin.

           -T, --upload-file <file>
                  This transfers the specified local file to the remote URL. If there is no file part in the specified URL, curl will  append
                  the  local  file  name.  [NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md) that you must use a trailing / on the last directory to really prove to Curl that there is no
                  file name or curl will think that your last directory name is the remote file name to use. That will most likely cause  the
                  upload operation to fail. If this is used on an HTTP(S) server, the PUT command will be used.

                  Use  the  file name "-" (a single dash) to use stdin instead of a given file.  Alternately, the file name "." (a single pe‐
                  riod) may be specified instead of "-" to use stdin in non-blocking mode to allow reading server output while stdin is being
                  uploaded.

                  You can specify one -T, --upload-file for each URL on the command line. Each -T, --upload-file + URL pair specifies what to
                  upload and to where. curl also supports "globbing" of the -T, --upload-file argument, meaning that you can upload  multiple
                  files to a single URL by using the same URL globbing style supported in the URL.

                  When  uploading  to  an SMTP server: the uploaded data is assumed to be RFC 5322 formatted. It has to feature the necessary
                  set of headers and mail body formatted correctly by the user as curl will not transcode nor encode it further in any way.

                  -T, --upload-file can be used several times in a command line

                  Examples:
                   curl -T file https://example.com
                   curl -T "img[1-1000].png" ftp://ftp.example.com/
                   curl --upload-file "{file1,file2}" https://example.com

                  See also -G, --get and -I, --head.

#### Copy from terminal

If all of the above tools/applets are unavailable, you may copy from telnet terminal but it may not work for binary file.

base64 would be a common choice to work around this limitation, but many routers lack such a command. You can first escape binary data to screen-safe hexadecimal by piping to busybox hexdump on the router:

``` bash
hexdump -v -e '/1 "%02x"'
```

You can then reverse it on the computer with the following command:

``` bash
xxd -r -p
```

---

# Building image with support for 3g/4g and usb tethering

## Preparing build environment

First of all, you need a complete build environment, either physical or virtual system, as described on the [OpenWrt developer guide](/docs/guide-developer/start).

You need to clone OpenWrt git repository on your build system and synchronize all package feeds with your config file.

Be sure to understand the [build procedure](/docs/guide-user/additional-software/imagebuilder) to prevent build failure.

## Configuring packages

### Selecting target architecture and profile

Run `make menuconfig`.

Select your architecture on which you would put your compiled OpenWrt image. Then select your target profile, according your hardware type.

If you have selected correct value for target system, target profile, and target images, go to next step.

### Selecting kernel modules for usb networking support.

Go to `Kernel Modules -> USB Support`.

Select the following modules by pressing `y` to include the modules within the compiled image.

    Kernel Modules -> USB Support
    <*> kmod-usb2
    <*> kmod-usb-ohci
    <*> kmod-usb-uhci
    <*> kmod-usb-acm # For ACM based modem, such as Nokia Phones
    <*> kmod-usb-net # For tethering and rndis support

**kmod-usb-net** -\> to support usb networking interface.

Select all subsets if you want perfect support for usb network interfaces, including Android and iPhone tethering. Some newer 4g dongles use usb network interface (rndis) instead of legacy serial protocol.

    <*> kmod-usb-net............... Kernel modules for USB-to-Ethernet convertors
      <*>   kmod-usb-net-asix...... Kernel module for USB-to-Ethernet Asix convertors
      <*>   kmod-usb-net-cdc-eem..................... Support for CDC EEM connections
      -*-   kmod-usb-net-cdc-ether.............. Support for cdc ethernet connections
      <*>   kmod-usb-net-cdc-mbim..................... Kernel module for MBIM Devices
      -*-   kmod-usb-net-cdc-ncm..................... Support for CDC NCM connections
      <*>   kmod-usb-net-cdc-subset...... Support for CDC Ethernet subset connections
      <*>   kmod-usb-net-dm9601-ether........ Support for DM9601 ethernet connections
      <*>   kmod-usb-net-hso.. Kernel module for Option USB High Speed Mobile Devices
      <*>   kmod-usb-net-ipheth..................... Apple iPhone USB Ethernet driver
      <*>   kmod-usb-net-kalmia................... Samsung Kalmia based LTE USB modem
      <*>   kmod-usb-net-kaweth.. Kernel module for USB-to-Ethernet Kaweth convertors
      <*>   kmod-usb-net-mcs7830
      <*>   kmod-usb-net-pegasus
      <*>   kmod-usb-net-qmi-wwan.................................... QMI WWAN driver
      <*>   kmod-usb-net-rndis......................... Support for RNDIS connections
      <*>   kmod-usb-net-sierrawireless.......... Support for Sierra Wireless devices
      <*>   kmod-usb-net-smsc95xx. SMSC LAN95XX based USB 2.0 10/100 ethernet devices

**kmod-usb-serial** -\> to support legacy 3g dongles.

Select all subsets to ensure that your dongle works. Most 3g dongles use the option driver or generic serial driver to work. Note that option driver has better capability of distinguishing between modem serial interfaces and storage interface than generic usb serial driver.

    <*> kmod-usb-serial..................... Support for USB-to-Serial converters
      <*>   kmod-usb-serial-ark3116........ Support for ArkMicroChips ARK3116 devices
      <*>   kmod-usb-serial-belkin........................ Support for Belkin devices
      <*>   kmod-usb-serial-ch341.......................... Support for CH341 devices
      <*>   kmod-usb-serial-cp210x........... Support for Silicon Labs cp210x devices
      <*>   kmod-usb-serial-cypress-m8.............. Support for CypressM8 USB-Serial
      <*>   kmod-usb-serial-ftdi............................ Support for FTDI devices
      <*> kmod-usb-serial-ipw.................... Support for IPWireless 3G devices
      <*> kmod-usb-serial-keyspan........ Support for Keyspan USB-to-Serial devices
      <*> kmod-usb-serial-mct.............. Support for Magic Control Tech. devices
      <*> kmod-usb-serial-mos7720.............. Support for Moschip MOS7720 devices
      <*> kmod-usb-serial-motorola-phone............ Support for Motorola usb phone
      <*> kmod-usb-serial-option................... Support for Option HSDPA modems
      <*> kmod-usb-serial-oti6858...... Support for Ours Technology OTI6858 devices
      <*> kmod-usb-serial-pl2303............... Support for Prolific PL2303 devices
      <*> kmod-usb-serial-qualcomm................. Support for Qualcomm USB serial
      <*> kmod-usb-serial-sierrawireless....... Support for Sierra Wireless devices
      <*> kmod-usb-serial-ti-usb...................... Support for TI USB 3410/5052
      <*> kmod-usb-serial-visor............... Support for Handspring Visor devices
      -*- kmod-usb-serial-wwan..................... Support for GSM and CDMA modems

### Additional packages required for 3g functionality

#### ppp, chat, and uqmi

Go to `Network` section. Select \`uqmi\` to support qmi interface and \`ppp\` to support standard point-to-point protocol. `chat` is needed to establish serial communication to prepare PPP link negotiation.

    Network
      <*>chat
      <*>ppp
      <*>uqmi

#### mbim

Some dongles are using mbim protocol. To make use of mbim protocol, install `umbim` package.

    Network
      <*>umbim

#### comgt and usb-modeswitch

Go to `Utilities` section. Select `comgt` to provide control over 3g interface and `usb-modeswitch` to provide mode switching between virtual cd-rom interface to serial interface.

    Utilities
      <*>comgt
      <*>usb-modeswitch

#### minicom, picocom, and screen

If you want to debug serial communication, you may want to install serial terminal. There are several choices of serial terminal, such as minicom, picocom, and screen. I recommend `picocom` because of its small size.

    Utilities --> Terminal
      <*>picocom

Screen can be used as persistent session manager. Minicom has a nice interface, optimized for serial communication.

    Utilities
      < >screen
    Utilities --> Terminal
      < >minicom

For devices with 4MB flash, `picocom` is the only serial terminal that can be installed.

### Web Interface Support

If you want to control your 3g dongle with Luci web interface, go to Luci.

    Luci
    1. Collections
      <*> luci
    3. Applications
      <*> luci-app-multiwan (optional to support multiple 3g dongles)
      <*> luci-app-qos (optional to provide QOS support)
    6. Protocols
      <*> luci-proto-3g
      -*- luci-proto-ppp

===== Build process ===== Continue selecting packages as needed. When you are done, run the build process

    time make V=s download &&
    time make V=s

Faster build time can be achieved by enabling multiple build jobs. In case of quad-core cpu.

    time make -j8 V=s

If build process is successful, your firmware images will be located on `bin/target-platform/`.

If your hardware-specific image name could not be found, it's possible that you added too many packages that don't fit your hardware flash memory. Try reducing packages and restart the build process if such case happens.

---

# Building MPD-full with PulseAudio

More information about building from source: [OpenWrt Buildroot - Usage](/docs/guide-developer/toolchain/start)

First you need to follow the HowtoBuild [MPD-full building from source](/docs/guide-developer/build.mpd-full)

Based on the following reference: [BB + MPD-full + PulseAudio, unable to build](https://forum.openwrt.org/viewtopic.php?pid=287809#p287809)

### 18.06.02

#### The MPD Makefile

In your git clone directory edit the makefile `/openwrt/feeds/packages/sound/mpd/Makefile`.

Detect the area in the Makefile involved with the full MPD installation. Add `+pulseaudio-daemon` to DEPENDS.

      TITLE+= (full)
      DEPENDS+= +libffmpeg +libid3tag +libmms +libupnp +libshout +pulseaudio-daemon
      PROVIDES:=mpd
      VARIANT:=full

Edit the --disable-pulse to **--enable-pulse**

         --disable-nfs \
         --disable-openal \
         --disable-opus \
         --enable-pulse \
         --disable-sidplay \
         --disable-smbclient \
         --disable-sndfile \

Edit the EXTRA_LDFLAGS and add

    -Wl,-rpath-link=$(STAGING_DIR)/usr/lib/pulseaudio

The complete line looks like that:

      EXTRA_LDFLAGS += $(if $(ICONV_FULL),-liconv,-Wl,--whole-archive -liconv -Wl,--no-whole-archive) -Wl,-rpath-link=$(STAGING_DIR)/usr/lib/pulseaudio

Maybe the path has to be adapted to \$(STAGING_DIR)/opt/lib/pulseaudio.

---

# MPD-full building from source

More information about building from source: [OpenWrt Buildroot - Usage](/docs/guide-developer/toolchain/start)

Based on the following reference:
[Help on compiling MPD full](https://forum.openwrt.org/viewtopic.php?pid=158385#p158385)
If you build from source you will only be able to select the MPD-mini from the make menuconfig interface.
To display and enable the full version in the menuconfig interface, you'll have to edit the MPD Makefile.

### Barrier Breaker and Chaos Calmer

1.  In your git clone directory edit `/openwrt/feeds/packages/sound/mpd/Makefile`.
    It is a good idea to make a backup copy before starting.
2.  Detect the area in the Makefile involved with the full MPD installation and edit `+libffmpeg` to `+libffmpeg-full`
3.  Save the file

Orignal file:

      TITLE+= (full)
      DEPENDS+= \
       +AUDIO_SUPPORT:alsa-lib \
       +libaudiofile +BUILD_PATENTED:libfaad2 +libffmpeg +libid3tag \
       +libmms +libogg +libsndfile +libvorbis
      PROVIDES:=mpd
      VARIANT:=full

Edited file:

      TITLE+= (full)
      DEPENDS+= \
       +AUDIO_SUPPORT:alsa-lib \
       +libaudiofile +BUILD_PATENTED:libfaad2 +libffmpeg-full +libid3tag \
       [+libmms +libogg +libsndfile +libvorbis
      PROVIDES:=mpd
      VARIANT:=full

Now if you start `make menuconfig`, you'll have the choice to build the full or the mini MPD version

---

# Building OpenWrt for Netgear WNDR3700

**WNDR3700 Developers' Overview**

This page contains, thus far, one user's complete notes on how to build a working OpenWrt WNDR3700 image from scratch, including working wireless on 2.4 GHz and 5 GHz bands. This page assumes that you are comfortable with building software and using kernel-style makefile systems, but otherwise, the page describes how to build the system from the ground up (including getting your base OS ready to build OpenWrt in the first place).

This page also describes the method used to unbrick a WNDR3700 (which does NOT require a serial cable), as well as optional instructions for manufacturing a serial cable (should you wish to use it for running ramdisk images).

These instructions are working fine as of the relatively-recent trunk revision 19064.

## Prerequisites

- [OpenWrt Buildroot – Installation](/docs/guide-developer/toolchain/install-buildsystem)
- [OpenWrt Buildroot – Usage](/docs/guide-developer/toolchain/start)

Until WNDR3700 support is integrated into a release, you'll need to execute the following commands to pull down the latest bleeding-edge code:

``` bash
cd ~
mkdir openwrt
cd openwrt
git clone git://git.openwrt.org/openwrt.git trunk
```

If you also want to check out the extra packages that can be installed on your system (including the helpful `ntpclient` and the *WebUI LuCI*), you can also run this:

``` bash
cd ~/openwrt/trunk
./scripts/feeds update packages luci
./scripts/feeds install -a -p luci
./scripts/feeds install <package_name>
```

## Configuration

Run the OpenWrt's BuildRoot menu configuration system to get started:

``` bash
cd ~/openwrt/trunk
make menuconfig
```

Make the following selections beyond the defaults. You might be able to get away with building things as kernel modules instead of built-in, but the author has not tried.

1.  Target System: Atheros AR71xx/AR7240/AR913x
2.  Target Profile: NETGEAR WNDR3700
3.  Target Images: if you want to build a ramdisk image, select "ramdisk" and ensure that LZMA compression is listed. Otherwise, leave the defaults alone (should be jffs2, squashfs and tgz). You seemingly need to rebuild everything except the toolchain if you want to switch from the ramdisk to a firmware image or vice versa.
4.  Image Configuration: Use this section to set up the defaults for the LAN ports on your router. If you don't have a serial cable connected to the router, you'll need to do this so that you can access the router once your newly-flashed code boots up. I recommend entering values for DNS server (on your ISP's network), LAN network mask (for the addresses to be doled out via DHCP), and LAN IP address (private IP address on your router's side).
    - eg. LAN DNS = (whatever your ISP tells you to use), LAN network mask=255.255.255.0, LAN IP address=192.168.0.1
    - [NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md): **pfk3** didn't do this step and by default OpenWrt was built with 192.168.1.1 & 255.255.255.0 for it's LAN IP/subnet.
    - [NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md): You still have to "\*" this option in order for the router to be on the network. You don't have to change the settings though
    - [NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md): It is not possible to set this feature in the latest [attitude adjustment](https://dev.openwrt.org/changeset/31258/) release. See this [mailing list post](http://www.mail-archive.com/openwrt-devel@lists.openwrt.org/msg15992.html) for more information.
5.  Network -\> CRDA = YES (compile as built-in package with "\*", not as a module with "M")
6.  Kernel Modules -\> LED Modules -\> kmod-leds-wndr3700-usb = YES (compile as built-in driver as "\*", not as a module with "M")
7.  Kernel Modules -\> Wireless Drivers -\> kmod-ath -\> Configuration -\> Force Atheros drivers to respect the user's regdomain settings = YES

If you want to slap a USB memory stick in the back of your router to allow you to install many more packages read the pages [USB Basic Support](/docs/guide-user/storage/usb-installing) and [USB Storage](/docs/guide-user/storage/usb-drives).

A sample .config file is linked to below. If you use this, at the very least, you will need to edit the DNS server address listed in the "image configuration" step (see \#4 above).

Type

    make

and it should merrily build away for at least a good half hour (or more). When you're done, you should have the resulting binaries stored in `~/openwrt/trunk/bin/ar71xx`. As of trunk revision 25119, separate binaries will be created for the WNDR3700v1 and WNDR3700v2.

## Installation

Please see [WNDR3700 - Installation](toh/netgear/wndr3700#installation) or [OpenWrt - Installation](/docs/guide-user/installation/generic.flashing)

---

# Building OpenWrt Kernel for Debian System

For now this page serves to keep some notes about using OpenWrt kernels with Debian distribution.

## Floating Point Unit (MIPS)

If you boot OpenWrt kernel and expects it to start init but you see a kernel panic:

`Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000004`

OpenWrt userland packages are compiled with soft-FPU instructions by default. (The floating point math is emulated by the compiler during compile time.)

Debian binaries (jessie) are compiled with hard FPU instructions. As most embedded devices do not have FPUs, it's usually necessary for the kernel to emulate them in order for these instructions to be executed correctly. Since OpenWrt makes use of soft-FPU, the FPU emulation is turned off in the kernel by default. Inability to execute FP instructions is a possible reason for the crash.

To compile the kernel with FPU emulation, in kernel configuration check that you set CONFIG_MIPS_FPU_EMULATOR=y. See [use-buildsystem#Kernel configuration (optional)](/docs/guide-developer/toolchain/use-buildsystem#Kernel configuration (optional)).

## udev

Debian uses udev to populate /dev. For udev to work, devtmpfs pseudo filesystem must be enabled. Check that CONFIG_DEVTMPFS=y in kernel_menuconfig and CONFIG_KERNEL_DEVTMPFS=y in menuconfig.

## SELinux

Debian bins (e.g. init) are compiled with SELinux support. Init will try to initialise SELinux when starting. Since SELinux is not enabled in OpenWrt kernel, init might display a failure:

`Mount failed for selinuxfs on /sys/fs/selinux: No such file or directory`

This message is safe to ignore. Basically selinux initialisation attempts to mount the selinux filesystem but fails. Init ignores this failure and carries on booting as long as you do not provide enforcing=1 in kernel cmdline.

## IKConfig

The OpenWrt system messes with the kernel .config so you might not end up with the same options you set when you run kernel_menuconfig. If you want to know the final kernel options, look in your build_dir (e.g. build_dir/target-mips_34kc_glibc-2.19/linux-ar71xx_mikrotik/linux-3.18.23/.config). Alternatively if you can afford a bigger kernel, set CONFIG_IKCONFIG=y and CONFIG_IKCONFIG_PROC=y in kernel_menuconfig so that the kernel .config is saved in the kernel itself.

---

# Setting up a build VM in VirtualBox

The OpenWrt build VM will run on a Debian OS in VirtualBox. You are required to have a 64-bit OS and at least 8 GB free disk space.

## Instructions

### 1. Get VirtualBox

This program will let you run a virtual Linux machine on your PC. Download the newest version from [virtualbox.org](https://www.virtualbox.org/) and install using default settings.

### 2. Get a Debian image

Download the newest VirtualBox (VDI) 64-bit Debian image (currently 12 Bookworm) from [osboxes.org](http://www.osboxes.org/debian/) and unpack it using 7zip. 7zip can be downloaded from [7-zip.org](http://www.7-zip.org/).

### 3. Install the virtual machine

1.  Start Oracle VM VirtualBox
2.  Click New
3.  Name: OpenWrtDev
4.  Type: Linux
5.  Version: Debian (64-bit). See [here](https://superuser.com/questions/866962/why-does-virtualbox-only-have-32-bit-option-no-64-bit-option-on-windows-7) if 64-bit is not available.
6.  Hard Disk: Select "Use an existing virtual hard disk file" and choose the Debian .vdi file you just unpacked.
7.  Click Create
8.  Right click on the OpenWrtDev image and click Settings
9.  Select General, Advanced, Shared Clipboard: Bidirectional
10. Select Shared Folders
11. Right click Machine Folders and select Add Shared Folder
12. Folder path: Click the down arrow, select Other and then the folder you want to share with the virtual Debian machine (for transferring the firmware).
13. Folder Name: Shared
14. Select Auto-mount

### 4. Initial Debian setup

1.  Select the OpenWrtDev image and click Start
2.  Wait for it to finish booting and click osboxes.org
3.  Password: osboxes.org
4.  Click Activities, type term in the search field and click terminal

The interface for changing the keyboard is a bit weird, but you can find the correct place like this:

1.  Click Activites, type reg, click Region & Language
2.  Click + under Input Sources and then the vertical dots
3.  Click Other, select the language and click Add. You can now delete English.

From now on, whenever you should be in the terminal to type a command the syntax will look like this:

``` bash
ls -l
```

This means you should type `ls -l` and press enter (try it).

Follow up questions with obvious answers like typing the passsword (osboxes.org) og confirming with y will not be included specifically in this guide. Cut and paste will unfortunately not work at this moment.

``` bash
su -
nano /etc/apt/sources.list
```

You are now editing the list of servers to get updates from.

- Delete the lines containing "deb cdrom". Lines can be deleted with ctrl-k.
- From the last two lines, remove the leading \# and space, and the -updates after bullseye. They should now look like this:

    deb http://deb.debian.org/debian/ bullseye main contrib
    deb-src http://deb.debian.org/debian/ bullseye main contrib

- Type ctrl-x and then y and then enter to save and exit.

``` bash
su -
apt update
apt dist-upgrade
apt install linux-headers-amd64 make sudo
reboot
```

Log in and open the terminal again when it has rebooted.

Click Devices (top line), select the last option (Install Guest Additions). The automatic install does not seem to work, so it doesn't matter if you select cancel or run.

``` bash
su -
sh /media/cdrom/VBoxLinuxAdditions.run
```

Finally, allow osboxes to use sudo (takes effect next time osboxes logs in).

``` bash
adduser osboxes sudo
```

After this you will need to start the machine again.

Now you can change to a higher resolution so you get a larger window if you like:

1.  Click Activities, type disp in the search field.
2.  Click Displays, VBX
3.  Select a different resolution

Your virtual Debian machine should now be set up correctly for following the rest of the guide. Congratulations. As a bonus, you now have a fully functional Linux computer that you can use for anything, and with the added safety of running it as a virtual machine. If you let the resolution match your monitor and select View/Full-screen mode there is almost no difference from a standalone Linux computer.

---

# Configuration in scripts

![howto_links#config-network-device&noheader&nofooter&noeditbutton](/section>meta/infobox/howto_links#config-network-device&noheader&nofooter&noeditbutton)

OpenWrt offers a set of standard shell procedures to interface with [UCI](/docs/guide-user/base-system/uci) in order to efficiently read and process configuration files from within shell scripts. This is most likely useful for writing startup scripts in `/etc/init.d/`.

## Loading

To be able to load UCI configuration files, you need to include the common functions with:

``` bash
. /lib/functions.sh
```

(If your startup script starts with:

``` bash
#!/bin/sh /etc/rc.common
```

then you do not need to include `/lib/functions.sh` directly, because `/etc/rc.common` includes `/lib/functions.sh` by default.)

Then you can use `config_load name` to load config files.

The function first checks for `name` as absolute filename and falls back to loading it from `/etc/config/` (which is the most common way of using it).

## Callbacks

The first method for parsing an UCI config file is through **callbacks**, which will be called for each `section`, `option` and `list` encountered during parsing.

You can define three callbacks: `config_cb()`, `option_cb()`, and `list_cb()`. You need to define these functions before calling `config_load`, but after including `/lib/functions.sh`.

Additionally, you may call `reset_cb()` to reset all three callbacks to no-op functions.

### `config_cb` callback

The `config_cb` procedure is called every time a UCI section heading is encountered during parsing. Also an extra call to `config_cb` (without any argument) is generated after `config_load` is done. This may be useful if you accumulate something while parsing options (see below) and want to do something with the accumulated values (write them to a file, ...) when a section has been entirely parsed.

When called, the procedure receives two arguments:

1.  Type, the section type, e.g. `interface` for `config interface wan`
2.  Name, the section name, e.g. `wan` for `config interface wan` or an autogenerated ID like `cfg13abef` for anonymous sections like `config route`

``` bash
config_cb() {
    local type="$1"
    local name="$2"
    # commands to be run for every section
}
```

Also an extra call to `config_cb` (without a new section) is generated after config_load is done - this allows you to process sections both before and after all options were processed.

### `option_cb` callback

Similar to `config_cb`, the `option_cb` procedure is called each time a UCI option is encountered.

When called, the procedure receives two arguments:

1.  Name, the option name, e.g. `ifname` for `option ifname eth0`
2.  Value, the option value, e.g. `eth0` for `option ifname eth0`

``` bash
option_cb() {
    local name="$1"
    local value="$2"
    # commands to be run for every option
}
```

Within the callback, the ID of the current section is accessible via the `$CONFIG_SECTION` variable.

You can define `option_cb` inside `config_cb`: this allows to define different `option_cb` callbacks based on the section type. This allows you to process every single config section based on its type individually.

### `list_cb` callback

`list_cb` works exactly like `option_cb` above, but gets called each time a `list` item is encountered.

When called, the procedure receives two arguments:

1.  Name, the list name, e.g. `server` for `list server 192.168.42.1`
2.  Value, the list value, e.g. `192.168.42.1` for `list server 192.168.42.1`

``` bash
list_cb() {
    local name="$1"
    local value="$2"
    # commands to be run for every list item
}
```

Each item of a given list generates a new call to `list_cb`.

## Iterating (config_foreach)

An alternative approach to callback based parsing is iterating the configuration sections with the `config_foreach` procedure.

The `config_foreach` procedure takes at least one argument:

1.  Function, name of a previously defined procedure called for each encountered section
2.  Type (optional), only iterate sections of the given type, skip others
3.  Additional arguments (optional), all following arguments are passed to the callback procedure as-is

In the example below, the `handle_interface` procedure is called for each `config interface` section in `/etc/config/network`. The string `test` is passed as second argument on each invocation.

``` bash
handle_interface() {
    local config="$1"
    local custom="$2"
    # run commands for every interface section
}

config_load network
config_foreach handle_interface interface test
```

Note that `config_foreach` will iterate through all sections without regard to the callback function's return value.

Within the per-section callback, the `config_get` or `config_set` procedures may be used to read or set values belonging to the currently processed section.

## Reading options (config_get)

The `config_get` procedure takes at least three arguments:

1.  Name of a variable to store the retrieved value in
2.  ID of the section to read the value from
3.  Name of the option to read the value from
4.  Default (optional), value to return instead if option is unset

``` bash
#...
# read the value of "option ifname" into the "iface" variable
# $config contains the ID of the current section
local iface
config_get iface "$config" ifname
echo "Interface name is $iface"
#...
```

## Setting options (config_set)

The `config_set` procedure takes three arguments:

1.  ID of the section to set the option in
2.  Name of the option to assign the value to
3.  Value to assign

``` bash
...
# set the value of "option auto" to "0"
# $config contains the ID of the current section
config_set "$config" auto 0
...
```

Note:

- values changed with `config_set` are only kept in memory. Subsequent calls to `config_get` will return the updated values but the underlying configuration files are *not* altered. If you want to alter values, use the uci\_\* functions from /lib/config/uci.sh which are automatically included by /etc/functions.sh.
- config_set is arcane and buggy (config_get is fine), use "uci set" instead.

## Direct access

If the name of a configuration section is known in advance (it is named), options can be read directly without using a section iterator callback.

The example below reads "option proto" from the "config interface wan" section.

``` bash
...
local proto
config_get proto wan proto
echo "Current WAN protocol is $proto"
...
```

## Reading lists

Some UCI configurations may contain `list` options in the form:

    ...
    list network lan
    list network wifi
    ...

Calling `config_get` on the `network` list will return the list values separated by space, `lan wifi` in this example.

However, this behaviour might break values if the list items itself contain spaces like illustrated below:

    ...
    list animal 'White Elephant'
    list animal 'Mighty Unicorn'
    ...

The `config_get` approach would return the values in the form `White Elephant Mighty Unicorn` and the original list items are not clearly separated anymore.

To circumvent this problem, the `config_list_foreach` iterator can be used. It works similar to `config_foreach` but operates on list values instead of config sections.

The `config_list_foreach` procedure takes at least three arguments:

1.  ID of the section to read the list from
2.  Name of the list option to read items from
3.  Procedure to call for each list item
4.  Additional arguments (optional), all following arguments are passed to the callback procedure as-is

``` bash
# handle list items in a callback
# $config contains the ID of the section
handle_animal() {
    local value="$1"
    # do something with $value
}

config_list_foreach "$config" animal handle_animal
```

Note: for editing value, use the [uci](/docs/guide-user/base-system/uci) command line tool.

## Reading booleans

Boolean options may contain various values to signify a *true* value like `yes`, `on`, `true`, `enabled` or `1`. If in doubt, read [the source](https://github.com/openwrt/openwrt/blob/main/package/base-files/files/lib/functions.sh) and scan for `get_bool`.

The `config_get_bool` procedure simplifies the process of reading a boolean option and casting it to a plain integer value (`1` for *true* and `0` for *false*).

At least three arguments are expected by the procedure:

1.  Name of a variable to store the retrieved value in
2.  ID of the section to read the value from
3.  Name of the option to read the value from
4.  Default (optional), boolean value to return if option is unset

Note that there is no equivalent `set` procedure, so you must use care when setting values to ensure you are using one of the values defined above.

(For the equivalent LuCI JS function, see [LuCI.uci.get_bool](https://openwrt.github.io/luci/jsapi/LuCI.uci.html#get_bool).)

## Should I use callbacks or explicit access to options?

It depends on what you want to parse.

### Use case and example for callbacks

If, for a given section, all options should be treated in the same way (say, write them to a config file), whatever their order or name, then callbacks are a good option. It allows you to parse all options without having to know their name in advance.

For instance, consider this script:

``` bash
config_cb() {
    local type="$1"
    local name="$2"
    if [ "$type" = "mysection" ]
    then
        option_cb() {
            local option="$1"
            local value="$2"
            echo "${option//_/-} $value" >> /var/etc/myfile.conf
        }
    else {
        option_cb() { return; }
    }
}
```

This would parse a configuration like this one:

    config mysection foo
        option link_quality auto
        option rxcost 256
        option hello_inverval 4

And generate a file containing:

    link-quality auto
    rxcost 256
    hello-interval 4

### Use case and example for direct access

On the other hand, if different options play a very different role, then it may be more convenient to pick each option explicitly.

For instance, [babeld](http://www.pps.univ-paris-diderot.fr/~jch/software/babel/) has the following syntax for filters:

    {in|out|redistribute} selector* [allow|deny|metric n]

where a selector can be one of:

    local
    ip prefix
    proto p
    if interface
    ...

At most one instance of each selector type is allowed in a filter. The UCI configuration looks like this:

    config filter
        option ip '172.22.0.0/15'
        option local 'true'
        option type 'redistribute'
        option action 'metric 128'

The result of this section should be:

    redistribute ip 172.22.0.0/15 local metric 128

That is, the type should come first, then selectors (with a special case for `local`, which doesn't take an argument), and finally the action. The basic parsing method is the following:

``` bash
parse_filter() {
    local section="$1"
    local _buffer
    local _value

    config_get _value "$section" "type"
    append _buffer "$_value"

    config_get _value "$section" "ip"
    append _buffer "ip $_value"
    config_get _value "$section" "proto"
    append _buffer "proto $_value"
    ...

    config_get_bool _value "$section" "local" 0
    [ "$_value" -eq 1 ] && append _buffer "local"

    config_get _value "$section" "action"
    append _buffer "$_value"

    echo "$_buffer" >> /var/etc/babeld.conf
}
config_load babeld
config_foreach parse_filter filter
```

### Mixing the two styles

Of course, it is possible to mix the two styles of parsing, for instance parsing one section with callbacks and another section explicitly. Don't forget to reset or unset the callbacks (`reset_cb` or `option_cb() { return; }`) for sections you don't want to parse with callbacks.

---

# Create a Cmake package in OpenWrt

In the [Meson tutorial](/docs/guide-developer/creating_a_meson_based_package), we learned how to create a Meson package with a detailed guide. Since Cmake and Meson have similar roots, this tutorial will only focus on their differences.

## CMakeLists.txt

To begin, let's create a CMake project. The `main.c` file for this project will be the same as the one in the Meson tutorial, which includes a single `"Hello, World"` program. However, in order to use CMake, we need to include a `CMakeLists.txt` file. The most basic CMake file is presented here for simplicity.

``` cmake
cmake_minimum_required(VERSION 3.1...3.27)

project(
  hellocmake
  VERSION 1.0
  LANGUAGES C)

add_executable(hellocmake main.c)
install(TARGETS hellocmake DESTINATION /usr/bin)
```

## Makefile

The `Makefile` is very similar to other OpenWrt-based makefiles. The only difference is that it includes `cmake.mk` instead of `meson.mk`:

``` Makefile
include $(TOPDIR)/rules.mk

PKG_NAME:=hellocmake
PKG_VERSION:=0.1
PKG_RELEASE:=1

SOURCE_DIR:=/media/workspace/packages/cmakepackages/hellocmake
PKG_BUILD_DIR:=$(BUILD_DIR)/hellocmake-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/hellocmake
    CATEGORY:=custom
    TITLE:=Simple Cmake package
    #DEPENDS:=+libstdcpp +ixwebsocket +libatomic
endef

define Package/hellocmake/description
    hellocmake is a simple application to demonstrate OpenWrt build system with cmake packages
endef

define Package/hellocmake/install
    $(INSTALL_DIR) $(1)/usr/bin
    $(INSTALL_BIN) $(PKG_BUILD_DIR)/hellocmake $(1)/usr/bin/
endef

$(eval $(call BuildPackage,hellocmake))
```

## Passing Cmake options

In order to pass `Cmake` options, we can use the following syntax in the `Makefile`

``` Makefile
CMAKE_OPTIONS+= \
    -D<OPTION>bool=OFF
```

For example:

``` Makefile
CMAKE_OPTIONS+= \
    -DBUILD_TESTING:bool=OFF
```

## Build

To enable this package, open the configuration menu by typing `make menuconfig` in the command line. From there, go to `custom` → `hellocmake` and select the package.

If everything goes smoothly, the package that is built will be located in `<BIN_DIR>/packages/<target>/cmakepackages/`.

For instance:

``` bash
hellocmake_0.1-1_arm_cortex-a7_neon-vfpv4.ipk
```

---

# Create Meson-based packages in OpenWrt

This tutorial provides a step-by-step guide to creating and installing meson-based packages in OpenWrt. We assume that the source code is local, but the process is the same for other cases such as Git, SVN, etc.

## General instructions in building packages

The `include` directory in OpenWrt contains information about the build system for different types of packages. Here, For example, `meson.mk` in the `include` directory provides useful insights:

``` bash
# To build your package using meson:
#
# include $(INCLUDE_DIR)/meson.mk
# MESON_ARGS+=-Dfoo -Dbar=baz
#
# To pass additional environment variables to meson:
#
# MESON_VARS+=FOO=bar
#
.
.
.
#
# same for Build/Compile and Build/Install
#
# Host packages are built in the same fashion, just use these vars instead:
#
# MESON_HOST_ARGS+=-Dfoo -Dbar=baz
# MESON_HOST_VARS+=FOO=bar
```

To create a Meson package for OpenWrt, we need to perform a few steps. Firstly, we should include `$(INCLUDE_DIR)/meson.mk` in the `Makefile`, which will enable us to use Meson build system within the OpenWRT environment. Secondly, we can pass Meson arguments to specify various configuration options by using the `MESON_ARGS+=<arg>` syntax. This is especially useful when we want to customize build settings, such as choosing a specific compiler or setting optimization flags. Additionally, we can also pass environmental variables to Meson by using `MESON_VARS`. This allows us to define environment-specific settings or pass additional information to the build system. By following these steps, we can create a robust and flexible Meson package for OpenWRT that meets our specific requirements.

## A simple Meson package

Meson is a build system that is designed to optimize and simplify the process of building software. By creating a Meson package, we can take advantage of this build system to automate the process of building and installing our software package. To begin with, we will be creating a single Meson package. This package will be located in the directory path `/media/workspace/packages/mesonsexmpl/`.

``` bash
mkdir /media/workspace/packages/mesonsexmpl/helloworld
cd /media/workspace/packages/mesonsexmpl/helloworld
```

Next, we will create the required files. These files are `main.c` source file and `meson.build` configuration file.

``` bash
touch main.c  meson.build
```

### main.c

To demonstrate a basic scenario, we will be populating the `main.c` file with a straightforward yet classic `"Hello World!"` message.

``` c
// main.c
#include <stdio.h>

int main(int argc, char** argv)
{
    printf(“Hello World\n”);
    return 0;
}
```

### meson.build

For the `meson.build` file, we use the simple build file provided by the meson tutorial:

``` cmake
# meson.build
project('helloworld', 'c')
executable('helloworld', 'main.c')
```

### Makefile

The `Makefile` plays a crucial role in our `helloworld` package, as it provides instructions for compiling and building the software. Without it, the program would not be able to run properly. To ensure that our `helloworld` package is functional, we have created a `Makefile` that outlines the necessary steps for building the program. You can find the `Makefile` below.

``` makefile
include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/meson.mk
include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/nls.mk
# Name, version and release number
# The name and version of your package are used to define the variable to point to the build directory of your package: $(PKG_BUILD_DIR)
PKG_NAME:=helloworld
PKG_VERSION:=1.0
PKG_RELEASE:=1

# Source settings (i.e. where to find the source codes)
# This is a custom variable, used below
SOURCE_DIR:=/media/workspace/packages/mesonsexmpl/helloworld/src

# Package definition; instructs on how and where our package will appear in the overall configuration menu ('make menuconfig')
define Package/helloworld
  SECTION:=examples
  CATEGORY:=Examples
  TITLE:=Hello, World!
endef

# Package description; a more verbose description on what our package does
define Package/helloworld/description
  A simple "Hello, world!" -application.
endef

define Package/helloworld/install
    $(INSTALL_DIR) $(1)/usr/bin/
    $(INSTALL_BIN)  $(PKG_BUILD_DIR)/openwrt-build/helloworld $(1)/usr/bin

endef

$(eval $(call BuildPackage,helloworld))
```

In order to incorporate our new package, we will need to make some changes to the `feeds.conf` file that is located at the root directory of OpenWrt source code . By making these modifications, we can ensure that our new package is successfully added and integrated into the system.

``` bash
src-link mesonpackages /media/workspace/packages/mesonsexmpl
```

### feeds.conf

Next, we need to update the package feed.

    ./scripts/feeds update mesonpackages
    ./scripts/feeds install -a -p  mesonpackages

Once we have updated the necessary feeds, the next step is to select the correct package for building. To do this, we must open the configuration menu by typing `make menuconfig` in the command line. From there, we should look for the `helloworld` package and select it to proceed with the build process.

To finish building the package, we need to execute the build command. Running this command will compile all the necessary files and create the final package that can be used for deployment or distribution.

``` bash
make package/helloworld/compile
```

If everything goes smoothly, the package that is built will be located in ''\<BIN_DIR\>/packages/\<target\>/mesonpackages/packages'. For instance:

    helloworld_1.0-1_arm_cortex-a7_neon-vfpv4.ipk

---

# Debugging

Debugging hardware can be tricky especially when doing kernel and drivers development. It might become handy for you to add serial console to your device as well as using JTAG to debug your code.

## Serial Port

-\> [port.serial](/docs/techref/hardware/port.serial)

## JTAG

-\> [port.jtag](/docs/techref/hardware/port.jtag)

## GDB

:!: -\> [gdb](/docs/guide-developer/gdb) a very short introduction on the GNU Debugger

## perf/oprofile cpu profiling

-\> <http://false.ekta.is/2012/11/cpu-profiling-applications-on-openwrt-with-perf-or-oprofile/>

## Wireless

When encountering wireless bugs, such as connection drop or wpa rekeying issues, it is possible to remotely run `tcpdump` in order to capture wireless management traffic for later analysis of the communication leading to the problem.

### Capture Management Traffic

The command below will spawn a monitor interface with a mac80211 based driver, start `tcpdump` and save the captured data locally into `/tmp`:

``` bash
ssh root@192.168.1.1 'grep -q mon0 /proc/net/dev || /usr/sbin/iw phy phy0 interface add mon0 type monitor;
    /sbin/ifconfig mon0 up; /usr/sbin/tcpdump -s 0 -i mon0 -y IEEE802_11_RADIO -w -' > /tmp/wifi.pcap
```

A smaller alternative to `tcpdump` is the `iwcap` utility. Its MIPS binary only ~5KB large and it does not require `libpcap` to function. It also supports the filtering of data frames through the `-D` switch to cut down the amount of captured traffic;

``` bash
ssh root@192.168.1.1 'grep -q mon0 /proc/net/dev || /usr/sbin/iw phy phy0 interface add mon0 type monitor;
    /sbin/ifconfig mon0 up; /usr/sbin/iwcap -i mon0 -s' > /tmp/wifi.pcap
```

### Logging hostapd behaviour

Note that recent versions of openwrt ship with a version of hostapd which has verbose debug messages disabled in order to save on space (see <https://dev.openwrt.org/ticket/15658> ).

\<del\>To enable debug you need to install the debug build of hostapd from the packages for your router (package name hostapd), having first removed the cut-down version:

``` bash
opkg remove wpad-mini
[download the wpad-debug package for your router to /tmp]
opkg install /tmp/wpad-debug*.ipk
```

\</del\>

Increase the log level for hostapd:

    # Levels (minimum value for logged events):
    #  0 = verbose debugging
    #  1 = debugging
    #  2 = informational messages
    #  3 = notification
    #  4 = warning"

... the default is "informational messages". The example below shows you how to change this to "debugging".

Check the log level currently being used:

``` bash
root@OpenWrt:~# ps | grep hostapd
 6948 root      1784 S    /usr/sbin/hostapd -P /var/run/wifi-phy1.pid -B /var/run/hostapd-phy1.conf
 6987 root      1784 S    /usr/sbin/hostapd -P /var/run/wifi-phy0.pid -B /var/run/hostapd-phy0.conf
 7019 root      1448 S    grep hostapd
```

let say for the sake of argument you're only interested in addressing a problem with the phy0 hostapd. First check the current level for this hostapd:

``` bash
root@OpenWrt:~# grep _level /var/run/hostapd-phy0.conf
logger_syslog_level=2
logger_stdout_level=2
```

... log level 2 is selected. Let's change this:

``` bash
root@OpenWrt:~# uci set wireless.radio0.log_level=1
root@OpenWrt:~# uci commit wireless
root@OpenWrt:~# wifi up
root@OpenWrt:~# grep _level /var/run/hostapd-phy0.conf
logger_syslog_level=1
logger_stdout_level=1
```

... and we can see that the level has been changed. The logread command will now show brief debug messages like those below:

``` bash
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 MLME: MLME-REASSOCIATE.indication(20:16:d8:db:aa:56)
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 MLME: MLME-DELETEKEYS.request(20:16:d8:db:aa:56)
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 WPA: event 1 notification
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 WPA: start authentication
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 IEEE 802.1X: unauthorizing port
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 WPA: sending 1/4 msg of 4-Way Handshake
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 WPA: received EAPOL-Key frame (2/4 Pairwise)
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 WPA: sending 3/4 msg of 4-Way Handshake
Tue Apr 22 11:35:41 2014 daemon.debug hostapd: wlan0: STA 20:16:d8:db:aa:56 WPA: received EAPOL-Key frame (4/4 Pairwise)
```

... you may want to then setup remote logging via syslog to another computer by setting a logfile (warning - this won't be auto-rotated, so make sure it doesn't fill up a vital filesystem).

``` bash
uci set system.@system[0].log_file=[path-to-my-logfile]
uci commit
[reboot required]
```

or alternatively, if you're able to, it might be better to use system.@system\[0\].log_ip to log to a remote machine (which must be running an appropriate listener e.g. rsyslogd - see <https://forum.openwrt.org/viewtopic.php?id=11912>).

If you wish to debug on the command line instead, you may be able to do-so using a command like this:

``` bash
kill `cat /var/run/wifi-phy0.pid` ; /usr/sbin/hostapd -dd -P /var/run/wifi-phy0.pid  /var/run/hostapd-phy0.conf
```

... use the output of ps above to create the necessary commandline - remove the '-B' argument to stop hostapd forking into the background, and add '-dd' to verbose debug to stdout.

depending on your hardware and interface state, it may be necessary to create or re-create the relevant wlan device before starting hostapd e.g.

``` bash
iw dev wlan0 del
iw phy phy0 interface add wlan0 type managed
```

## Add and modify compiler debug flags

:!: The "Compile with debug" entry in advanced developer menu enables "-g3" compile option.

:!: You have to disable \_sstrip\_ to keep debug information.

Note, if you just want to build a single package unstripped, try, "make package/foo/compile STRIP=true" Also, unstripped binaries are placed in "staging_dir/target-\*/root-\*/" where your host side tools can use them. (Remember, gdbserver can attach to the stripped binary, while gdb loads the unstripped binary) see [gdb](/docs/guide-developer/gdb)

Alternatively: You can add or modify "Custom Target Options" like add "-g3 -ggdb3"

:!: Be aware there are default compiler options defined in include/[target.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) for example ("-Os -pipe")

:!: Some packets might overwrite or not use the flags. Check your compile log.

Additional tips:

- check with different gcc versions
- There is "-O0" to disable compiler optimizations.
- "-Wall -Wextra" might provide useful warnings
- see <https://gcc.gnu.org/bugs/>

---

# Device Tree Usage in OpenWrt (DTS)

Current development (2019) uses kernel based on Device Tree (DT) files (.dts, .dtsi, .dtb) rather than the older "mach" files.

This page tries to pull together some of the knowledge about DT usage and conventions used by the OpenWrt project.

## References

- <https://elinux.org/Device_Tree_Reference>
- <https://elinux.org/Device_Tree_Mysteries>
- <https://elinux.org/Device_Tree_Source_Undocumented>
- <https://developer.toradex.com/device-tree-customization>
- <https://events.static.linuxfound.org/sites/events/files/slides/petazzoni-device-tree-dummies.pdf>
- Linux binding defintions, in source or online at <https://www.kernel.org/doc/Documentation/devicetree/bindings/>
- OpenWrt wiki on Defining software partitions in all DTS targets
- <https://devicetree-specification.readthedocs.io/en/latest/source-language.html>
- <https://github.com/devicetree-org/devicetree-specification/blob/master/source/source-language.rst>

## General

Use c-style `#include` instead of DT-specific `/include/`

If possible, license the content as `// SPDX-License-Identifier: GPL-2.0-or-later OR MIT`

Use tab indentation -- see also <https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Documentation/process/coding-style.rst>

While upstream, architecture-specific .dtsi files *may* remain stable (such as `qcom-ipq4019.dtsi`), board-specific files (such as `qcom-ipq4019-ap.dk07.1.dtsi`) may change, causing breakage to specific devices, perhaps just one, that may go unnoticed. At least if, for example, the generic IPQ4019 .dtsi changes, there is a chance that it would be seen quickly by or more of the boards that use that SoC.

## Defining software partitions in all DTS targets

Partition nodes should be named `partition@<start address>`

Boot loader binaries, firmware, and configuration partitions (such as "ART") should be marked as read-only. This helps reduce the risk of users following outdated or questionable advice in using low-level writes. Users advanced enough to need to write these partitions should be sophisticated enough to be able to compile their own kernel to do so.

The MTD labels of "firmware" and "ubi" have special meaning to the OpenWrt kernel.

See below on supplying the proper "compatible" label so that the OpenWrt kernel can properly "split" the partition and `CONFIG_MTD_SPLIT_FIRMWARE` is not needed. (note that `CONFIG_MTD_SPLIT_UIMAGE_FW` is still required!)

 this article was an email sent to the OpenWrt-devel mailing list by OpenWrt dev Rafał Miłecki
**Subject:** \[OpenWrt-Devel\] Specifying "firmware" partition format on all DTS targets
**Date:** Sat, 24 Nov 2018 11:32:25 +0100

Parsing "firmware" partition (to create kernel + rootfs) was implemented using OpenWrt downstream code enabled by CONFIG_MTD_SPLIT_FIRMWARE.
With recent upstream mtd changes we can do it in a more clean way for DTS targets. It just requires adding a proper "compatible" string to the "firmware" partition node.

I'd like all DTS supported devices to use that "compatible" and disable CONFIG_MTD_SPLIT_FIRMWARE eventually.

*Wiki note: This objective may be a challenge for dual-firmware units as the partition to be split will be different depending on which was selected by the boot loader.*

1\) Default uimage
If you see:
2 uimage-fw partitions found on MTD device firmware
please use "denx,uimage"; e.g.
`partition@70000 {
        label = "firmware";
        reg = <0x070000 0x790000>;
        compatible = "denx,uimage";
};`

2\) Netgear's uimage
If you see:
2 netgear-fw partitions found on MTD device firmware
please use "netgear,uimage"; e.g.
`partition@70000 {
        label = "firmware";
        reg = <0x070000 0xf80000>;
        compatible = "netgear,uimage";
};`

3\) TP-LINK's firmware
If you see:
2 tplink-fw partitions found on MTD device firmware
please use "tplink,firmware"; e.g.
`firmware@20000 {
        label = "firmware";
        reg = <0x020000 0xfd0000>;
        compatible = "tplink,firmware";
};`

Please kindly:
1) Use that for all newly added devices
2) Port already supported devices you can test
--
Rafał

---

# Using Dependencies

## Topic

A typical package Makefile will contain a section like:

    define Package/tcpdump/default
      SECTION:=net
      CATEGORY:=Network
      DEPENDS:=+libpcap
      TITLE:=Network monitoring and data acquisition tool
      URL:=http://www.tcpdump.org/
    endef

This page talks about what the DEPENDS:= line should look like.

## Dependency types

- If you specify a package name without any ornaments then that means that the current package cannot be selected unless the package named in enabled. e.g., in `tcpdump` above,

    DEPENDS:=libpcap

would mean that tcpdump would not be shown as possible to be selected unless `libpcap` were already selected

     * If you say ''+package'' that means if the current package is selected, it will cause ''package'' to be selected.  This is the case with ''tcpdump'' above.  It says that if ''tcpdump'' is selected, then select ''libpcap''. e.g.

    DEPENDS:=+libpcap

     * If you say ''+PACKAGE_packageb:packagec'', it means that ''packagec'' will only get selected by the current package (e.g. ''tcpdump'') if ''packageb'' is enabled. e.g.

    DEPENDS:=+PACKAGE_arpd:libpcap

would mean that if `tcpdump` was selected, then if `arpd` was also selected, select `libpcap`.

Useful is the negation ! to only select a Package if it's not build into busybox

    DEPENDS:=+!BUSYBOX_CONFIG_HOSTNAME:net-tools-hostname

This means select net-tools-hostname only if hostname is not build into busybox. But don't try it the other way around, see the last case.

     * If you say ''@SYMBOL'' that means that CONFIG_SYMBOL must be defined by OpenWrt in order for the ''package'' to be available for selection. e.g

    DEPENDS:=@USB_SUPPORT

would mean that the package wouldn't even appear unless config symbol CONFIG_USB_SUPPORT was defined, for example by the package `usb-core`

     * If you say ''+@SYMBOL'' that means if the current package is selected, it will cause CONFIG_SYMBOL to be selected.

    DEPENDS:=+@KERNEL_DEBUG_FS

would mean that the if you select the package, it would automatically set the config symbol CONFIG_KERNEL_DEBUG_FS. Beware: This works while compiling your own image. If you install this package on a running box with opkg, this dependency is not checked!

     * Don't be so clever and combine everything:

    DEPENDS:=+@!PACKAGE_net-tools-hostname:BUSYBOX_CONFIG_HOSTNAME

Here we select the Symbol BUSYBOX_CONFIG_HOSTNAME if the package net-tools-hostname is not selected. The @ belongs to BUSYBOX_CONFIG_HOSTNAME. This works while compiling your own image, but the resulting ipkg depends on the unresolvable BUSYBOX_CONFIG_HOSTNAME, so your package cannot be installed later on a box with opkg.

As busybox can never be extended on a working box, always select an installable package when a busybox applet is not selected.

    DEPENDS:=+!BUSYBOX_CONFIG_HOSTNAME:net-tools-hostname

### Special Notes

It is possible to do select and depend on packages outside the usual `DEPENDS` definition. If, in the package `Makefile`, you have a definition:

    define Package/package-name/config
        ...config stuff
    endef

then you can include the following directives.

| Directive                    | Meaning                                                                                   |
|------------------------------|-------------------------------------------------------------------------------------------|
| select package               | Selects a package if this package is selected                                             |
| select package if packageb   | Selects a package if packageb is selected as well as this package                         |
| select package if SYMBOL     | Selects a package if CONFIG_SYMBOL is defined                                             |
| depends packageb             | This package depends on packageb (i.e. won't even show up, unless packageb is selected)   |
| depends packageb if packagec | This package depends on packageb if packagec is selected                                  |
| select SYMBOL                | Sets a symbol to y if this package is selected (.e.g. select BUSYBOX_FEATURE_MKSWAP_UUID) |
| select SYMBOL if packageb    | Like select SYMBOL but only if packageb is selected                                       |
| select SYMBOL if SYMBOL2     | Like select SYMBOL but only if SYMBOL2 is defined                                         |

The author is not aware of the ability to do `depends SYMBOL`.

Note that the `if` directives may also include &&, \|\|, !, and uses parentheses () to use logical expression for AND (&&), OR (\|\|) and NOT (!), and for order of operations ('()').

There is also a `default 'y' SYMBOL` directive but the author is hazy on the details.

:!: It is important to note that using `select bar` in `Package/foo/config` directives will select `bar` for building, but it will not be included in the dependencies when `opkg` installs `foo`, nor will it guarantee that `bar` will be built before `foo`. Using `DEPENDS` will take care of all that.

## Caveats

Dependencies MAY NOT be circular (i.e. Package A may not depend on Package B, which in turn depends on Package A). If a circular dependency is created (whether directly or through another package), strange `make menuconfig` behaviour will be the result.

### Using boolean operators

\- The `DEPENDS:@SYMBOL` and `DEPENDS:@SYMBOL:package` syntax have good support for boolean operators, including parentheses, negation (`!`), `&&` and `||`.

\- The support for operators in the `DEPENDS:+SYMBOL:package` syntax is limited. Negation `!` is only supported to negate the whole condition. Parentheses are ignored, so use them only for readability. Like C, `&&` has a higher precedence than `||`. So `+(YYY||FOO&&BAR):package` will select package if `CONFIG_YYY` is set or if both `CONFIG_FOO` and `CONFIG_BAR` are set. You may use `+YYY||(FOO&&BAR):package` for readability, but :!: writing `+(YYY||FOO)&&BAR:package` will **not** change the condition to select package if either YYY or FOO is selected and BAR is selected.

## Bugs

There may be bugs in the OpenWrt build system wrt to dependencies. If you can confirm that you have a dependency problem, please report a bug. The developers would appreciate the following information:

- the relevant portions of `$TOPDIR/tmp/.config-package.in` (where \$TOPDIR is the directory where you checked out OpenWrt and where you initiate your builds)

**NB** Many apparent bugs are caused by circular dependencies. The OpenWrt build system doesn't like circular dependencies.

---

# Device support policies / best practices

Check this one beforehand: [Submitting patches](/submitting-patches)

This page provides additional guidelines for adding device support.

These guidelines are no rules, but may help you to improve the experience for both yourself and the reviewers when you submit a device support patch. Beyond that, they may just describe recommended and/or frequently applied practice throughout OpenWrt.

What's actually *required* will depend on who is reviewing your submission, though.

## Commit message

General guidelines for how to write a good commit message are found in [Submitting patches](/submitting-patches)

For device support commits, the commit message needs to contain at least the Specifications and Flashing instructions section.

Beyond that, it is recommended to add an overview of the MAC address assignment that you evaluated (see MAC address section below for further details).

Additional information is always helpful: While you shouldn't tell every detail of your struggle to support the device, it is generally a good idea to provide information that might help other developers in the future to understand why you did things as you did them.

## DTS files

### License

Please add a license via SPDX identifier to every file: <https://spdx.org/licenses/>

A very abundant license for DTS(I) files is:

    // SPDX-License-Identifier: GPL-2.0-or-later OR MIT

Please don't add a full-text license, but choose the appropriate identifier for it.

### dts-v1

The `/dts-v1/;` identifier must only be defined once and needs to be before any other content (except the license).

For several targets, it's already defined in the parent/SoC-based DTSI file, and does not need to be included a second time then.

### Model/device name

**Naming of the device should be consistent.** Many targets enforce that programmatically anyway, but if that's not the case please be consistent in your naming anyway.

If your model property contains a "v1", then your compatible should as well. Try to avoid abbreviations, these might cause confusion. The easiest way is to just create the compatible from the model by converting everything to lower case and replacing every space by a hyphen:

        model = "TP-Link TL-WR841N v14";
        compatible = "tplink,tl-wr841n-v14", "mediatek,mt7628an-soc";

An exception should be made for the vendor part of the compatible, where the kernel provides a list of strings to be used: <https://www.kernel.org/doc/Documentation/devicetree/bindings/vendor-prefixes.txt>

### General style

Indent style for DTS files is **tabs-only**.

To enhance readability, it is recommended to separate all blocks by empty lines. Despite, it may be helpful to structure properties into groups separated by empty lines.

For the status property, a frequent practice is to put it as a node's first line and add an empty line afterwards.

### LEDs

Typically, LEDs should have a label property following the `color:function` scheme.

The node name should be chosen in order to match the `function` from the label, i.e. if `green:wlan` is used, the node name should be `wlan` as well, and not `wifi`. If there is more than one LED with the same use, the color should be added to the node name, typically *after* the function in this case (`wlan_green`).

The *DT label* (not the label property) should be created from the node name by adding a `led_` prefix, because the DT label will be used in global context. Only add a DT label if you use it for something, otherwise just omit it.

Example:

    leds {
        compatible = "gpio-leds";

        lan {
            label = "green:lan";
            gpios = <&gpio 39 GPIO_ACTIVE_LOW>;
        };

        wan_green {
            label = "green:wan";
            gpios = <&gpio 40 GPIO_ACTIVE_LOW>;
        };

        wan_amber {
            label = "amber:wan";
            gpios = <&gpio 41 GPIO_ACTIVE_LOW>;
        };

        led_system: system {
            label = "green:system";
            gpios = <&gpio 42 GPIO_ACTIVE_LOW>;
        };
    };

## base-files

The cases in base-files are sorted in two levels: Within each block the devices are sorted alphabetically, and all of the blocks are sorted alphabetically based on the first device.

Where possible, add your device to an existing block instead of creating a new one.

### No wildcards

Occationally, you might be tempted to use wildcards in a case like the following:

    vendor_model-v1|\
    vendor_model-v2)
        ...

While this technically could be replaced by `vendor_model-*` to make your code shorter, this is generally not a good idea, because:

- You never know whether a different model will come up later that will be different, but fall within your wildcard
- Wildcard will prevent effective searching: If you e.g. want to grep for all settings applied to `vendor_model-v1`, grepping won't work because it won't match the wildcard definition. However, you cannot possibly guess the wildcard used in many cases.

## MAC addresses

In general, it is safest to define MAC addresses the same way as the vendor does it on it's device. Don't invent your own MAC address assignment scheme.

This may produce overlapping MAC addresses e.g. for LAN and one WiFi interface for several vendors, but that's still better than having overlapping MAC addresses with another device when using OpenWrt in a network afterwards (consecutive addresses in real world networks do happen).

Further reading on MAC address setup is found here: [Device support: MAC address setup](/docs/guide-developer/mac.address)

### Documentation

It will be helpful to other people if you document your MAC address assignment (flash locations and adresses or address increments) in the commit message. An easy and helpful way can be a simple table:

Example 1:

    MAC addresses as verified by OEM firmware:

    use   address   source
    LAN   *:f0      config 0x0 (label)
    WAN   *:f1      config 0x6
    2g    *:f0      art 0x1002
    5g    *:ef      art 0x5006

Example 2:

    MAC addresses as verified by OEM firmware:

    vendor   OpenWrt   address
    LAN      eth0      label
    WAN      eth1      label + 1
    2g       phy0      label + 2
    5g       phy1      label + 3

    The label MAC address was found in u-boot 0x1fc00.

### Data source

When defining MAC addresses in board.d and hotplug.d files, calculate them based on the flash locations and *not* relative to other interfaces. The numbering of interfaces may change, and then the address would be calculated incorrectly ...

For example

    wan_mac=$(macaddr_add $(mtd_get_mac_binary u-boot 0x1fc00) 1)

will always yield the same address while

    wan_mac=$(macaddr_add $(cat /sys/class/net/eth0/address) 1)

might be wrong if eth0/eth1 are swapped.

So, effectively, don't chain assignments, but read from the upmost data source where possible.

Try to always use hex locations (0x0 instead of 0) and lower-case characters for consistency.

## Backports

Generally, there is no hard rule or formal consensus about what is allowed to be backported from master into a stable.

However, the concept of a stable branch implies that backports will typically be *fixes, not features*. Adding support to a new device obviously is considered a feature in that context.

While feature backports still should be an exception, they typically are done for changes that are easy and well isolated. In contrast, requiring new drivers or patches to kernel subsystems etc. will drive your chances close to zero.

### Device support backports

Reviewing device support backports requires a detailed knowledge not only of the target setup in general, but also of all the changes applied to it until the last branch was made. Depending on the age of the stable branch and the number of changes to the target in the meantime, reviewing a backport will range from trivial to more work than reviewing the actual initial support.

In a project where reviewing time is scarce, doing backport reviews will obviously draw away time from other features that may be merged into master.

**Thus, device support *typically* is not backported.**

Exceptions have been made in the past for the following reasons. This is an observation, it will not constitute any claim:

1.  Device support is trivial, e.g. for a 100 % clone of a device already existing in stable.
2.  There are two similar devices that may be confused, and only one is present in stable branch. Backporting may prevent some users from destroying their devices.
3.  A device backport has been created by one of the committers: If the work has been done already, there is no reason to not share it with others. (Note that this is *not* the same as reviewing a patch provided by somebody else, as the committer will have to invest time for reviewing that one.)

Of course, despite everything said in this paragraph, every committer is free to choose whatever (s)he may find suitable. The lines above are just a description of what will probably happen.

---

# Drivers

Linux is a [monolithic](https://en.wikipedia.org/wiki/Monolithic kernel) [Kernel (computing)](https://en.wikipedia.org/wiki/Kernel (computing)) and thus all drivers belong in the kernel. Drivers can be compiled into the kernel or loaded as Modules.

The source code of a driver can be:

- completely Open Source, partially Open Source or Closed Source(Binary Blobs).
- integrated into the mainline kernel yet, not any more or never)

The Linux Kernel and Open Source drivers are maintained and developed by many different people around the world.

Closed Source drivers are developed and maintained by their creators since only they have access to the source code.

The source code for the drivers already integrated into the mainline kernel can be found here:

- -\> <http://kernel.org/>

In OpenWRT, all kernel module package filenames begin with kmod-.
The modprobe command is not available in at least some firmware version of OpenWrt. Use insmod instead.

## Learning more

No central information center exists. Instead you can try different pages like [FSF hw](http://www.fsf.org/resources/hw), [Ubuntu](https://wiki.ubuntu.com/HardwareSupport), [ALSA](http://alsa-project.org/main/index.php/Matrix:Main), <https://wireless.kernel.org>, [ger Ubuntu Wiki](http://wiki.ubuntuusers.de/Hardwaredatenbank/Ausgabeger%C3%A4te/Soundkarten).

You can also contact the developers. You can often reach them on one or more **mailing lists**.

---

# embedding-files-in-image

 UPDATE: This functionality was [removed in April 2017](https://git.lede-project.org/?p=source.git;a=commit;h=b044bd5921e9644c9df9655bef10cee0af730724).

The easy way is to include the files as [custom files](/docs/guide-developer/toolchain/use-buildsystem#custom_files)

This is a plain copy-paste from mailing list, if you have some time to turn it in a proper wiki article please do so.

Hi Karl,
let me introduce a not strictly new way but another heavily under documented buildroot feature which you can use to implement custom modifications to packages which do not require source code edits.
For every processed package Makefile, the buildroot tries to include a a Makefile fragment in \$(TOPDIR)/overlay/\*/\$(PKG_DIR_NAME).mk which one can use to monkey-patch internals without directly touching the package recipes.
For example to amend "base-files" to include a custom banner and inittab, you could create an overlay file called

    "overlay/my-example-organization/base-files.mk"\\

which extends the default Package/base-files/install recipe to copy your custom files in the end.
Assuming a directory structure like this
\* overlay/my-example-organization/banner
\* overlay/my-example-organization/inittab
\* overlay/my-example-organization/base-files.mk
the base-files.mk would need to include something like the following code to splicy your custom files into the packaging procedure:

    --- 8< ---
    # Figure out the containing dir of this Makefile
    OVERLAY_DIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

    # Declare custom installation commands
    define custom_install_commands
            @echo "Installing extra files from $(OVERLAY_DIR)"
            $(INSTALL_DIR) $(1)/etc/config
            $(INSTALL_DATA) $(OVERLAY_DIR)/banner $(1)/etc/banner
            $(INSTALL_DATA) $(OVERLAY_DIR)/inittab $(1)/etc/inittab
    endef

    # Append custom commands to install recipe,
    # and make sure to include a newline to avoid syntax error
    Package/base-files/install += $(newline)$(custom_install_commands)
    --- >8 ---

HTH, Jo

---

# External Toolchain

## Use OpenWrt as External Toolchain

Using an external toolchain reduce build time when starting with a cleaned-up source tree. Useful when using an automated build system like Hudson/Tinderbox.

### Step 1: Build Toolchain

Just do the same as everytime you (re)compile OpenWrt. Checkout openwrt repo, set your options in .config and build the whole thing. Only difference you have to select `Package the OpenWrt-based Toolchain` in the main view of `make menuconfig`

Alternatively you can download precompiled toolchain from openwrt download page by searching for the correct toolchain for your target. For example if you need precompiled toolchain for openwrt 22.03.0 for target ipq806x/generic [this is the link to use](https://downloads.openwrt.org/releases/22.03.0/targets/ipq806x/generic/openwrt-toolchain-22.03.0-ipq806x-generic_gcc-11.2.0_musl_eabi.Linux-x86_64.tar.xz).

### Step 2: Build Firmware

1.  Checkout OpenWrt into directory **openwrt**
2.  Follow normal instruction for openwrt prereq
3.  Use the utility script to setup your buildroot `   ./scripts/ext-toolchain.sh \
                --toolchain TOOLCHAIN_FILE_LOCATION \
                --config TARGET_NAME (example ipq806x/generic)
      `
4.  Use your buildroot like a normal one. Edit your config with `make menuconfig` and run `make` to compile your image

If you want to update a .config to use an external toolchain you can use the `--overwrite-config`. For example:

       ./scripts/ext-toolchain.sh \
                --toolchain TOOLCHAIN_FILE_LOCATION \
                --overwrite-config
                --config TARGET_NAME (example ipq806x/generic)

---

# OpenWrt Feeds

In OpenWrt, a "feed" is a collection of [packages](/docs/guide-developer/packages) which share a common location. Feeds may reside on a remote server, in a version control system, on the local filesystem, or in any other location addressable by a single name (path/URL) over a protocol with a supported feed method.

Feeds are additional predefined package build recipes for OpenWrt Buildroot. They may be configured to support custom feeds or non-default feed packages via a feed configuration file.

## Feed Configuration

The list of usable feeds is configured from either the `feeds.conf` file, if it exists, or otherwise the `feeds.conf.default` file. This file contains a list of feeds with each feed listed on a separate line. Each feed line consists of 3 whitespace-separated components: The feed method, the feed name, and the feed source. Blank lines, excessive white-space/newlines, and comments are ignored during parsing. Comments begin with \`#\` and extend to the end of a line.

Nowadays (AToW 2026-01-17) the `main` branch, the defaults contained within `feeds.conf.default` appear as follows. Note that the `#` prefixed lines are commented out and included for ease of configuration.

``` xml
src-git packages https://git.openwrt.org/feed/packages.git
src-git luci https://git.openwrt.org/project/luci.git
src-git routing https://git.openwrt.org/feed/routing.git
src-git telephony https://git.openwrt.org/feed/telephony.git
src-git video https://github.com/openwrt/video.git
#src-git targets https://github.com/openwrt/targets.git
#src-git oldpackages http://git.openwrt.org/packages.git
#src-link custom /usr/src/openwrt/custom-feed
```

The git method can specify a specific branch or commit using the following formats

    src-git local_feed_name https://example.com/repo_name/something.git;branch_name
    src-git local_feed_name https://example.com/repo_name/something.git^commit_hash

As of this writing, the following feed methods are supported:

| Method       | Function                                                                                                                  |
|:-------------|---------------------------------------------------------------------------------------------------------------------------|
| src-bzr      | Data is downloaded from the source path/URL using `bzr`                                                                   |
| src-cpy      | Data is copied from the source path. The path can be specified as either relative to OpenWrt repository root or absolute. |
| src-darcs    | Data is downloaded from the source path/URL using `darcs`                                                                 |
| src-git      | Data is downloaded from the source path/URL using `git` as a shallow (depth of 1) clone                                   |
| src-git-full | Data is downloaded from the source path/URL using `git` as a full clone                                                   |
| src-gitsvn   | Bidirectional operation between a Subversion repository and git                                                           |
| src-hg       | Data is downloaded from the source path/URL using `hg`                                                                    |
| src-link     | A symlink to the source path is created. The path must be absolute.                                                       |
| src-svn      | Data is downloaded from the source path/URL using `svn`                                                                   |

Feed names are used to identify feeds and serve as the basis for several file and directory names that are created to hold information about the feeds. The feed source is the location from which the feed data is downloaded.

For the methods listed above which rely on version control systems that support a "limited history" option (such as `--depth=1` for git and `--lightweight` for bzr) the smallest available history is downloaded. This is a good default, but developers who are actively committing to a feed and/or using the commit history may want to change this behavior. This can be done by editing `scripts/feeds` to use `src-git-full` or by checking out the feed without using `scripts/feeds`. A shallow git clone can be updated to a "full" clone through use of `git fetch --unshallow`

## Working with Feeds

As of December, 2018, feeds are retrieved and managed by the script `scripts/feeds` within the `openwrt/openwrt.git` repository. The `feeds` script incorporates packages from a variety of feed sources into the OpenWrt build system. This is a two step process done by the developer before building an image by updating a feed followed by installing packages from specific to that feed.

During the `update` step, the feeds are obtained from their sources listed within a [feed configuration](/docs/guide-developer/feeds#feed_configuration) and then copied into the `feeds` directory. After a successful update, each package recipe within a feed is represented within a folder in `feeds/<feed_name>/<package_name>/`, but they are not currently incorporated into the OpenWrt build system as they are not contained within the \`package/\` directory.

During the `install` step, packages from the feeds obtained during an \`update\` are then linked into the `package/feeds/<feed_name>` folder, where `<feed_name>` is replaced by the name of the feed in the feed configuration. After this step, it is then possible to perform package specific make operations by utilizing their path within the `package/` folder. For example:

`make package/feeds/<feed_name>/<package_name>`

    $ ./scripts/feeds
    Usage: ./scripts/feeds <command> [options]

    Commands:
            list [options]: List feeds, their content and revisions (if installed)
            Options:
                -n :            List of feed names.
                -s :            List of feed names and their URL.
                -r <feedname>:  List packages of specified feed.
                -d <delimiter>: Use specified delimiter to distinguish rows (default: spaces)
                -f :            List feeds in opkg [feeds.conf](../wiki/chunked-reference/wiki_page-guide-developer-creating-a-meson-based-package.md) compatible format (when using -s).

            install [options] <package>: Install a package
            Options:
                -a :           Install all packages from all feeds or from the specified feed using the -p option.
                -p <feedname>: Prefer this feed when installing packages.
                -d <y|m|n>:    Set default for newly installed packages.
                -f :           Install will be forced even if the package exists in core OpenWrt (override)

            search [options] <substring>: Search for a package
            Options:
                -r <feedname>: Only search in this feed

            uninstall -a|<package>: Uninstall a package
            Options:
                -a :           Uninstalls all packages.

            update -a|<feedname(s)>: Update packages and lists of feeds in [feeds.conf](../wiki/chunked-reference/wiki_page-guide-developer-creating-a-meson-based-package.md) .
            Options:
                -a :           Update all feeds listed within [feeds.conf](../wiki/chunked-reference/wiki_page-guide-developer-creating-a-meson-based-package.md). Otherwise the specified feeds will be updated.
                -r :           Update by rebase. (git only. Useful if local commits exist)
                -s :           Update by rebase and autostash. (git only. Useful if local commits and uncommited changes exist)
                -i :           Recreate the index only. No feed update from repository is performed.
                -f :           Force updating feeds even if there are changed, uncommitted files.

            clean:             Remove downloaded/generated files.

### Feed Commands

Feeds can be utilized through the `scripts/feeds` script. A list of the available commands is generated by invoking `scripts/feeds` without any arguments. Most commands require the feed information to be available locally, so running update first is usually necessary. In the following discussion the term "applicable packages" usually refers to the package names given on the command line or all packages in a feed when the -a option is used.

#### Clean

The clean command removes the locally stored feed data, including the feed indexes and data for all packages in the feed (but not the symlinks created by the install command, which will be dangling until the feeds are re-downloaded by the update command). This is done by removing the `feeds` directory and all subdirectories.

#### Install

The install command installs the applicable packages and any packages on which the applicable packages depend (both direct dependencies and build dependencies). The installation process consists of creating a symbolic link from `package/feeds/$feed_name/$package_name` to `feeds/$feed_name/$package_name` so that the package will be included in the configuration process when the directory hierarchy under `packages` is searched.

| Command                            | Description                                                                                                  |
|:-----------------------------------|--------------------------------------------------------------------------------------------------------------|
| ./scripts/feeds install -a         | Install all packages (not required; packages can be installed on an as-needed basis for slow build machines) |
| ./scripts/feeds install luci       | Install only the package LuCI                                                                                |
| ./scripts/feeds install -a -p luci | Install the complete LuCI WebUI by installing all (-a) packages from the preferred feed (-p) luci            |

See the above section for a list of the feeds available by default.

|                                                                   |                                                                                                                                               |
|-------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|
| ![48px-outdated.svg.png](/meta/icons/tango/48px-outdated.svg.png) | Please note that this replaces the old method of creating symlinks, which can be still found on-line in many old forum and user-group entries |

#### List

The list command reads and displays the list of packages in each feed from the index file for the applicable feeds. The index file is stored in the `feeds` directory with the name of the feed suffixed with `.index`. The file is generated by the update command.

#### Search

The search command reads through the feed metadata and lists packages which match the given search criteria.

#### Uninstall

The uninstall command does the opposite of the install command (although it does not address dependent packages in any way). It simply removes any symlinks to the package from the subdirectories of `package/feeds`.

#### Update

When `scripts/feeds update` is invoked, each of the applicable feeds are downloaded from their source location into a subdirectory of `feeds` with the feed name. It then parses the package information from the feed into an index file used by the list and search commands.

| Command                              | Description                          |
|:-------------------------------------|--------------------------------------|
| ./scripts/feeds update packages luci | Checkout the packages and luci feeds |

Note that update also stores the configured location of the feed in `feeds/$feed_name.tmp/location` such that changes to the configuration can be detected and handled appropriately.

After retrieval the downloaded packages need to be *"installed"*. Only after installation will they be available in the configuration interface!

## Custom Feeds

Ok, you've developed your package, and now you want to use it via make menuconfig, OR you are developing a package and you want to test it in a build before you try to get it included in OpenWrt.

The solution is a custom feed. You can either create an entirely new feed, or use a modified version of one of the standard ones.

### Creating the package directory

For this example we assume that your are in `/home/user/openwrt` as your base directory.

#### Adding your package to an existing feed

FIXME

#### Adding your package to your own feed

For this example we assume that you name your feed `custom` and your project is called `helloworld` and its openwrt Makefile is located at `/usr/src/openwrt/custom-feed/helloworld/Makefile`.

1.  Edit `/home/user/openwrt/feeds.conf.default`
2.  Add a new line for your feed. `src-link custom /usr/src/openwrt/custom-feed/`

1.  Update the feed: from the `<buildroot dir>` (e.g. `/home/user/openwrt`) do: `./scripts/feeds update custom`
2.  And then install it `./scripts/feeds install -a -p custom`

### Using the feed

1.  Now your package(s) should be available when you do `make menuconfig`

## Explanations

The downloaded sources (referenced in package Makefiles) are not there... The downloads go first to \<buildroot\>/dl as gzipped .gz files. And there they are stored and then they get unzipped to /build_dir. See e.g. \<buildroot\>/build_dir/target-\*/ and below it you will find subdirectories for each package's sources.

### Documentation

1.  [OpenWrt Buildroot – About](/docs/guide-developer/toolchain/start)
2.  [OpenWrt Buildroot – Installation](/docs/guide-developer/toolchain/install-buildsystem)
3.  [OpenWrt Buildroot – Usage](/docs/guide-developer/toolchain/use-buildsystem)
4.  OpenWrt Buildroot – Feeds
5.  [OpenWrt Buildroot – Technical Reference](/docs/techref/buildroot)  this article needs *your* attention.

## Links

---

# Frequent PR mistakes or "How to prevent my PR from getting delayed for sure"

A lot of PR initial reviews include the very same basic review comments each and every time again.

In order to not have to write the very same things more than a few hundred times, this page is meant to serve as a collection of very frequent "mistakes", or things that you should avoid in order to get a quick(er) review.

If you are pointed here and/or find yourself in the list below, you should probably read [Submitting patches](/submitting-patches) (again).

For device support, [Device Support Policies](/docs/guide-developer/device-support-policies) might help as well.

Those references up there are the real thing. In contrast, this page here is not exhaustive.

**So, in order to improve for your next try, or give a good first impression, please:**

## 1. Add a commit message

Commit message is mandatory. And if you think your particular PR maybe does not need a commit message, remember: Commit message is mandatory. Is. Mandatory.

## 2. Add a Signed-off-by with your real name

Use your real name. And a real e-mail address. Really.

    Signed-off-by: Firstname Lastname <myreal@emailadre.ss>

## 3. Do not multi-post or re-post PRs

If you have opened one PR, stick to it. If you have issues with Git, ask and try to get help.

If you accidentally closed the PR, reopen it as described here: [Reopen closed PR](/docs/guide-developer/working-with-github-pr#reopen_closed_pr)

Simply posting another, new PR will invalidate all the previous discussion - your work so far - and annoy the reviewers, because they will have to do extra work.

Just don't do it. Please.

## 4. Know the difference between the PR (Pull Request) and the commit

PR and commit are not same the same. *PR* is for preparation only, but the *commit(s) inside* the PR are the real thing. They will stay in the Git history. So, they are the important aspect.

So, while keeping the PR up-to-date is not a bad thing, remember: If you are asked to change the *commit*, change the commit; not the PR's initial post or title.

## 5. Answer questions

If I ask questions in OpenWrt GitHub PRs, in about 90 % of the cases I do not get an answer. I don't fully understand why this is the case, but probably people think my question only implies the necessity to change something. Since without answering the initial question there has been no discussion, these changes might help - or they make it worse.

So, please, if you are asked a question, just answer it. Maybe the answer is enough, and you don't have to change anything at all. Maybe there is a need to change - but now the reviewers will probably be able to help you with what has to be done, since they have been given information.

Thus, if you are asked "Have you tested this?", please answer. "Yes" or "no", and some explanation. If someone wanted you to change anything already, they would simply have said so.

## 6. Do not resolve comment that are not resolved

"Resolved" means the issue/question is dealt with completely and there is no doubt about the correct response.

If you are not sure - keep it open.

If there are multiple opinions, of which you chose one for your changes - keep it open.

If you have done nothing at all - keep it open.

If it might be helpful for review - keep it open.

Having all comments closed won't make the review process faster. Actually, if you have more than a few and they all are resolved it's quite suspicious. Ask yourself: If reviewers find that you closed something that is not resolved, will they trust you more - or less ...

## 7. Use checkpatch.pl

The OpenWrt core repository includes a script that is able to check most of the formal issues automatically. You just have run it. Please do.

<https://github.com/openwrt/openwrt/blob/master/scripts/checkpatch.pl>

## 8. Address all issues

Occasionally, people do 90 % of the requested changes and simply ignore the rest.

Don't do that. It will waste the reviewer's life-time (since they have to come back for another round) and will have you waiting longer for a chance to be merged (since they have to come back for another round).

---

# GNU Debugger

- **`Note:`** This guide is by no means a Howto, just some short instructions to use GDB on OpenWrt.
  Please look upstream for multilingual instructions and manuals, like e.g. here: <https://sourceware.org/gdb/documentation/>

## Compiling Tools

in [menuconfig](/docs/guide-developer/toolchain/use-buildsystem#image_configuration) enable gdb

    Advanced configuration options (for developers) -> Toolchain Options ->  Build gdb

and gdbserver

    Development -> gdbserver

## Add debugging to a package

Add CFLAGS to the package Makefile and recompile it.

    TARGET_CFLAGS += -ggdb3

Alternatively recompile the package with `CONFIG_DEBUG` set

    make package/busybox/{clean,compile} V=s CONFIG_DEBUG=y

Or you can enable debug info in [menuconfig](/docs/guide-developer/toolchain/use-buildsystem#image_configuration)

    Global build settings > Compile packages with debugging info

Disable stripping in your package in Makefile

    STRIP:=:

You might also want to disable stripping in [menuconfig](/docs/guide-developer/toolchain/use-buildsystem#image_configuration)

    Global build settings > Binary stripping method > None

## Starting GNU Debugger

Start gdbserver on target (router)

    gdbserver :9000 /bin/ping example.org

Start gdb on host (in compiling tree)

    ./scripts/remote-gdb 192.168.1.1:9000 ./build_dir/target-*/busybox-*/busybox

now you have a gdb shell. Set breakpoints, start program, backtrace etc.

    (gdb) b source-file.c:123
    (gdb) c
    (gdb) bt

If you want to restart the program, you'll need to set the remote path and arguments

    (gdb) set remote exec-file /usr/bin/blah
    (gdb) set args -v -x -merry-fishing
    (gdb) run

---

# Hardware Hacking First Steps

You bought yourself a new router, and it's nice. You can connect a hard disc to it and then it shares its content over samba. It even can do torrent. Wow. But then you stumbled over OpenWrt and its 2000 packages you can install just like that. Never mind all the other FOSS software you could compile for it. And you started crying and decided: you **neeeed** OpenWrt on your router. And if your router is already supported, dandy, flash it on and have fun. But if your router is not (yet) supported? Well, then do this:

## Gain Access

- you could login to some **unix shell** *after booting*, over Ethernet with `telnet`/`ssh`. Example: [hacking.dockstar](/toh/seagate/dockstar/hacking.dockstar) ([dockstar](/toh/seagate/dockstar))
- you could login to **bootloader console** *while booting*, over Ethernet or over the [Serial Port](/docs/techref/hardware/port.serial)
- you could access the hardware *without any booting, without any software present*, over the [JTAG Port](/docs/techref/hardware/port.jtag) with [JTAG](../wiki/chunked-reference/wiki_page-guide-developer-debugging.md) Software, like HairyDairyMaid

## Gather Information about Hardware

- Depending on the [bootloader](/docs/techref/bootloader) that is being used, you could utilize different `commands` to gather hardware information. Please see the manual for that particular bootloader to get this done. Once you have the information you could keep it for yourself or post it online. Depending on how fast you are, there probably is going to be information regarding this already available or you are the first one. This simple step is necessary because the manufacturer usually does not document exactly what hardware has been installed. Now with this information you are going to use google or the search engine of your choice, to see what GNU/Linux drivers are available, and if, in which kernel version they have been integrated into. For example:
- <http://en.wikipedia.org/wiki/Comparison_of_open_source_wireless_drivers#Linux> you can see, since which or until which Kernel version drivers for wireless radio circuitry, has been integrated.
- But of course there is much more to a system, in this case in form of a SoC, then the wireless drivers. Anything needs drivers. For example the [VLYNQ](https://en.wikipedia.org/wiki/VLYNQ) needs to be supported by the Kernel. etc. And you are done. If you really want to continue, you could find help here:

- <http://www.tldp.org/LDP/tlk/tlk.html> *The Linux Kernel*
- <http://www.tldp.org/LDP/lkmpg/index.html> *The Linux Kernel Module Programming Guide*
- <http://lwn.net/Articles/driver-porting/> you could also check this thread
- ~~<http://linux.junsun.net/porting-howto/porting-howto.html>~~ [Link on archive.org](https://web.archive.org/web/20191031031349/http://linux.junsun.net/porting-howto/porting-howto.html) Jun Sun's *Linux MIPS Porting Guide*
- <http://www.win.tue.nl/~aeb/linux/lk/lk.html> an overview over the history and also technical insights

Oh, you should also learn a programming language, like C.

## Gather Information about Software

- [bootloader](/docs/techref/bootloader) This is probably going to be the first piece of software you are going to notice. But the rest of the system could be of interest as well:
- Most probably it's a kind of outdated GNU/Linux Kernel with FOSS drivers or with binary only drivers or both. Then you are lucky, because the source code of the Linux Kernel is licensed under the GPLv2 and this constrains the seller to make the modified source code, if they actually bothered to modify anything, and they probably did, available to the customers (and not necessarily to the public) free of charge.

Now maybe the drivers for the components have already been integrated into mainline kernel, which means that a newer kernel should work on this device out of the box. If not, you could continue to use the one, from the manufacturer. So combine this kernel with other FOSS software, you want to run on it... ;-)

- In case the manufacturer did not use a Linux Kernel but some kind of \*BSD, you're fucked, since the license the \*BSD sources are under are not GPL. This particularly means, the usurper does not have to make source code available. They could, but they don't have to. Oh may you have much "fun" with \*BSD. :-P

## Gather Information about Flash Layout

### Overall Flash Layout

The overall Flash Layout looks like the [example](/docs/techref/flash.layout#example_flash_partitioning). Simply an overview over the different MTD-partition there are. And what their meaning is.

- An even better example is the [DIR-300 flash layout](/toh/D-link/DIR-300#flash_layout).
- Other ones you find here: ~~<http://wiki.ip-phone-forum.de/software:ds-mod:development:flash#flash_partitionierung>~~ [Link on archive.org](https://web.archive.org/web/20160306091048/http://wiki.ip-phone-forum.de/software:ds-mod:development:flash)

### Precise Flash Layout

This is more tricky, here you want to know exactly what is written on the flash: [flash.layout](/docs/techref/flash.layout)

The data could be zipped or g'zipped or even be encrypted. Also, there is going to be some number's between the data blocks, like CRC or whatever.

## Software Development

Now you want to run you own Software on your device. Maybe its hardware has already support in **some projects** or in the **mainline kernel**. If not, then consider adding a new device or a complete new platform to develop software for. Please do not bother developers or potential developers to write code for this. Present the information you gathered, if it is interesting enough, somebody is going to do that ;-) Now to write code, the developer needs only some bread and water and a simple text editor, but to test this code, they're going to need the hardware itself. You could donate or maybe just lend the hardware.

### Add Device

[add.new.device](/docs/guide-developer/add.new.device)

### Add Platform

[add.new.platform](/docs/guide-developer/add.new.platform)

## Software Development

The homepage needs no cookies, no javascript, no nothing enabled. It simply works. ;-) It is available under the Creative Commons BY-SA license:

- <http://bootlin.com/doc/legacy/block-drivers/>
- <http://bootlin.com/doc/training/buildroot/>
- <http://toolchains.bootlin.com/>
- <http://bootlin.com/doc/legacy/network-drivers/>

---

# Image Builder frontends

This page lists software based on [Image Builder](/docs/guide-user/additional-software/imagebuilder) whose goal is to automate or make it easier to generate OpenWrt images.

For one-shot OpenWrt image generation or light customization, it is probably still best to directly use the Image Builder.

### OpenWrt Firmware Selector

Modern Javascript interface that allows to locate and download an OpenWrt image. Note this implementation is not an image builder frontend and is simply and official image locator tool.

- <https://firmware-selector.openwrt.org/>

Based on original Attended Sysupgrade interface from <https://sudhanshu16.github.io/openwrt-firmware-selector/>

### Chef Online Imagebuilder / Attended Sysupgrade(asu)

Javascript app that connects to a Attendedsysupgrade server via an API, this is a work in progress. It's frontend resembles the Firmware Selector although provides customization options such as package selection.

Web-based asu frontends:

- <https://asu.aparcar.org/>
- <https://chef.libremesh.org/>

On router packages cli:auc and luci:luci-app-attendedsysupgade offer alternative frontends to communicate with asu server infrastructure in addition to the web based frontends above.

This project intends to simplify the sysupgrade process of devices running OpenWrt or distributions based on the former like LibreMesh. The provided tools here offer an easy way to reflash the router with a new version or package upgrades, without the need of opkg installed.

Additionally it offers an API (covered below) to request custom images with any selection of packages pre-installed, allowing to create firmware images without the need of setting up a build environment, even from mobile devices.

Flask-based code: <https://github.com/aparcar/asu>

## Gluon

Gluon is a modular framework for creating OpenWrt-based firmware images for wireless mesh nodes. Several Freifunk communities in Germany use Gluon as the foundation of their Freifunk firmware.

Documentation: <https://gluon.readthedocs.io/en/latest/>

## Freifunk Berlin firmware

This tool creates customized OpenWrt images for the needs of Freifunk Berlin. It builds images directly from the OpenWrt source code to create an Imagebuilder and SDK. The final images are build with the created Imagebuilder or a prebuild Imagbuilder can be used directly.

Code: <https://github.com/freifunk-berlin/firmware>

Documentation: <https://github.com/freifunk-berlin/firmware#development>

## Temba (TEMplate BAsed firmware)

Buildsystem to generate custom Openwrt-Firmware files for different nodes in a community network.

It uses erb templates on config files per device, evaluated from inherited yaml files. There are two interfaces: command-line (rake) and web (simple Ruby on Rails app).

Code: <https://gitlab.com/guifi-exo/temba>

Slide of the presentation at Battlemesh v12: <https://www.battlemesh.org/BattleMeshV12?action=AttachFile&do=get&target=custom_pseudofirmware_with_OpenWrt_imagebuilder.pdf>

## imagebuilder.sh

Part of Temba, a helper script to build the environment to run the image builder.

Code: <https://gitlab.com/guifi-exo/temba/blob/master/imagebuilder.sh>

## openwrt-tools

Project by tetaneutral.net, a community ISP in France.

Python program that uses YAML templates to generate images for various devices. No web interface.

Code: <https://redmine.tetaneutral.net/projects/git-tetaneutral-net/repository/openwrt-tools>

## openwrt-auto-extroot

[openwrt-auto-extroot](https://github.com/attila-lendvai/openwrt-auto-extroot) can be used to build a custom firmware image that will automatically format and set up extroot on **any** plugged-in, but not yet setup storage device. The primary audience of this project is developers, who can use it to build customized firmware images for their applications, but advanced users should also be able to build a firmware by just running its build script as-is.

## lime-sdk cooker

The "LibreMesh software development kit" uses the OpenWRT SDK and ImageBuilder to generate (cook) LibreMesh packages and firmware. If you want to create your own LibreMesh flavor because you need some specific configuration or you just want to have control over your binaries, the cooker is your friend!

Command-line interface, but can also be used with [Chef](https://github.com/libremesh/chef/).

Code: <https://github.com/libremesh/lime-sdk>

## openwrt-linksys8450-ubi-installer

A script which uses the IB to generate easy-to-use installer images for the Linksys E8450 and Belkin RT3200.

Code: <https://github.com/dangowrt/linksys-e8450-openwrt-installer>

## openwrt-metabuilder

Simple wrapper around ImageBuilder, that automatically downloads the right ImageBuilder archive.

Code: <https://github.com/aparcar/openwrt-metabuilder>

## openwrt_autobuild

A simple, standalone python3 wrapper around ImageBuilder that consumes a declarative INI-style configuration file and builds images for multiple targets and devices in parallel.

Code: <https://johannes.truschnigg.info/code/openwrt_autobuild/>

## Mesh testbed generator

Older initiative, was the basis of Temba: <https://github.com/yanosz/mesh_testbed_generator/>

## Meshkit

Project by Freifunk: meshkit is a webinterface for the OpenWrt image generator. It allows you to build customized OpenWrt firmware images to use on your router/access point. It also offers templates for each Freifunk community.

FIXME Demo: <http://imagebuilder.augsburg.freifunk.net/meshkit>

Relevant links:

- <https://wiki.freifunk.net/Freifunk_Firmware/Meshkit>
- <https://github.com/freifunk/meshkit>
- <https://github.com/freifunk/meshkit-community_files>
- <http://doc.meshkit.freifunk.net/daily/html/>
- <https://wiki.freifunk.net/Freifunk-Firmware/Community-Profile>

---

# jshn: a JSON parsing and generation library in for shell scripts

`jshn` (JSON SHell Notation), a small utility and shell library for parsing and generating [JSON](https://en.wikipedia.org/wiki/JSON) data.

Shell scripts (ash, bash, zsh) doesn't have built-in functions to work with JSON or other hierarchical structures so OpenWrt provides a shell library [/usr/share/libubox/jshn.sh](https://git.openwrt.org/?p=project/libubox.git;a=blob;f=sh/jshn.sh;hb=HEAD) from `libubox` package. You need to include it into your scripts and then you can call it's functions:

``` bash
#!/bin/sh

# source jshn shell library
. /usr/share/libubox/jshn.sh

# generating json data
json_init
json_add_int "code" "0"
json_add_string "msg" "Hello, world!"
json_add_object "test"
json_add_int "testdata" "1"
json_close_object
MSG_JSON=`json_dump`
# the MSG_JSON var now contains: { "code": 0, "msg": "Hello, world!", "test": { "testdata": 1 } }

# parsing json data from the MSG_JSON variable
local var1 code msg # declare local variables to load data into
json_load "$MSG_JSON"
json_select test # go into the object inside of the "test" field
json_get_var var1 testdata # first is var name "var1" then the JSON field name "testdata"
json_select .. # go back to the upper level
# load the "code" field into corresponding code var, and the "msg" field into the msg var
json_get_vars code msg

echo "code: $code, msg: $msg, testdata: $var1"
```

Another example:

``` bash
#!/bin/sh

# source jshn shell library
. /usr/share/libubox/jshn.sh

# initialize JSON output structure
json_init

# add a boolean field
json_add_boolean foo 0

# add an integer field
json_add_int code 123

# add a string, take care of escaping
json_add_string result "Some complex string\n with newlines\n and even command output: $(date)"

# add an array with three integers
json_add_array alist
json_add_int "" 1
json_add_int "" 2
json_add_int "" 3
json_close_array

# add an object (dictionary)
json_add_object adict
json_add_string foo bar
json_add_string bar baz
json_close_object

# build JSON object and print to stdout
json_dump

# will output something like this:
# { "foo": false, "code": 123, "result": "Some complex string\\n with newlines\\n and even command output: Fri Jul 13 07:11:39 CEST 2018", "alist": [ 1, 2, 3 ], "adict": { "foo": "bar", "bar": "baz" } }
```

### More complicated examples

#### Parse file example

Given the file:

``` yaml
{
  "status": 200,
  "msg": "ok",
  "result": {
    "number": "99",
    "mac": "d85d4c9c2f1a",
    "last_seen": 1363777473407
  }
}
```

Script to parse it:

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_init
json_load_file /data2.txt  ## Load JSON from file
## json_get_var <local_var> <json_var>
json_get_var status status    ## Get Value of status inside JSON string (i.e. MSG) into local "status" variable
json_get_var msg msg
json_select result            ## Select "result" object of JSON string (i.e. MSG)
json_get_var number number
json_get_var mac mac
json_get_var last_seen last_seen
```

#### Parse arrays example

Given the file:

``` yaml
{
  "ip_addrs": {
    "lan": ["192.168.0.100","192.168.0.101","192.168.0.200"]
  }
}
```

Script to parse it:

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_init
json_load_file /data2.json
json_select "ip_addrs"

if json_is_a lan array
then
  json_select lan
  idx=1 # note that array element position starts from 1 not, 0
  while json_is_a ${idx} string  ## iterate over data inside "lan" object
  do
    json_get_var ip_addr $idx
    echo "$ip_addr"
    idx=$(( idx + 1 ))
  done
fi
```

#### Parse list of objects

The example will download electricity hourly prices for Finland in JSON and parse it. The prices JSON looks like

``` yaml
{
  "prices": [
    {
      "date": "2024-08-03T11:00:00.000Z",
      "value": 6.41
    },
    {
      "date": "2024-08-03T12:00:00.000Z",
      "value": 4.1
    },
  ]
}
```

Script to parse it:

``` bash
#!/bin/sh
set -e
. /usr/share/libubox/jshn.sh
date=$(date -u +%Y-%m-%dT%H:00:00.000Z)

# download prices JSON via wget in quiet mode with output to stdout that will be saved to a variable PRICES_JSON
PRICES_JSON=$(wget -qO - "https://sahkotin.fi/prices?start=$date")
exit_status=$?
# check exit code: if any error then exit
if [ $exit_status -ne 0 ]; then
   >&2 echo "error $exit_status"
   exit $exit_status
fi

json_load "$PRICES_JSON"
json_select "prices"
idx=1 # note that array element position starts from 1 not, 0
# iterate over data inside "price" array until elements are objects
while json_is_a $idx object
do
  json_select  $idx
  # now parse {"date": "2024-08-04T21:00:00.000Z", "value": 22.58}
  json_get_var price_date "date"
  echo "price_date: $price_date"
  json_get_var price_value "value"
  echo "price_value: $price_value"
  idx=$(( idx + 1 ))
  json_select .. # go back to the upper level to the prices array
done

echo "Total parsed $idx"
```

## json_for_each_item

Function useful to iterate through the different elements of an array or object. The provided callback function is called for each element which is passed the value, key and user provided arguments. For field types different from array or object the callback is called with the retrieved value.

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_load_file /data2.json

dump_item() {
 echo "item: $1 '$2'"
}

json_for_each_item "dump_item" "ip_addrs"
```

## json_get_values

To get all values of an array use the `json_get_values`:

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_load '{"alist":[1,2]}'
json_get_values values "alist"
echo "${values}" #=> 1 2
# print comma separated
echo "${values// /, }" #=> 1, 2
```

## Get all fields into variables

Get all fields and declare variables for them:

``` bash
json_load '{"params":{"id": 1, "name": "Alice"}}'
json_select "params"
json_get_keys keys
for key in $keys
do
  json_get_var "$key" "$key"
done
echo "$id" #=> 1
echo "$name" #=> Alice
```

## jshn utility

Internally the `/usr/share/libubox/jshn.sh` is just a wrapper for [/usr/bin/jshn](https://git.openwrt.org/?p=project/libubox.git;a=blob;f=jshn.c;hb=HEAD) utility.

    root@OpenWrt:/# jshn
    Usage: jshn [-n] [-i] -r <message>|-R <file>|-o <file>|-p <prefix>|-w

Options:

- `-r <message>` parse from string `<message>`: called from `json_load()`
- `-R <file>` parse from file `<file>`: called from `json_load_file()`
- `-w` write the constructed object to stdout: called from `json_dump()`
- `-o <file>` write to file `<file>`
- `-p <prefix>` set prefix
- `-n` no newlines \n on formatting
- `-i` indent nested objects on formatting

You can call it directly:

``` bash
root@OpenWrt:/# jshn -R /etc/board.json
json_init;
json_add_object 'model';
json_add_string 'id' 'innotek-gmbh-virtualbox';
json_add_string 'name' 'innotek GmbH VirtualBox';
json_close_object;
json_add_object 'network';
json_add_object 'lan';
json_add_string 'ifname' 'eth0';
json_add_string 'protocol' 'static';
json_close_object;
json_add_object 'wan';
json_add_string 'ifname' 'eth1';
json_add_string 'protocol' 'dhcp';
json_close_object;
json_close_object;
```

The output is then evaluated inside of the shell script to create in memory structure as in file.

If you created an object like:

``` bash
json_init;
json_add_string 'username' 'root';
json_dump;
```

Then internally it will call `jshn -w` with the json obj passed via multiple env variables like

    root@OpenWrt:/# JSON_CUR=J_V T_J_V_username=string K_J_V=username J_V_username=root jshn -w
    { "username": "root" }

Here `J_V` stands for "JSON value":

- `JSON_CUR` means a name of var with root object to format
- `K_J_V` is a key name i.e. `username`
- `T_J_V_username` is a type of the `username` field
- `J_V_username=root` is a value of the the `username` field i.e. `root`

## Other examples

### Get bridge status

OpenWrt have a command `devstatus` to check network device status. E.g. `devstatus br-lan` prints:

``` yaml
{
        "external": false,
        "present": true,
        "type": "bridge",
        "up": true,
        "carrier": true,
        "bridge-members": [
                "eth0.1",
                "wlan0"
        ],
        "mtu": 1500,
        "mtu6": 1500,
        "macaddr": "84:16:f9:9b:e0:7a",
        "txqueuelen": 1000,
        "ipv6": true,
        "promisc": false,
        "rpfilter": 0,
        "acceptlocal": false,
        "igmpversion": 0,
        "mldversion": 0,
        "neigh4reachabletime": 30000,
        "neigh6reachabletime": 30000,
        "neigh4gcstaletime": 60,
        "neigh6gcstaletime": 60,
        "neigh4locktime": 100,
        "dadtransmits": 1,
        "multicast": true,
        "sendredirects": true,
        "statistics": {
                "collisions": 0,
                "rx_frame_errors": 0,
                "tx_compressed": 0,
                "multicast": 0,
                "rx_length_errors": 0,
                "tx_dropped": 0,
                "rx_bytes": 10609108786,
                "rx_missed_errors": 0,
                "tx_errors": 0,
                "rx_compressed": 0,
                "rx_over_errors": 0,
                "tx_fifo_errors": 0,
                "rx_crc_errors": 0,
                "rx_packets": 39594607,
                "tx_heartbeat_errors": 0,
                "rx_dropped": 0,
                "tx_aborted_errors": 0,
                "tx_packets": 91154927,
                "rx_errors": 0,
                "tx_bytes": 121051584071,
                "tx_window_errors": 0,
                "rx_fifo_errors": 0,
                "tx_carrier_errors": 0
        }
}
```

You can check the `devstatus` sources to see that internally it makes a [ubus call](/docs/techref/ubus) and uses the `jshn` to format output:

``` bash
cat /sbin/devstatus
#!/bin/sh
. /usr/share/libubox/jshn.sh
DEVICE="$1"

[ -n "$DEVICE" ] || {
    echo "Usage: $0 <device>"
    exit 1
}

json_init
json_add_string name "$DEVICE"
ubus call network.device status "$(json_dump)"
```

### Check if Link is up using devstatus and jshn

``` bash
#!/bin/sh

. /usr/share/libubox/jshn.sh

WANDEV="$(uci get network.wan.ifname)"

json_load "$(devstatus $WANDEV)"

json_get_var var1 speed
json_get_var var2 link

echo "Speed: $var1"
echo "Link: $var2"
```

## Additional JSON parsing tools

### jsonfilter

The [jsonfilter](commit>project/jsonpath.git) tool in included into OpenWrt. The help output:

    root@openwrt:~# jsonfilter --help
    == Usage ==

      # jsonfilter [-a] [-i <file> | -s "json..."] {-t <pattern> | -e <pattern>}
      -q            Quiet, no errors are printed
      -h, --help    Print this help
      -a            Implicitely treat input as array, useful for JSON logs
      -i path       Specify a JSON file to parse
      -s "json"     Specify a JSON string to parse
      -l limit      Specify max number of results to show
      -F separator  Specify a field separator when using export
      -t <pattern>  Print the type of values matched by pattern
      -e <pattern>  Print the values matched by pattern
      -e VAR=<pat>  Serialize matched value for shell "eval"

    == Patterns ==

      Patterns are JsonPath: http://goessner.net/articles/JsonPath/
      This tool implements $, @, [], * and the union operator ','
      plus the usual expressions and literals.
      It does not support the recursive child search operator '..' or
      the '?()' and '()' filter expressions as those would require a
      complete JavaScript engine to support them.

    == Examples ==

      Display the first IPv4 address on lan:
      # ifstatus lan | jsonfilter -e '@["ipv4-address"][0].address'

      Extract the release string from the board information:
      # ubus call system board | jsonfilter -e '@.release.description'

      Find all interfaces which are up:
      # ubus call network.interface dump | \
            jsonfilter -e '@.interface[@.up=true].interface'

      Export br-lan traffic counters for shell eval:
      # devstatus br-lan | jsonfilter -e 'RX=@.statistics.rx_bytes' \
            -e 'TX=@.statistics.tx_bytes'

Usage example:

``` bash
ubus call network.wireless status | jsonfilter -e '@[*]' | jsonfilter -a -e '@[1]'
```

The first jsonfilter call will output one radio JSON structure object per line, the second call then consumes this lines while using the -a flag to treat them like an array, this allows you to select the first or second radio regardless of the name.

### jq

[jq](https://stedolan.github.io/jq/) jq is a flexible command-line JSON processor that is very popular for scripting. It's not installed by default in OpenWRT because is too big (more than 200Kb) so to install use `opkg update; opkg install jq` By default it just colorize an output e.g. `cat /etc/board.json | jq`

### See also

- [Awesome JSON](https://github.com/burningtree/awesome-json) A curated list of awesome JSON libraries and resources.
- [OpenWrt script samples](https://github.com/yurt-page/openwrt-script-samples)
- [Writing shell scripts support forum topic](https://forum.openwrt.org/t/writing-shell-scripts-support-topic/206144)

---

# Links to Libraries

Here we could place links to light-build libraries you could link against:

## C standard library

- [GNU C Library](https://en.wikipedia.org/wiki/GNU C Library) (LGPL) "working horse", up-to-date, heavily worked on, most commonly used on non-embedded Linux distributions
  - License LGPL:
- [Embedded GLIBC](https://en.wikipedia.org/wiki/Embedded GLIBC) (LGPL) is an abstraction of the glibc, and more configurable and embedded friendly
  - License LGPL:
- [uClibc](https://en.wikipedia.org/wiki/uClibc) (LGPL) At the moment OpenWrt uses µClibc as C standard library. <http://www.uclibc.org/>
  - License LGPL:
- [dietlibc](https://en.wikipedia.org/wiki/dietlibc) (GPLv2) <http://www.fefe.de/dietlibc/> and some [FAQ](http://www.fefe.de/dietlibc/FAQ.txt).
  - License GPLv2:
- [Newlib](https://en.wikipedia.org/wiki/Newlib) (LGPL)
  - License LGPL:

## C++ standard library

## SSL/TLS

[Comparison_of_TLS_Implementations](https://en.wikipedia.org/wiki/Comparison_of_TLS_Implementations)

- `libopenssl` [OpenSSL](https://en.wikipedia.org/wiki/OpenSSL)
  - [Dual license: 4-clause BSD-like and Apache License 1.0](http://www.openssl.org/source/license.html)
    - `umurmur`
- `libpolarssl` [PolarSSL](https://en.wikipedia.org/wiki/PolarSSL)
  - [GPLv2 with FOSS exception or Commercial Licensing](http://polarssl.org/licensing)
    - `umurmur`
- `libmatrixssl` [MatrixSSL](https://en.wikipedia.org/wiki/MatrixSSL)

      *[[http://www.matrixssl.org/]] GPLv2+
        * ''[[docs:guide-user:services:webserver:http.mini-httpd]]''
    * ''libcyassl'' [[wp>CyaSSL]] [[http://www.yassl.com/yaSSL/Home.html]]
      * [[http://www.yassl.com/yaSSL/License.html|GPLv2 with FOSS exception or Commercial Licensing]]
        * ''[[doc:howto:luci|uhttpd-mod-tls]]''
    * ''libgnutls'' [[wp>GnuTLS]] [[http://www.gnu.org/software/gnutls/]]
      * [[http://www.gnu.org/software/gnutls/gnutls.html|LGPLv2.1+]]
    * [[wp>cryptlib]] [[http://www.cs.auckland.ac.nz/~pgut001/cryptlib/]]
      * [[http://www.cs.auckland.ac.nz/~pgut001/cryptlib/download.html|dua license: GPL-like or Commercial Licensing]]
    * ''libgcrypt'' [[wp>Libgcrypt]] [[http://directory.fsf.org/project/libgcrypt/]] LGPL or GPLv3
    * [[http://directory.fsf.org/project/BeeCrypt/|BeeCrypt]] LGPLv2.1+
    * ''libmcrypt'' [[http://mcrypt.sourceforge.net/]]

---

# Device Support: MAC address setup

## Retrieve addresses from stock firmware

The first step is to find out which addresses are present in stock configuration. The procedure depends on your level of access to the device's firmware.

The result would be a list like the following:

    LAN ..:..:..:..:..:0a
    WAN ..:..:..:..:..:0b
    2.4 GHz ..:..:..:..:..:0c
    5 GHz ..:..:..:..:..:0a

## Find out about flash locations

If you already have OpenWrt running on the device, you can try to find out about MAC locations on flash (note that not all devices store addresses there).

List partitions:

    $ cat /proc/mtd
    dev:    size   erasesize  name
    mtd0: 00020000 00010000 "u-boot"
    mtd1: 00189ce4 00010000 "kernel"
    mtd2: 0064631c 00010000 "rootfs"
    mtd3: 003b0000 00010000 "rootfs_data"
    mtd4: 00010000 00010000 "art"
    mtd5: 007d0000 00010000 "firmware"

You would normally expect WiFi MAC addresses in the art partition. To check for that, use hexdump on the corresponding mtd4:

    $ hexdump -C /dev/mtd4

This will dump the whole partition to your console. Now you can look for addresses there: Take one byte of the vendor part of the address (first three bytes) and do text search ...

The same should be done for other partitions. Usual suspects are:

- factory
- mac
- config
- art
- u-boot

If you are successful, you will have a list of addresses and locations, e.g.

    factory 0xe000 *:0A
    factory 0xe006 *:0B
    art 0x4 *:0A

You can check your data by using OpenWrt's get_mac_binary command (based on mtdX):

    . /lib/functions/system.sh
    get_mac_binary /dev/mtd4 0x4

or by using mtd_get_mac_binary (based on partition label):

    . /lib/functions/system.sh
    mtd_get_mac_binary art 0x4

## Merge your data

Now, combine data from stock firmware and your research to have a complete list:

    LAN *:0a factory 0xe000
    WAN *:0b factory 0xe006
    5 GHz *:0a art 0x4
    2.4 Ghz *:0c calculated from art 0x4 + 2

You could also include this list in your commit message to preserve the information.

As in the example, it is possible that the same address is present in different locations. In this case, use the location that "belongs" to the interface, i.e. art for WiFi, others for ethernet.

## Set MAC addresses

TBD: mtd_mac_address, 02_network, ...

### MAC address pulled by driver

In several cases, the MAC address is already provided at the correct location for the driver to use it automatically.

*(This list is incomplete. Please extend it.)*

Known cases:

- ath79: **mtd-cal-data**: The MAC address will be read from start +2
- ramips: **mediatek,mtd-eeprom/ralink,mtd-eeprom**: The MAC address will be read from start +4
- **ath9k**: offset + 2 (mostly)
- **ath10k**: offset + 6

So, if you have MAC location matching those, you do not have to specify the MAC address in DTS or base-files for the particular interface.

Correct:

    &wmac {
        status = "okay";

        mtd-cal-data = <&art 0x1000>;
    };

Suboptimal (not precisely wrong):

    &wmac {
        status = "okay";

        mtd-cal-data = <&art 0x1000>;
        mtd-mac-address = <&art 0x1002>;
    };

This can also be exploited for setting the label MAC address (see below) via 02_network.

## Label MAC address

refs: <https://github.com/openwrt/openwrt/pull/2159> <https://github.com/openwrt/openwrt/pull/2253>

Many devices bear a label with one or several MAC addresses on it. Those may be used to identify the device in the network and thus represent a valuable additional information about the device.

When adding device support, you should also check which of the interface addresses corresponds to address on the label. If we assume the label MAC address ends with `0a`, we could assign either LAN or 5 GHz to it. The choice for an ambiguous address is arbitrary, so let's choose 5 GHz.

There are two options to specify the label MAC address in OpenWrt:

### label-mac-device DTS file

We can refer to the device bearing the label MAC address in DTS. For that purpose, one needs to reference the node with an alias, e.g.

    aliases {
        label-mac-device = &wifi0;
    }

Obviously, this is only valid if the 5 GHz Wifi device tree node actually has been named wifi0.

*Attention: Not all interface can be referenced this way. To check whether there actually is a usable MAC address, check the device tree on your router:*

Run

    find /proc/device-tree/ -name "*mac-address"

on your device.

*Attention: This will only work if you have already set up MAC addresses correctly based on the information retrieved above.*

It will give you a list like the following:

    /proc/device-tree/ahb/eth@1a000000/mac-address
    /proc/device-tree/ahb/eth@1a000000/mtd-mac-address
    /proc/device-tree/ahb/eth@19000000/mac-address
    /proc/device-tree/ahb/eth@19000000/mtd-mac-address
    /proc/device-tree/ahb/apb/wmac@18100000/mac-address
    /proc/device-tree/ahb/apb/wmac@18100000/mtd-mac-address

For each of the returned paths (if there are any), retrieve the mac-address, e.g.

    . /lib/functions/system.sh
    get_mac_binary "/proc/device-tree/ahb/eth@1a000000/mac-address" 0

Valid choices are only `mac-address` or `local-mac-address`. There may be one, two or no paths giving the correct address.

If you find the label MAC address here, check your DTS for the corresponding parent node. The correct node for `/proc/device-tree/ahb/apb/wmac@18100000/mac-address` would be `/ahb/apb/wmac@18100000`. Use this node's alias or add a reasonable one yourself if missing.

*Attention: Note that label MAC addresses are assigned relatively randomly by vendors, so label-mac-device should be regularly put into DTS files or DTSIs with few users, so it is not inherited by accident.*

### Set label MAC address via 02_network

If device tree does not lead to the relevant MAC address, we can still set it in 02_network. In this case, you need to set label_mac in a similar way as it is already used for lan_mac and wan_mac, e.g.

    cudy,wr1000)
        wan_mac=$(mtd_get_mac_binary factory 0x2e)
        label_mac=$(mtd_get_mac_binary factory 0x4) # e.g. on ramips when caldata is read from factory 0x0

    belkin,f9k1109v1)
        wan_mac=$(mtd_get_mac_ascii uboot-env HW_WAN_MAC)
        lan_mac=$(mtd_get_mac_ascii uboot-env HW_LAN_MAC)
        label_mac=$wan_mac

This is evaluated below by the line

    [ -n "$label_mac" ] && ucidef_set_label_macaddr $label_mac

If possible, setting the address with the DTS approach is preferred.

### Using the label MAC address

When everything is set up correctly, the label MAC address can be accessed with:

    . /lib/functions.sh
    . /lib/functions/system.sh
    label_mac_addr=$(get_mac_label)

## Common MAC address locations

If there is an ART partition, WiFi MAC addresses are frequently/typically stored there.

ath79:

- All TP-LINK routers using old tp-link header (those using Device/tplink-Xm or Device/tplink-Xmlzma templates defined in target/linux/ath79/image/common-tplink.mk), store only one mac address in \<&uboot 0x1fc00\>, which is the label mac address.

ramips: For ramips, typical locations for ethernet addresses are as follows:

- mt7621: lan mac is at factory 0xe000 and wan mac at factory 0xe006. This is the default location for mt7621 boards in MTK's SDK.
- For mt7620/mt76x8 boards if there's a lan mac at 0x28 there may be a wan mac at 0x2e. (There's only one GMAC for these two chips so GMAC2_OFFSET defined above isn't used.)

//Attention: Those are *typical* addresses. Some vendors mix them, invert them, or even use completely different locations!//

---

# umdns for Local Device Discovery

The [umdns](/packages/pkgdata/umdns) package creates a local DNS name for your router. When `umdns` is installed, the router and all its services are available using the name *hostname.local* instead of requiring the router's IP address.

`umdns` relies on mDNS ("multicast DNS") also known as Bonjour, zero-configuration networking (ZeroConf) or DNS Service Discovery (DNS-SD). mDNS enables automatic discovery of computers, devices, and services on the local network. It is an internet standard documented in [RFC6762](https://tools.ietf.org/html/rfc6762).

## Installation

The [umdns](/packages/pkgdata/umdns) package provides a compact implementation of this standard, well integrated with the OpenWrt system environment. It requires no configuration to work "right out of the box". `umdns` is available using LuCI web interface, or with `opkg install umdns` (OpenWRT 17 and later).

### Configuration

**I NEED HELP NAILING DOWN THE DEFAULT, AND THE [CORRECT](../cookbook/chunked-reference/uci-read-write-from-ucode.md) DESCRIPTION OF ALL THE FOLLOWING LINES**

**Hostname:** `umdns` advertises the hostname that is present in `/etc/config/system`.

``` bash
option hostname 'your_openwrt_device'      # sets the mDNS name to your_openwrt_device.local
```

**Local domain:** OpenWrt uses `.lan` by default. There is an [ongoing discussion](https://forum.openwrt.org/t/use-home-arpa-as-default-tld-for-local-network/165056/) about the proper suffix for the local domain - `.local`, `.lan`, or even `.home.arpa`. Choose one, and everything in your network will interoperate.

Configure the local domain in LuCI in the **Network -\> DNS and DHCP** in the **Local domain** field, or by editing `/etc/config/dhcp`.

``` bash
config dnsmasq
    ...
    option local '/lan/'
    option domain 'lan'
    ...
```

**umdns configuration:** `umdns` has its own configuration file.

``` bash
config umdns
    option jail 1 # enables jail - see procd
    list network lan
    list network dmz # Provides visibility into both networks, but does not act as a repeater
```

**Notes:**

- The `option jail` **DOES WHAT?**

- The `list network` lines indicate the interfaces where `umdns` advertises its names. The interface name is found from `/etc/config/network`, not the device name shown by `ifconfig`. So if the network configuration file contains `config interface 'vlan1'` in your `/etc/config/network`, use `vlan1`. To test for the correct name name use `ifstatus`.

- It is considered unsafe to enable umdns on `wan` interface because it makes those hosts more visible to the external world.

### Firewall

mDNS requires UDP port 5353. If you choose to advertise on `wan` (see security warning above) or other networks, open that port in the firewall:

``` bash
config rule
        option src_port '5353'
        option src '*'
        option name 'Allow-mDNS'
        option target 'ACCEPT'
        option dest_ip '224.0.0.251'
        option dest_port '5353'
        option proto 'udp'
```

To configure from GUI see "Firewall rules" section of [Resolving mDNS across VLANs with Avahi on OpenWRT](https://blog.christophersmart.com/2020/03/30/resolving-mdns-across-vlans-with-avahi-on-openwrt/)

### mDNS Alternatives

As noted above, the [umdns](/packages/pkgdata/umdns) package works well with the OpenWrt system environment, and is suitable for most straightforward environments.

If you know you need additional capabilities, there are several other packages that can provide mDNS services. They are described on the [Zero configuration networking in OpenWrt](/docs/guide-user/network/zeroconfig/zeroconf) page.

## For Developers

The following information is useful if you are developing a service that uses mDNS.

### Browsing announced services

Almost all interaction with the daemon is via [ubus](/docs/guide-developer/ubus).

    $ ubus call umdns update
    # wait a second or two
    $ ubus call umdns browse
    # big json dump example...
            ....
        "_printer._tcp": {
            "HP\\032Color\\032LaserJet\\032CP2025dn\\032(28A6CC)": {
                "port": 515,
                "txt": "txtvers=1",
                "txt": "qtotal=1",
                "txt": "rp=RAW",
                "txt": "ty=HP Color LaserJet CP2025dn",
                "txt": "product=(HP Color LaserJet CP2025dn)",
                "txt": "priority=50",
                "txt": "adminurl=http:\/\/NPI28A6CC.local.",
                "txt": "Transparent=T",
                "txt": "Binary=T",
                "txt": "TBCP=T"
            },
            "HP\\032LaserJet\\032P3010\\032Series\\032[46A14F]": {
                "port": 515,
                "txt": "txtvers=1",
                "txt": "qtotal=4",
                "txt": "rp=RAW",
                "txt": "pdl=application\/postscript,application\/vnd.hp-PCL,application\/vnd.hp-PCLXL",
                "txt": "ty=HP LaserJet P3010 Series",
                "txt": "product=(HP LaserJet P3010 Series)",
                "txt": "usb_MFG=Hewlett-Packard",
                "txt": "usb_MDL=HP LaserJet P3010 Series",
                "txt": "priority=52",
                "txt": "adminurl=http:\/\/NPI46A14F.local."
          },
       ....
    $ ubus call umdns hosts
    #Show hosts discovered via mDns
            "SteakPrinter.local": {
                    "ipv4": "192.168.1.159"
            },
            "Upstairs.local": {
                    "ipv4": "192.168.1.151"
            },

### Issues/Bugs

- IP addresses are missing.
- TXT records aren't valid json in the dump, so jsonfilter can't be used.
- How long is data cached? What causes it to update? No idea.
- You may not see locally advertised services with `ubus call umdns browse`. See the [discussion](https://forum.openwrt.org/t/how-to-announce-service-with-umdns/5029/7)

### Announcing local services

The umdns scans all the services listed in ubus (`ubus call service list`) and looks for `mdns` objects in their data object. You can view this more selectively for example with:

    # ubus call service list | jsonfilter -e "$[*]['instances'][*]['data']['mdns']"
    { "ssh_22": { "service": "_ssh._tcp.local", "port": 22, "txt": [ "daemon=dropbear" ] } }

Here we can see that ssh is being advertised locally.

If you want to advertise your own service, your service needs to be a [procd](/docs/guide-developer/procd) managed service. You can use the `procd_add_mdns` call to provide a basic definition.

    [procd_open_instance](../cookbook/chunked-reference/procd-service-lifecycle.md)
    ....
    procd_add_mdns <service> <proto> <port> [<textkey=textvalue> ... ]
    ...
    procd_close_instance

As an example, the following call

``` bash
procd_add_mdns "webdav" "tcp" "80" "path=/nextcloud/remote.php/dav/files/YOUR_USER/" "u=YOUR_USER"
```

advertises `_webdav._tcp.local` with two text records. In the example we published a WebDAV folder from Nextcloud and now it can be seen in Network folder of a file manager in GNOME and KDE and can be [discovered from a Kodi media player](https://kodi.wiki/view/Avahi_Zeroconf). The service names may be taken from the [IANA register](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) and the txt-records may be taken from the official DNS-SD keys (see [ServiceTypes](http://www.dns-sd.org/ServiceTypes.html) under "Defined TXT keys".

If you wish to create a more complicated mdns information block, see `procd_add_mdns_service` in `/lib/functions/procd.sh` but be warned that umdns probably can't automatically support everything you can represent in json.

### Service description files in /etc/umdns

umdns advertises the services whose `*.json` files are found in `/etc/umdns`. This is similar to how Avahi advertises `*.service` files in `/etc/avahi/services/`.

**IMPORTANT!** Keep the json formating as in the following examples, i.e. the service definition needs to be a one-liner, otherwise it won't work!

For example the same WebDAV service description:

``` yaml
{
  "nextcloud_webdav": { "service": "_webdav._tcp.local", "port": 80, "txt": [ "path=/nextcloud/remote.php/dav/files/YOUR_USER/", "u=YOUR_USER" ] }
}
```

Or you can advertise SFTP and SSH:

``` yaml
{
  "ssh_login": { "service": "_ssh._tcp.local", "port": 22, "txt": [ "u=root" ] },
  "sftp_share": { "service": "_sftp-ssh._tcp.local", "port": 22, "txt": [ "path=/", "u=root" ] }
}
```

See more examples in [umdns sources](commit>?p=project/mdnsd.git;a=tree;f=json;hb=HEAD)

The reload the umdns service with: `ubus call umdns reload` or `service umdns reload`

### Testing

To see that service was advertised you may use `avahi-discover` GUI application. To see from a command line use `avahi-browse --all`. To find a specific service use: `avahi-browse -d local _webdav._tcp`.

### Links

- [Sources](commit>?p=project/mdnsd.git;a=tree;hb=HEAD)
- [Sources on GitHub](https://github.com/openwrt/mdnsd/)

---

# Network scripts

netifd can (probably) bring up a wired, static ip configuration without shell scripts. For everything else (PPPoE or 3G) it needs *protocol handlers* implemented as sets of shell functions.

## Writing protocol handlers

Each protocol handler is a shell script in `/lib/netifd/proto/`. It is run (or maybe sourced) when netifd daemon starts. Changes made to the scripts do not take effect until netifd restarts. The name of the file usually matches `option proto` in `/etc/config/network`.

To be able to access the network functions, the script needs to include the necessary shell scripts at the beginning:

``` bash
#!/bin/sh

[ -n "$INCLUDE_ONLY" ] || {
    . /lib/functions.sh
    . ../netifd-proto.sh
    init_proto "$@"
}
```

Current working directory is `/lib/netifd/proto/` when the handler is sourced.

At the end of the script a handler should register itself by calling `add_protocol protocolname`.

A handler should at least define 2 shell functions: `proto_protocolname_init_config` and `proto_protocolname_setup`.

netifd then calls the script with a JSON blob of the configuration parameters:

    /bin/sh ..../<protocolname>.sh <protocolname> setup <interfacename> '{"proto":"<protocolname>","a":true,"b":["192.0.2.10"],...}'

    ubus call network.interface notify_proto '{ "action": 0, "link-up": true, "keep": false, "interface": "<interfacename>" }'

### init_config

The main purpose of this function is to let netifd know which parameters this protocol has. These parameters stored in `/etc/config/network` are referenced for use by the proto handler. This is what netifd monitors. If any of these parameters change via rpcd/ubus, netifd can trigger a reload or restart of the interface whose parameters have changed.

``` bash
proto_protocolname_init_config() {
    proto_config_add_string "stringparam"
    proto_config_add_int "intparam"
    proto_config_add_boolean "boolparam"
    ...
}
```

e.g. It will 'validate' the following: i.e. monitor them for changes, and update the interface with them when they do.

``` bash
config interface 'foo'
    option proto 'protocolname'
    option stringparam 'f00'
    option intparam '12345'
    option boolparam '1'
    ...
}
```

As you may have noticed, this is good for monitoring properties of an interface. What if an interface has various peer type entries also in the network config? netifd won't see when any of those peer entries related to the interface have changed. It doesn't 'validate' those.

This is why changes to peers and most WireGuard interface properties are not put into operation until a manual interface restart.

One can employ a work-around: have the proto script 'validate' an option which stores a hash of the peers, a hash which is simultaneously updated when peers are modified and written e.g. in luci, so when the hash of the peers is saved, netifd will notice the interface property change and reload the interface. Note that changes via uci command line go unnoticed by netifd.

Another approach is to use a procd handler which can monitor when changes occur to `/etc/config/network` in general, and trigger a reload of the interface.

### Setup

The setup procedure implements the actual protocol specific configuration logic and interface bring-up.

When called, one or two parameters are passed:

1.  Config (the UCI section name suitable for `config_get` calls)
2.  Interface name (only if `no_device=0`)

``` bash
proto_protocolname_setup() {
    local config="$1"
    # set up the interface
}
```

This function must be implemented by any protocol back-end.

There's usually no need to call `ifconfig iface up` at the end of this function. If `no_device=0`, netifd won't even try to start our profile until the device is already up. It waits for `operstate=up` and `carrier=1`, then starts the profile.

If `no_device=1`, netifd will bring it up, when it receives a notification from us:

``` bash
proto_protocolname_setup () {
    ...
    proto_init_update "$iface" 1
    proto_send_update "$config"
    ...
}
```

This only works once, however. If someone called `ifconfig iface down`, netifd won't try to bring it up again (at least in BB), so just in case you may put the "up" command in the function.

### renew

The renew procedure implements logic for when an interface or daemon config has changed and it might need a restart or reload, or SIGHUP to reload its config.

When called, one or two parameters are passed:

1.  Config (the UCI section name suitable for `config_get` calls)
2.  Interface name (only if `no_device=0`)

``` bash
proto_protocolname_renew() {
    local config="$1"
    # reload the interface
}
```

This function can be implemented by any protocol back-end.

### Teardown

Protocols that need special shutdown handling, for example to kill associated daemons, may implement a stop procedure. This procedure is called when an interface is brought down before the associated UCI state is cleared.

The function is called when we do `ifdown profile` or when `no_device=0` and netifd detects link connectivity loss.

When called, two parameters are passed:

1.  Config (the UCI section name suitable for `config_get` calls)
2.  interface (the network device)

``` bash
proto_protocolname_teardown() {
    local config="$1"
    local iface="$2"
    # tear down the interface
}
```

This function is optional.

### Coldplug

By default, only interfaces present in `/proc/net/dev`, like *eth0*, are brought up on boot. Protocols which use virtual interfaces must set two variables at the beginning of init_config.

``` bash
proto_protocolname_init_config() {
    no_device=1
    available=1
    ...
}
```

### Keep config

Use `proto_set_keep()` to maintain configuration across updates, by keeping the proto process alive.

``` bash
proto_set_keep 1
```

An example in context:

``` bash
...
    proto_init_update ppp0 1
    proto_set_keep 1
    proto_add_ipv4_address "192.168.2.1" 32
    proto_add_dns_server "192.168.2.2"
    proto_add_ipv4_route "0.0.0.0" 0 192.168.2.2
    proto_add_data
    json_add_string "ppp-type" "pppoe"
    proto_close_data
    proto_send_update "$interface"

    proto_init_update ppp0 1
    proto_set_keep 1
    proto_add_ipv6_address "fe80::2" 64
    proto_add_ipv6_route "::0" 0 "fe80::1"
    proto_add_data
    json_add_string "ppp-type" "pppoe"
    proto_close_data
    proto_send_update "$interface"
...
```

### Debugging

- STDERR in protos is redirected to the syslog. `echo "message" > 2>&1` can be used to print.
- As `set -x` also prints to STDERR, it can be used to trace which commands are called inside the proto. However this is very spammy.
- There is a pending patch: <https://patchwork.ozlabs.org/project/openwrt/patch/20201229233319.164640-1-me@irrelefant.net/>.

### Available proto flags

Flags can be added to a proto handler in `proto_protoname_init_config`, by setting their value to `1`. The information about all loaded protocols can be obtained by calling *ubus call network get_proto_handlers*.

| Name | Name in *ubus call network get_proto_handlers* | Meaning |
| --- | --- | --- |
|   | force_link_default | Instruct netifd to prefer link-based default routing behavior for the interface (affects how link state influences routing selection). |
|   | immediate | Protocol should be started/processed immediately upon attach instead of waiting for link or other conditions (useful for static/always-on protos). |
| available | init_available | Indicates the protocol handler is present/usable on the system (1 = available, 0 = not). |
| lasterror | last_error | True when the last setup attempt failed and the handler wants to expose that state. |
| no_device | no_device | Protocol does not create/use a kernel network device. Example: PPP uses a logical proto and does not provide a physical device. |
| no_device_config | no_device_config | Protocol has no device-specific configuration (config applies to the protocol itself). |
| no_proto_task | no_task | Protocol does not spawn a long-running background task. Mainly for protocols like xl2tpd in which control commands are sent to another daemon xl2tpd to start L2TP negotiation and pppd process who is not under netifd's control as proto_task as is the case in other ppp related protocols like pppoe, pptp, etc.; As an example, WireGuard is built into the kernel and has no running daemon, so it has no daemon or 'proto task'. |
| peer_detect | peer_detect | netifd calls renew when it detects that a \_peer in the config changed. |
| renew_handler | renew_available | Protocol implements the "renew" action/handler `proto_*_renew()`, which can be called by netifd. |
| teardown_on_l3_link_down | teardown_on_l3_link_down | If the l3 device receives state down (e.g. ifdown), call the `proto_*_teardown()`. Mainly for shell protocols that have no_proto_task so that we can still do teardown and setup of the interface on l3_dev link lost instead of depending on the running state of proto_task |

### Error codes

If errors for interfaces occur, the json object in *ifstatus interfacename* or in *ubus call network.interface dump* have an attribute *"error"*. If there are no errors, this attribute is not existing.

| CODE                | Meaning                                                                                                                                                                                                                                                                                                                                                                                        |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| NO_DEVICE           | The configured device in ifname is not found.                                                                                                                                                                                                                                                                                                                                                  |
| DEVICE_CLAIM_FAILED | One of the reasons for this is, that the device configured by ifname does not exist. Usually this would result in NO_DEVICE as the device is only claimed when it is available. However when the proto flags *available=1* and *no_device=0* are set, the device specified by ifname is tried to be claimed directly. TBD: Is this the only case? Is this correct? |
| SETUP_FAILED        | TBD                                                                                                                                                                                                                                                                                                                                                                |

Custom error codes can be thrown from the proto scripts aswell. This is done via `proto_notify_error "$config" MY_CUSTOM_ERROR_ID`.

### How does it work internally?

``` bash
init_proto $proto $cmd $interface $data $ifname
```

This function takes all all arguments from the *proto.sh* file, interprets them and then defines the implementation of *add_protocol()*.

If `$cmd = "dump"` then *add_protocol()* will do the following:

- A json output dump of the results of `proto_protocolname_init_config` will be printed.
- Other parameters than `$cmd` will be ignored.

If `$cmd ∈ {"setup", "teardown", "renew"}` *add_protocol()* will do the following:

- If `$proto ≠ protoname` nothing will be done.
- `$data` is loaded via *json_load*
- `proto_protoname_... $interface $ifname` will be called.

Otherwise the script will fail with something like:

- `add_protocol: not found`

## API

The following functions are defined in `/lib/netifd/netifd-proto.sh`.

### netifd functions

#### initialization functions

- `add_protocol`
- `init_proto`
- `proto_config_add_boolean`
- `proto_config_add_int`
- `proto_config_add_string`
- `proto_config_add_array` (for uci config ''list xxx 'value' '' types

#### notification functions

Note: some of these function exit immediately. These functions are dispatched to ubus and arrive [here](commit>?p=project/netifd.git;a=blob;f=proto-shell.c;hb=c00c8335d6188daa326ecfe5a62da15a9b9987e1#l792)

- `proto_block_restart $interface`
- `proto_init_update $ifname $up [$external]`
- `proto_kill_command $interface [$signal]`
- `proto_notify_error $interface $str1 [$str2] [$str3] ...`
- `proto_run_command`

We can start a daemon that maintains the connection asynchronously by calling `proto_run_command "$config" custom_script`. Netifd remembers its pid. It can be killed manually by calling `proto_kill_command "$config"`. Netifd can automatically kill it, when the profile stopped.

\* `proto_add_host_dependency`

It seems to avoid race conditions in protos. We can register the following type of dependencies by calling:

- `proto_add_host_dependency "$config" "$host" "$ifname"`
- `proto_add_host_dependency "$config" \'\' "$ifname"` (only wait for an iface)
- (maybe more?)

Only if `$iface` is up, the corresponding `$config` will be loaded. So we need another proto to be completed, we can use this here.

From some observations I think it looks like technically the `$config` is initially loaded, then the `proto_add_host_dependency` is called inside the proto handler and then the `$config` is removed again until `$iface` is available, up, ... or so. However, currently I do not know where to find the source code, so this is only a vague idea of what happens.

- ''proto_send_update \$interface ''
- '' proto_set_available \$interface \$state''

### common functions

- '' json_add_string ''
- '' json_dump ''
- '' json_init ''
- '' [json_get_var](../wiki/chunked-reference/wiki_page-guide-developer-jshn.md) ''
- '' json_get_vars ''

## Examples

[Network functions](https://github.com/openwrt/openwrt/blob/master/package/base-files/files/lib/functions/network.sh) rely on runtime configuration and can return unexpected result if you are using MWAN or VPN. Replace automatic WAN detection with explicit interface definition if necessary.

### Get LAN address

``` bash
# Runtime configuration
NET_IF="lan"
. /lib/functions/network.sh
network_flush_cache
network_get_ipaddr NET_ADDR "${NET_IF}"
network_get_ipaddr6 NET_ADDR6 "${NET_IF}"
echo "${NET_ADDR}"
echo "${NET_ADDR6}"
```

### Get WAN interface

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
echo "${NET_IF}"
echo "${NET_IF6}"
```

### Get WAN L2 device

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_physdev NET_L2D "${NET_IF}"
network_get_physdev NET_L2D6 "${NET_IF6}"
echo "${NET_L2D}"
echo "${NET_L2D6}"
```

### Get WAN L3 device

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_device NET_L3D "${NET_IF}"
network_get_device NET_L3D6 "${NET_IF6}"
echo "${NET_L3D}"
echo "${NET_L3D6}"

# Persistent configuration
uci get network.wan.device
uci get network.wan6.device
```

### Get WAN address

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_ipaddr NET_ADDR "${NET_IF}"
network_get_ipaddr6 NET_ADDR6 "${NET_IF6}"
echo "${NET_ADDR}"
echo "${NET_ADDR6}"

# Persistent static configuration
uci get network.wan.ipaddr
uci get network.wan6.ip6addr
```

### Get WAN gateway

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan NET_IF
network_find_wan6 NET_IF6
network_get_gateway NET_GW "${NET_IF}"
network_get_gateway6 NET_GW6 "${NET_IF6}"
echo "${NET_GW}"
echo "${NET_GW6}"

# Persistent static configuration
uci get network.wan.gateway
uci get network.wan6.ip6gw
```

### Get WAN prefix

``` bash
# Runtime configuration
. /lib/functions/network.sh
network_flush_cache
network_find_wan6 NET_IF6
network_get_prefix6 NET_PFX6 "${NET_IF6}"
echo "${NET_PFX6}"

# Persistent static configuration
uci get network.wan6.ip6prefix
```

### Get WAN gateway for unmanaged default route

``` bash
# Runtime configuration
ubus call network.interface dump \
| jsonfilter -e "$['interface'][*]['inactive']
['route'][*]['target'='0.0.0.0','mask'='0','nexthop']"
```

---

# Using the SDK

 THIS IS THE *OLD* DOCUMENT :!:
**See [Using the SDK](/docs/guide-developer/toolchain/using_the_sdk) for the latest version** :!:

The [SDK](https://en.wikipedia.org/wiki/Software_development_kit) is a relocatable, precompiled OpenWrt [toolchain](https://en.wikipedia.org/wiki/Toolchain) suitable to [cross compile](https://en.wikipedia.org/wiki/Cross_compile) single [userspace](https://en.wikipedia.org/wiki/User_space) packages for a specific target without compiling the whole system from scratch.

Reasons for using the SDK are:

- Compile custom software for a specific release while ensuring binary and feature compatibility
- Compile newer versions of certain packages
- Recompile existing packages with custom patches or different features

## Obtain SDK

You can either download an already compiled SDK, or compile it yourself by using the "make menuconfig" command.

#### Prerequisites

Please see [Build system – Installation](/docs/guide-developer/toolchain/install-buildsystem) page how to install the needed software to build the packages on the SDK.

------------------------------------------------------------------------

Note: On some hosts it is needed to install the **ccache** package

### Download

You should find bz2-archives ready for download in the corresponding download directory:

- [Trunk SDK](https://downloads.openwrt.org/snapshots/trunk/) -\> [Platform](https://dev.openwrt.org/wiki/platforms) -\> OpenWrt-SDK-\<Platform\>-for-linux-x86_64-gcc-\<version\>-linaro-uClibc-\<version\>.tar.bz2
- [Stable SDK "Chaos Calmer (15.05.1)"](https://downloads.openwrt.org/chaos_calmer/15.05.1/) -\> [Platform](https://dev.openwrt.org/wiki/platforms) -\> OpenWrt-SDK-\<Platform\>-for-linux-x86_64-gcc-\<version\>-linaro-uClibc-\<version\>.tar.bz2
- [Legacy SDKs (Historic Releases)](https://downloads.openwrt.org/), -\> [Platform](https://dev.openwrt.org/wiki/platforms) -\> OpenWrt-SDK-\<Platform\>-for-linux-x86_64-gcc-\<version\>-linaro-uClibc-\<version\>.tar.bz2

### Package Feeds

After decompressing the SDK archive, edit the `feeds.conf.default` file to download the needed package definitions

## Usage

By default the SDK ships with no package definitions. Makefiles for packages to compile must be checked out from the OpenWrt repository and placed into the `package/` directory first.

### Obtain Definitions

- Use the `./scripts/feeds update -a` command to obtain package definitions.
- After the definitions have been updates, execute `./scripts/feeds install <packagename>` to prepare the package and its dependencies.

### Compile Packages

After the Makefile is in place, the usual buildroot commands apply:

- `make package/example/download` - download the soures of *example*
- `make package/example/prepare` - extract the sources, apply patches and download if necessary
- `make package/example/compile` - compile *example*, prepare and download if necessary
- `make package/example/clean` - clean the sourcecode
- `make package/index` - build a repository index to make the output directory usable as local *opkg* source

Some packages are built on host:

|                                                    |
|----------------------------------------------------|
| `$ make package/example/host/{clean,compile} V=99` |

The common command to recompile a package *example* and enable verbose output is:

|                                               |
|-----------------------------------------------|
| `$ make package/example/{clean,compile} V=99` |

After the compilation is finished, the generated .ipk files are placed in the bin directory.

The output of make might contain `WARNING: your configuration is out of sync. Please run make menuconfig, oldconfig or defconfig!`. That warning is misleading and wrong in the SDK case. Since everything is precompiled you cannot run oldconfig (see [Why is the SDK configuration out of sync?](https://forum.openwrt.org/viewtopic.php?id=43055)).

### Example: existing package

The example below rebuilds *tmux*.

    $ ./scripts/feeds install tmux
    Installing package 'tmux'
    Installing package 'toolchain'
    Installing package 'ncurses'
    Installing package 'libevent2'
    Installing package 'openssl'
    Installing package 'zlib'
    Installing package 'ocf-crypto-headers'
    $ make package/tmux/download
    Collecting package info: done
    tmp/.config-package.in:36:warning: ignoring type redefinition of 'PACKAGE_libc' from 'boolean' to 'tristate'
    tmp/.config-package.in:64:warning: ignoring type redefinition of 'PACKAGE_libgcc' from 'boolean' to 'tristate'
    #
    # configuration written to .config
    #
     make[1] package/tmux/download
     make[2] -C feeds/packages/utils/tmux download
    $ make package/tmux/prepare
    tmp/.config-package.in:36:warning: ignoring type redefinition of 'PACKAGE_libc' from 'boolean' to 'tristate'
    tmp/.config-package.in:64:warning: ignoring type redefinition of 'PACKAGE_libgcc' from 'boolean' to 'tristate'
    #
    # configuration written to .config
    #
     make[1] package/tmux/prepare
     make[2] -C feeds/packages/utils/tmux prepare
    $ make package/tmux/compile
    tmp/.config-package.in:36:warning: ignoring type redefinition of 'PACKAGE_libc' from 'boolean' to 'tristate'
    tmp/.config-package.in:64:warning: ignoring type redefinition of 'PACKAGE_libgcc' from 'boolean' to 'tristate'
    #
    # configuration written to .config
    #
     make[1] package/tmux/compile
     make[2] -C feeds/base/package/libs/toolchain compile
     make[2] -C feeds/base/package/libs/ocf-crypto-headers compile
     make[2] -C feeds/base/package/libs/zlib compile
     make[2] -C feeds/base/package/libs/openssl compile
     make[2] -C feeds/base/package/libs/libevent2 compile
     make[2] -C feeds/base/package/libs/ncurses host-compile
     make[2] -C feeds/base/package/libs/ncurses compile
     make[2] -C feeds/base/package/libs/ncurses compile
     make[2] -C feeds/base/package/libs/ncurses compile
     make[2] -C feeds/packages/utils/tmux compile

     make[1] package/index

     make[1] package/index
    $ ls bin/ar71xx/packages/packages
    tmux_1.9a-1_ar71xx.ipk

### Build your own packages

See [Creating packages](/docs/guide-developer/packages)

## Troubleshooting

:!: Some SDK versions have bugs.

Bug: BB SDK for BRCM2708: wants to compile with "ccache_cc" see <https://dev.openwrt.org/ticket/13949>

Bug: BB SDK for BRCM2708: static compilation broken

---

# Overview

If you are familiar with GNU/Linux systems, you should find your way around pretty easily; if you are not, you will need to learn some basic concepts and terminology first.

You might have read that OpenWrt is a **GNU/Linux distribution** (or "distro") aimed at embedded devices.
A GNU/Linux **distribution** is a project that creates and maintains *packages*, used with a Linux kernel to create a GNU/Linux operating system tailored to users' needs.
A **package** is a compressed archive containing a program, a [library](https://en.wikipedia.org/wiki/Library_(computing)) or some scripts, its accompanying configuration files and also information used to integrate it in the operating system. These packages are handled by a **package manager** (opkg in OpenWrt); a program that downloads/opens/installs/uninstalls the packages.
So, an OpenWrt firmware is made by assembling packages around a Linux kernel.

Each package is compiled separately, and when all are done the needed packages are "installed" in a temporary directory that will then be the compressed-read-only [SquashFS](https://en.wikipedia.org/wiki/SquashFS) partition in the device firmware.

While the kernel is handled as a package, it is added to firmware images in the special way each device's bootloader expects. So you can replace the stock firmware without touching the bootloader (which is dangerous and not always possible).

The last step in the build process is actually creating the firmware file, the file to install or upgrade OpenWrt.
This file is usually a memory image ready to be written as is on the internal flash storage of the device. You may notice that many developers simply call it "image" on IRC or in the mailing list.

## How Packages are Compiled

If you look at a package's **Makefile**[^1], you will notice it states the official download link for the sources to be compiled, a SHA256 hash to check the integrity of such download, a version number of the upstream project as package base and a release number to indicate OpenWrt changes. On some packages the version number states git commit, timestamp or another expression to identify the source code version to pull down and build. They generally favor archives with sources from official releases, but some upstream projects don't always have that.

In **patches** directory of each package you will find any patches that will be applied to the source after downloading and before compiling it: (e.g. [pathches dir of busybox](https://github.com/openwrt/openwrt/tree/master/package/utils/busybox/patches)). There are also other directories for configuration files or uci integration.

The kernel's Makefile is a bit more complex, but you can see that it still uses the same structure for pulling down the same kernel version depending on device every time. e.g. [Linux Makefile](https://github.com/openwrt/openwrt/blob/master/package/kernel/linux/Makefile)

All packages are compiled by OpenWrt's own toolchain, which is also handled like packages (see /toolchain and /tools in the source), so you will always have the same compilers/tools as everyone else as they are downloaded from the same sources at the same version.

When you run `make` the OpenWrt build system will use your system's existing building infrastructure to compile the OpenWrt's toolchain first, and then use that to compile the packages. This also has the major benefit of not requiring the user to set up a cross-compiling toolchain that is rather annoying and relatively complex.

## Package Feeds

Not all packages you can install in OpenWrt are from OpenWrt project proper, in fact most packages are not.

The packages from OpenWrt's main repository are maintained directly by core developers, and they are the important, even essential components of OpenWrt firmware or parts of the build system. "**package feeds**" are source repositories that contain additional packages maintained by the community, and each package has its own maintainer.

This is OpenWrt's main repo on github: <https://github.com/openwrt/openwrt>

These are official package feeds:

- <https://github.com/openwrt/luci>
- <https://github.com/openwrt/telephony>
- <https://github.com/openwrt-routing/packages>
- <https://github.com/openwrt/packages>

Being "official feeds", the packages therein will be compiled and offered by the official download server, but they are not technically OpenWrt proper, they are community-maintained. The "package feed" system is designed to allow easy addition of your own custom feeds to your own custom firmware images, but of course you will have to compile them and host them on your own servers.

If you look at the built packages [here](https://downloads.openwrt.org/releases/21.02.1/packages/x86_64/) on the download server (this is the same server opkg uses to download packages in a live OpenWrt system), they are divided by feed name, packages in "base" come from the main repository, and also from main repository are packages that are found in target-specific directories, for example [here](https://downloads.openwrt.org/releases/24.10.1/packages/x86_64/packages/) what you see are mostly drivers like kmod-\*.

## Package Versions

As stated above, package Makefiles have a PKG_VERSION tag that shows the upstream version which is the major version of the package, and a PKG_RELEASE tag that is used to show changes on the OpenWrt side, that is the minor version. If you see a package that lists version as 123-1, its major version is 123 and minor version is 1.

Some packages have timestamp or git commit as major version, for example 2016-09-21-42ad5367-1 where the last "1" is the minor version.

You can see all versions used in the first page of the [table of packages](/packages/table/start).

Or by browsing a Package.manifest in the package download directory <https://downloads.openwrt.org/releases/24.10.1/packages/mips_24kc/base/Packages.manifest>

## Repeatable Builds

The aforementioned system allows repeatable builds. The major version of source archives are written in the packages' Makefiles in the git repositories of main and community package feeds; you can see full history of changes to that file with *git*.

There is a cache server that stores source archives because it's more convenient than having the build bots spamming the upstream download servers, and it is also a fallback should the upstream server disappear. It should keep the packages' sources for a long while, as they are used by build bots for as long as the releases that depend on them are supported.

This server index may be browsed here: <https://sources.openwrt.org/>

[^1]: the file defines settings for building the package, [e.g. busybox's](https://github.com/openwrt/openwrt/blob/master/package/utils/busybox/Makefile)

---

# OpenWrt packages

The OpenWrt system is maintained and distributed as a collection of *packages*.

Almost all pieces of software found in a typical OpenWrt firmware image are provided by such a package with a notable exception being the Linux kernel itself.

The term *OpenWrt package* may either refer to one of two things:

- an OpenWrt *source package* which essentially is a directory consisting of:
  - an *OpenWrt package Makefile* describing the acquisition, building and packaging procedures for a piece of software (required)
  - a supplemental directory with *OpenWrt package patches* which modify the acquired source code (optional)
  - other static files that go with the package, such as init script files, default configurations, scripts or other support files (optional)

- an OpenWrt *binary package*, which is a GNU tar compatible archive containing binary executable software artifacts and the accompanying *package control files* for installation on a running system, similar to the `.deb` or `.rpm` files used in other package managers

OpenWrt *binary packages* are almost exclusively produced from *source packages* by invoking either the *OpenWrt buildroot* or the *OpenWrt SDK* in order to translate the source package Makefile descriptions into executable binary artifacts tailored for a given target system.

Although it is possible to manually assemble binary packages by invoking tools such as *tar* and placing the appropriate control files in the correct directories, it is strongly discouraged to do so since such binary packages are usually not easily reproducible and verifiable.

Source packages are developed in multiple OpenWrt *package feeds* hosted in different locations and following different purposes. Each *package feed* is a collection of *source package* definitions residing within a publicly or privately reachable source code repository.

## Source packages

Source packages describe how a piece of software has to be *downloaded*, *patched*, *compiled* and *packaged* in order to form a binary software artifact suitable for use on a running target system. They also describe relations to other source packages required either at *build time* or at *run time*.

Each source package should have a *globally unique name* closely resembling the name of the software described by it. OpenWrt often follows the lead of other distributions when deciding about the naming of packages and sticks to the same naming conventions in many cases.

### Structure

A *source package* is a subdirectory within its corresponding *package feed* containing at least one Openwrt `Makefile` and optionally `src`, `files` or `patches` directories.

#### Makefile

An OpenWrt *source package Makefile* contains a series of header variable assignments, action recipes and one or multiple OpenWrt specific signature footer lines identifying it as OpenWrt specific package Makefile.

See [Creating packages](/docs/guide-developer/packages) for details on Makefile contents.

#### The files directory

Static files accompanying a source package, such as OpenWrt specific init scripts or configuration files, must be placed inside a directory called `files`, residing within the same subdirectory as the `Makefile`. There are no strict rules on how such static files are to be named and organized within the `files` directory but by convention, the extension `.conf` is used for OpenWrt UCI configration files and the extension `.init` is used to denote OpenWrt specific init scripts.

The actual placement and naming of the resources within the `files` directory on the target system is controlled by the source package Makefile and unrelated to the structure and naming within the `files` directory.

#### The patches directory

The `patches` directory must be placed in the same parent directory as the `Makefile` file and may only contain *patch files* used to modify the source code being packaged.

Patch files must be in *unified diff* format and carry the extension `.patch`. The file names must also carry a numerical prefix to denote the order in which the patch files must be applied. Patch file names should be concise and avoid characters other than ASCII alphanumerics and hyphens.

Suitable patch file names could look like:

- `000-patch-makefile.patch`
- `010-backport-frobnicate-crash-fix.patch`
- `999-add-local-hack-for-openwrt-compatibility.patch`

It is recommended to use [Quilt](/docs/guide-developer/toolchain/use-patches-with-buildsystem) to manage source package patch collections.

#### The src directory

Some packages do not actually fetch their program code from an external source but bundle the code to be compiled and packages directly within the package feed. This is usually done for packages which are specific to OpenWrt and do not exist outside of their respective package feed.

Sometimes the `src` directory may also be used to supply additional code to the compilation process, in addition to the program code fetched from external sources.

If present, the OpenWrt build system will automatically copy the contents of the `src` directory verbatim to the compilation scratch directory (*build directory*) of the package, retaining the structure and naming of the files.

### Feature Considerations

Many OpenWrt supported devices still have only a few megabytes of flash and RAM available which makes it important to shrink the packages as much as possible. Opt for the lowest common denominator whenever possible.

Some general considerations when packaging a new piece of software are:

- Do not ship man pages or documentation, a typical installation lacks both the infrastructure and the space to view and store man page databases
- Minimize external dependencies - try to avoid optional external dependencies whenever possible. An extreme example is `ICU` which weighs around 12MB and is an optional dependency for Unicode multi language support in various packages
- Modularize packages - if the software you're packaging supports and uses plugins then put those plugins into separate binary package declarations instead of lumping them all together along with the main program. This way you can externalize dependencies and move them into the plugin packages instead of having them in the main component, which makes the package usable on a wider range of targets because users can omit parts with large dependencies.
- Try to rely on standard facilities - instead of requiring extra programs to implement tasks like user context switching, use the `procd` facilities to run a service as a different user.

Often it is tempting to add various `menuconfig` configuration options to allow the customization of the package features by the users compiling their own variant of OpenWrt but it should be kept in mind that large parts of the userbase will use the package solely by installing binary archives from the OpenWrt repositories.

Binary packages in the official OpenWrt repositories are always built with the default settings of a package so a maintainer should ensure that the default feature selection represents a fair balance between resource requirements and most common user needs.

### Copyright statements

Historically, packages for OpenWrt used to contain a copyright notice at the top of the Makefile, stating something like:

    # Copyright (C) 2007-2010 OpenWrt.org
    This is free software, licensed under the GNU General Public License v2.
    See /[LICENSE](../openwrt-core/chunked-reference/makefile_meta-category-utils.md) for more information.

Since contributors likely do not have a formal contract with OpenWrt to develop packages, they cannot disclaim their own copyrights and assign them to the project.

When adding new packages, please don't simply copy the statement from another package but add either your own in the form:

    # Copyright (C) 2016 Joe Random <joe@example.org>

or omit it entirely.

### Versioning

There are a number of Makefile variables influencing the visible version of the resulting packages. When packaging upstream release tarballs, the `PKG_VERSION` variable should be set to the version of the upstream software being packaged. For example, if the `openssl` package compiles the released `openssl-1.0.2q.tar.gz` archive, then `PKG_VERSION` variable should be set to the value `1.0.2q`.

When there are no upstream release tarballs available or when software is packaged straight from a source code repository, the `PKG_SOURCE_DATE` and `PKG_SOURCE_VERSION` variables should be used instead. The `PKG_SOURCE_DATE` value must correspond to the modification date in the format `YYYY-MM-DD` of the source repository revision being packaged and `PKG_SOURCE_VERSION` must be set to the corresponding revision identifier of the repository, e.g. the commit hash for Git or the revision number for SVN repositories. For example, if the `ubus` package clones from Git revision <https://git.openwrt.org/?p=project/ubus.git;a=commitdiff;h=221ce7e7ff1bd1a0c9995fa9d32f58e865f7207f>, then its Makefile should specify `PKG_SOURCE_DATE:=2018-10-06` and `PKG_SOURCE_VERSION:=221ce7e7ff1bd1a0c9995fa9d32f58e865f7207f`.

The build system will combine these variables into a common version identifier and truncate the revision identifier if needed. Given the values in the example, the resulting version identifier will be `2018-10-06-221ce7e7`. This is done to make repository revision identifiers comparable to each other since SCM systems like Git or Mercurial use SHA hashes to identify revisions which are no monotonically increasing numerical values.

#### Package Revisions

Source packages must specify a `PKG_RELEASE` value identifying the revision of the source package. In contrast to the `PKG_VERSION`, `PKG_SOURCE_DATE` and `PKG_SOURCE_VERSION` variables which are identifying the upstream version of the program code being packaged, the `PKG_RELEASE` variable denotes the revision of the package itself.

The package revision should start with the value `1` and must be increased whenever modifications are made to the package which might cause changes to the executables or other files contained within the resulting binary packages. When the package is updated to a newer `PKG_VERSION` or `PKG_SOURCE_VERSION`, the `PKG_RELEASE` must be reset back to `1`.

Some examples for dealing with the `PKG_RELEASE` are:

- Fixed a typo in the maintainer's mail address -\> `PKG_RELEASE` stays unchanged
- Added a `--disable-acl` to the configure arguments -\> `PKG_RELEASE` is incremented
- Updated `libfoo` from version `0.2.1` to `0.2.2` -\> `PKG_RELEASE` is reset to `1` and `PKG_VERSION` set to `0.2.2`

### Downloading

When declaring the source download method in the Makefile, direct tarball downloads via [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) or HTTPS are the preferred way to acquire package sources, Git or other SCM clones should be avoided, mainly to keep the locally cached source downloads reproducible.

If direct Git cloning is required (for example because there is no release tarballs available upstream) then Git via HTTPS is preferred over Git via [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) is preferred over Git via its native protocol. Many OpenWrt users are behind corporate firewalls which disallow Git native traffic (TCP 9418).

#### Mirror Sites

The use of mirror sites for tarball download locations is encouraged and helps to reduce the traffic load on upstream project sites. When choosing mirrors for a package, please try to ensure that the mirror is:

- officially endorsed by the upstream project (E.G. mentioned on their download page).
- well reachable by people from a wide range of different locations.
- using proper SSL certificates when using HTTPS.
- hosting the most current version of the software in question.

Multiple mirrors can be specified in a package Makefile by assigning a white-space separated list of URLs to the `PKG_SOURCE_URL` variable. It is a good convention to assign the upstream project site itself to the end of the mirror list. This provides a canonical fallback location in case a new version has not yet propagated to all mirrors and conveys the original download location to casual readers.

Try to limit the amount of mirror sites to 3 to 5 different locations, including the main download site.

### Building

The build recipes in a source package should adhere to the OpenWrt defaults as much as possible. This ensures that source package declarations remain compact and free of copy-pasted boilerplate code.

By default, the build system uses a set of standard `./configure` and `make` invocations to build packages in a refined manner. Most of these steps can be influenced through a number of variables to alter the way the actual commands are executed.

Please refer to [package-defaults.mk](https://git.openwrt.org/?p=openwrt/openwrt.git;a=blob;f=include/package-defaults.mk) to learn how the default recipes are implemented.

Whenever possible, try to avoid redefining the default macros but use the provided variables to encode functional differences.

Example for a bad redefinition:

    define Build/Compile
            (cd $(PKG_BUILD_DIR)/nonstandard/dir/; make)
    endef

Example for achieving the same using variable overrides:

    MAKE_PATH := nonstandard/dir/

Likewise, do not attempt to override `Build/Configure` but use `CONFIGURE_ARGS` to pass switches like `CONFIGURE_ARGS += --enable-acl` or `CONFIGURE_ARGS += --without-systemd` and `CONFIGURE_VARS` to pass environment variables to the configuration script, like `CONFIGURE_VARS += ac_cv_func_snprintf=yes`.

#### Hooks

In some cases it is possible to arrange things before e.g. the `./configure` script is invoked in order to touch files, remove things or echo values into stampfiles. In such cases, it is permissible to redefine the recipe in order to achieve the desired result. Use the default implementations of the macros to call the original behaviour after the custom work is done. Refer to the examples below for some common use cases.

##### Running custom commands after unpacking but before patching the sources:

    define Build/Prepare
      echo "1.2.3" > $(PKG_BUILD_DIR)/version.txt
      $(call Build/Prepare/Default)
    endef

##### Running custom commands after unpacking and patching the sources:

    define Build/Prepare
      $(call Build/Prepare/Default)
      rm -f $(PKG_BUILD_DIR)/m4/libtool.m4
      cp $(PKG_BUILD_DIR)/make/Makefile.linux $(PKG_BUILD_DIR)/Makefile
    endef

##### Running custom commands before invoking configure:

    define Build/Configure
      touch $(PKG_BUILD_DIR)/ChangeLog
      $(call Build/Configure/Default)
    endef

##### Running custom commands after executing make:

    define Build/Compile
      $(call Build/Compile/Default)
      cp $(PKG_BUILD_DIR)/src/libfoo.so.1.2 $(PKG_BUILD_DIR)/src/libfoo.so
    endef

#### Autotools

Many open source projects rely on GNU autoconf and automake as their build system which may lead to a number of problems in a cross compilation setting.

Usual problems revolve around:

- `configure` scripts attempting to call programs to test certain features which might fail if the called program has been built for another architecture
- Pregenerated `configure` scripts embedding faulty and possibly outdated versions of `libtool` causing runtime problems on the target system
- Macros in configure scripts probing host system details to configure the package for the target, like calling `uname` to figure out the kernel version or endianess
- Projects shipping convenience scripts like `autogen.`sh which make certain assumptions about the host system or try to call the improper version of utilities like `autopoint` or `autoconf,` leading to macro errors and version mismatches when executing the generated configure scripts and Makefiles

Due to the complex nature of the GNU autoconf/automake system there is no single set of solutions to a given problem but rather a general list of guidelines and best practices to adhere to.

- Never patch the generated / shipped `configure` script but fix the underlying `configure.ac` or `configure.in` files and rely on the `PKG_FIXUP:=autoreconf` facility to regenerate the config script. This also has the nice side-effect of updating the embedded `libtool` version and using a cross-compile-safe set of standard macros, replacing unsafe ones in many cases.
- Make `./configure` invocations as explicit as possible by forcibly disabling or enabling any feature which depends on the presence of an external library, e.g. `--disable-acl` to build a given package without `libacl` support on both systems having `libacl` in their staging directory and systems not providing this library. Failure to do so will result in errors like `Package example is missing dependencies for the following libraries: libfoo.so.1` on systems that happen to build `libfoo` before building example.
- Pre-seed `configure` tests that cannot be reliably determined in a cross-compile setting. Properly written autoconf test macros can be overridden by cache-variables in the form `ac_cv_somename=value` - use this facility to skip tests which would otherwise fail or result in host-system specific values. For example the `libpcap` package passes `ac_cv_linux_vers=$(LINUX_VERSION)` to prevent `./configure` from calling the host systems `uname` in order to figure out the kernel version. The names of the involved cache variables can be found in the `config.log` file within the package build directory or by inspecting the generated shell code of the `configure` program. Use the `CONFIGURE_VARS` variable to pass the cache variables down to the actual `./configure` invocation
- Never trust shipped `autogen.sh` and similar scripts, rather use `PKG_FIXUP:=autoreconf` to (re)generate the configure script and automake templates and encode additionally needed steps in the appropriate build recipes.

## Dependencies

A *source package* may depend on a number of other packages, either to satisfy compilation requirements or to enforce the presence of specific functionality, such as shared libraries or support programs at runtime on the target system.

There are two kinds of dependencies; *build dependencies*, specified by the `PKG_BUILD_DEPENDS` Makefile variable and *runtime dependencies*, declared in the `DEPENDS` variable of the corresponding `define Package/...` Makefile sections.

*Build dependencies* are resolved at package compilation time and instruct the build system to download, patch and compile each mentioned dependency before the source package itself is compiled. This is required when the compilation process of a package depends on resources such as header files from another package. *Build dependencies* are not transformed into *runtime dependencies* and should only be used when the resources of the packages being depended upon are solely required at compilation time. This usually is the case for header-only libraries such as the C++ Boost project or static `.a` library archives that result in no dynamic runtime requirements.

*Runtime dependencies*, on the other hand, specify the relation of *binary packages*, instructing the package manager to fetch and install the listed dependencies before installing the binary package itself. A *runtime dependency* automatically implies a *build dependency*, so if a `DEPENDS` variable within a `define Package/...` section of a given source package specifies the name of a `define Package/...` section of another source package, the build system will take care of compiling the other package before compiling the source package specifiying the runtime dependency.

Package dependencies, regardless of whether they're build-time or runtime ones, should only require packages within the same *package feed* or provided by the *base feed* located within the main OpenWrt `package/` directory.

Dependencies among packages in different, non-base feeds are strongly discouraged as it is not guaranteed that each build system has access to all feeds.

## Shared libraries

Packages providing shared libraries require additional care to ensure that software depending on these libraries remains functional and is not accidentally broken by incompatible updates, changed APIs, removed functionality and so on.

While the package dependency mechanisms will ensure that the build system compiles library packages before the program packages requiring them, they do not guarantee that such programs are getting rebuilt when the library package itself is updated.

Also, in the case of binary package repositories, installing a newer, incompatible version of library packages would break installed programs relying on this library unless an additional version constraint is applied to the dependency.

The OpenWrt build system introduced the concept of an `ABI_VERSION` to address the issue of program dependencies on specific versions of a shared library, requiring exactly the ABI the program was initially compiled and linked against. The `ABI_VERSION` value is supposed to reflect the `SONAME` of the library being packaged.

### SONAME

Most upstream libraries contain an [ELF SONAME](https://en.wikipedia.org/wiki/Soname) attribute denoting the canonical name of the library including a version suffix specifying the version of the exposed ABI. Changes breaking the exposed ABI usually result in a change to the `SONAME`.

When a program is linked against such a library, the linker will resolve the `SONAME` of the requested shared object and put it into the `DT_NEEDED` section of the resulting program executable. Upon starting the program, the dynamic linker on the target system will consult the `DT_NEEDED` section to find the required libraries within the standard library search path.

### ABI Version

Setting an `ABI_VERSION` variable on a library package definition will cause the build system to track the value of this variable and trigger recompilations in all packages depending on this library package whenever the value is incremented. This is useful to force re-linking of all programs after a library has been changed to an incompatible version.

The `ABI_VERSION` value is also appended to the binary package name and all dependencies mentioning the binary library package will be automatically expanded to contain the `ABI_VERSION` suffix. If for example a library package `libfoo` specifies `ABI_VERSION:=1.0`, the resulting binary package will be called `libfoo1.0` and when a package `bar` specifies `DEPENDS:=+libfoo`, the resulting runtime dependency will be `Depends: libfoo1.0`.

This ensures that incompatible updates to the `libfoo` library, denoted by an `ABI_VERSION` increase, will cause programs linked against it from then on to have a different runtime dependency, allowing the OpenWrt package manager to notice the change.

Example: when `libfoo` is updated to a new, incompatible version and its `SONAME` property changed from `libfoo.so.1.0` to `libfoo.so.1.1`, then `ABI_VERSION` should be increased from `1.0` to `1.1`, causing the resulting `libfoo` binary package to be called `libfoo1.1`. Source packages linking `libfoo` from then on, will have runtime dependencies on `libfoo1.1`.

When a shared library is packaged, the `ABI_VERSION` variable of the corresponding `define Package/lib...` section should be set to the `SONAME` of the `.so` library file contained within the binary package. The `SONAME` usually reflects the library's internal `ABI` version and is incremented whenever incompatible changes to the public APIs are made within the library, E.G. when changing a function call signature or when removing exported symbols.

The public [ABI tracker](https://abi-laboratory.pro/index.php?view=tracker) is useful to decide whether an `ABI_VERSION` change is required when updating an existing library package to a newer upstream version.

Some upstream library projects do not use a `SONAME` at all or do not properly version their libraries, in such cases, the `ABI_VERSION` must be set to a value in the form `YYYYMMDD`, reflecting the source code change date of the last incompatible change being made.

### Contents

In order to allow multiple versions of binary library packages to coexist on the same system, each library package should only contain shared object files specific to the `SONAME` version of the library getting packaged.

A typical upstream library `libbar` with version 1.2.3 and `SONAME` of `libbar.so.1` will usually provide these files after compilation:

    libbar.so       -> libbar.so.1.2.3 (symlink)
    libbar.so.1     -> libbar.so.1.2.3 (symlink)
    libbar.so.1.2.3      (shared library object)

The binary `libbar1` package should only contain `libbar.so.1` and `libbar.so.1.2.3` as the common `libbar.so` symlink would clash with a `libbar2` package providing version `2.0.0` of `libbar`.

Versionless symlinks are usually not needed for libraries using the `SONAME` attribute and are only used during the linking phase when compiling programs depending on the library.

#### NOTE

`$(INSTALL_DATA)` and `$(INSTALL_BIN)` will currently copy the file contents instead of the symlink itself, so prefer `$(CP)` when copying the library symlinks. Consider the example above, if you run

    $([INSTALL_BIN](../cookbook/chunked-reference/minimal-openwrt-package-makefile.md)) $(PKG_INSTALL_DIR)/usr/lib/libbar.so.* $(1)/usr/lib/

it will result in two copies of the library in regular files:

    libbar.so.1               (regular file)
    libbar.so.1.2.3           (regular file)

Instead, use

    $(CP) $(PKG_INSTALL_DIR)/usr/lib/libbar.so.* $(1)/usr/lib/

and you'll get the intended result:

    libbar.so.1     -> libbar.so.1.2.3 (symlink)
    libbar.so.1.2.3                    (regular file)

While there has been a proposal to change `$(INSTALL_BIN)` behavior, `$(CP)` will continue to work.

### Development Files

Source packages defining binary packages that ship shared libraries should declare a `Build/InstallDev` recipe that copies all resources required to discover and link the shared libraries into the staging directory.

A typical `InstallDev` recipe usually copies all library symlinks (including the unversioned ones), header files and, in case they're provided, pkg-config (`*.pc`) files.

---

# Overriding Build Options

Some packages might require overriding certain build options because we are cross compiling.

The build system allows for several entries under **Advanced configuration options (for developers) \> Kernel extra CFLAGS** and **Advanced configuration options (for developers) \> Target Options** which will pass the defined flags onto the kernel and packages respectively.

## Autotools: Autoconf

**CONFIGURE_VARS**

1.  Override ac_cv\_\* variables that are normally set during autoconf ./configure phase.
2.  override pkgconfig configure vars

Example: Some packages check for features (header files) and do not offer -enable/-with or -disable/-without configure options (to be written into \_ARGS). Search for the configure variable in config.log and preset it in CONFIGURE_VARS.

          CONFIGURE_VARS += \
                  ac_cv_header_regex_h=no

**CONFIGURE_ARGS**

1.  Add options/test after ./configure

:!: Looking into config.log can help

## Compiler flags

Available compiler flags are handled in rules.mk

    TARGET_CFLAGS:=$(TARGET_OPTIMIZATION)$(if $(CONFIG_DEBUG), -g3) $(EXTRA_OPTIMIZATION)
    TARGET_CXXFLAGS = $(TARGET_CFLAGS)
    TARGET_ASFLAGS_DEFAULT = $(TARGET_CFLAGS)
    TARGET_ASFLAGS = $(TARGET_ASFLAGS_DEFAULT)
    TARGET_CPPFLAGS:=-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/include
    TARGET_LDFLAGS:=-L$(STAGING_DIR)/usr/lib -L$(STAGING_DIR)/lib

Typically you should only add additional options to compile flags.

    TARGET_CFLAGS+= -Wall

Example: Support multiple library versions via .../usr/lib/libname-v1/ or .../usr/lib/libname-v2/ and select them.

:!: BUG CXXFLAGS can contain wrong options because GCC/G++ accept different ones.

## Make

MAKE_VARS in include/package-defaults.mk

    MAKE_VARS = \
            CFLAGS="$(TARGET_CFLAGS) $(EXTRA_CFLAGS) $(TARGET_CPPFLAGS) $(EXTRA_CPPFLAGS)" \
            CXXFLAGS="$(TARGET_CXXFLAGS) $(EXTRA_CXXFLAGS) $(TARGET_CPPFLAGS) $(EXTRA_CPPFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) $(EXTRA_LDFLAGS)"

MAKE_FLAGS

    MAKE_FLAGS = \
            $(TARGET_CONFIGURE_OPTS) \
            CROSS="$(TARGET_CROSS)" \
            ARCH="$(ARCH)"

## CMake

include/cmake.mk

CMAKE_OPTIONS

CMAKE_HOST_OPTIONS

## Scons

SCONS_VARS are set in include/scons.mk

    SCONS_VARS = \
            CC="$(TARGET_CC_NOCACHE)" \
            CXX="$(TARGET_CXX_NOCACHE)" \
            CFLAGS="$(TARGET_CFLAGS) $(EXTRA_CFLAGS)" \
            CXXFLAGS="$(TARGET_CFLAGS) $(EXTRA_CFLAGS)" \
            CPPFLAGS="$(TARGET_CPPFLAGS) $(EXTRA_CPPFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) $(EXTRA_LDFLAGS)" \
            DESTDIR="$(PKG_INSTALL_DIR)"

SCONS_OPTIONS have no default set.

scons is only used by a few packages: [iotivity](https://github.com/openwrt/packages/blob/master/net/iotivity/Makefile) smartsnmpd

---

# Creating packages

**See also -\> [Package Policy Guide](package-policies)**, which contains a wealth of extra technical information not covered here.

One of the things that we've attempted to do with OpenWrt's template system is make it incredibly easy to port software to OpenWrt. If you look at a typical package directory in OpenWrt you'll find three things:

- package/Makefile
- package/patches
- package/files

The patches directory is optional and typically contains bug fixes or optimizations to reduce the size of the executable. The files directory is optional. It typically includes default config or init files.

The package `Makefile` is the important item because it provides the steps actually needed to download and compile the package.

Looking at one of the package makefiles, you'd hardly recognize it as a makefile. Through what can only be described as blatant disregard and abuse of the traditional make format, the `Makefile` has been transformed into an object oriented template which simplifies the entire ordeal.

Here, for example, is package/bridge/Makefile:

``` make
include $(TOPDIR)/rules.mk

PKG_NAME:=bridge
PKG_VERSION:=1.0.6
PKG_RELEASE:=1

PKG_BUILD_DIR:=$(BUILD_DIR)/bridge-utils-$(PKG_VERSION)
PKG_SOURCE:=bridge-utils-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=@SF/bridge
PKG_HASH:=9b7dc52656f5cbec846a7ba3299f73bd

include $(INCLUDE_DIR)/package.mk

define Package/bridge
  SECTION:=base
  CATEGORY:=Network
  TITLE:=Ethernet bridging configuration utility
  URL:=http://bridge.sourceforge.net/
endef

define Package/bridge/description
 Ethernet bridging configuration utility
 Manage ethernet bridging; a way to connect networks together to
 form a larger network.
endef

define Build/Configure
  $(call Build/Configure/Default,--with-linux-headers=$(LINUX_DIR))
endef

define Package/bridge/install
        $(INSTALL_DIR) $(1)/usr/sbin
        $(INSTALL_BIN) $(PKG_BUILD_DIR)/brctl/brctl $(1)/usr/sbin/
endef

$(eval $(call BuildPackage,bridge))
```

## BuildPackage variables

As you can see, there's not much work to be done; everything is hidden in other makefiles and abstracted to the point where you only need to specify a few variables.

- `PKG_NAME` - The name of the package, as seen via menuconfig and ipkg. Avoid using underscores in the package name, to avoid build failures--for example, the underscore separates name from version information, and may confuse the build system in hard-to-spot places.
- `PKG_VERSION` - The upstream version number that we're downloading
- `PKG_RELEASE` - The version of this package Makefile. Should be initially set to 1, and reset to 1 whenever the `PKG_VERSION` is changed. Increment it when `PKG_VERSION` stays the same, but when there are functional changes to the installed artifacts.
- `PKG_LICENSE` - The license(s) the package is available under, [SPDX](https://spdx.org/licenses/) form.
- `PKG_LICENSE_FILES`- file containing the license text
- `PKG_BUILD_DIR` - Where to compile the package
- `PKG_SOURCE` - The filename of the original sources
- `PKG_SOURCE_URL` - Where to download the sources from (directory)
- `PKG_HASH` - A checksum to validate the download. It can be either a MD5 or SHA256 checksum, but SHA256 should be used, see [scripts/download.pl](commit>?p=openwrt/openwrt.git;a=blob;f=scripts/download.pl;h=676c6e9e6b10b6a44ed2bbc03a7ba3c983aaf639;hb=HEAD#l66)
- `PKG_CAT` - How to decompress the sources (zcat, bzcat, unzip)
- `PKG_URL`. - Upstream project homepage
- `PKG_BUILD_DEPENDS` - Packages that need to be built before this package. Use this option if you need to make sure that your package has access to includes and/or libraries of another package at build time. Specify the directory name (i.e. openssl) rather than the binary package name (i.e. libopenssl). This build variable only establishes the build time dependency. Use `DEPENDS` to establish the runtime dependencies. This variable uses the same syntax as `DEPENDS` below.
- `PKG_CONFIG_DEPENDS` - specifies which config options influence the build configuration and should trigger a rerun of Build/Configure on change
- `PKG_INSTALL` - Setting it to "1" will call the package's original "make install" with prefix set to `PKG_INSTALL_DIR`
- `PKG_INSTALL_DIR` - Where "make install" copies the compiled files
- `PKG_FIXUP` - See below
- `PKG_CPE_ID` - Variable defining Common Platform Enumeration (CPE) identifier, which uniquely identifies application usually in vulnerability tracking. The CPE standard itself is maintained by NIST and documented at[Official Common Platform Enumeration (CPE) Dictionary](https://nvd.nist.gov/products/cpe)
- `PKG_CVE_IGNORE` - Variable for defining CVEs that don't apply to this version of the package due to features not enabled, or affecting other platforms (e.g. Windows issues or features that are not used and so not relevant)
- `PKG_CVE_FIXED` - Variable for defining CVEs that are patches in the current version, but aren't properly marked as fixed at cve.org in the current version

Optional support for fetching sources from a VCS (git, bzr, svn, etc), see [Use source repository](#use_source_repository) below for more information:

- `PKG_SOURCE_PROTO` - the protocol to use for fetching the sources (git, svn, etc).
- `PKG_SOURCE_URL` - source repository to fetch from. The URL scheme must be consistent with `PKG_SOURCE_PROTO` (e.g. `git://`), but most VCS accept `http://` or `https://` URLs nowadays.
- `PKG_SOURCE_VERSION` - must be specified, the commit hash or SVN revision to check out.
- `PKG_SOURCE_DATE` - a date like `2017-12-25`, will be used in the name of generated tarballs.
- `PKG_MIRROR_HASH` - SHA256 checksum of the tarball generated from the source repository checkout (previously named `PKG_MIRROR_MD5SUM`). See [below](#use_source_repository) for details.
- `PKG_SOURCE_SUBDIR` - where the temporary source checkout should be stored, defaults to `$(PKG_NAME)-$(PKG_VERSION)`

The `PKG_*` variables define where to download the package from; @SF is a special keyword for downloading packages from sourceforge. The md5sum is used to verify the package was downloaded correctly and PKG_BUILD_DIR defines where to find the package after the sources are uncompressed into \$(BUILD_DIR). PKG_INSTALL_DIR defines where the files will be copied after calling "make install" (set with the PKG_INSTALL variable), and after that you can package them in the install section.

At the bottom of the file is where the real magic happens, "BuildPackage" is a macro setup by the earlier include statements. BuildPackage only takes one argument directly -- the name of the package to be built, in this case "bridge". All other information is taken from the define blocks. This is a way of providing a level of verbosity, it's inherently clear what the DESCRIPTION variable in Package/bridge is, which wouldn't be the case if we passed this information directly as the Nth argument to BuildPackage.

Avoid reuse of PKG_NAME in call, define and eval lines for consistency and readability. Write the full name instead.

## Testing a package Makefile

There is [support for a range of sanity checks](commit>?p=openwrt/openwrt.git;a=commit;h=7a315b0b5d6aa91695853a8647383876e4b49a7a) like mismatched checksums.

To check your package:

    make package/nlbwmon/download
    make package/nlbwmon/check V=s

To automatically attempt to fix the Makefile:

    make package/nlbwmon/check V=s FIXUP=1

Note: despite the similar name, this has nothing to do with the `PKG_FIXUP` variable presented below.

## PKG_FIXUP

Some packages that use autotools end up needing fixes to work around autotools using host tools instead of the build environment tools. OpenWrt defines some PKG_FIXUP rules to help work around this.

``` make
PKG_FIXUP:=autoreconf
PKG_FIXUP:=patch-libtool
PKG_FIXUP:=gettext-version
```

Any variations of this you see in the wild are simply aliases for these.

##### autoreconf

This fixup performs

- autoreconf -f -i
- touch required but maybe missing files
- ensures that openwrt-libtool is linked
- suppresses autopoint/gettext

##### patch-libtool

If the shipped automake recipes are broken beyond repair, then simply find instances of libtool, detect their version and apply OpenWrt fix patches to it.

##### gettext-version

This fixup suppresses version mismatch errors in automake's gettext support.

#### Tips

Packages that are using Autotools should work with simply "PKG_FIXUP:=autoreconf". However there might be issues with required versions.

:!: Instead of patching `./configure`, one should fix the file from which `./configure` is generated in autotools: `configure.ac` (or `configure.in`, for very old packages). Another important file is `Makefile.am` from which `Makefile`s (with `configure` output) are generated.

## Package Sourcecode

OpenWrt Buildroot supports many different ways to download external source code.

### Use packed source code archive

Most packages use a packed .tar.gz, .tar.bz2, .tar.xz or similar source code file.

### Use source repository

`PKG_SOURCE_PROTO` supports download from various repositories to integrate development versions:

``` make
PKG_SOURCE_PROTO:=bzr
PKG_SOURCE_PROTO:=cvs
PKG_SOURCE_PROTO:=darcs
PKG_SOURCE_PROTO:=git
PKG_SOURCE_PROTO:=hg
PKG_SOURCE_PROTO:=svn
```

Besides the source repository `PKG_SOURCE_URL`, you also need to specify which exact version you are building using `PKG_SOURCE_VERSION` e.g. a commit hash for git, or a revision number for svn. The `PKG_SOURCE_VERSION` can be a git tag and specified like `PKG_SOURCE_VERSION:=v$(PKG_VERSION)`.

Buildroot will first clone the source repository, and then generate a tarball from the source repository, with a name like `dl/odhcpd-2017-08-16-94e65ee0.tar.xz`.

You should also define `PKG_MIRROR_HASH` with the SHA256 checksum of this generated tarball. This way, users building OpenWrt will directly download the generated tarball from a buildbot and verify its checksum, thus avoiding a clone of the source repository.

:!: The tarballs generated from svn checkouts are not reproducible, so you should avoid defining `PKG_MIRROR_HASH` when building from svn!

To generate `PKG_MIRROR_HASH` automatically, use the following (replace `package/odhcpd` by your package):

    # First add "PKG_MIRROR_HASH:=skip" to the package Makefile and/or "HASH:=skip", if required.
    make package/odhcpd/download V=s
    make package/odhcpd/check FIXUP=1 V=s

:!: `PKG_MIRROR_HASH:=skip` does not currently work, see [GitHub issue \#19757](https://github.com/openwrt/openwrt/issues/19757)

Complete git example:

``` make
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/jow-/nlbwmon.git
PKG_SOURCE_DATE:=2017-08-02
PKG_SOURCE_VERSION:=32fc0925cbc30a4a8f71392e976aa94b586c4086
PKG_MIRROR_HASH:=caedb66cf6dcbdcee0d1525923e203d003ef15f34a13a328686794666f16171f
```

History: `PKG_MIRROR_MD5SUM` was [introduced in 2011](commit>?p=openwrt/openwrt.git;a=commitdiff;h=b568a64f8c1f7c077c83d8c189d4c84ca270aeb4) and [renamed to `PKG_MIRROR_HASH` in 2016](commit>?p=openwrt/openwrt.git;a=commitdiff;h=7416d2e046b87b262b407f8af70b8dd9b2927c70).

### Bundle source code with OpenWrt Makefile

It is also possible to have the source code in the package/\<packagename\> directory. Often a ./src/ subdirectory is used.

    Examples: px5g , px5g-standalone

### Download override

Bundled source code does not need overriding.

You can download additional data from external sources.

``` make
USB_IDS_VER:=0.321
USB_IDS_FILE:=usb.ids.$(USB_IDS_VER)
define Download/usb_ids
  FILE:=$(USB_IDS_FILE)
  URL_FILE:=usb.ids
  URL:=@GITHUB/vcrhonek/hwdata/v$(USB_IDS_VER)
  HASH:=00aa21766bb078186d2bc2cca9a2ae910aa2b787a810e97019b1b3f94c9453f2
endef
$(eval $(call Download,usb_ids))
```

and unpack it or integrate it into the build process

``` make
define Build/Prepare
        $(Build/Prepare/Default)
        $(CP) $(DL_DIR)/$(USB_IDS_FILE) $(PKG_BUILD_DIR)/usb.ids
endef
```

You can modify UNPACK_CMD or call/modify PKG_UNPACK manually in your Build/Prepare section.

``` make
UNPACK_CMD=ar -p "$(DL_DIR)/$(PKG_SOURCE)" data.tar.xz | xzcat | tar -C $(1) -xf -
```

``` make
define Build/Prepare
        $(PKG_UNPACK)
#       we have to download additional stuff before patching
        (cd $(PKG_BUILD_DIR) && ./contrib/download_prerequisites)
        $(Build/Patch)
endef
```

    Examples: px5g, px5g-standalone, usbutils, debootstrap, gcc,

## BuildPackage defines

##### Package/

matches the argument passed to buildroot, this describes the package the menuconfig and ipkg entries. Within Package/ you can define the following variables:

-  SECTION - The type of package (currently unused)
-  CATEGORY - Which menu it appears in menuconfig
-  TITLE - A short description of the package
-  URL - Where to find the original software
-  MAINTAINER - (required for new packages) Who to contact concerning the package
-  DEPENDS - (optional) Which packages must be built/installed before this package. See [below](#dependency_types) for the syntax
-  EXTRA_DEPENDS - (optional) Runtime dependencies, don't get built, only added to package `control` file
-  PROVIDES - (optional) allow to define a virtual package that might be provided by multiple real-packages
-  PKGARCH - (optional) Set this to "all" to produce a package with "Architecture: all" (See below)
-  USERID - (optional) a username:groupname pair to create at package installation time.

##### PKGARCH (optional)

By default, packages are built for the target architecture, and the ipk files generated are tagged that way. This is normally correct, for any compiled code, but if a package only contains scripts or resources, marking it with PKGARCH:=all will make a single ipk file that can be installed on any target architecture. (It will still be compiled into `bin/packages/arch/`, however.)

##### Package/conffiles (optional)

A list of config files installed by this package, one file per line. The file list section should not be indented: no leading tabs or spaces in the section.

##### Package/description

A free text description of the package

##### Build/Prepare (optional)

A set of commands to unpack and patch the sources. You may safely leave this undefined.

##### Build/Configure (optional)

You can leave this undefined if the source doesn't use configure or has a normal config script, otherwise you can put your own commands here or use "\$(call Build/Configure/Default,)" as above to pass in additional arguments for a standard configure script.

##### Build/Compile (optional)

How to compile the source; in most cases you should leave this undefined, because then the default is used, which calls make. If you want to pass special arguments to make, use e.g. "\$(call Build/Compile/Default,FOO=bar)"

##### Build/Install (optional)

How to install the compiled source. The default is to call "make install". Again, to pass special arguments or targets, use "\$(call Build/Install/Default,install install-foo)". Note that you need put all the needed make arguments here. If you just need to add something to the "install" argument, don't forget the "install" itself.

##### Build/InstallDev (optional)

For things needed to compile packages against it (static libs, header files), but that are of no use on the target device.

##### Build/Clean (optional)

For things needed to be wiped out during cleanup procedure.

##### Package/install

A set of commands to copy files into the ipkg which is represented by the \$(1) directory. As source you can use relative paths which will install from the unpacked and compiled source, or \$(PKG_INSTALL_DIR) which is where the files in the Build/Install step above end up.

##### Package/preinst

The actual text of the script which is to be executed before installation. Don't forget to include the `#!/bin/sh`. If you need to abort installation, have the script return `false`.

##### Package/postinst

The actual text of the script which is to be executed after installation. Don't forget to include the `#!/bin/sh`. Alternatively you can also use an [uci-default script](/docs/guide-developer/uci-defaults) which will be executed automatically on runtime installations by opkg or embedding into an image.

##### Package/prerm

The actual text of the script which is to be executed before removal. Don't forget to include the `#!/bin/sh`. If you need to abort removal, have the script return `false`.

##### Package/postrm

The actual text of the script which is to be executed after removal. Don't forget to include the `#!/bin/sh`.

The reason that some of the defines are prefixed by "Package/" and others are simply "Build" is because of the possibility of generating multiple packages from a single source. OpenWrt works under the assumption of one source per package `Makefile`, but you can split that source into as many packages as desired. Since you only need to compile the sources once, there's one global set of "Build" defines, but you can add as many "Package/" defines as you want by adding extra calls to BuildPackage -- see the dropbear package for an example.

## Building in a subdirectory of the source

Some software has no Makefile directly at the root of the tarball. For instance, it is common to have a `src/` directory with all source files and a Makefile. The problem is that OpenWRT's build system will try to run `make` in `PKG_BUILD_DIR`; this will fail if there is no Makefile there. To solve this problem, use the `MAKE_PATH` variable, for instance:

    MAKE_PATH:=src

This path is relative to `PKG_BUILD_DIR` and defaults to `.`. Alternatively, you can override `Build/Compile` (see above), though this is more work.

## Dependency Types

Various types of dependencies can be specified, which require a bit of explanation for their differences. More documentation is available at [Using Dependencies](/docs/guide-developer/dependencies)

|              |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|:-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| +\<foo\>     | Package will depend on package \<foo\> and will select it when selected.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| \<foo\>      | Package will depend on package \<foo\> and will be invisible until \<foo\> is selected.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| @FOO         | Package depends on the config symbol CONFIG_FOO and will be invisible unless CONFIG_FOO is set. This usually used for depending on certain Linux versions or targets, e.g. @TARGET_foo will make a package only available for target foo. You can also use boolean expressions for complex dependencies, e.g. @(!TARGET_foo&&!TARGET_bar) will make the package unavailable for foo and bar.                                                                                                                                                                                                                                                                       |
| +FOO:\<bar\> | Package will depend on \<bar\> if CONFIG_FOO is set, and will select \<bar\> when it is selected itself. The typical use case would be if there are compile time options for this package toggling features that depend on external libraries. :!: Note that the + replaces the @. :!: There is limited support for boolean operators here compared to the @ type above. Negation ! is only supported to negate the whole condition. Parentheses are ignored, so use them only for readability. Like C, && has a higher precedence than \|\|. So +(YYY\|\|FOO&&BAR):package will select package if CONFIG_YYY is set or if both CONFIG_FOO and CONFIG_BAR are set. |
| @FOO:\<bar\> | Package will depend on \<bar\> if CONFIG_FOO is set, and will be invisible until \<bar\> is selected when CONFIG_FOO is set.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

Some typical config symbols for (conditional) dependencies are:

|                                   |                                                                                                                                                                                 |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TARGET\_\<foo\>                   | Target \<foo\> is selected                                                                                                                                                      |
| TARGET\_\<foo\>\_\<bar\>          | If the target \<foo\> has subtargets, subtarget \<foo\> is selected. If not, profile \<foo\> is selected. This is in addition to TARGET\_\<foo\>                                |
| TARGET\_\<foo\>\_\<bar\>\_\<baz\> | Target \<foo\> with subtarget \<bar\> and profile \<baz\> is selected.                                                                                                          |
| LINUX_3_X                         | Linux version used is 3.x.\*                                                                                                                                                    |
| LINUX_2_6_X                       | Linux version used is 2.6.x.\* (:1: only used for backfire and earlier)                                                                                                         |
| LINUX_2_4                         | Linux version is 2.4 (:!: only used in backfire and earlier, and only for target brcm-2.4)                                                                                      |
| USE_UCLIBC, USE_GLIBC, USE_EGLIBC | To (not) depend on a certain libc.                                                                                                                                              |
| BROKEN                            | Package doesn't build or work, and should only be visible if "Show broken targets/packages" is selected. Prevents the package from failing builds by accidentally selecting it. |
| IPV6                              | IPv6 support in packages is selected.                                                                                                                                           |

Note that the syntax above applies to the `DEPENDS` field only.

`PKG_BUILD_DEPENDS` does not use `+` or `@`, but otherwise uses the same syntax. You can write `FOO:bar` to build `bar` if `CONFIG_FOO` is defined (if you want to build bar if package FOO is selected, use `PACKAGE_FOO:bar`). You may use `!`, `||` and `&&` as explained above. `PKG_BUILD_DEPENDS` uses the name from the `PKG_NAME`, not the individual packages. For example, if you want to have openssl to be a build-dependency, you would write `PKG_BUILD_DEPENDS:=openssl`, whereas if your package depends and selects the openssl library, you'd have `DEPENDS:=+libopenssl`. Notice that there's no installable package named `openssl`: the library is `libopenssl`, the utility is `openssl-util`, but their `PKG_NAME` is `openssl`. If you need a host-built package, append `/host` to the `PKG_NAME`, e.g. `PKG_BUILD_DEPENDS:=openssl/host`. A package listed in `PKG_BUILD_DEPENDS` will be built even if it is not selected in `make menuconfig`.

`EXTRA_DEPENDS` does not accept the conditional or select dependency syntax. However, unlike `DEPENDS` and `PKG_BUILD_DEPENDS`, it is generated at package-build-time, so you may use Makefile functions to add them conditionally. For example, to get the equivalent of `DEPENDS:=@SOMESYMBOL:foo +PACKAGE_somepkg:bar`, you can write `EXTRA_DEPENDS:=$(if $(CONFIG_SOMESYMBOL),foo) $(if $(CONFIG_PACKAGE_somepkg),bar)`. :!: Note that neither `foo` or `bar` will be selected in menuconfig, or guaranteed to be built before your package, even if selected somewhere else. For this reason, it is seldom used in packages.

`EXTRA_DEPENDS` is more often used to depend on specific versions, by adding the desired version specification in parentheses, using \>=,\>,\<,\<=,=. Make sure you add the `PKG_RELEASE` number if you're using '=', such as `EXTRA_DEPENDS:=foo (=2.0.0-1)`: where foo's `PKG_VERSION` is 2.0.0, and `PKG_RELEASE` is 1.

## Configure a package source

Example:

``` make
CONFIGURE_ARGS += \
        --disable-native-affinity \
        --disable-unicode \
        --enable-hwloc

CONFIGURE_VARS += \
        ac_cv_file__proc_stat=yes \
        ac_cv_file__proc_meminfo=yes \
        ac_cv_func_malloc_0_nonnull=yes \
        ac_cv_func_realloc_0_nonnull=yes

```

To set variables (autoconfig internal ones or CPPFLAGS,CFLAGS, CXXFLAGS, LDFLAGS for example) or configure arguments. Setting configure arguments is common. Setting VARS is needed when the configure.ac autoconf source script does not work well on cross compilation or finding libraries.

:!: The article [packages.flags](/docs/guide-developer/packages.flags) contains more information and examples about overriding and setting these.

### Host tools required

In order to build your package, you may require some extra build tools or libraries that are not already in the standard OpenWrt toolchain. These must be built as part of the OpenWrt build process ie. you cannot rely on them being installed via the build system's package manager (or manually by the user or administrator). This is so that OpenWrt can be built reliably and repeatably on a wide variety of machines. These are referred to as *host tools* because they run on (or are compiled for) the host, not the target.

If your package requires host tools in order to be built for the target machine, these should go in `PKG_BUILD_DEPENDS` and will end with `/host`. For example, the `json-glib` package requires the [Meson build system](https://mesonbuild.com/) to generate build files, as well as Glib2 on the host, so it has:

``` make
PKG_BUILD_DEPENDS:=glib2/host meson/host
```

A package might itself provide host tools, and building or using *those* might require *other* host tools to be built first. These other tools go in `HOST_BUILD_DEPENDS`. For example, the host tool that the Meson package provides requires another build tool, [Ninja](https://ninja-build.org/), so it has this line:

``` make
HOST_BUILD_DEPENDS:=ninja/host
```

The makefile for a package that provides host tools will:

- Include `$(INCLUDE_DIR)/host-build.mk`. You can look at this makefile for the details of the host tool build process.
- Have sections similar to the `Build/...` sections of other packages, but they will start with `Host/`. For example, `Host/Configure`, `Host/Compile` and `Host/Install` are common.
- Call `$(eval $(call HostBuild))` at the end.

Some examples of packages that *provide* host tools (and their makefiles):

- [Meson](https://github.com/openwrt/packages/blob/master/devel/meson/Makefile)
- [Samba 4](https://github.com/openwrt/packages/blob/master/net/samba4/Makefile) - note that the Samba 4 *target* package actually depends on the Samba 4 *host* package provided in the same makefile
- [Go (golang)](https://github.com/openwrt/packages/blob/master/lang/golang/golang/Makefile) - this is a much more complex example, and useful if you're thinking of adding support for a new language in OpenWrt.

##### BUILD

If you want to build only the host tool to test or check a compilation error for host compilation, then you could also build only the host tool with the following command.

- Compile:
  make ./package/\<package_name\>/**host**/compile
- Clean:
  make ./package/\<package_name\>/**host**/clean
- Update:
  make ./package/\<package_name\>/**host**/update

The make arguments **QUILT=1** and **V=s** are also valid.

##### PATCHES

If you want to patch the host and target tool separately, then you have to add `HOST_PATCH_DIR:=./<directory>`. For example, add `HOST_PATCH_DIR:=./patches-host` to the `Makefile` so the host tool has its own patch directory. The target tool will still use the standard patch directory `./patches` in its package directory.

##### NOTES

All variables in your pre/post install/removal scripts should have double (\$\$) instead of a single (\$) string characters. This will inform "make" to not interpret the value as a variable, but rather just ignore the string and replace the double \$\$ by a single \$ -- [More Info](https://forum.openwrt.org/viewtopic.php?pid=85197#p85197)

After you've created your package Makefile, the new package will automatically show in the menu the next time you run "make menuconfig" and if selected will be built automatically the next time "make" is run.

DESCRIPTION is obsolete, use Package/PKG_NAME/description.

## Adding configuration options

If you would like to configure your package installation/compilation in the menuconfig you can do the following: Add MENU:=1 to your package definition like this:

``` make
define Package/mjpg-streamer
  SECTION:=multimedia
  CATEGORY:=Multimedia
  TITLE:=MJPG-streamer
  DEPENDS:=@!LINUX_2_4 +libpthread-stubs +jpeg
  URL:=http://mjpg-streamer.wiki.sourceforge.net/
  MENU:=1
endef
```

Create a config key in the Makefile:

``` make
define Package/mjpg-streamer/config
    source "$(SOURCE)/Config.in"
endef
```

Create a Config.in file directory where the Makefile is located with the content like this:

``` make
    # Mjpg-streamer configuration
    menu "Configuration"
        depends on PACKAGE_mjpg-streamer

    config MJPEG_STREAMER_AUTOSTART
        bool "Autostart enabled"
        default n

        menu "Input plugins"
            depends on PACKAGE_mjpg-streamer
            config MJPEG_STREAMER_INPUT_FILE
                bool "File input plugin"
                help
                    You can stream pictures from jpg files on the filesystem
                default n

            config MJPEG_STREAMER_INPUT_UVC
                bool "UVC input plugin"
                help
                    You can stream pictures from an Universal Video Class compatible webcamera
                default y

            config MJPEG_STREAMER_FPS
                depends MJPEG_STREAMER_INPUT_UVC
                int "Maximum FPS"
                default 15

            config MJPEG_STREAMER_PICT_HEIGHT
                depends MJPEG_STREAMER_INPUT_UVC
                int "Picture height"
                default 640

            config MJPEG_STREAMER_PICT_WIDTH
                depends MJPEG_STREAMER_INPUT_UVC
                int "Picture width"
                default 480

            config MJPEG_STREAMER_DEVICE
                depends MJPEG_STREAMER_INPUT_UVC
                string "Device"
                default /dev/video0

            config MJPEG_STREAMER_INPUT_GSPCA
                bool "GSPCA input plugin"
                help
                    You can stream pictures from a gspca supported webcamera Note this module is deprecated, use the UVVC plugin instead
                default n
        endmenu

        # ......

    endmenu
```

Above, you can see examples for various types of config parameters. Finally, you can check your configuration parameters in your Makefile in the following way (note that you can reference the parameter's value with its name prefixed with `CONFIG_`):

``` make
ifeq ($(CONFIG_MJPEG_STREAMER_INPUT_UVC),y)
    $(CP) $(PKG_BUILD_DIR)/input_uvc.so $(1)/usr/lib
endif
```

## Working on local application source

If you are still working on the application, itself, at the same time as you are working on the packaging, it can be very useful to have OpenWrt build your work in progress code, rather than a specific version+md5sum combination checked out of revision control, or downloaded from your final "release" location. There are a few ways of doing this.

### CONFIG_SRC_TREE_OVERRIDE

This is an option in menuconfig. See "Advanced configuration options (for developers)" -\> "Enable package source tree override"

This allows you to point to a local git tree. (And only git) Say your package is defined in my_cool_feed/awesome_app.

    ln -s /path/to/local/awesome_app_tree/.git feeds/my_cool_feed/awesome_app/git-src
    make package/awesome_app/{clean,compile} V=s

Benefits of this approach are that you don't need any special infrastructure in your package makefiles, they stay completely as they would be for a final build. The downside is that it only builds whatever is currently **committed** in HEAD of your local tree. (This could be a private testing branch, but everything you want to include in the package must be committed: uncommitted local changes will not be included in the build.) This will also use a **separate** directory for building and checking out the code. So, any built objects in your local git tree (for example, a build targeting a different architecture) will be left alone, but whichever **branch** is checked out in your tree determines where HEAD is.

### USE_SOURCE_DIR

As part of deprecating `package-version-override.mk` (below), a method to point directly to local source was introduced.

    make package/awesome_app/clean V=s
    make package/awesome_app/prepare USE_SOURCE_DIR=~/src/awesome_src V=s
    make package/awesome_app/clean V=s

(`V=s` is optional above)

This doesn't require any config change to enable rules, doesn't require that you have a local git tree, and doesn't require any files to be committed.

At least at present, however, this has the following problems:

- make clean doesn't clean the source link directory, but still seems to be removing a link
- make prepare needs to be run every time
- make package/awesome_app/{clean,compile} USE_SOURCE_DIR=~blah doesn't work
- Seems to have bad interactions with leaving USE_SOURCE_DIR set for other (dependent?) packages.

See <http://www.mail-archive.com/openwrt-devel@lists.openwrt.org/msg23122.html> for the original discussion of this new feature

:!: Since OpenWrt 19.07.5, `USE_SOURCE_DIR` only works with packages that have a valid `PKG_MIRROR_HASH`. For packages under development, hash checking can be disabled by setting `PKG_MIRROR_HASH=skip`. This allows using `USE_SOURCE_DIR` for packages pulling sources from a developer branch (e.g. having `PKG_SOURCE_VERSION:=branchname`) without updating `PKG_MIRROR_HASH` every time.

### (Deprecated) package-version-override.mk

:!: \*\* Don't use this anymore! \*\*

Support for this style of local source building was removed. This style required a permanent modification to your package makefile, and then entering a path via menuconfig to where the source was found. It was fairly easy to use, and didn't care whether your local source was in git or svn or visual source safe even, but it had the major downside that the "clean" target simply didn't work (as it simply removed a symlink for cleaning).

If you build a current OpenWrt tree, with packages that still attempt to use this style of local building, you **will** receive errors like so: ERROR: please fix package/feeds/feed_name/application_name/Makefile - see logs/package/feeds/feed_name/application_name/dump.txt for details

If you need/want to keep using this style, where it's available, make sure you include without failing if it was missing:

    -include $(INCLUDE_DIR)/package-version-override.mk

## Creating packages for kernel modules

A [kernel module](https://wiki.archlinux.org/title/Kernel_module) is an installable program which extends the behavior of the linux kernel. A kernel module gets loaded after the kernel itself, E.G. using `insmod`.

Many kernel programs are included in the Linux source distribution; typically the kernel build may be configured to, for each program,

- compile it into the kernel as a built-in,
- compile it as a loadable kernel module, or
- ignore it.

See ***FIX:Customizingthekerneloptions customizing the kernel options*** for including it in the kernel.

To include one of these programs as a loadable module, select the corresponding kernel option in the OpenWrt configuration (see [Build Configuration](/docs/guide-developer/toolchain/use-buildsystem#image_configuration)). If your favorite kernel module does not appear in the OpenWrt configuration menus, you must add a stanza to one of the files in the package/kernel/linux/modules directory. Here is an example extracted from .../modules/block.mk:

``` make
define KernelPackage/loop
  SUBMENU:=$(BLOCK_MENU)
  TITLE:=Loopback device support
  KCONFIG:= \
        CONFIG_BLK_DEV_LOOP \
        CONFIG_BLK_DEV_CRYPTOLOOP=n
  FILES:=$(LINUX_DIR)/drivers/block/loop.ko
  AUTOLOAD:=$(call AutoLoad,30,loop)
endef

define KernelPackage/loop/description
 Kernel module for loopback device support
endef

$(eval $(call KernelPackage,loop))
```

Changes to the \*.mk files are not automatically picked up by the build system. To force re-reading the metadata, either touch the kernel package Makefile using `touch package/kernel/linux/Makefile` (on older revisions `touch package/kernel/Makefile`) or to delete the `tmp/` directory of the buildroot.

You can also add kernel modules which are *not* part of the linux source distribution. In this case, a kernel module appears in the package/ directory, just as any other package does. The package/Makefile uses `KernelPackage/xxx` definitions in place of `Package/xxx`.

For example, here is `package/madwifi/Makefile`:

``` make
#
# Copyright (C) 2006 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#
# $Id$

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=madwifi
PKG_VERSION:=0.9.2
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.bz2
PKG_SOURCE_URL:=@SF/$(PKG_NAME)
PKG_HASH:=a75baacbe07085ddc5cb28e1fb43edbb
PKG_CAT:=bzcat

PKG_BUILD_DIR:=$(KERNEL_BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

RATE_CONTROL:=sample

ifeq ($(ARCH),mips)
  HAL_TARGET:=mips-be-elf
endif
ifeq ($(ARCH),mipsel)
  HAL_TARGET:=mips-le-elf
endif
ifeq ($(ARCH),i386)
  HAL_TARGET:=i386-elf
endif
ifeq ($(ARCH),armeb)
  HAL_TARGET:=xscale-be-elf
endif
ifeq ($(ARCH),powerpc)
  HAL_TARGET:=powerpc-be-elf
endif

BUS:=PCI
ifneq ($(CONFIG_LINUX_2_4_AR531X),)
  BUS:=AHB
endif
ifneq ($(CONFIG_LINUX_2_6_ARUBA),)
  BUS:=PCI AHB  # no suitable HAL for AHB yet.
endif

BUS_MODULES:=
ifeq ($(findstring AHB,$(BUS)),AHB)
  BUS_MODULES+=$(PKG_BUILD_DIR)/ath/ath_ahb.$(LINUX_KMOD_SUFFIX)
endif
ifeq ($(findstring PCI,$(BUS)),PCI)
  BUS_MODULES+=$(PKG_BUILD_DIR)/ath/ath_pci.$(LINUX_KMOD_SUFFIX)
endif

MADWIFI_AUTOLOAD:= \
    wlan \
    wlan_scan_ap \
    wlan_scan_sta \
    ath_hal \
    ath_rate_$(RATE_CONTROL) \
    wlan_acl \
    wlan_ccmp \
    wlan_tkip \
    wlan_wep \
    wlan_xauth

ifeq ($(findstring AHB,$(BUS)),AHB)
    MADWIFI_AUTOLOAD += ath_ahb
endif
ifeq ($(findstring PCI,$(BUS)),PCI)
    MADWIFI_AUTOLOAD += ath_pci
endif

define KernelPackage/madwifi
  SUBMENU:=Wireless Drivers
  DEFAULT:=y if LINUX_2_6_BRCM |  LINUX_2_6_ARUBA |  LINUX_2_4_AR531X |  LINUX_2_6_XSCALE, m if ALL
  TITLE:=Driver for Atheros wireless chipsets
  DESCRIPTION:=\
    This package contains a driver for Atheros 802.11a/b/g chipsets.
  URL:=http://madwifi.org/
  VERSION:=$(LINUX_VERSION)+$(PKG_VERSION)-$(BOARD)-$(PKG_RELEASE)
  FILES:= \
        $(PKG_BUILD_DIR)/ath/ath_hal.$(LINUX_KMOD_SUFFIX) \
        $(BUS_MODULES) \
        $(PKG_BUILD_DIR)/ath_rate/$(RATE_CONTROL)/ath_rate_$(RATE_CONTROL).$(LINUX_KMOD_SUFFIX) \
        $(PKG_BUILD_DIR)/net80211/wlan*.$(LINUX_KMOD_SUFFIX)
  AUTOLOAD:=$(call AutoLoad,50,$(MADWIFI_AUTOLOAD))
endef

MADWIFI_MAKEOPTS= -C $(PKG_BUILD_DIR) \
        PATH="$(TARGET_PATH)" \
        ARCH="$(LINUX_KARCH)" \
        CROSS_COMPILE="$(TARGET_CROSS)" \
        TARGET="$(HAL_TARGET)" \
        TOOLPREFIX="$(KERNEL_CROSS)" \
        TOOLPATH="$(KERNEL_CROSS)" \
        KERNELPATH="$(LINUX_DIR)" \
        LDOPTS=" " \
        ATH_RATE="ath_rate/$(RATE_CONTROL)" \
        DOMULTI=1

ifeq ($(findstring AHB,$(BUS)),AHB)
  define Build/Compile/ahb
    $(MAKE) $(MADWIFI_MAKEOPTS) BUS="AHB" all
  endef
endif

ifeq ($(findstring PCI,$(BUS)),PCI)
  define Build/Compile/pci
    $(MAKE) $(MADWIFI_MAKEOPTS) BUS="PCI" all
  endef
endif

define Build/Compile
    $(call Build/Compile/ahb)
    $(call Build/Compile/pci)
endef

define Build/InstallDev
    $(INSTALL_DIR) $(STAGING_DIR)/usr/include/madwifi
    $(CP) $(PKG_BUILD_DIR)/include $(STAGING_DIR)/usr/include/madwifi/
    $(INSTALL_DIR) $(STAGING_DIR)/usr/include/madwifi/net80211
    $(CP) $(PKG_BUILD_DIR)/net80211/*.h $(STAGING_DIR)/usr/include/madwifi/net80211/
endef

define KernelPackage/madwifi/install
    $(INSTALL_DIR) $(1)/etc/init.d
    $(INSTALL_DIR) $(1)/lib/modules/$(LINUX_VERSION)
    $(INSTALL_DIR) $(1)/usr/sbin
    $(INSTALL_BIN) ./files/madwifi.init $(1)/etc/init.d/madwifi
    $(CP) $(PKG_BUILD_DIR)/tools/{madwifi_multi,80211debug,80211stats,athchans,athctrl,athdebug,athkey,athstats,wlanconfig} $(1)/usr/sbin/
endef

$(eval $(call KernelPackage,madwifi))
```

------------------------------------------------------------------------

#### The use of MODPARAMS

If a module require some special param to be passed on Autoload, it's available MODPARAMS using the following syntax:

    MODPARAMS.module_ko:=example_param1=example_value example_param2=example_value2

For example here is `package/kernel/cryptodev-linux/Makefile`:

``` make
define KernelPackage/cryptodev
    SUBMENU:=Cryptographic API modules
    TITLE:=Driver for cryptographic acceleration
    URL:=http://cryptodev-linux.org/
    VERSION:=$(LINUX_VERSION)+$(PKG_VERSION)-$(BOARD)-$(PKG_RELEASE)
    DEPENDS:=+kmod-crypto-authenc +kmod-crypto-hash
    FILES:=$(PKG_BUILD_DIR)/cryptodev.$(LINUX_KMOD_SUFFIX)
    AUTOLOAD:=$(call AutoLoad,50,cryptodev)
    MODPARAMS.cryptodev:=cryptodev_verbosity=-1
endef
```

------------------------------------------------------------------------

#### Make a Kernel Module required for boot

Some modules may be required for the correct operation of the device. One example would be an ethernet driver required for the correct operation of the switch on the device.
To flag a Kernel Module this way it's needed to append `1` to `AUTOLOAD` at the end.
This cause the module file to get placed in /etc/modules-boot.d/ instead of /etc/modules.d/, modules-boot.d is processed by procd init before launching preinit and correctly works both in a normal boot and in a failsafe boot. All of this is with the assumption that the module is installed in the firmware and not with OPKG on a loaded system as **it needs to be present before /overlay is mounted**. (OPKG installed module are present only in after /overlay is mounted)

For example here is `phy-realtek` in `package/kernel/linux/modules/netdevices.mk`:

``` make
define KernelPackage/phy-realtek
   SUBMENU:=$(NETWORK_DEVICES_MENU)
   TITLE:=Realtek Ethernet PHY driver
   KCONFIG:=CONFIG_REALTEK_PHY
   DEPENDS:=+kmod-libphy
   FILES:=$(LINUX_DIR)/drivers/net/phy/realtek.ko
   AUTOLOAD:=$(call AutoLoad,18,realtek,1)
endef
```

## File installation macros

INSTALL_DIR, [INSTALL_BIN](../cookbook/chunked-reference/minimal-openwrt-package-makefile.md), INSTALL_DATA are used for creating a directory, copying an executable, or copying a data file. +x is set on the target file for [INSTALL_BIN](../cookbook/chunked-reference/minimal-openwrt-package-makefile.md), independent of its mode on the host.

From the big document:

Package/\<name\>/install:

A set of commands to copy files out of the compiled source and into the ipkg which is represented by the \$(1) directory. Note that there are currently 4 defined install macros:

    INSTALL_DIR
    install -d -m0755
    [INSTALL_BIN](../cookbook/chunked-reference/minimal-openwrt-package-makefile.md)
    install -m0755
    INSTALL_DATA
    install -m0644
    INSTALL_CONF
    install -m0600

## Packaging a service

If you want to install a service (something that should start/stop at boot time, that has a /etc/init.d/blah script), read the [Init Scripts](/docs/techref/initscripts) section of the Technical Reference and the [Procd init scripts](/docs/guide-developer/procd-init-scripts) section of the Developer's Guide. A key point is to make sure that the init.d script can be run on the host. At image build time, all init.d scripts found are run on the host, looking for the START=20/STOP=99 lines. This is what installs the symlinks in /etc/rc.d.

Packages have default postinst/prerm scripts that will run `/etc/init.d/foo enable` (creating the symlinks) or `/etc/init.d/foo disable` (removing the symlinks) when they are installed/removed by opkg.

Very basic example of a suitable init.d script. Please note that the newer style version does not work properly with interpreted executables (i.e. scripts). That is because start-stop-daemon is used by service_stop() in a way that it makes it confuse the script name with the interpreter name.

:!: **procd** style init is used in some init.d scripts since [this commit](commit>?p=openwrt/openwrt.git;a=commit;h=f87409440298121ae1fbd718a17267cc180438e4). See [procd-init-scripts](/docs/guide-developer/procd-init-scripts) for more details on that.

``` bash
#!/bin/sh /etc/rc.common
# "new(er)" style init script
# Look at /lib/functions/service.sh on a running system for explanations of what other SERVICE_
# options you can use, and when you might want them.

START=80
APP=mrelay
SERVICE_WRITE_PID=1
SERVICE_DAEMONIZE=1

start() {
        service_start /usr/bin/$APP
}

stop() {
        service_stop /usr/bin/$APP
}
```

``` bash
#!/bin/sh /etc/rc.common
###########################################
# NOTE - this is an old style init script #
###########################################

START=80
APP=mrelay
PID_FILE=/var/run/$APP.pid

start() {
        start-stop-daemon -S -x $APP -p $PID_FILE -m -b
}

stop() {
        start-stop-daemon -K -n $APP -p $PID_FILE -s TERM
        rm -rf $PID_FILE
}
```

See [Configuration in scripts](/docs/guide-developer/config-scripting) for details on how to access UCI configuration information from an init.d script, for instance to set command-line parameters or to generate a config file for your service.

## How To Submit Patches to OpenWrt

Packages are maintained in a separate repository to reduce maintenance overhead. The general guidelines for OpenWrt still apply, but see the README in the packages repository for latest information.

- <https://github.com/openwrt/packages>
- [https://dev.openwrt.org/wiki/SubmittingPatches](/submitting-patches)

See [the original announcement](https://web.archive.org/web/20170629071358/https://lists.openwrt.org/pipermail/openwrt-devel/2014-June/025810.html) of this change.

---

# Create a sample procd init script

 This article is a mostly verbatim copy of [this archived article](https://web.archive.org/web/20220518121856/https://joostoostdijk.com/posts/service-configuration-with-procd), all credit goes to the original author, **Joost Oostdijk**
It was adapted to use an equivalent shell script instead of NodeJS JavaScript, because it's lighter and better for a simple testing setup on most OpenWrt devices.

Procd init scripts gives us many nice to use features by default such as a restart strategy and the ability to store and read configuration from the UCI system.

## Setting up

As example, lets say we’d want to create shell script as a service and that this service can be configured with a message and a timeout in order for us to be reminded to get up from ur desks once in a while. Our service name will be myservice and it depends on the following script

``` bash
#!/bin/sh

#these if statements will check input and place default values if no input is given
#they will also check if input is a number so you can call
#this script with just a time and it will still work correctly

if [ "$1" = '' ]; then
    name="You"
else
    if echo "$1" | egrep -q '^[0-9]+$'; then
        name="You"
    else
        name="$1"
    fi
fi

if [ "$2" = '' ]; then
    every="5"
else
    every="$2"
fi

if echo "$1" | egrep -q '^[0-9]+$'; then
    every="$1"
fi

#endless loop, will print the message every X seconds as indicated in the $every variable

while [ 1 ]; do
    echo "Hey, $name, it's time to get up"
    sleep $every
done

exit 0

```

Place it in **/var/myscript.sh** and test it by running on OpenWrt

    $ /bin/sh /var/myscript.sh "Name Surname"

## Creating a basic procd script

Now that we have a working script, we can make a service out of it. Create a file in /etc/init.d/myservice with the following content

``` bash
#!/bin/sh /etc/rc.common
USE_PROCD=1
START=95
STOP=01
start_service() {
    procd_open_instance
    procd_set_param command /bin/sh "/var/myscript.sh"
    procd_close_instance
}
```

First, it includes the common ‘run commands’ file /etc/rc.common needed for a service. This file defines several functions that can be used to manage the service lifecycle, it supports old style init scripts as well as procd scripts. In order to tell that we want to use the new style we then set the [USE_PROCD](../cookbook/chunked-reference/procd-service-lifecycle.md) flag.

The START option basically tell the system when the service should start and stop during startup and shutdown of OpenWrt.

This init script isn’t very useful at the moment but it shows the basic building blocks on which we will develop the script further.

## Enabling the service

To tell OpenWrt that we have a new service we would need to run

\<code\> /etc/init.d/myservice enable\</code\>

This will install a symlink for us in directory /etc/rc.d/ called S95myservice (because `START=95`) which points to our respective service script in /etc/init.d/. OpenWrt will start the services according the the order of S\* scripts in /etc/rc.d/. To see the order you could simply run

    $ ls -la /etc/rc.d/S*

...

It is useful to be able to influence the order of startup of services, if our service would be dependent on the network we’d make sure that the START sequence ‘index’ is at least 1 more than the START sequence of the network service.

The same rules apply for the optional STOP parameters, only this time it defines in which order the services will be shutdown. To see Which shutdown scripts are activated you can run

    $ ls -la /etc/rc.d/K*

You always need to define a START or STOP sequence in your script (you can also define both). If you define a STOP sequence you also want to define a stop_service() handler in the init script. This handler is usually taking care of cleaning up service resources or persistence of data needed when the service starts again. Testing the service

Finally, lets just test our service. Open a second shell to the OpenWrt device and run

    $ logread -f

This will tail the system logs on the device. then enable (if you havent done that yet), and start the service.

    $ /etc/init.d/myservice enable
    $ /etc/init.d/myservice start

After about 5 seconds we should see the message repeat itself in the log, but we didn’t… We still need to redirect stdout and stderr to logd in order to see the console.log output in the system logs.

``` bash
#!/bin/sh /etc/rc.common

USE_PROCD=1

START=95
STOP=01

start_service() {
    procd_open_instance
    procd_set_param command /bin/sh "/var/myscript.sh"
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}
```

Now, when we restart we should see something like

    $ logread -f
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ... ommitted ... Hey, You, it's time to get up
    ...

Setting up a service simple script like above with procd already gives us some advantages

\* Common api to manage services \* The service will automatically start at every boot

## Service configuration

It’s time to get more personal, and to that we will use OpenWrts UCI configuration interface. Create a configuration file /etc/config/myservice with the following content

    config myservice 'hello'
        option name 'Joost'
        option every '5'

UCI will immediately pick this up and the config for our service can be inspected like

    $ uci show myservice
    myservice.hello=myservice
    myservice.hello.name=Joost
    myservice.hello.every='5'

Also single options can be requested

    $ uci get myservice.hello.name

and we can also change specific configuration with UCI

    $ uci set myservice.hello.name=Knight
    $ uci commit

Now, we’ll introduce a couple of changes to the service script in order to read and use the configuration in our script.

## Loading service configuration

We can already pass configuration to the node script by passing arguments to it. The only thing we need to do is load the services matching configuration, store the values of the options we need into some variables and pass them into the command that starts the script.

``` bash
#!/bin/sh /etc/rc.common

USE_PROCD=1

START=95
STOP=01

CONFIGURATION=myservice

start_service() {
    # Reading config
    config_load "${CONFIGURATION}"
    local name
    local every

    config_get name hello name
    config_get every hello every

    procd_open_instance

    # pass config to script on start
    procd_set_param command /bin/sh "/var/myscript.sh" "$name" "$every"
    procd_set_param file /etc/config/myservice
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}
```

We can pass new configuration by running

    $ uci set myservice.hello.name=Woodrow Wilson Smith
    $ uci commit

Note that in the service script the arguments are quoted, which allows us to use spaces in the name option. If we wouldn’t do this, each part of the name would be treated as a separate argument.

Apart from the loading and passing of config to our script we also added

    ...
    [procd_set_param](../cookbook/chunked-reference/procd-service-lifecycle.md) file /etc/config/myservice
    ...

With that line in place we are able to restart the service whenever only our configuration has changed.

    $ /etc/init.d/myservice reload

## Advanced options

There are a couple of more options that can be configured in a procd scripts ‘instance block’ that might be handy to know about. I’ll list a few here, but this is by no means covering everything.

- **respawn**
  respawn your service automatically when it terminates for some reason.
  `[procd_set_param](../cookbook/chunked-reference/procd-service-lifecycle.md) respawn \
        ${respawn_threshold:-3600} \
        ${respawn_timeout:-5} ${respawn_retry:-5}`
  In this example we respawn if process terminates sooner than respawn_threshold, it is considered crashed and after 5 retries the service is stopped. However, if it terminates later than respawn_threshold, it would be respawned indefinitely.

- **pidfile**
  Configure where to store the pid file
  `procd_set_param pidfile $PIDFILE`

- **env vars**
  Pass environment variables to your process with
  `procd_set_param env A_VAR=avalue`

- **ulimit**
  If you need to set resource limits for your process you can use
  `procd_set_param limits core="unlimited"`
  To see the system wide settings for ulimt on an OpenWrt device you can run
  `$ ulimit -a
  -f: file size (blocks)             unlimited
  -t: cpu time (seconds)             unlimited
  -d: data seg size (kb)             unlimited
  -s: stack size (kb)                8192
  -c: core file size (blocks)        0
  -m: resident set size (kb)         unlimited
  -l: locked memory (kb)             64
  -p: processes                      475
  -n: file descriptors               1024
  -v: address space (kb)             unlimited
  -w: locks                          unlimited
  -e: scheduling priority            0
  -r: real-time priority             0
  `
- **user**
  To change the user that runs the service you can use
  \<code\> [procd_set_param](../cookbook/chunked-reference/procd-service-lifecycle.md) user nobody \</code\>
  Default OpenWrt only has a ‘root’ user or ‘nobody’ as the process owner.
  You can add users with the usual linux way, see [Create a non-privileged user in OpenWrt](/docs/guide-user/security/secure.access#create_a_non-privileged_user_in_openwrt) or if you are creating an actual package you can use [buildpackage defines](/docs/guide-developer/packages#buildpackage_defines) to make OpenWrt generate the user when the package is installed.

---

# Procd Init Scripts

A procd init script is similiar to an old init script, but with a few differences:

- procd expects services to start as if they were to **run in the foreground**, but of course procd runs them the background from the user's perspective.
- Different shebang line: `#!/bin/sh /etc/rc.common`
- procd expects that shell variable (not environment variable) `initscript` is set to the path of the script that invoked it
- Explicitly use procd `USE_PROCD=1`

Example:

``` bash
#!/bin/sh /etc/rc.common

START=90
STOP=01
USE_PROCD=1

service_data() {
    /usr/sbin/mesh11sd -v
}

start_service() {
    procd_open_instance
    procd_set_param command /bin/sh "/usr/sbin/mesh11sd"
    procd_append_param command daemon
    procd_set_param pidfile /var/run/mesh11sd.pid
    procd_set_param term_timeout 1
    procd_set_param stdout 1
    procd_set_param respawn 150 10 10
    procd_close_instance
}

stop_service() {
    /sbin/uci revert mesh11sd
    /sbin/uci revert wireless
    /sbin/uci revert dhcp
    /sbin/uci revert network
    /usr/sbin/nft delete table bridge mesh11s 2> /dev/null
}

```

## How do these scripts work?

Init script has to handle two main tasks:

1.  Define current configuration (state) for service instance(s)
2.  Specify when (and optionally how) to reconfigure service

Defining configuration is handled in the `start_service()`. For each instance to be run it has to specify service command and all its parameters. All that info is stored internally by `procd`. On a single change (compared to the last used configuration) `procd` restarts a service.

Init script has to specify all possible `procd` events that may require service reconfiguration. Defining all triggers is done in the `service_triggers()` using `procd_add_*_trigger` helpers.

Optionally init script may handle service reconfiguration process on its own. It's useful for services that don't require complete restart to use new configuration. It can be handled by specifying custom `reload_service()` which prevents `start_service()` from being called and so stops `procd` from restarting service.

## Service Data

Service data is sent to `stdout` by the function `service_data()`. This would typically be the version of the service (see the example).

## Defining service instances

The purpose of `start_service()` (see next section to see when it's called) is to define instance(s) with:

1.  Command to execute to start service
2.  Information on what to observe for changes (e.g. files or devices) - optional
3.  Settings that `procd` should use (e.g. auto respawning, logging stdout, user to use) - optional

The above information is stored by `procd` as a service instance state. On every relevant system change (e.g. config change), `start_service()` is called by designed triggers. If it generates any different state (e.g. command will change) than the previous one, `procd` will detect it and restart the service.

Defining service instance details is handled by setting parameters. Some values are set directly in the `start_service()` (like `command`) while some are determined by `procd` (like `file` and file hash). There are two helpers for setting parameters:

1.  `procd_set_param()`
2.  `procd_append_param()`

The below example lists supported parameters and describes them. For implementation details see the [procd.sh](commit>?p=openwrt/openwrt.git;a=blob;f=package/system/procd/files/procd.sh).

``` bash
start_service() {
         procd_open_instance [instance_name]
         procd_set_param command /sbin/your_service_daemon -b -a --foo # service executable that has to run in **foreground**.
         procd_append_param command -bar 42 # append command parameters

         # respawn automatically if something died, be careful if you have an alternative process supervisor
         # if process exits sooner than respawn_threshold, it is considered crashed and after 5 retries the service is stopped
         # if process finishes later than respawn_threshold, it is restarted unconditionally, regardless of error code
         # notice that this is literal respawning of the process, not in a respawn-on-failure sense
         procd_set_param respawn ${respawn_threshold:-3600} ${respawn_timeout:-5} ${respawn_retry:-5}

         procd_set_param env SOME_VARIABLE=funtimes  # pass environment variables to your process
         procd_set_param limits core="unlimited"  # If you need to set ulimit for your process
         procd_set_param file /var/etc/your_service.conf # /etc/init.d/your_service reload will restart the daemon when these files have changed
         procd_set_param netdev dev # likewise, but for when dev's ifindex changes.
         procd_set_param data name=value ... # likewise, but for when this data changes.
         procd_set_param stdout 1 # forward stdout of the command to logd
         procd_set_param stderr 1 # same for stderr
         procd_set_param user nobody # run service as user nobody
         procd_set_param pidfile /var/run/somefile.pid # write a pid file on instance start and remove it on stop
         procd_set_param term_timeout 60 # wait before sending SIGKILL
         procd_close_instance
}
```

### Stopping services

`stop_service()` is only needed when you need special things to stop your service. `stop_service()` is called *before* procd killed the service.

If you want to add a check *after* procd has sent the terminate signal (e.g. wait for the process to be really gone), you can define an extra function `service_stopped()`.

### Init scripts during compilation

WARNING: initscripts **will run** while building OpenWrt images (when installing packages in what will become a ROM image) in the **host system** (right now, for actions "*enable*" and "*disable*"). **They must not fail, or have undesired side-effects in that situation.** When being run by the build system, environment variable **\${IPKG_INSTROOT}** will be set to the working directory being used. On the "target system", that environment variable will be empty/unset. Refer to "/lib/functions.sh" and also to "/etc/rc.common" in package "base-files" for the nasty details.

## Specifying triggers

While `start_service()` takes care of setting service instances states and submitting them to the `procd` (for a potential service restart), it has to be explicitly called to do so. In most cases it should happen on some related change.

That's where `service_triggers()` comes in handy and allows specifying triggers. Most system important changes result in generating events that `service_triggers()` can use for triggering various actions. There are multiple `procd_add_*_trigger()` helpers for that purpose.

Every configurable service has to specify what system changes should result in its reconfiguration. Those events should be defined in the `service_triggers()` using available helpers. When related `procd` `service` event occurs it will result in executing `/etc/init.d/<foo> reload`.

Example:

``` bash
service_triggers()
{
        procd_add_reload_trigger "<uci-file-name>" "<second-uci-file>"
        procd_add_reload_interface_trigger <interface>
        procd_add_reload_mount_trigger <path> [<path> ...]
}
```

| Function                           | Arguments            | Event used      | Description                                     |
|:-----------------------------------|:---------------------|:----------------|-------------------------------------------------|
| procd_add_reload_trigger           | list of config files | `config.change` | Uses `/etc/init.d/<foo> reload` as the handler  |
| procd_add_reload_interface_trigger | interface name       | `interface.*`   | Uses `/etc/init.d/<foo> reload` as the handler  |
| procd_add_reload_mount_trigger     | paths to watch for   | `mount.add`     | Uses `/etc/init.d/<foo> reload` as the handler  |
| procd_add_restart_mount_trigger    | paths to watch for   | `mount.add`     | Uses `/etc/init.d/<foo> restart` as the handler |

 When using `uci` from command line `uci commit` doesn't generate `config.change` event. It requires calling `reload_config` afterwards.

This does not apply to using `uci` over `rpcd` plugin.

 Adding `interface.*` trigger and having `/etc/init.d/<foo> reload` called won't automatically make `procd` notice any state change and won't make it restart a service.

Relevant interface has to be made part of service state using the `procd_set_param netdev`.

 Using mount triggers depends on mount notifications emitted by `blockd`. Hence `blockd` needs to be installed and the mount need to be configured in `/etc/config/fstab`.

See also [fstab](/docs/guide-user/storage/fstab)

See use cases of [procd_add_interface_trigger](https://github.com/openwrt/packages/search?q=procd_add_interface_trigger), [procd_add_reload_trigger](https://github.com/openwrt/packages/search?q=procd_add_reload_trigger), [procd_add_reload_mount_trigger](https://github.com/openwrt/packages/search?q=procd_add_reload_mount_trigger) in the OpenWrt packages repository.

### ucitrack

In older versions of OpenWrt, a system called "ucitrack" attempted to track UCI config files, and the processes that depended on each of them, and would restart them all as needed. This too, is replaced with ubus/procd, and expanded to allow notifying services when network interfaces change.

## Manual reload

Sometimes service state may depend on information that doesn't have any events related. This may happen e.g. with service native configuration files that don't get build using UCI config.

In such cases `procd` should be told to use relevant config file using `procd_set_param file /etc/foo.conf`. After every config file modification `/etc/init.d/foo reload` should be called manually.

## Custom service reload

By default (without `reload_service()` specified) calling `/etc/init.d/<foo> reload` results in running `start_service()` and `procd` comparing states. In some cases a more complete control over `reload` action may be needed thought.

### Forcing service restart

If some service requires a restart when `reload` is called, it can be implemented as follows:

``` bash
reload_service()
{
        echo "Explicitly restarting service, are you sure you need this?"
        stop
        start
}
```

j==== Reloading service setup ====

Some services may support reloading configuration without a complete restart. It's usually implemented using \`SIGHUP\` or similar signal.

OpenWrt comes with a `procd_send_signal()` helper that doesn't require passing PID directly. Example:

    reload_service() {
             procd_send_signal service_name [instance_name] [signal]
    }

The *signal* argument is `SIGHUP` by default and must be specified by NAME. You can get available signals using `kill -l`.

The *service_name* is the basename of the `init.d` script, e.g. `yourapp` for the `/etc/init.d/yourapp`.

The *instance_name* allows specifying custom instance name in case it was used like `procd_open_instance [instance_name]`. If *instance_name* is unspecified, or '' '\*' '' then the signal will be delivered to all instances of the service.

**Note** You can also send signals to named procd services from outside initscripts. Simply load the procd functions and send the signal as before.

    #!/bin/sh
    . /lib/functions/procd.sh
    procd_send_signal service_name [instance_name] [signal]

 You can also configure reload by signal with `procd_set_param reload_signal` service option.

## Service jails

procd can isolate services using various Linux features typically used for (slim-)containers: *chroot* and *namespaces* (and *limits*, *seccomp*, *capabilities* as well as setting `PR_SET_NO_NEW_PRIVS`, see [Service Parameters](#service_parameters)).

| Function                | Arguments        | Description                                                   |
|:------------------------|:-----------------|:--------------------------------------------------------------|
| procd_add_jail          | jail name, flags | Set up service jail (with features according to *flags*)      |
| procd_add_jail_mount    | read-only paths  | Read-only bind the paths listed to the jail's mount namespace |
| procd_add_jail_mount_rw | read-write paths | Bind the paths listed to the jail's mount namespace           |

| Flag        | Description                                                           |
|:------------|:----------------------------------------------------------------------|
| log         | Allow jailed service to log to syslog                                 |
| ubus        | Allow jailed service to access ubus                                   |
| procfs      | Mount /proc in jail                                                   |
| sysfs       | Mount /sys in jail                                                    |
| ronly       | Re-mount jail rootfs read-only                                        |
| requirejail | Do not fall back to run without jail in case jail could not be set up |
| netns       | Run jailed process in new network namespace                           |
| userns      | Run jailed process in new user namespace                              |
| cgroupsns   | Run jailed process in new cgroups namespace                           |
| console     | Set up console accessible with `ujail-console`                        |

See use cases of [procd_add_jail](https://github.com/openwrt/packages/search?q=procd_add_jail).

## Debugging

Set PROCD_DEBUG=1 to see debugging information when starting or stopping a procd init script. Also, `INIT_TRACE=1 /etc/init.d/mything $action` Where \$action is start/stop etc.

### A common gotcha with stopping a service

Keep in mind that `procd` only tracks the main process. For example, consider the following script that reads from log file and then performs an action:

``` sh
#!/usr/bin/sh

tail -f /var/log/messages |  while read -r match; do
    echo foo
done
```

Because this script uses a pipe a sub-process is spawned. Calling `/etc/init.d./<foo> stop` will only terminate the parent process. The sub-process will still be alive and continue running. This is also true if you call `kill` on the main process's PID manually. The program needs to keep track of its sub-processes and terminate them properly when it receives a `SIGTERM` signal.

For this case in particular, here is a working solution:

``` sh
#!/usr/bin/sh

pid=
_cleanup() {
    kill "$pid"
    exit
}

trap _cleanup TERM INT

tail -f /var/log/messages |  while read -r match; do
    echo foo
done & # Beware the &: In order to be able to receive signals at all, the above `while read`
       # needs to be run in the background.
pid=$!
wait $pid
```

## Examples

- [r39617 firewall3](https://dev.openwrt.org/changeset/39617)
- [r40635 radsecproxy](https://dev.openwrt.org/changeset/40635)
- [r40674 xupnpd](https://dev.openwrt.org/changeset/40674)
- [r40785 shairport](https://dev.openwrt.org/changeset/40785)
- [r40997 igmpproxy](https://dev.openwrt.org/changeset/40997)
- [Create a sample procd init script](/docs/guide-developer/procd-init-script-example)

## Service Parameters

The following table contains a listing of the possible values to `procd_set_param()` and a description of their effects. List values are passed space-separated, e.g. `procd_set_param env HOME=/root ENVIRONMENT=production FOO="bar baz"`. String values are implicitely concatenated, so `procd_set_param error An error occurred` is equivalent to `procd_set_param error "An error occurred"`.

| Parameter       | Data Type      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|-----------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `env`           | Key-Value-List | Sets a number of environment variables in `key=value` notation exported to the spawned process.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `data`          | Key-Value-List | Sets arbitrary user data in `key=value` notation to the ubus service state. This is mainly used to store additional meta data with spawned services, such as [mDNS](../wiki/chunked-reference/wiki_page-guide-developer-mdns.md) announcements or firewall rules which may be picked up by other services.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `limits`        | Key-Value-List | Set ulimit values in `key=value` notation for the spawned process. The following limit names are recognized by *procd*: `as` (`RLIMIT_AS`), `core` (`RLIMIT_CORE`), `cpu` (`RLIMIT_CPU`), `data` (`RLIMIT_DATA`), `fsize` (`RLIMIT_FSIZE`), `memlock` (`RLIMIT_MEMLOCK`), `nofile` (`RLIMIT_NOFILE`), `nproc` (`RLIMIT_NPROC`), `rss` (`RLIMIT_RSS`), `stack` (`RLIMIT_STACK`), `nice` (`RLIMIT_NICE`), `rtprio` (`RLIMIT_RTPRIO`), `msgqueue` (`RLIMIT_MSGQUEUE`), `sigpending` (`RLIMIT_SIGPENDING`) **Two numeric values, separated by blank space, are expected for RLIMIT: the first value represents the soft limit and the other the hard limit; e.g.: [procd_set_param](../cookbook/chunked-reference/procd-service-lifecycle.md) limits nofile="10000 20000"; the "unlimited" value can be used in cases where "ulimit -{parameter} unlimited" works, for example for the "core" parameter.**                                                                                               |
| `command`       | List           | Sets the command vector (`argv`) used to execute the process.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `netdev`        | List           | Passes a list of Linux network device names to *procd* to be monitored for changes. Upon starting a service, the interface index of each network device name is resolved and stored as part of *procd*'s in-memory service state. When a service reload request is processed and the interface index of any of the associated network devices changed or if the list itself changed, the running service state is invalidated and *procd* will restart the associated process or deliver a UNIX signal to it, depending on how the service was set up.                                                                                                                                                                                                                                                                                                                                                                                   |
| `file`          | List           | Passes a list of file names to *procd* to be monitored for changes. Upon starting a service, the content of each passed file is checksummed and stored as part of *procd*'s in-memory service state. When a service reload request is processed and the checksum of one of the associated files changed, or the list of files itself changed, the running service state is invalidated and *procd* will restart the associated process or deliver a UNIX signal to it, depending on how the service was set up.                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `respawn`       | List           | A series of three consecutive numbers which set the *respawn threshold*, the *respawn timeout* and the *respawn retry* respectively. The timeout specifies the amount of seconds to wait before a service restart attempt, the retry value controls how many restart attempts will be made before a service is considered crashed and the threshold value in seconds controls the time frame in which the restart attempts are counted towards the retry limit. For example a threshold of 300 with a retry value of 10 will cause *procd* to consider the service to be crashed if the associated UNIX process terminated more than 10 times within a time frame of 5 minutes. No further restart attempts will be made for such crashed services unless an explicit restart is performed. Setting the retry value to `0` will cause *procd* to try restarting the service indefinitely. The default value for `respawn` is `3600 5 5`. |
| `watch`         | List           | Passes a list of *ubus* namespaces to watch - *procd* will subcribe to each namespace and wait for incoming *ubus* events which are then forwarded to registered JSON script triggers for evaluation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `error`         | List           | Passes one or more free formed error strings to *procd*. The error strings are stored as part of the in-memory service state and are exposed verbatim in *ubus* for use by other tools. This facility is mainly useful to allow init scripts to signal configuration errors or other transient issues preventing a successful start up. If any error string is passed to *procd*, no attempt will be made to actually spawn the associated UNIX process of the service but the service instance itself is still registered in *procd*.                                                                                                                                                                                                                                                                                                                                                                                                   |
| `nice`          | Integer        | Set the scheduling priority of the spawned process. Valid values range from `-20` (most favorable) to `19` (least favorable).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `term_timeout`  | Integer        | Specifies the amount of seconds to wait for a clean process exit after delivering the `TERM` signal. If the process fails to completely exit within the specified time frame, the process is forcibly terminated using an uncatchable `KILL` signal. The default termination timeout value is 5 seconds. Services with expensive shutdown operations, such as database systems, should set the `term_timeout` parameter to sufficiently large value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `reload_signal` | String         | Instructs *procd* to handle process reloads by delivering a UNIX signal instead of terminating the running process and spawning it again. This is useful for programs that provide extensive native configuration reload handling which allows for updated configurations to be applied on the fly without the need to restart the process. Note that this parameter only makes sense in conjunction with fixed command lines. When a reload signal is specified, any updated command line will be ignored since the running process is retained and not executed again. Valid values for this parameter are UNIX signal names as listed by `kill -l`.                                                                                                                                                                                                                                                                                   |
| `pidfile`       | String         | Instructs *procd* to write the PID of the spawned process into the specified file path. While *procd* itself does not use or require PID files to track spawned processes, this option is useful for sitation where knowledge of the PID is required, e.g. for monitoring or control client software.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `user`          | String         | Specifies the name of the user to spawn the process as. *procd* will look up the given name in `/etc/passwd` and set the effective uid and primary gid of the spawned processaccordingly. If omitted, the process is spawned as `root` (uid 0, gid 0)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `seccomp`       | String         | Specifies file path to read seccomp filter rules from, the file should be JSON formatted like the [seccomp object of the OCI run-time spec](https://github.com/opencontainers/runtime-spec/blob/master/config-linux.md#seccomp)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `capabilities`  | String         | Specifies file path to read capability set, the file should be JSON formatted like the [capabilities object of the OCI run-time spec](https://github.com/opencontainers/runtime-spec/blob/master/config.md#linux-process)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `stdout`        | Boolean        | If set to `1`, instruct *procd* to relay the spawned process' stdout to the system log. The stdout will be fed line-wise to `syslog(3)` using the basename of the first command argument as identity, `LOG_INFO` as priority and `LOG_DAEMON` as facility.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `stderr`        | Boolean        | If set to `1`, instruct *procd* to relay the spawned process' stderr to the system log. The stderr will be fed line-wise to `syslog(3)` using the basename of the first command argument as identity, `LOG_ERR` as priority and `LOG_DAEMON` as facility.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `no_new_privs`  | Boolean        | Instructs *ujail* to not allow privilege elevation. Sets the *ujail* `-c` parameter when true.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

---

# RPC daemon

In OpenWrt we commonly use [ubus](/docs/techref/ubus) for all kinds of communication. It can provide info from various software as well as request various actions. Nevertheless, not every part of OpenWrt has a daemon that can register itself using `ubus`. For an example `uci` and `opkg` are command-line tools without any background process running all the time.

It would be not efficient to write a daemon for every software like this and run them independently. This is why `rpcd` was developed. It’s a tiny daemon with support for plugins using trivial API. It loads library `.so` files and calls init function of each of them.

The code is published under [ISC license](https://en.wikipedia.org/wiki/ISC_license) and can be found via git at <https://git.openwrt.org/project/rpcd.git>.

### Default plugins

There are few small plugins distributed with the `rpcd` sources. Two of them (`session` and `uci`) are built-in, others are optional and have to be build as separated `.so` libraries. Apart from that there are other projects providing their own plugins.

See details here: [rpcd: OpenWrt ubus RPC daemon for backend server](/docs/techref/rpcd)

---

# High-level security incident response handling process

The goal of this high-level process is to identify what needs to be done for a security response, and who can help making it happen.

|                               \*\*1. Awareness \*\*                                |          |                                          |                                                                                                                                                                                                                                                          |
|:----------------------------------------------------------------------------------:|----------|------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                                        Task                                        | Duration | Who can do it                            | Notes                                                                                                                                                                                                                                                    |
| [Make security team aware](/docs/guide-developer/security#vulnerability_reporting) | \-       | Whoever being aware about security issue | Its important to handle the issue properly from the beginning.                                                                                                                                                                                           |
|                                                                                    |          |                                          |                                                                                                                                                                                                                                                          |
|                             \*\*2. Identification \*\*                             |          |                                          |                                                                                                                                                                                                                                                          |
|                                        Task                                        | Duration | Who can do it                            | Notes                                                                                                                                                                                                                                                    |
|                                   Analyze report                                   | \-       | Security response team                   | Assess incoming reports for validity and potential severity.                                                                                                                                                                                             |
|                                                                                    |          |                                          |                                                                                                                                                                                                                                                          |
|                               \*\*3. Assesment \*\*                                |          |                                          |                                                                                                                                                                                                                                                          |
|                                        Task                                        | Duration | Who can do it                            | Notes                                                                                                                                                                                                                                                    |
|                                 Impact evaluation                                  | \-       | Security response team                   | Determine the potential impact on users and the project (e.g., data exposure, remote code execution).                                                                                                                                                    |
|                                Risk categorization                                 | \-       | Security response team                   | Assign severity levels (e.g., Critical, High, Medium, Low) using frameworks like CVSS.                                                                                                                                                                   |
|                                 Confirm the issue                                  | \-       | Security response team                   | Reproduce the issue in a controlled environment to confirm its validity.                                                                                                                                                                                 |
|                                                                                    |          |                                          |                                                                                                                                                                                                                                                          |
|                              \*\*4. Containment \*\*                               |          |                                          |                                                                                                                                                                                                                                                          |
|                                        Task                                        | Duration | Who can do it                            | Notes                                                                                                                                                                                                                                                    |
|                            Prevent further exploitation                            | \-       | \-                                       | Take immediate action to limit the incident’s impact (e.g., temporarily disabling a vulnerable feature, service)                                                                                                                                         |
|                               Communicate internally                               | \-       | Security response team                   | Notify relevant maintainers, sysadmins to coordinate the response                                                                                                                                                                                        |
|                                                                                    |          |                                          |                                                                                                                                                                                                                                                          |
|                              \*\*5. Remediation \*\*                               |          |                                          |                                                                                                                                                                                                                                                          |
|                                        Task                                        | Duration | Who can do it                            | Notes                                                                                                                                                                                                                                                    |
|                               Fix the vulnerability                                | \-       | \-                                       | Patch the issue in the codebase and thoroughly test the fix                                                                                                                                                                                              |
|                                   Backport fixes                                   | \-       | \-                                       | Apply fixes to older supported versions, if necessary                                                                                                                                                                                                    |
|                               \*\*6. Disclosure \*\*                               |          |                                          |                                                                                                                                                                                                                                                          |
|                                        Task                                        | Duration | Who can do it                            | Notes                                                                                                                                                                                                                                                    |
|                             Communicate with reporter                              | \-       | Security response team                   | Notify the reporter of the fix and thank them for their contribution.                                                                                                                                                                                    |
|                                     Submit CVE                                     | \-       | Security response team                   | If applicable, request a CVE ID for tracking and disclosure                                                                                                                                                                                              |
|                         Publish security advisory on wiki                          | \-       | Security response team                   | Use [previous advisories](/advisory/start) as template                                                                                                                                                                                                   |
|                          Publish advisory to mailing list                          | \-       | Security response team                   | Use [previous emails](https://lists.openwrt.org/pipermail/openwrt-announce/2022-October/thread.html) as template, **GPG sign** email!                                                                                                                    |
|                             Publish advisory on forum                              | \-       | Security response team                   | Use [previous posts](https://forum.openwrt.org/t/security-advisory-2022-10-04-1-wolfssl-buffer-overflow-during-a-tls-1-3-handshake-cve-2022-39173/138880) as template, probably makes sense always for remotely exploitable or critical vulnerabilities. |
|                                                                                    |          |                                          |                                                                                                                                                                                                                                                          |

---

# Security

See [Security old](/docs/guide-developer/security/old) for the old page.

This page lists the processes, tools, and mechanisms the OpenWrt project uses for the security of OpenWrt. This policy covers the OpenWrt distribution with the official package feeds hosted at <https://github.com/openwrt/> and also the OpenWrt specific tools hosted at <https://git.openwrt.org/> such as procd, ubus, and libubox.

## Vulnerability reporting

Security bugs should be reported in confidentiality to <contact@openwrt.org>, please see [Reporting security bugs](/bugs#reporting_security_bugs) and [High-level security incident response handling process](/docs/guide-developer/security_incidents_response) for additional details.

Note that the <contact@openwrt.org> mail box is not always monitored and we may not notice when you send a mail to this mail address. If you do not get an answer or the vulnerability is severe, please contact our public mailing list <openwrt-adm@lists.openwrt.org> with a brief statement that a vulnerability has been reported to <contact@openwrt.org> and a general description of its severity. Please avoid providing detailed information on the public mailing list that would aid exploitation, such as the vulnerable component and exploit details. Note that the mailing list email does not accept formatted HTML emails, so make sure that your mail client allows sending plaintext emails.

## Security advisories

/\*\* Omit the footer because the edit/create date is inaccurate because the page's contents are autogenerated. \*/ ![start&link&nofooter](/page>advisory/start&link&nofooter)

This only lists security advisories for components directly maintained by the OpenWrt project. This does not list fixed security problems in third-party components used by OpenWrt which may also affect the security of OpenWrt. We do not list known security problems in the Linux kernel, openssl, and other third-party components even when they affect use cases relevant to OpenWrt. The OpenWrt project monitors the upstream projects and backports security fixes for components used in the OpenWrt core repository to supported OpenWrt versions. For example [159 CVEs](https://www.cvedetails.com/product/47/Linux-Linux-Kernel.html?vendor_id=33) were assigned for the Linux kernel in 2021 alone, OpenWrt regularly updates the minor Linux kernel version to get these recent fixes.

## Support Status

This table lists the support status of various OpenWrt releases:

| Version           | Current status       | Initial Release    | EoL (Projected)   | Latest Release | Release Date      |
|:------------------|:---------------------|:-------------------|:------------------|:---------------|:------------------|
| @lightgreen:25.12 | Supported            | 2026, March 06     | (2027, March)     | 25.12.1        | 2026, March 18    |
| @yellow:24.10     | Security Maintenance | 2025, February 06  | (2026, September) | 24.10.6        | 2026, March 18    |
| @pink:23.05       | End of Life          | 2023, October 13   | 2025, August      | 23.05.6        | 2025, August 20   |
| @pink:22.03       | End of Life          | 2022, September 06 | 2024, July        | 22.03.7        | 2024, July 25     |
| @pink:21.02       | End of Life          | 2021, September 04 | 2023, May         | 21.02.7        | 2023, May 01      |
| @pink:19.07       | End of Life          | 2020, January 06   | 2022, April       | 19.07.10       | 2022, April 20    |
| @pink:18.06       | End of Life          | 2018, July 31      | 2020, December    | 18.06.9        | 2020, December 09 |
| @pink:17.01       | End of Life          | 2017, February 22  | 2019, June        | 17.01.7        | 2019, June 20     |

The listed **Version** numbers reference the code base and the support status applies to the the latest minor release of that branch:

- **Supported**: The OpenWrt project will provide updates for the core packages fixing security and other problems we are aware of.
- **Security Maintenance**: The OpenWrt project will fix only security problems in this release, existing bugs will remain.
- **End of Life**: The OpenWrt project will **NOT** provide any updates, even for severe security vulnerabilities, please update to a more recent version.

A major release will be **Supported** after its initial release.

When the next major release is published, the previous version will move into **Security Maintenance** status.

A major release will move into **End of Life** status one year after the initial release, or 6 months after the next major release, whichever date is later. The project aims to do a final minor release at the end of the support cycle.

#### Notes

:!: This timeline only covers core OpenWrt packages and not the external package feeds hosted on GitHub.

:!: Some package feed maintainers do not support all OpenWrt versions that are still supported by the OpenWrt project.

:!: For the best security support we strongly suggest that every device is upgraded to the most recent stable version.

:!: The **Projected EoL** date may be subject to change depending on circumstances, such as the timing of the next release.

## Identifying problems

The OpenWrt project uses multiple tools to identify potential security problems. This information is normally available to everyone and we appreciate fixes for problems reported by these tools from everyone.

### uscan

The [uscan report](https://sdwalker.github.io/uscan/index.html) shows the version number of all packages from the base and the package repository and compares it against the recent upstream released versions. In addition the tool which generates this page also checks for existing CVEs assigned to the packages based on the Common Platform Enumeration (CPE) which is listed in the PKG_CPE_ID variable of many packages. That page is updated weekly for master and the active release branches.

### Coverity Scan

OpenWrt uses the commercial [Coverity Scan](https://scan.coverity.com/projects/openwrt) tool which is available for free to open source projects to do static code analyses on the OpenWrt components. This scans one OpenWrt build per week and reports the problems found in the components developed in the OpenWrt project like procd and ubus, but not on (patched) third party components.

## Reproducible builds

The [reproducible builds project](https://reproducible.debian.net/openwrt/openwrt.html) checks that OpenWrt master is still reproducible. This proves that the produced releases really match the delivered source code and no backdoors were introduced in the build process.

## Deliver to users

OpenWrt operates multiple [build bot instances](/infrastructure#Buildbot) which are building snapshots of the `master` and the supported release branches.

When a change to a package is committed to the OpenWrt base repository of package feed, the build bots are automatically detecting this change and will rebuild this package. The newly built package can then be installed with opkg or be integrated with the image builder by users of OpenWrt. This allows us to ship updates in about 2 days to the end users.

The kernel is normally located in its own partition and upgrades are not so easily possible. Therefore this mechanism currently does not work for the kernel itself and kernel modules and a new minor release is needed to ship fixes to end users.

## Hardening build options

OpenWrt activates some build hardening options in the [build configuration](https://git.openwrt.org/?p=openwrt/openwrt.git;a=blob;f=config/Config-build.in) at compile time for all package builds. Note that individual packages and/or targets may ignore or otherwise not respect these settings.

| .config line | Enabled by default | Notes |
| --- | --- | --- |
| `CONFIG_PKG_CHECK_FORMAT_SECURITY=y` | Yes | `-Wformat -Werror=format-security` |
| `CONFIG_PKG_CC_STACKPROTECTOR_REGULAR=y` | Yes | `-fstack-protector` |
| `CONFIG_PKG_CC_STACKPROTECTOR_STRONG=y` | No | `-fstack-protector-strong` |
| `CONFIG_KERNEL_CC_STACKPROTECTOR_REGULAR=y` | Yes | Kernel config CONFIG_STACKPROTECTOR |
| `CONFIG_KERNEL_CC_STACKPROTECTOR_STRONG=y` | No | Kernel config CONFIG_STACKPROTECTOR_STRONG |
| `CONFIG_PKG_FORTIFY_SOURCE_1=y` | Yes | `-D_FORTIFY_SOURCE=1` (Using [fortify-headers](https://git.2f30.org/fortify-headers/) for musl libc) |
| `CONFIG_PKG_FORTIFY_SOURCE_2=y` | No | `-D_FORTIFY_SOURCE=2` (Using [fortify-headers](https://git.2f30.org/fortify-headers/) for musl libc) |
| `CONFIG_PKG_RELRO_FULL=y` | Yes | `-Wl,-z,now -Wl,-z,relro` |
| `CONFIG_PKG_ASLR_PIE_REGULAR=y` | Yes | `-fPIC` CFLAGS and `-specs=hardened-build-ld` LDFLAGS; PIE is activated for some binaries, mostly network exposed applications |
| `CONFIG_PKG_ASLR_PIE_ALL=y` | No | PIE is activated for all applications |
| `CONFIG_KERNEL_SECCOMP` | Yes | Kernel config CONFIG_SECCOMP |
| `CONFIG_SELINUX` | No | Kernel config SECURITY_SELINUX |

---

# OpenWrt SELinux policy development, customization, and testing

⚠️ **WARNING: FOLLOWING THESE PROCEDURES MAY RESULT IN A BRICKED OR INACCESSIBLE DEVICE !!!** ⚠️

This article demonstrates OpenWrt SELinux policy customization/development and testing/deployment. If you intend to deploy your own customized version of **selinux-policy** to your device, or if you intend to help improve the selinux-policy models provided by OpenWrt, then you should familiarize yourself with this procedure.

## Introduction and Prerequisites

This example assumes using Fedora 34 GNU/Linux for image building, and that there is at least 20GB of storage available on the host system used for building these components. In this example workflow, the resulting SELinux policy will be deployed and tested on a Linksys WRT1900ACS wireless router. In addition to the above, we require access to a git repository that can be accessed using the HTTPS protocol. This can be a private git repository, or a repository hosted on public services such as GitLab or Github. Please make sure that you carefully review all example commands for plausibility before trying to execute them in your specific build environment - filenames, commit hashes, personal data, etc. will differ from environment to environment and over time!

### Goals

The purpose of this exercise is to help familiarize potential contributors with the procedure of SELinux policy development for OpenWrt. OpenWrt can be configured and assembled in many ways, and the more scenarios are tested and supported the better. Please see Wish List for a list of known configurations that are not yet currently addressed and that need attention. Also see Feedback Checklist for a list of requested information (and instructions to gather this information) to determine and test whether the policy configuration is accurate and comprehensive.

In this example we're going to start by assembling the OpenWrt SELinux policy. By default, OpenWrt provides a generic policy with the aim to include support for all known common functionality. The goal of this default policy is to cover as many aspects of OpenWrt as possible and to make it "just work" by default on as many devices and device configurations as possible. The downside of this default policy is that, because it is so generic, it is also somewhat inefficient: The policy might include rules for components and functionalitty that you may not have installed or use and thereby it may require more space than strictly needed. Ideally, you would pick and choose a selection of modules appropriate and relevant for your target device's setup. (The goal is to eventually make assembling OpenWrt SELinux policy from available modules as easy as assembling OpenWrt images with the OpenWrt Image Builder.) Once we have assembled and deployed OpenWrt SELinux policy appropriate to our target device, we are going to work on extending functionality by adding policy for a simple `Hello World` shell script. Once tested, we're going to build an image with the resulting policy integrated, and deploy that to our target device.

Eventually, when everything works as intended and the policy you created is useful to the general public, you may consider submitting a patch with your changes to OpenWrt, so that all interested parties can benefit from your hard work.

## Installing and setting up build requirements

We're going to start by creating an OpenWrt Image Builder (IB) archive that can be used to assemble OpenWrt factory and sysupgrade images with included SELinux support. We have to ensure that we have all required build dependencies installed on our build system. In addition to the usual required host packages, we also need the `secilc` program, so that we can compile SELinux policy written in [Common Intermediate Language (CIL)](https://github.com/SELinuxProject/selinux/blob/master/secilc/docs/README.md).

    [kcinimod@brutus ~]$ sudo dnf install gcc-c++ git make bc make patch wget unzip tar bzip2 gettext ncurses-devel perl-FindBin perl-Data-Dumper perl-Thread-Queue perl-base findutils which diffutils file perl-File-Copy openssl-devel flex libxslt intltool zlib-devel rsync secilc

### Clone OpenWrt source code using git

Now that we have the build requirements taken care of, we can get the sources for OpenWrt. In this example, we'll clone OpenWrt from its mirror on Github:

    [kcinimod@brutus ~]$ git clone https://github.com/openwrt/openwrt.git

#### Addressing feeds

We'll now update and install all available feeds:

    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds update -a
    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds install -a

#### Addressing build configuration

Now, we will create an OpenWrt Image builder archive that is (somewhat) tailored to our requirements. (Remember: It has to have support for both SELinux, and for our example Linksys WRT1900ACS target device.)

    [kcinimod@brutus ~]$ cd ~/openwrt
    [kcinimod@brutus openwrt]$ make -j$(($(nproc) + 1)) menuconfig

After a short while a menu appears. We will address the Linksys WRT1900ACS target requirement first. The first three entries in the menu are used for this:

      Target System (Marvell EBU Armada)  --->
      Subtarget (Marvell Armada 37x/38x/XP)  --->
      Target Profile (Linksys WRT1900ACS v1)  --->

Select the "Build OpenWrt Image Builder" option from the menu.

      [*] Build the OpenWrt Image Builder

Next, we'll enable SELinux in the "Global Build Settings" submenu.

      Global build settings  --->
          [*] Enable SELinux (NEW)

Save the configuration and then exit the configuration tool using the menu on the bottom of the screen.

### Building OpenWrt and its Image Builder

Now we are ready to compile OpenWrt and its Image Builder. This will take some time.

    [kcinimod@brutus openwrt]$ make -j$(($(nproc) + 1))

The procedure above will create various images with regular SELinux support and the default SELinux selinux-policy model, in addition to an SELinux enabled Image Builder. In this example we will do a clean factory install using the created `~/openwrt/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img` factory image to test and ensure that the unmodified defaults work. The procedure of doing a factory install is documented elsewhere, but here is a quick summary:

1.  My host Ethernet network interface with static IP address 192.168.1.15 is connected to my WRT1900ACS device
2.  I browse to the stock Linksys WRT1900ACS web interface at address <https://192.168.1.1>
3.  The interface provides an option to manually flash the device with a specified image, and I point that to `~/openwrt/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img` factory image
4.  The device reboots and I use `ssh root@192.168.1.1` to log in to the device now running OpenWrt

#### Applying basic customization

There is a good chance that the selinux-policy enclosed n this image is slightly outdated and there may have been changes to upstream since. If you want to contribute policy, it is probably best to build on top of upstream. As a base for this work, you probably want to use the default policy with all modules enabled, so that you can have a good idea of how things work in the default scenario.

As an example, we will however exclude an optional module that is not depended on by any other modules to give you an idea of how you would go about assembling and building the policy with a customized module selection. Picking and choosing modules to install can be tricky, as modules may have dependencies on other modules. It is advised that you test locally whether all dependencies of your selection of modules can be resolved.

Depending on how integrated the component you want to target is, it is wise to set the default SELinux mode to "permissive", at least during the policy development phase. Even though this reasoning does not really apply to this contrived example, we will default to permissive mode for now for illustrative purposes.

At this point, you are essentially forking the policy. Publish your forked Git repository and ensure that the forked Git repository is accessible with the HTTPS protocol. You can for example use GitLab or Github for this but we'll use Github in this example.

### Creating a new selinux-policy-myfork repository on Github

#### Forking selinux-policy

I created a new empty `override/selinux-policy-myfork.git` repository on Github. I then clone this into a local working directory, and also clone the upstream selinux-policy. After that, I consolidate the two, and push my changes to selinux-policy-myfork to its Github upstream.

    [kcinimod@brutus openwrt]$ cd ~
    [kcinimod@brutus ~]$ git clone git@github.com:doverride/selinux-policy-myfork.git
    [kcinimod@brutus ~]$ git clone https://git.defensec.nl/selinux-policy.git
    [kcinimod@brutus ~]$ rm -rf selinux-policy/.git
    [kcinimod@brutus ~]$ cp -r selinux-policy-myfork/.git selinux-policy/.git
    [kcinimod@brutus ~]$ rm -rf selinux-policy-myfork
    [kcinimod@brutus ~]$ mv selinux-policy selinux-policy-myfork
    [kcinimod@brutus ~]$ cd selinux-policy-myfork
    [kcinimod@brutus selinux-policy-myfork (master #)]$ git init .
    [kcinimod@brutus selinux-policy-myfork (master #)]$ git add .
    [kcinimod@brutus selinux-policy-myfork (master +)]$ git commit -am 'initial commit'
    [kcinimod@brutus selinux-policy-myfork (master)]$ git push

#### Adding a custom target to the Makefile

One of our goals has been achieved: We forked the OpenWrt selinux-policy straight from upstream, and are working with an up-to-date policy snapshot as of now. To continue, we would like to build the whole policy minus the sandbox.cil module. To that end, we will add a target to ~/selinux-policy-myfork/Makefile that can be used to achieve the desired effect. Before pushing the result to Github, we will ensure that the policy actually builds. Edit ~/selinux-policy-myfork/Makefile and make the following changes.

Add a "myfork" target - Change this line ...:

``` Makefile
.PHONY: all clean minimal policy check install
```

... to read like this instead:

``` Makefile
.PHONY: all clean minimal myfork policy check install
```

Define which modules to enclose - locate the following line in the file:

``` Makefile
polvers = 31
```

... and insert this block right **after** it:

``` Makefile
modulesmyfork = $(shell find src -type f -name '*.cil' \
        ! -name sandbox.cil -printf '%p ')
```

Now, define the "myfork" target - locate this line:

``` Makefile
policy: policy.$(polvers)
```

... and insert this block **right before**:

``` Makefile
myfork: myfork.$(polvers)
myfork.%: $(modulesmyfork)
        secilc -vvv --policyvers=$* $^
```

Now, see if it builds:

    [kcinimod@brutus ~]$ cd ~/selinux-policy-myfork
    [kcinimod@brutus selinux-policy-myfork]$ make myfork
    [kcinimod@brutus selinux-policy-myfork]$ echo $?

If the build failed, look carefully at the compiler output - it will report any dependency issues that you can then manually resolve. Iterate on this until you get a successful build. Now, commit the result and push your changes to the Github remote, like so:

    [kcinimod@brutus selinux-policy-myfork (master *=)]$ git commit -am "adds myfork target to makefile"
    [kcinimod@brutus selinux-policy-myfork (master>)]$ git push

#### Building a selinux-policy-myfork ipk package

Now we have to package the policy, so that it can be enclosed with a factory and sysupgrade image using our Image Builder. For this, we have to create a package manifest, which defines how an ipk package gets assembled. Lucky for us, our selinux-policy-myfork repository has a template for this at `~/selinux-policy-myfork/support` that can serve as a reference.

First, we create a local feeds directory (example ~/mypackages):

    [kcinimod@brutus selinux-policy-myfork]$ cd ~
    [kcinimod@brutus ~]$ mkdir mypackages

Now we recursively copy `~/selinux-policy-myfork/support/selinux-policy-XXXX` to the local feeds' `~/mypackages` directory and rename it to `selinux-policy-myfork`:

    [kcinimod@brutus ~]$ cp -r selinux-policy-myfork/support/selinux-policy-XXXX mypackages/selinux-policy-myfork

We will need to replace the PKG_NAME variable's value next, which will determine the name of the package that will be generated:

    [kcinimod@brutus ~]$ sed -i 's/PKG_NAME:=.*/PKG_NAME:=selinux-policy-myfork/' mypackages/selinux-policy-myfork/Makefile

We replace PKG_SOURCE (point to your repository HTTPS URL, as this is where the source will be retrieved from):

    [kcinimod@brutus ~]$ sed -i 's#PKG_SOURCE_URL:=.*#PKG_SOURCE_URL:=https://github.com/doverride/selinux-policy-myfork.git#' mypackages/selinux-policy-myfork/Makefile

We need to also change PKG_SOURCE_DATE (use the current date or the date of the last commit):

    [kcinimod@brutus ~]$ sed -i 's/PKG_SOURCE_DATE:=.*/PKG_SOURCE_DATE:=2020-10-19/' mypackages/selinux-policy-myfork/Makefile

And we alse replace PKG_SOURCE_VERSION (use the commit ID of your latest commit):

    [kcinimod@brutus ~]$ sed -i 's/PKG_SOURCE_VERSION:=.*/PKG_SOURCE_VERSION:=4b8d8c06c5f1dc8641b2b08b44d7fde955e2b9db/' mypackages/selinux-policy-myfork/Makefile

Replace PKG_MIRROR_HASH (we'll skip this during development):

    [kcinimod@brutus ~]$ sed -i 's/PKG_MIRROR_HASH:=.*/PKG_MIRROR_HASH:=skip/' mypackages/selinux-policy/myfork/Makefile

Replace PKG_MAINTAINER (use your name and e-mail address instead of mine):

    [kcinimod@brutus ~]$ sed -i 's/PKG_MAINTAINER:=.*/PKG_MAINTAINER:=Dominick Grift <dominick.grift@defensec.nl>/' mypackages/selinux-policy-myfork/Makefile

Replace PKG_CPE_ID (whatever):

    [kcinimod@brutus ~]$ sed -i 's#PKG_CPE_ID:=cpe:/a:XXXX:selinux-policy-XXXX#PKG_CPE_ID:=cpe:/a:myfork:selinux-policy-myfork#' mypackages/selinux-policy-myfork/Makefile

Replace define/Package:

    [kcinimod@brutus ~]$ sed -i 's#define Package/selinux-policy-XXXX#define Package/selinux-policy-myfork#' mypackages/selinux-policy-myfork/Makefile

Replace TITLE:

    [kcinimod@brutus ~]$ sed -i 's/TITLE:=XXXX SELinux policy for OpenWrt/TITLE:=Myfork SELinux policy for OpenWrt/' mypackages/selinux-policy-myfork/Makefile

Replace URL:

    [kcinimod@brutus ~]$ sed -i 's#URL:=https://XXXX/#URL:=https://whatever/#' mypackages/selinux-policy-myfork/Makefile

Replace define/Package/description:

    [kcinimod@brutus ~]$ sed -i 's/XXXX SELinux security policy designed specifically for OpenWrt/Myfork SELinux security policy designed specifically for OpenWrt/' mypackages/selinux-policy-myfork/Makefile

Replace Build/Compile/Default (we'll use our new "myfork" target):

    [kcinimod@brutus ~]$ sed -i 's#$(call Build/Compile/Default,policy)#$(call Build/Compile/Default,myfork)#' mypackages/selinux-policy-myfork/Makefile

Replace the final occurrence of selinux-policy-XXXX:

    [kcinimod@brutus ~]$ sed -i 's/selinux-policy-XXXX/selinux-policy-myfork/' mypackages/selinux-policy-myfork/Makefile

Change the "mode from config" to "permissive", and change the policy model to selinux-policy-myfork:

    [kcinimod@brutus ~]$ sed -i 's/SELINUX=.*/SELINUX=permissive/' mypackages/selinux-policy-myfork/files/selinux-config
    [kcinimod@brutus ~]$ sed -i 's/SELINUXTYPE=.*/SELINUXTYPE=selinux-policy-myfork/' mypackages/selinux-policy-myfork/files/selinux-config

Add/update the "mypackages" custom feed and selinux-policy-myfork:

    [kcinimod@brutus ~]$ echo "src-link custom ${HOME}/mypackages" >> openwrt/[feeds.conf](../wiki/chunked-reference/wiki_page-guide-developer-creating-a-meson-based-package.md).default
    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds update custom
    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds install selinux-policy-myfork

After these modifications have succeeded, we have to perform `menuconfig` again, to also select **selinux-policy-myfork** for being built:

    [kcinimod@brutus ~]$ cd ~/openwrt
    [kcinimod@brutus openwrt]$ make -j$(($(nproc) + 1)) menuconfig

Now we'll enable selinux-policy-myfork from the "Base system" submenu.

      Base system  --->
          <*> selinux-policy-myfork.................. Myfork SELinux policy for OpenWrt

Save the configuration first and then exit the menu using the menu on the bottom of the screen.

Now, we build the ipk package file:

    [kcinimod@brutus openwrt]$ make package/selinux-policy-myfork/compile

If this succeeds, the resulting ipk package can be found in `~/openwrt/bin/packages/*/custom`:

    [kcinimod@brutus openwrt]$ ls ~/openwrt/bin/packages/*/custom/*.ipk
    /home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-4b8d8c06_all.ipk

=== Creating installation and upgrade media with selinux-policy-myfork included using Image Builder

First, we will extract the Image Builder archive:

    [kcinimod@brutus openwrt]$ cd ~
    [kcinimod@brutus ~]$ mv ~/openwrt/bin/targets/*/*/openwrt-imagebuilder*.tar.xz ~
    [kcinimod@brutus ~]$ tar xf openwrt-imagebuilder*.tar.xz

Since we have a policy package, we can conveniently include it in firmware images generated by the Image Builder:

    [kcinimod@brutus ~]$ cd openwrt-imagebuilder*-x86_64
    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ make image PACKAGES="/home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-4b8d8c06_all.ipk"

This should yield **factory** and **sysupgrade** images which can be deployed onto a WRT1900ACS like any other OpenWrt image:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ ls bin/targets/*/*
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-linksys_wrt1900acs-linksys_wrt1900acs.manifest
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    sha256sums

#### Deploying sysupgrade image with customized selinux-policy-myfork

We should now be able to copy the resulting `openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin` image to the device using the `scp` utility (provided that the router is reachable on the network) and perform the upgrade:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ cd ~
    [kcinimod@brutus ~]$ scp /home/kcinimod/openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin root@192.168.1.1:/tmp/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    [kcinimod@brutus ~]$ ssh root@192.168.1.1
    root@OpenWrt:~# sysupgrade -F -n -v /tmp/*.bin

Give the device a moment to reboot and log back into it over ssh. Verify that your policy model is used and, again, follow the Feedback Checklist to see if all works well.

    [kcinimod@brutus ~]$ ssh root@192.168.1.1
    root@OpenWrt:~# sestatus
    SELinux status:           enabled
    SELinuxfs mount:          /sys/fs/selinux
    Current mode:             permissive
    Mode from config file:    permissive
    Policy version:           31
    Policy from config file:  selinux-policy-myfork

## Policy development overview

The next step will be to extend the policy by targeting a simple "Hello World" shell script. I will not get into the details of writing SELinux policy in this exercise. The policy is written in **Common Intermediate Language** and I am working on documenting that. You can try to find help in [\#selinux on the freenode IRC network](irc://irc.freenode.org/#selinux), but if you need assistance or have any questions related to OpenWrt selinux-policy and SELinux policy/CIL in particular, then I can be reached on the [OFTC IRC network in the \#openwrt-devel](irc://irc.oftc.net/#openwrt-devel) channel under the IRC nickname **grift**.

### Confining "Hello World"

We will be creating a simple script: `/root/helloworld`. It simply prints the output of `echo "Hello from: $(id -Z)"` to standard output and exits. Then, we will develop a policy for this script at runtime and test the result "on-device". Once the policy has been verified to work as intended, we will deploy a sysupgrade image with the resulting customization enclosed, and we will change the default SELinux mode back to "enforcing". This simple example will hopefully be illustrative enough to get you started. Please use the knowledge gained to help improve the policy, so that everyone can benefit.

#### Creating and testing the script

First, we need to create the script that our policy will interact with:

    root@OpenWrt:~# printf '#!/bin/sh\n echo "hello from: $(id -Z)\n"' > /root/helloworld
    root@OpenWrt:~# chmod +x /root/helloworld

To see what it does at this stage, let's run it:

    root@OpenWrt:~# /root/helloworld
    hello from: u:r:sys.subj

The script works, but the output of the script indicates that it currently operates within the "unconfined" `u:r:sys.subj` context. We would like the script to be contained, thereby applying the principle of least privilege to this process by subjecting it to our modified SELinux policy.

We can write a basic skeleton policy for this script off-device, using our cloned `selinux-policy-myfork` repository, then build and test that, and copy the compiled `policy.31` file (along with the updated `file_contexts` file) to the device. Then, we can run the `load_policy` command to apply the updated policy to the running system, and use that procedure to test and refine the policy until it works as we need it to.

#### Extend selinux-policy-myfork with basic skeleton for helloworld

    [kcinimod@brutus ~]$ cd selinux-policy-myfork
    [kcinimod@brutus selinux-policy-myfork]$ cat > src/agent/helloworld.cil <<EOF
    (block helloworld ;; declare a new container
    (blockinherit .agent.base_template) ;; this will declare types for both the process and executable file and associate some basic rules with them
    (filecon "/root/helloworld" file execfile_file_context)) ;; this will associate the file context with /root/helloworld and close container
    (in .sys (call .helloworld.subj_type_transition (subj))) ;; this macro was made available when we inherited the agent.base_template inside the helloworld container
    ;; it will cause selinux to automatically transition the context of any process associated with u:r:sys.subj to u:r:helloworld.subj when files with the u:r:helloworld.execfile context are executed
    EOF
    [kcinimod@brutus selinux-policy-myfork]$ make myfork

The compilation results in two files: `policy.31` and `file_contexts`, both found within `~/selinux-policy-myfork`. We copy these to the router using the `scp` command. The customized policy can then be loaded via `load_policy`, and the file context for `/root/helloworld` can be applied by running `restorecon`, like reproduced here:

    [kcinimod@brutus selinux-policy-myfork]$ scp policy.31 root@192.168.1.1:/etc/selinux/selinux-policy-myfork/policy/policy.31
    [kcinimod@brutus selinux-policy-myfork]$ scp file_contexts root@192.168.1.1:/etc/selinux/selinux-policy-myfork/contexts/files/file_contexts
    [kcinimod@brutus selinux-policy-myfork[$ ssh root@192.168.1.1
    root@OpenWrt:~# load_policy
    root@OpenWrt:~# restorecon -v /root/helloworld

Now it is time to test again - but before we do that, we will clear the kernel debug message ring buffer, so that we cannot get confused by any avc denials triggered by us copying the `policy.31` and `file_contexts` files over, because SELinux would not have permitted these operations if it had already been enforcing the policy.

A peculiar thing to be aware of is that SELinux will cache access vectors and events that occur in permissive mode, and that these will **only be printed once** to avoid flooding the logs. If you need to flush this cache, you can toggle the mode from permissive to enforcing, and then back again.

We perform both these operations here, before re-executing our script:

    root@OpenWrt:~# dmesg -c
    root@OpenWrt:~# setenforce 1 && setenforce 0
    root@OpenWrt:~# /root/helloworld
    hello from: u:r:helloworld.subj

The test concluded that the specified domain transition from `u:r:sys.subj` to `u:r:helloworld.subj` took place, due to our custom policy having taken effect. Since we are still operating in "permissive" mode for development purposes, we can use the `dmesg` command to see which permissions would have been denied if we had instead been operating in "enforcing" mode.

    root@OpenWrt:~# dmesg | grep -i denied

The resulting avc denials can be interpreted and translated to policy, that we can then append to our modifications, and then test again. Eventually, no new avc denials should be printed to dmesg when testing in "oermissive" mode, indicating that the resulting process has all the permissions and contexts assigned that it needs to function. Once we arrive at that point, the update should be ready for real-worl use.

We will now append some of the rules we were able to identify from the output of the `dmesg | grep -i` denied command. Some of these might not be obvious to you at this point. Suffice to say that rules can be (and in fact often are) grouped for common patterns, and with sufficient experience, you learn to recognise these patterns and how to correlate them to provided macros and templates commonly used to address these issues.

There is another gotcha you should be aware of: There are rules present in the policy that instruct SELinux to "silently" block specified events. This functionality can be useful if you want to block some access on purpose without SELinux printing avc denials. However, sometimes, knowing these events actually occurred (and were blocked) might actually be needed. The `secilc` compiler allows you to compile the policy with these "dontaudit" rules removed via the `-D` or `--disable-dontaudit` switches, but that's beyond the scope of this exercise. For now, suffice to say that `helloworld` wants to operate on the terminal (as it needs to print the output to a terminal) but the current policy has rules that tell SELinux to silently block this access. We need to change this to keep our policy-confined program working:

    [kcinimod@brutus selinux-policy-myfork]$ cat >> src/agent/helloworld.cil <<EOF
    (in .helloworld ;; insert into existing helloworld container
    (call .shell.execute_execfile_files (subj)) ;; executes /bin/sh which leads to busybox shell
    (call .selinux.linked.subj_type (subj)) ;; busybox links with libselinux which needs some access to determine selinux state
    (call .sys.readwriteinherited_ptydev_chr_files (subj)) ;; operate on pty, this was silently blocked
    (call .dev.readwriteinherited_ttydev_chr_files (subj))) ;; operate on tty. this was silently blocked
    ;; close helloworld container
    EOF
    [kcinimod@brutus selinux-policy-myfork]$ make myfork

Following the same procedure as before, copy over the `policy.31` and `file_contexts` files, reload policy, clear the ring buffer using `dmesg -c`, flush the SELinux log cache by toggling its state, retry running the script, and check dmesg again for avc messages, like so:

    [kcinimod@brutus selinux-policy-myfork]$ scp policy.31 root@192.168.1.1:/etc/selinux/selinux-policy-myfork/policy/policy.31
    [kcinimod@brutus selinux-policy-myfork]$ scp file_contexts root@192.168.1.1:/etc/selinux/selinux-policy-myfork/contexts/files/file_contexts
    [kcinimod@brutus selinux-policy-myfork[$ ssh root@192.168.1.1
    root@OpenWrt:~# load_policy
    root@OpenWrt:~# dmesg -c
    root@OpenWrt:~# setenforce 1 && setenforce 0
    root@OpenWrt:~# /root/helloworld
    hello from: u:r:helloworld.subj

    root@OpenWrt:~# dmesg | grep -i denied

The above dmesg invocation prints one more avc denial in permissive mode, so let's try this in enforcing mode:

    root@OpenWrt:~# dmesg -c
    root@OpenWrt:~# setenforce 1
    root@OpenWrt:~# /root/helloworld
    hello from: u:r:helloworld.subj

    root@OpenWrt:~# dmesg | grep -i denied
    root@OpenWrt:~# exit

This demonstrates that it works in enforcing mode. We can just add that last rule and then commit and push the policy to Github:

    [kcinimod@brutus selinux-policy-myfork]$ cat >> src/agent/helloworld.cil <<EOF
    (in .helloworld ;; insert into existing helloworld container
    (call .tmpfile.search_runtimetmpfile_dirs (subj))) ;; busybox traverses /tmp/run for some reason
    ;; close helloworld container
    EOF
    [kcinimod@brutus selinux-policy-myfork]$ make myfork
    [kcinimod@brutus selinux-policy-myfork]$ git add .
    [kcinimod@brutus selinux-policy-myfork]$ git commit -am "adds helloworld example"
    [kcinimod@brutus selinux-policy-myfork]$ git push

Next, we will build a new ipk package including our recent work, and also create a new sysupgrade image with our new policy package integrated, again using the Image Builder.

For that to work, we need to adjust two things in our local build artifacts:

\* The `~/mypackages/selinux-policy-myfork/Makefile` **PKG_SOURCE_VERSION** has to be updated to point to the new latest git commit ID \* The `~/mypackages/selinux-policy-myfork/files/selinux-config` has to be updated to change the mode from "permissive" to "enforcing".

Replace **PKG_SOURCE_VERSION** (use the commit ID of your latest commit):

    [kcinimod@brutus selinux-policy-myfork]$ cd ~
    [kcinimod@brutus ~]$ sed -i 's/PKG_SOURCE_VERSION:=4b8d8c06c5f1dc8641b2b08b44d7fde955e2b9db/PKG_SOURCE_VERSION:=c5e28890e61bed077477bcc526b8fb6639728c93/' mypackages/selinux-policy-myfork/Makefile

Change the "mode from config" to enforcing:

    [kcinimod@brutus ~]$ sed -i 's/SELINUX=.*/SELINUX=enforcing/' mypackages/selinux-policy-myfork/files/selinux-config

Now, we are ready to Create the updated ipk package:

    [kcinimod@brutus ~]$ cd openwrt
    [kcinimod@brutus openwrt]$ make package/selinux-policy-myfork/compile

If the operation succeeds, the resulting ipk package can be found in `~/openwrt/bin/packages/*/custom`:

    [kcinimod@brutus openwrt]$ ls ~/openwrt/bin/packages/*/custom/*.ipk
    /home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-c5e28890_all.ipk

Now that we have an updated ipk package, we can create new installation and upgrade images using Image Builder:

    [kcinimod@brutus openwrt]$ cd ~/openwrt-imagebuilder*-x86_64
    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ make image PACKAGES="/home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-c5e28890_all.ipk"

This should yield factory and sysupgrade images, just like before:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ ls bin/targets/*/*
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-linksys_wrt1900acs-linksys_wrt1900acs.manifest
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    sha256sums

Again, we deploy the new sysupgrade image with our customized selinux-policy-myfork:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ cd ~
    [kcinimod@brutus ~]$ scp /home/kcinimod/openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin root@192.168.1.1:/tmp/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    [kcinimod@brutus ~]$ ssh root@192.168.1.1
    root@OpenWrt:~# sysupgrade -F -n -v /tmp/*.bin

After the device has booted up again, our policy should be enforcing least privileges for our hello world script.

## In closing

This wraps up the exercise. Remember that this is meant to illustrate the SELinux policy development (and deployment) workflow in broad strokes. To be able to contribute your work back your policy, you need to adhere to a number of established style rules. I suggest that you take a close look at the existing policy, to identify patterns and clues on how to make your policy feel familiar to someone who's already familiar with pre-existing upstream policy code. To help with that, see if you can find a module that closely resembles yours, and compare and contrast the two in order to find ways to improve and align your module with existing best practices. If you need help, feel free to just ask [on IRC](irc://irc.oftc.net/#openwrt-devel)! Happy policy hacking! :)

---

# uBus IPC/RPC System

## uBus - IPC/RPC

uBus is the interconnect system used by most services running on a *OpenWrt* setup. Services can connect to the bus and provide methods that can be called by other services or clients.

See [uBus Technical Reference](/docs/techref/ubus)

### Reference documentation for ubus

**Path only contains the first context. E.g. network for network.interface.wan**

| path                                          | Description                     | Package      |
|-----------------------------------------------|---------------------------------|--------------|
| [dhcp](/docs/guide-developer/ubus/dhcp)       | dhcp server                     | odhcpd       |
| [file](/docs/guide-developer/ubus/file)       | file                            | rpcd         |
| [hostapd](/docs/guide-developer/ubus/hostapd) | acesspoints                     | wpad/hostapd |
| [iwinfo](/docs/guide-developer/ubus/iwinfo)   | wireless informations           | rpcd iwinfo  |
| [log](/docs/guide-developer/ubus/log)         | logging                         | procd        |
| [mdns](/docs/guide-developer/ubus/mdns)       | mdns avahi replacement          | mdnsd        |
| [network](/docs/guide-developer/ubus/network) | network                         | netifd       |
| [service](/docs/guide-developer/ubus/service) | init/service                    | procd        |
| [session](/docs/guide-developer/ubus/session) | Session management              | rpcd         |
| [system](/docs/guide-developer/ubus/system)   | system misc                     | procd        |
| [uci](/docs/guide-developer/ubus/uci)         | Unified Configuration Interface | rpcd         |

---

# UCI defaults

See also: [The UCI system](/docs/guide-user/base-system/uci)

*OpenWrt* relies on UCI, the *Unified Configuration Interface*, to configure its core services. UCI defaults provides a way to preconfigure your images, using UCI.

To set some system defaults the first time the device boots, create a script in the directory `/etc/uci-defaults`.

All scripts in that directory are automatically executed by the `boot` service:

- If they exit with code 0 they are deleted afterwards.
- Scripts that exit with non-zero exit code are not deleted and will be re-executed at the next boot until they also successfully exit.

In a live router you can see the existing UCI defaults scripts in `/rom/etc/uci-defaults` , as `/etc/uci-defaults` itself is typically empty (after all scripts have been run successfully and have been deleted).

UCI defaults scripts can be created by packages or they can be inserted into the build manually as custom files.

## Integrating custom settings

See also: [Build system - Custom files](/docs/guide-developer/toolchain/use-buildsystem#custom_files), [Image builder - Custom files](/docs/guide-user/additional-software/imagebuilder#custom_files)

Easiest way to include uci-defaults scripts in your firmware may be as custom files. You can preload custom settings by adding batch scripts containing UCI commands into the `/files/etc/uci-defaults` directory. The path is identical for the buildroot and the image generator. The scripts will be run **after** the flashing process - in case of upgrading, that also includes appending the existing configuration to the JFFS2 partition (mounted as `/overlay`). Scripts should not be executable. To ensure your scripts are not interfering with any other scripts, make sure they get executed last by giving them a high prefix (e.g. *xx_custom*). A basic script that creates the actual uci-defaults script could look like this:

``` bash
cat << "EOF" > /etc/uci-defaults/99-custom
uci -q batch << EOI
set network.lan.ipaddr='192.168.178.1'
set wireless.@wifi-device[0].disabled='0'
set wireless.@wifi-iface[0].ssid='OpenWrt0815'
add dhcp host
set dhcp.@host[-1].name='bellerophon'
set dhcp.@host[-1].ip='192.168.2.100'
set dhcp.@host[-1].mac='a1:b2:c3:d4:e5:f6'
rename firewall.@zone[0]='lan'
rename firewall.@zone[1]='wan'
rename firewall.@forwarding[0]='lan_wan'
EOI
EOF
```

Naturally the script can be created by any text editor, too. The uci-defaults script itself is:

``` bash
uci -q batch << EOI
set network.lan.ipaddr='192.168.178.1'
set wireless.@wifi-device[0].disabled='0'
set wireless.@wifi-iface[0].ssid='OpenWrt0815'
add dhcp host
set dhcp.@host[-1].name='bellerophon'
set dhcp.@host[-1].ip='192.168.2.100'
set dhcp.@host[-1].mac='a1:b2:c3:d4:e5:f6'
rename firewall.@zone[0]='lan'
rename firewall.@zone[1]='wan'
rename firewall.@forwarding[0]='lan_wan'
EOI
```

This is a simple example to set up the LAN IP address, SSID, enable Wi-Fi, configure a static DHCP lease, rename firewall zone and forwarding sections. Once the script has run successfully and exited cleanly (exit status 0), it will be removed from `/etc/uci-defaults`. You can still consult the original in `/rom/etc/uci-defaults` if needed.

## Ensuring scripts don’t overwrite custom settings: implementing checks

Scripts in `/etc/uci-defaults` will get executed at every first boot (i.e. after a clean install or an upgrade), possibly overwriting already existing values. If this behaviour is undesired, we recommend you implement a test at the top of your script - e.g. probe for a custom setting your script would normally configure:

``` bash
[ "$(uci -q get system.@system[0].zonename)" = "America/New York" ] && exit 0
```

This will make sure, when the key has the correct value set, that the script exits cleanly and gets removed from `/etc/uci-defaults` as explained above.

## Examples

- [Restricting root access](/docs/guide-user/additional-software/imagebuilder#restricting_root_access)
- [uci-defaults @ base-files](https://github.com/openwrt/openwrt/tree/master/package/base-files/files/etc/uci-defaults)
- [uci-defaults @ Freifunk Berlin](https://github.com/freifunk-berlin/firmware-packages/tree/master/defaults)
- [uci-defaults @ Freifunk Ulm](https://github.com/ffulm/firmware/blob/master/files/etc/uci-defaults/50_freifunk-setup)
- [config-openwrt @ richb-hanover](https://github.com/richb-hanover/OpenWrtScripts/blob/main/config-openwrt.sh)

---

# OpenWrt on UEFI based x86 systems

## Introduction

UEFI boot has been required for years now, boards that only support UEFI are common, and Intel has stated back in 2017 that "legacy" BIOS will no longer be supported after 2020.[^1][^2]

To accommodate this, the OpenWrt build system generates UEFI bootable images.

## Status

As of OpenWrt `a6b7c3e672764858fd294998406ae791f5964b4a`, EFI-compatible images are available on the x86-64 [snapshots](https://downloads.openwrt.org/snapshots/targets/x86/64/) downloads page.

## Building UEFI bootable OpenWrt image

To build an EFI-compatible OpenWrt image:

      * Run ''make menuconfig''.

      * Go to **Target Images** and make sure that the option **Build GRUB EFI images (Linux x86 or x86_64 host only)** is checked.

Select additional packages as necessary and finally save changes and exit menuconfig.

Run `make` as usual to build the image.

The resulting image(s) will be available in `./bin/targets/x86/64/` (depending on the image format(s) you chose), which can be written to disk after decompression.

Note that these are **disk images**, not partition images, which must be written to a block device directly e.g. `/dev/sdb`.

## UEFI Secure Boot

To generate signed image for use with secure boot, there is a [development repository](https://github.com/alive4ever/openwrt) with corresponding [packages feed](https://github.com/alive4ever/packages) under `feature-uefi-secure-boot` branch.

The repository contains changes based on Jow-staging branch to generate secure boot capable image

The related packages feed repository contains stuffs needed to sign efi binaries, i.e. gnu-efi and sbsigntool and stuffs to manipulate efi variables, i.e. efivar, efibootmgr, and efitools.

``` bash
# Add the development git repository
$ git remote add devrepo https://github.com/alive4ever/openwrt
$ git fetch devrepo
$ git checkout feature-uefi-secure-boot

# Configure the corresponding package repository
$ echo 'src-git packages https://github.com/alive4ever/packages;feature-uefi-secure-boot' > ./feeds.conf
$ ./scripts/feeds clean
$ ./scripts/feeds update packages
$ ./scripts/feeds update -i
$ ./scripts/feeds install -a

# Now, configure the build system
# Select x86 as Target, x86_64 as Subtarget
# make sure to select 'Sign EFI executable binaries' under 'Target Images'
# UEFI related tools are available under Utilities section,
# which consist of efitools, efibootmgr, efivar, and sbsigntool
$ make menuconfig

# The certificate and key need to be generated
# to perform uefi binary signing
$ OLD_UMASK=$(umask)
$ umask 077
$ openssl req -new -x509 -sha256 \
  -days 90 -out ./db.crt \
  -subj '/CN=secure boot signing certificate' \
  -newkey rsa:2048 -nodes \
  -keyout ./db.key
$ umask $OLD_UMASK

# run make to generate UEFI secure bootable OpenWrt image
$ make

```

Remember to import `db.crt` (which may needs to be converted into DER or other format) into `db` UEFI variable to securely boot the resulting image.

[^1]: <https://www.anandtech.com/show/12068/intel-to-remove-bios-support-from-uefi-by-2020>

[^2]: <http://www.uefi.org/sites/default/files/resources/Brian_Richardson_Intel_Final.pdf>

---

# Sending patches by git send-email

Send an email to the [development mailing list](https://lists.openwrt.org/mailman/listinfo/openwrt-devel). All patches need to be sent in the same format as those that are listed on [patchwork](https://patchwork.ozlabs.org/project/openwrt/list/). If the patch does not get listed in patchwork then it won't get processed.

Using [git send-email](https://git-scm.com/docs/git-send-email) is warmly recommended, as email clients tend to add spaces and screw up the formatting or add non-printable characters.

    git send-email --from=youremail@example.com --to="openwrt-devel@lists.openwrt.org" 001-description.patch

[git send-email documentation](http://git-scm.com/docs/git-send-email)

---

# Working with GitHub

There are GitHub mirrors of the source repository [here](https://github.com/openwrt/openwrt).

Fork the project to a public repo using GitHub web interface, clone the repo to your computer, create a branch for your changes, push these back to GitHub and submit a pull request.

In case you don't know how to do that, keep reading.

Create a GitHub account, this will host your public fork of OpenWrt source, and will be used for all interaction on GitHub.

Install git in your PC, and make sure that your local git settings have the right name and email:

``` bash
git config --global user.name "my name"
git config --global user.email "my@email.address"
```

You might also want to set the default text editor to your favorite editor. If you have a Linux system with a GUI, some choices are **geany**, **kwrite**, **pluma** and **gedit**. If you are using command line, **nano** is a good one.

``` bash
git config --global core.editor "editor-name-here"
```

Then follow GitHub's excellent documentation to [Fork A Repo](https://help.github.com/articles/fork-a-repo/) and [Create a local clone of your fork](https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork).

After you have set it up as described, write

``` bash
git checkout -b my-new-branch-name
```

to create a branch for your PR ("my-new-branch-name" is just an example name, use a more descriptive name in yours).

All commits you do after this command will be grouped in this branch. This allows to have multiple branches, one for each PR. To switch between branches you already created, use

``` bash
git checkout my-branch-name
```

After you made your changes, write

``` bash
git add -i
```

and use its interface to add untracked (new) files and update existing ones.

Then write

``` bash
git commit --signoff
```

This will open the git default editor and you can write the commit message.

The first line is the commit subject, then leave an empty line, then you write the commit description. This command will automatically add the Signed-off-by line with your name and email as set above. For example, a complete commit message might look like this:

``` bash
<area>: the best code update.

This is the best piece of code I have ever submitted.

Signed-off-by: John Doe <John.Doe@test.com>
```

To send your local changes over to your GitHub repo, write

``` bash
git push --all
```

You will be asked your GitHub user and password in the process.

After the code has been uploaded to your GitHub repo, you can submit pull request using GitHub web interface, see again GitHub's documentation about [Creating a pull request](https://help.github.com/articles/creating-a-pull-request/).

## Squashing commits

Commits in a PR or sent by email should be about full changes you want to merge, not about fixing all issues the reviewers found in your original PR.

So, there will come a time when you will need to either rewrite or squash your commits; so you end with a normal amount of true and sane commits.

Work with git commandline. Change to your development folder. Look at the branches you have with:

``` bash
git branch -a
```

get something like:

``` bash
  best_code_update
* master
```

Switch to the your development branch for this PR with:

``` bash
git checkout best_code_update
```

Look at the git log, so you can count the number of commits you want to squash ( the "X" below ) with:

``` bash
git log
```

Delete commits with:

``` bash
git reset HEAD~X
```

(where X is the number of commits you want to delete, counted from the last commit), this will not change modified files, it will only delete the commits.

Add the files to git tracking again with:

``` bash
git add -i
```

and commit again with:

``` bash
git commit --signoff
```

Send the updated branch over to GitHub with:

``` bash
git push -f
```

and the commits in the PR will be updated automatically.

### Alternative squashing advice

You can use **interactive rebase** to combine, reorder and edit your commits and their commit messages, with:

``` bash
git rebase -i HEAD~X
```

Where X is a number of commits to edit.

## Reopen closed PR

GitHub will grey out "Reopen" and will not let you reopen a PR if you force-pushed anything to the relevant branch after the PR has been closed, or deleted the branch.

However, reopening is still possible if you just set back the GitHub branch to the exact commit ID/hash it was at when you closed it. This even works when the branch or even the whole repository was deleted on GitHub. It just has to be recreated with the same name (for repo and branch) and the same commit hash at the branches HEAD.

A possible way to do that would be (there might be others, even shorter ones):

*We assume that the git remote referring to GitHub is called "origin", the branch of interest is called "testbranch", and the local and remote branch names are the same.*

``` bash
# Get the hash yyyyyyyyyyyyyyy of the current state of "testbranch" (we will move the branch head later)
git log -1 testbranch
# Checkout the latest state of the PR (commit hash xxxxxxxxxxx)
git checkout xxxxxxxxxx
# Delete old testbranch
git branch -D testbranch
# Label current state as testbranch
git checkout -b testbranch
# Push old state to GitHub
git push -f origin testbranch
```

Now you got GitHub at the state it was at when closing the PR. It should now be possible to "reopen" the PR. Note that this will only be possible if *you* closed it. If it was closed by an admin, you will have to ask an admin to reopen it (though they will also only be able to do that when the branch is at the proper hash). If the PR is reopened, you can update as usual, e.g.

``` bash
# Checkout the desired hash yyyyyyyyy (or branch)
git checkout yyyyyyyyy
# Delete intermediate testbranch
git branch -D testbranch
# Label current state as testbranch
git checkout -b testbranch
# Push new state to GitHub
git push -f origin testbranch
```

---

# Write shell scripts in OpenWrt

## The default OpenWrt shell is ash: the Almquist shell

The default [shell](https://en.wikipedia.org/wiki/Command-line_interface) provided with *OpenWrt* is the [Almquist shell](https://en.wikipedia.org/wiki/Almquist_shell), which is better known as the *ash shell* and is also the default [Busybox](https://en.wikipedia.org/wiki/BusyBox) shell. Most [Linux distros](https://en.wikipedia.org/wiki/Linux_distribution), such as [Ubuntu](https://en.wikipedia.org/wiki/Ubuntu) or [Debian](https://en.wikipedia.org/wiki/Debian), will use the [Bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)) shell, which is much bigger and more complex than *ash*. For example, a typical *bash* implementation requires approximately 1 MB of disk space, which is an extravagant waste of memory/space in an embedded device.

By contrast, *BusyBox* fits in less than 512 KB of space, and, in addition to providing the *ash* shell, it also provides many other tools you will need to manage your OpenWrt device. Some examples of the other very useful tools provided by *BusyBox* include [awk](https://en.wikipedia.org/wiki/AWK), [grep](https://en.wikipedia.org/wiki/grep), [sed](https://en.wikipedia.org/wiki/sed), and [vi/vim](https://en.wikibooks.org/wiki/Learning_the_vi_Editor/BusyBox_vi). Note that the stock (*i.e.* factory) firmware that ships with many routers also uses *BusyBox* for the reasons outlined here.

## OpenWrt, BusyBox, and the ash shell

OpenWrt firmware uses [BusyBox](https://en.wikipedia.org/wiki/Busybox) because it is extremely efficient with respect to 1) the size required to install it and run it in RAM, and 2) the amount of functionality it provides. Please be aware that many of the *BusyBox* implementations of common Linux/Unix tools might be more limited than their full desktop counterparts. However, *Bash* and *Busybox* shell are similar enough for the majority of daily use cases. If your script is using the [POSIX](https://en.wikipedia.org/wiki/POSIX) features of the *Bash* shell, then it will work in the *Ash* shell, too.

------------------------------------------------------------------------

**Q: Can I install a full version of Bash or other Linux CLI tools, including my favorite editor?**

**A: Yes!** *(but there is a catch)*

If your router supports USB storage and you choose to [install and configure a USB drive](/docs/guide-user/storage/usb-drives-quickstart) with your OpenWrt device, you will have much more storage space for installing programs. If you choose to go this route, then you can install the [bash package](/packages/pkgdata/bash) very easily. Also, OpenWrt contains many packages for installing the full versions of core Linux shell utilities, such as [basename](/packages/pkgdata/coreutils-basename), [cat](/packages/pkgdata/coreutils-cat), [rm](/packages/pkgdata/coreutils-rm), [sort](/packages/pkgdata/coreutils-sort), or [sleep](/packages/pkgdata/coreutils-sleep). To get an idea of the full list of available CLI packages, visit the web page for the OpenWrt packages in the [Utilities](/packages/index/utilities) category and search for all packages that start with *coreutils*. Also, OpenWrt contains many full sized versions of popular [Linux editors](/packages/index/utilities---editors) such as [nano](/packages/pkgdata/nano) and vim (see [vim](/packages/pkgdata/vim), [vim-full](/packages/pkgdata/vim-full), [vim-fuller](/packages/pkgdata/vim-fuller)).

**WARNING: DO NOT INSTALL ANY OF THE vim PACKAGES LINKED HERE UNLESS YOU HAVE INSTALLED A USB DRIVE.**

To illustrate the reason for this warning, as of v19.0x, the [vim-fuller](/packages/pkgdata/vim-fuller) package binary is ~2.8 MB, and it will be even larger when installed.

------------------------------------------------------------------------

## The shebang Operator and Shell Scripting for OpenWrt

Scripts in OpenWrt should have the shebang `#!/bin/sh` at the first line.

A shebang of `#!/bin/bash` can be used, but of course, only if the bash package is installed.

For more information, refer to the [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) operator.

------------------------------------------------------------------------

### Can I change my default shell from ash to bash?

The short answer is "*yes*", but this practice is not recommended.

**WARNING: If you update */etc/passwd* to change the *root* account's default shell to anything other than `#!/bin/sh`, there is a good chance you will be unable to log in to your router via SSH**.

If you've installed the [OpenWrt bash](/packages/pkgdata/bash) package on your router and then changed your default shell to `#!/bin/bash`, you will be able to login to your device via SSH. However, the risk in doing so is that you may still lock yourself out of your device inadvertently, for example, by upgrading. The working assumption for OpenWrt is that *ash* will be the default shell. If you want to use the *bash* shell regularly, then simply run the *bash* command each time you login to your device.

In the event you are having difficulty accessing your device via SSH, refer to the OpenWrt [failsafe process](/docs/guide-user/troubleshooting/failsafe_and_factory_reset).

------------------------------------------------------------------------

## Automated shell script checking

Write your bash scripts with `#!/bin/sh` first line in <https://www.shellcheck.net/> and it will check for features you cannot use in OpenWrt shell. see the <https://github.com/koalaman/shellcheck/blob/master/README.md#portability>

## Check if a tool is available

You may need to install additional command line tools in OpenWrt, as the default installation is very minimal. A Desktop PC Linux like Ubuntu has much more command line tools in default install.

Check if a tool is available by writing **type tool-name** and it will answer you where this tool is, or an error if there is no such tool installed. Use the package table or index (Packages link in the sidebar to the left of this article) to find the package with the tool you need.

    # type time
    time is /usr/bin/time

See also: [Configuration in scripts](config-scripting)

---

# OpenWrt – operating system architecture

Whereas desktop distributions use [glib](https://en.wikipedia.org/wiki/GLib)+[dbus](https://en.wikipedia.org/wiki/D-Bus)+[udev(part of systemd)](https://en.wikipedia.org/wiki/udev), OpenWrt uses [libubox](/docs/techref/libubox)+[ubus](ubus)+[procd](/docs/techref/procd). This provides some pretty awesome functionality without requiring huge libraries with huge dependencies (\*cough\* glib).

```tsv
 	Desktop Distributions	 	OpenWrt	 	[Android](https://en.wikipedia.org/wiki/Android (operating system))	[Replicant](https://en.wikipedia.org/wiki/Replicant (operating system))	[mer-based](https://en.wikipedia.org/wiki/Mer (software distribution))
Typical main memory size	**128 MiB** to 16 GiB (or more)	 	**32 MiB** to 512 MiB[^1]	 	min **92 MiB** for Android 2.1; min **340 MiB** for Android 4.0	 	?
Supported instruction sets	almost anything	 	almost anything	 	x86, 86-64, ARM, MIPS32
non-volatile storage space	100 MiB	 	8 MiB[^2]	 	150MiB for Android 2.1; 512MiB for Android 4.0	 	?
[kernel](https://en.wikipedia.org/wiki/Kernel (computing))	**`Linux kernel`**
:::	FOSS and binary drivers	 	FOSS drivers: e.g. [802.11](https://en.wikipedia.org/wiki/Comparison of open-source wireless drivers); [Iaccess](/docs/techref/hardware/internet.access.technologies)	 	Android binary drivers
[C standard library](https://en.wikipedia.org/wiki/C standard library)	[glibc](https://en.wikipedia.org/wiki/GNU C Library)	 	[uClibc](https://en.wikipedia.org/wiki/uClibc), [musl](https://en.wikipedia.org/wiki/musl)	 	[bionic](https://en.wikipedia.org/wiki/Bionic (software))	glibc + [libhybris](https://en.wikipedia.org/wiki/Hybris (software))	eglibc 2.15
[init](https://en.wikipedia.org/wiki/init)	[init](https://en.wikipedia.org/wiki/init); [Upstart](https://en.wikipedia.org/wiki/Upstart); [Initng](https://en.wikipedia.org/wiki/Initng)	**`systemd`**	busybox-initd	**`procd`**	Android init-fork	 	`systemd`
 	[rsyslog](https://en.wikipedia.org/wiki/rsyslog) / [syslog-ng](https://en.wikipedia.org/wiki/syslog-ng)	:::	busybox-klogd, busybox-syslogd	:::	 	 	:::
 	[watchdog](https://en.wikipedia.org/wiki/watchdog)	:::	busybox-watchdog	:::	 	 	:::
 	[udev](https://en.wikipedia.org/wiki/udev)	:::	[hotplug2](/docs/techref/hotplug_legacy)	:::	 	 	:::
 	[cron](https://en.wikipedia.org/wiki/cron)	:::	`busybox-crond`	 	 	 	:::
 	[atd](https://en.wikipedia.org/wiki/at (Unix))	:::	*na*	 	 	 	:::
 	[D-Bus](https://en.wikipedia.org/wiki/D-Bus)	 	[ubus](/docs/techref/ubus)	 	Binder	?	D-Bus
network configuration	[NetworkManager](https://en.wikipedia.org/wiki/NetworkManager) + GUI	 	`netifd`	 	ConnectivityManager; (not [ConnMan = ConnectionManager](https://connman.net/)!)	?	ConnMan
 	[GLib](https://en.wikipedia.org/wiki/GLib); (GObject, Glib, GModule, GThread, GIO)	 	[libubox](/docs/techref/libubox)	 	?	?	Qt-based?
 	[PulseAudio](https://en.wikipedia.org/wiki/PulseAudio)	 	[pulseaudio](/docs/guide-user/hardware/audio/pulseaudio) (optional)	 	PulseAudio	PulseAudio	PulseAudio
[Package management system](https://en.wikipedia.org/wiki/Package management system)	[dpkg](https://en.wikipedia.org/wiki/dpkg)/[APT](https://en.wikipedia.org/wiki/Advanced Packaging Tool); [RPM](https://en.wikipedia.org/wiki/RPM Package Manager)/[yum](https://en.wikipedia.org/wiki/Yellowdog Updater, Modified); [portage](https://en.wikipedia.org/wiki/Portage (software)); [pacman](https://en.wikipedia.org/wiki/pacman (package manager)); ...	 	`opkg`	 	[apk](https://en.wikipedia.org/wiki/APK (file format))	?	[RPM](https://en.wikipedia.org/wiki/RPM Package Manager)
```

[^1]: yes, *heavily* stripped OpenWrt can run on 16 or even 8MiB
[^2]: yes, 4MiB and 2MiB possible

### What's the difference between ubus vs dbus?

`dbus` is bloated, its C API is very annoying to use and requires writing large amounts of boilerplate code. In fact, the pure C API is so annoying that its own API documentation states: "If you use this low-level API directly, you're signing up for some pain."

`ubus` is tiny and has the advantage of being easy to use from regular C code, as well as automatically making all exported API functionality also available to shell scripts with no extra effort.

"Of course, NetworkManager should be renamed to ***`"unetwork"`***, dbus to ***`"ubus"`***, PulseAudio to ***`"usound"`***, and X.Org-Server/Wayland-Compositor to ***`"udisplay"`***; and then indescribable happiness would come down to all people of this world." – [Lennart Poettering](http://lists.freedesktop.org/archives/dbus/2010-April/012545.html)

------------------------------------------------------------------------

- →[OpenWrt Buildroot – About](/docs/guide-developer/toolchain/start)
- →[OpenWrt Buildroot – Installation](/docs/guide-developer/toolchain/install-buildsystem)
- →[OpenWrt Buildroot – Usage](/docs/guide-developer/toolchain/start)
- →[OpenWrt Buildroot – Patches](/docs/guide-developer/toolchain/use-patches-with-buildsystem)

------------------------------------------------------------------------

- →[file_system](/docs/techref/file_system) / [flash.layout](/docs/techref/flash.layout)
- →[internal.layout](/docs/techref/internal.layout)
- →[preinit_mount](/docs/techref/preinit_mount)/[process.boot](/docs/techref/process.boot)/[requirements.boot.process](/docs/techref/requirements.boot.process)

- [PulseAudio does not depend on GLib](https://www.freedesktop.org/wiki/Software/PulseAudio/FAQ/#index2h3) and does not seem to depends on D-Bus neither: [LFS](http://www.linuxfromscratch.org/blfs/view/svn/multimedia/pulseaudio.html)
- [FOSDEM2013: Can Linux network configuration suck less?](https://archive.fosdem.org/2013/schedule/event/dist_network/)

---

# Mounting Block Devices

This pages discuses the advanced details and underlying operation. For general usage, see [fstab](/docs/guide-user/storage/fstab).

## Overview

The mounting of block devices is handled by the `block-mount` source package, which contains the `block-mount` and `block-hotplug` packages. `block-mount` contains the code that does the actual mounting, and the mounting via `/etc/init.d/fstab` (i.e. on boot rather than when device is hotplugged), and `block-hotplug` takes care of mounting devices when the device is recognized by the system (.e.g. when modules are loaded and the partition detected).

## block-mount (binary package)

~~The `block-mount` binary package (i.e. the one you actually install, rather than the source package containing `block-mount` and `block-hotplug`), contains three library scripts (in addition to `/etc/init.d/fstab` and the sample config file `/etc/config/fstab`). These three scripts are: `block.sh`, `mount.sh`, and `fsck.sh`. ~~

|                                                                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|-------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ![48px-outdated.svg.png](/meta/icons/tango/48px-outdated.svg.png) | As of [r26314](https://dev.openwrt.org/changeset/26314/trunk) `block-extroot` and `block-hotplug` have been merged with `block-mount`. That means that once you install `block-mount` the scripts for [extroot](/docs/guide-user/additional-software/extroot_configuration) mounting and hotplug mounting are installed. With [r36988](https://dev.openwrt.org/changeset/36988) the original package `block-mount` was removed. Technically, the new package `ubox` replaced its functionality. For [Fstab configuration](/docs/guide-user/storage/fstab), the new block-mount package now contains the executable `block` which facilitates this. You can run `block <info|mount|umount|detect>`. See [Fstab configuration](/docs/guide-user/storage/fstab). |

With the new block mount mechanism you can run `block info` to get the same output that blkid delivered (however it only returns info for filesystems it supports). You can do "block mount" to mount all devices (same as what `/etc/init.d/fstab restart` used to do. If you run "`block detect`" you will get a sample uci file for the currently attached block devices. That way you can do "`block detect | uci import fstab`" to store it

:!: block info cannot detect btrfs (added [r43868](https://dev.openwrt.org/changeset/43868/trunk)), xfs , jfs, ntfs, exfat, and some other FS. Use manual scripting to mount them.

:!: For ntfs mount [read here](https://forum.openwrt.org/t/block-mount-ntfs-not-a-tty/64350)

    root@OpenWrt:~# blkid
    /dev/sda1: TYPE="ext2"
    /dev/sda2: UUID="890c87d4-e276-4fb0-a34a-296db408d792" TYPE="ext4"
    /dev/sdb1: LABEL="OPENWRT-BTRFS" UUID="2412e056-a1d8-4710-bf0e-d54b8ff0662f" UUID_SUB="edd04b0f-ccf6-4978-9d76-1fa17921fe58" TYPE="btrfs"
    root@OpenWrt:~# block info
    /dev/sda1: VERSION="1.0" TYPE="ext2"
    /dev/sda2: UUID="890c87d4-e276-4fb0-a34a-296db408d792" VERSION="1.0" TYPE="ext4"

### The new block-mount in Barrier Breaker

#### Usage: block \<info\|mount\|umount\|detect\>

- **info** -\> get the same output that blkid delivered (including mtdblock)

      /dev/mtdblock2: UUID="0906f1b4-51688c99-666b11b5-71d70575" VERSION="4.0" TYPE="squashfs"
      /dev/mtdblock3: TYPE="jffs2"
      /dev/sda1: UUID="e81a771e-249f-4f9e-ab30-b2fb73789744" LABEL="overlay" NAME="EXT_JOURNAL" VERSION="1.0" TYPE="ext4"
      /dev/sda2: UUID="090b67fa-afbb-4771-8efd-7a515c742c18" LABEL="swap" VERSION="2" TYPE="swap"
      /dev/sda5: UUID="91f1-f7ed" LABEL="TRANSPORT" VERSION="FAT32" TYPE="vfat"
      /dev/sda6: UUID="b01791a5-647a-4ab0-9adf-5b626ee5407c" LABEL="daten" NAME="EXT_JOURNAL" VERSION="1.0" TYPE="ext4"
      /dev/sda7: UUID="9f822714-fb75-40c3-9382-f1df42343229" LABEL="rest" NAME="EXT_JOURNAL" VERSION="1.0" TYPE="ext4"

- **mount** -\> mount all devices listed in fstab
- **umount** -\> unmount all devices listed in fstab
- **detect** -\> get a sample uci file for the currently attached block devices

    config 'global'
        option  anon_swap   '0'
        option  anon_mount  '0'
        option  auto_swap   '1'
        option  auto_mount  '1'
        option  delay_root  '5'
        option  check_fs    '0'

    config 'mount'
        option  target  '/mnt/sda1'
        option  uuid    'e81a771e-249f-4f9e-ab30-b2fb73789744'
        option  enabled '0'

    config 'swap'
        option  uuid    '090b67fa-afbb-4771-8efd-7a515c742c18'
        option  enabled '0'

    config 'mount'
        option  target  '/mnt/sda5'
        option  uuid    '91f1-f7ed'
        option  enabled '0'

    config 'mount'
        option  target  '/mnt/sda6'
        option  uuid    'b01791a5-647a-4ab0-9adf-5b626ee5407c'
        option  enabled '0'

    config 'mount'
        option  target  '/mnt/sda7'
        option  uuid    '9f822714-fb75-40c3-9382-f1df42343229'
        option  enabled '0'
        option  options 'lazytime,noatime,background_gc=off,gc_merge'

you can do "`block detect | uci import fstab`" to store it as a sample config file (already with UUID ;-) )

### working/not working in Barrier Breaker as of 2015/01/30

|       | info          | detect        | on boot       | on plug       | mount/umount[^1] | needs         | and                                                              |
|-------|---------------|---------------|---------------|---------------|------------------|---------------|------------------------------------------------------------------|
| ext4  | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔    | kmod-fs-ext4  | libext2fs, :?: kmod-fs-autofs4                                   |
| swap  | @lightgreen:✔ | @lightgreen:✔ | ?             | ?             | ?                | ???           | swap-utils                                                       |
| vfat  | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔ | @lightgreen:✔    | kmod-fs-vfat  | kmod-nls-base, kmod-nls-cp437, kmod-nls-iso8859-1, kmod-nls-utf8 |
| btrfs | @red:✘[^2]    | @red:✘        | @red:✘        | @red:✘        | @red:✘           | kmod-fs-btrfs | btrfs-progs                                                      |

## block-hotplug (binary package)

Block hotplug consists of three scripts, `10-swap`, `20-fsck`, and `40-mount`. When a block devices is added these scripts are executed in the order listed. So, first the device is checked for being a `swap` section, or to attempt to mount as swap, if it is not a defined section for swap or mount (this is known as `anon_swap` or anonymous swap). Then `20-fsck` checks if the device is listed as `enabled_fsck` and if so, attempts to check/repair the filesystem, and, finally, we check if the device should be mounted, either named, or anonymously (i.e. not listed in any section).

[^1]: with the mount command instead of block mount/block umount

[^2]: use btrfs-show to get the UUID

---

# The Bootloader

The [Bootloader](https://en.wikipedia.org/wiki/Bootloader) is a piece of software that is executed every time the hardware device is powered up. It is executable machine code and thus [ARCH](/docs/techref/hardware/cpu#the_isa_instruction_set_architecture)-specific. It's quite heavily device-specific because its main task is to initialize all the low-level hardware details. The bootloader can be contained on a separate [EEPROM](https://en.wikipedia.org/wiki/EEPROM) (very seldom) or directly on flash storage (most common).

 Being a piece of software, the bootloader is considered part of the firmware, but **the bootloader is not part of OpenWrt!**
Only on seldom occasions a change of the *bootloader settings* or the *bootloader code* is necessary to allow for booting/installing OpenWrt
There are a number of bootloaders under diverse [software license](https://en.wikipedia.org/wiki/software license)s

## Main Function

The bootloader's main function is to initialize the hardware, pass an abstraction of the initialized hardware, a hardware description, to and execute the Kernel. (A very nice technical example can be seen [here](https://web.archive.org/web/20111219072809/http://www.wehavemorefun.de/fritzbox/index.php/ADAM2) or see a suggestion until finding a better example: [here](https://www.moritz.systems/blog/before-the-bsd-kernel-starts-part-one-on-amd64/) and [here](https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html)) After that the bootloader is done and not needed in memory any longer. Most bootloaders offer [\#additional functions](#additional functions).

### Why this is necessary?

It's not. A bootloader is not required to boot Linux. The use of one (or several) bootloaders in a row to chainload (or [bootstrap](https://en.wikipedia.org/wiki/Bootstrapping (computing))) a Kernel is not a categorical necessity, it is merely a very crafty method to start an operating system. The main advantage for OpenWrt is, that the existence of a bootloader offers users and developers additional possibilities to [debrick](/docs/guide-user/troubleshooting/generic.debrick) a device.

## Features

### Limitations

Some bootloader or implementation of universal bootloaders come with certain limitation implemented by the OEM, such as:

- a willfully designed kernel/firmware size limitation
- make the bootloader expect a certain exotic firmware format
- inability of the bootloader to execute the [ELF](https://en.wikipedia.org/wiki/Executable and Linkable Format) binary format
- the need of some obscure "magic value" to be present and correct
- you name it

The reasons are variable, from simple ineptitude of the creators to the willful sabotage of the users' attempts to run [free software](https://en.wikipedia.org/wiki/free software) on their own property.

### Additional Functions

The bootloader can be more or less sophisticated, and offer none to many additional functions. In many situations additional functions would give the user a huge advantage, so most bootloaders offer them, such as:

- Flash new firmware, see [generic.flashing](/docs/guide-user/installation/generic.flashing)
- The bootloader can possibly validate data on the flash-storage, and e.g. should the firmware fail to pass a CRC, the bootloader would presume the firmware is corrupt and wait for a new firmware to be uploaded over the network. Of course, this also means, that every time you change something on the flash, you have to update this CRC-value...
- this could also be triggered by setting a boot_wait variable or by a command executed in the serial console
- a [CLI](https://en.wikipedia.org/wiki/Command-line interface) (aka *serial console*), which usually can be accessed over the [serial port](/docs/techref/hardware/port.serial) **only**. There are several ways to access the *serial console* port on your target system, such as using a terminal server, but the most common way is to attach it to a serial port on your host. Additionally, you will need a terminal emulation program on your host system, such as `cu` or `kermit`.
  - once the bootloader has fulfilled its main function - chainload the Kernel - it does not run any longer, so to play with it, you have to login to it before it loads the Kernel and you may also have to prevent it from loading the Kernel, i.e. to stop the boot process.
- boot from USB
  - Like the Kernel requires the module `kmod-fs-ext4` to read/write to a EXT3 filesystem, so a bootloader requires such a module to do the same. [GRUB2](https://en.wikipedia.org/wiki/GRUB2) has this functionality implemented, so with it, you can very comfortably configure your boot options and also update and maintain your OS. The lightweight bootloaders we use with OpenWrt, usually do not have this functionality. But see [flash.layout](/docs/techref/flash.layout) for further reference. One exception is the U-Boot implementation of the [dockstar](/toh/seagate/dockstar). It can not only initialize the USB (like all the rest of the hardware) but additionally utilize the USB and also understand the EXT2 filesystem. Thus, the dockstar can be booted directly from an ext2-formated harddisc/usb-stick connected to any of it's USB-ports.
- [net booting](/inbox/howto/netboot) functionality via [BOOTP](https://en.wikipedia.org/wiki/Bootstrap Protocol) or [PXE](https://en.wikipedia.org/wiki/Preboot Execution Environment) or DHCP or NFS or [TFTP](https://en.wikipedia.org/wiki/Trivial File Transfer Protocol)

## Boot Procedure

-\> **[boot process](process.boot)** should give a more detailed description of whole boot procedure. The bootloader is the beginning.

## Individual Bootloaders

[Comparison of boot loaders](https://en.wikipedia.org/wiki/Comparison of boot loaders)

|                                                                                                                                            |
|--------------------------------------------------------------------------------------------------------------------------------------------|
| *Please use `templates` to create and maintain these articles. ATM they are quite unmaintained and without a structure and almost useless* |

### PC

An embedded bootloader fulfills the same functionality as the [BIOS](https://en.wikipedia.org/wiki/BIOS) plus [GNU GRUB](https://en.wikipedia.org/wiki/GNU GRUB) together on a PC.

- [BIOS](https://en.wikipedia.org/wiki/BIOS) proprietary the BIOS of your PC *is* nothing else but a bootloader!
- [UEFI](https://en.wikipedia.org/wiki/Extensible Firmware Interface) proprietary successor want-to-be of the BIOS
- [coreboot](https://en.wikipedia.org/wiki/coreboot) GPLv2 successor of the BIOS, alternative to [UEFI](../wiki/chunked-reference/wiki_page-guide-developer-uefi-bootable-image.md) based on the Linux kernel;
  support for x86, x86-64 and ARM. There is no MIPS support.
  Coreboot does only "a little bit of hardware initialization"
- [GNU GRUB](https://en.wikipedia.org/wiki/GNU GRUB) GPLv2

### Embedded Devices

- **[Das U-Boot](/docs/techref/bootloader/uboot)** GPLv2 arguably the richest, most flexible, and most actively developed FOSS bootloader available
- [pepe2k-u-boot_mod](/docs/techref/bootloader/pepe2k) GPLv2 U-Boot 1.1.4 modification for routers <https://github.com/pepe2k/u-boot_mod>
- [RedBoot](/docs/techref/bootloader/redboot) mod GPL
- [CFE](/docs/techref/bootloader/cfe) BSD like by Broadcom; the orange color means, the OEM is not obliged to deliver the source code
- [Adam2](/docs/techref/bootloader/adam2) proprietary for AR7/UR8
  - [pspboot](/docs/techref/bootloader/pspboot) proprietary the only slightly compatible successor of Adam2.
- [brnboot](/docs/techref/bootloader/brnboot) unknown sometimes called AMAZON Loader.
- [bootbase](/docs/techref/bootloader/bootbase) unknown used by the ZyXEL Prestige 660HW-xx and Prestige 660M-xx devices (and probably other ZyXEL products). <http://www.ixo.de/info/zyxel_uclinux/>
- [jboot](/docs/techref/bootloader/jboot) unknown
- [myloader](/docs/techref/bootloader/myloader) unknown
- [pp_boot](/docs/techref/bootloader/pp_boot) unknown
- [yamon](/docs/techref/bootloader/yamon) unknown by [Imagination Technology](https://en.wikipedia.org/wiki/Imagination Technology); the Linux kernel can only be booted when it is in SREC format.
- [Breed](/docs/techref/bootloader/Breed) - Breed booatloader
- [bl-mt798x](/docs/techref/bootloader/bl-mt798x) - ATF and u-boot for mt798x-based routers

- VxWorks' own bootloader - most Atheros devices (There is a description of the basic workings on the [Netgear WGT624](/oldwiki/OpenWrtDocs/Hardware/Netgear/WGT624) page.)
- NetBoot - the standard loader in DWL7100AP allows to boot firmware image via network from [TFTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) server direct to RAM
- ThreadX - D-Link uses OS called ThreadX on lowend 1MiB Flash storage & 8MiB RAM models. They have custom boot loader that doesn't output anything sensible to serial port but does have recovery mode so you can upload firmware using browser.

## Bootloader Pages

![bootloader; hidejump;sort=name;display={title};](/pagequery>* @docs/techref/bootloader; hidejump;sort=name;display={title};)
