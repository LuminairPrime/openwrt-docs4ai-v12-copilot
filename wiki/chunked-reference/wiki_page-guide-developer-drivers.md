---
title: Drivers
module: wiki
origin_type: wiki_page
token_count: 331
source_file: L1-raw/wiki/wiki_page-guide-developer-drivers.md
last_pipeline_run: '2026-03-29T23:50:02.157846+00:00'
source_url: https://openwrt.org/docs/guide-developer/drivers
language: text
ai_summary: The Drivers module in OpenWrt provides an overview of how drivers operate within the Linux kernel, emphasizing that they can be compiled into the kernel or loaded as modules. It highlights the different types of driver source code, including Open Source, partially Open Source, and Closed Source (Binary Blobs). The document also notes that all kernel module package filenames in OpenWrt begin with 'kmod-' and that the modprobe command may not be available, recommending the use of insmod instead. Additionally, it suggests various resources for further learning and contacting developers.
ai_when_to_use: Use this module when developing or managing drivers in OpenWrt, especially when dealing with kernel modules and understanding driver source code types.
ai_related_topics:
- Kernel (computing)
- modprobe
- insmod
---

> **Source:** [https://openwrt.org/docs/guide-developer/drivers](https://openwrt.org/docs/guide-developer/drivers)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-29

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
