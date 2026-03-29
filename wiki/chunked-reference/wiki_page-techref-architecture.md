---
title: OpenWrt – operating system architecture
module: wiki
origin_type: wiki_page
token_count: 1656
source_file: L1-raw/wiki/wiki_page-techref-architecture.md
last_pipeline_run: '2026-03-29T21:42:16.100525+00:00'
source_url: https://openwrt.org/docs/techref/architecture
language: text
ai_summary: OpenWrt's operating system architecture is designed to be lightweight and efficient, utilizing components like libubox, ubus, and procd instead of the larger libraries commonly found in desktop distributions. This architecture allows OpenWrt to function effectively on devices with limited resources, such as 32 MiB to 512 MiB of RAM. Key features include a custom init system (procd), a package management system (opkg), and a unique network configuration tool (netifd). The system is built on the Linux kernel, providing essential functionalities without the overhead of traditional desktop environments.
ai_when_to_use: This architecture is particularly useful for embedded network devices that require a minimal footprint while still delivering robust networking capabilities. Use OpenWrt when developing firmware for routers or IoT devices with constrained hardware resources.
ai_related_topics:
- libubox
- ubus
- procd
- opkg
- netifd
---

> **Source:** [https://openwrt.org/docs/techref/architecture](https://openwrt.org/docs/techref/architecture)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-29

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
