---
title: External Documentation
module: wiki
origin_type: wiki_page
token_count: 771
source_file: L1-raw/wiki/wiki_page-techref-externaldocumentation.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_url: https://openwrt.org/docs/techref/externaldocumentation
language: text
ai_summary: The External Documentation module for OpenWrt provides links to various upstream documentation relevant to the components used within the OpenWrt Linux distribution. It includes resources for bootloaders like Das U-Boot and RedBoot, as well as the Linux Kernel and GNU/Linux drivers. Additionally, it covers libraries such as µClibc and BusyBox, which are integral to the OpenWrt environment. Other topics include package management with Opkg, networking with Netfilter, and server options like µHTTPd and lighttpd.
ai_when_to_use: Use this module when you need to reference external documentation for components integrated into OpenWrt, especially during development or troubleshooting. It is particularly useful for understanding the underlying systems and libraries that support OpenWrt functionalities.
ai_related_topics:
- Das U-Boot
- RedBoot
- CFE
- Linux Kernel
- µClibc
- EGLIBC
- newlib
- diet libc
- Opkg
- BusyBox
- Netfilter
- Dropbear
- Dnsmasq
- Samba
- µHTTPd
- httpd
- lighttpd
- mini-httpd
---

> **Source:** [https://openwrt.org/docs/techref/externaldocumentation](https://openwrt.org/docs/techref/externaldocumentation)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-04-01

# External Documentation

OpenWrt is a Linux distribution and comes with own documentation, but much documentation is provided upstream, by the creators of the components.

## Bootloader

### Das U-Boot (GPLv2)

<http://www.denx.de/wiki/U-Boot/>

### RedBoot (modified GPL)

RedBoot (Red Hat Embedded Debug and Bootstrap firmware) <http://ecos.sourceware.org/redboot/>

### CFE (BSD like)

CFE (Common Firmware Environment) is a firmware developed by Broadcom. <http://www.broadcom.com/support/communications_processors/downloads.php#cfe>

## Linux Kernel (GPLv2)

This is the Homepage of the Linux Kernel: <http://www.kernel.org/>.

## GNU/Linux Drivers (diverse)

While all drivers belong into the kernel, official Wikis additionally exist for wireless and sound:

- <http://wireless.kernel.org/>
- <http://alsa-project.org/main/index.php/Main_Page>

## C standard library

### µClibc (LGPL)

At the moment OpenWrt uses µClibc as C standard library. <http://www.uclibc.org/>

### EGLIBC (LGPL)

### newlib (LGPL)

### diet libc (GPLv2)

The project homepage <http://www.fefe.de/dietlibc/> and some [FAQ](http://www.fefe.de/dietlibc/FAQ.txt).

## Opkg (GPLv2)

OpenWrt can be seen as a Linux Distribution for embeded devices. It does bring a Package Manager: <http://code.google.com/p/opkg/>

## BusyBox (GPLv2)

OpenWRT uses [BusyBox](http://www.busybox.net/) to implement the shell environment and most of the usual Unix commands. Instead of having a collection of separate binaries, BusyBox condenses them into one. Executables like vi, ls and grep are merely symbolic links to the BusyBox binary. [BusyBox Command Help](http://busybox.net/downloads/BusyBox.html)

## Netfilter (GPLv2+)

iptables, ip6tables, ebtables: <http://www.netfilter.org/>

## Dropbear (MIT-style license)

OpenWrt prefers <http://matt.ucc.asn.au/dropbear/dropbear.html> over openssl-daemon because of its smaller footprint.

## Dnsmasq (GPL)

In order to handle various OpenWrt configurations, the dnsmasq init script is quite complex. Documentation on all the options passed to dnsmasq is available. [Dnsmasq manual](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)

## Samba (GPLv3)

Official documentation: <http://www.samba.org/samba/docs/>

## Web servers

### µHTTPd (New BSD License)

Since 10.03 'Backfire' OpenWrt utilizes µHTTPd instead of httpd included in Busybox. <https://dev.openwrt.org/browser/trunk/package/uhttpd/> (install `uhttpd`)

### httpd (Busybox) (GPLv2)

[httpd](http://www.busybox.net/downloads/BusyBox.html) (recompile busybox with this included)

### lighttpd (revised BSD)

Currently used by the X-Wrt project. [lighttpd](http://www.lighttpd.net/) (install `lighttpd` and mods)

### mini-httpd (GPLv3+)

[mini-httpd](http://www.nongnu.org/mini-httpd/) (install `mini-httpd` and mods)

### Audio Servers

- <http://pulseaudio.org/>
