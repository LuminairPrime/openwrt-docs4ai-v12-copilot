---
title: Drivers
module: wiki
origin_type: wiki_page
token_count: 331
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-drivers.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
language: text
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
