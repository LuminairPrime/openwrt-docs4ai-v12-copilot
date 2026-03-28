---
title: Adding new platform support
module: wiki
origin_type: wiki_page
token_count: 4884
source_file: L1-raw/wiki/wiki_page-guide-developer-add-new-platform.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_url: https://openwrt.org/docs/guide-developer/add.new.platform
language: text
ai_summary: The 'Adding new platform support' module provides guidance for developers looking to add new platform support to OpenWrt. It emphasizes the importance of Linux in embedded devices and outlines the need for open-source firmware to enhance functionality and security. The document includes methods for verifying if a device runs Linux, particularly through OS fingerprinting and port scanning using tools like *nmap*. Specific command examples illustrate how to gather information about the device's operating system and running services.
ai_when_to_use: This module is useful when you want to extend OpenWrt support to new hardware platforms or verify the Linux compatibility of existing devices. It is particularly relevant for developers aiming to create custom firmware for routers and other embedded devices.
ai_related_topics:
- add.new.device
- nmap
---

> **Source:** [https://openwrt.org/docs/guide-developer/add.new.platform](https://openwrt.org/docs/guide-developer/add.new.platform)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-28

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
