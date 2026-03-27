---
title: Hardware Hacking First Steps
module: wiki
origin_type: wiki_page
token_count: 1492
source_file: L1-raw/wiki/wiki_page-guide-developer-hw-hacking-first-steps.md
last_pipeline_run: '2026-03-27T07:16:36.403470+00:00'
source_url: https://openwrt.org/docs/guide-developer/hw.hacking.first.steps
language: text
ai_summary: The 'Hardware Hacking First Steps' module provides guidance for users looking to install OpenWrt on unsupported routers. It outlines essential steps such as gaining access to the device via Unix shell, bootloader console, or JTAG port, and emphasizes the importance of gathering hardware information to identify compatible drivers. Users are encouraged to research available GNU/Linux drivers and learn programming languages like C for further development. The module also references various resources for deeper understanding and assistance in hardware hacking.
ai_when_to_use: This module is useful when attempting to install OpenWrt on a router that is not officially supported, guiding users through the initial steps of hardware hacking.
ai_related_topics:
- unix shell
- bootloader console
- JTAG Port
- bootloader
- VLYNQ
---
# Hardware Hacking First Steps

You bought yourself a new router, and it's nice. You can connect a hard disc to it and then it shares its content over samba. It even can do torrent. Wow. But then you stumbled over OpenWrt and its 2000 packages you can install just like that. Never mind all the other FOSS software you could compile for it. And you started crying and decided: you **neeeed** OpenWrt on your router. And if your router is already supported, dandy, flash it on and have fun. But if your router is not (yet) supported? Well, then do this:

## Gain Access

- you could login to some **unix shell** *after booting*, over Ethernet with `telnet`/`ssh`. Example: [hacking.dockstar](/toh/seagate/dockstar/hacking.dockstar) ([dockstar](/toh/seagate/dockstar))
- you could login to **bootloader console** *while booting*, over Ethernet or over the [Serial Port](/docs/techref/hardware/port.serial)
- you could access the hardware *without any booting, without any software present*, over the [JTAG Port](/docs/techref/hardware/port.jtag) with [JTAG](../wiki/wiki_page-guide-developer-debugging.md) Software, like HairyDairyMaid

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
