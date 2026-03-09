---
title: "OpenWrt \u2013 operating system architecture"
module: wiki
origin_type: wiki_page
token_count: 3023
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-architecture.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
language: text
---
# OpenWrt – operating system architecture

Whereas desktop distributions use [glib](https://en.wikipedia.org/wiki/GLib)+[dbus](https://en.wikipedia.org/wiki/D-Bus)+[udev(part of systemd)](https://en.wikipedia.org/wiki/udev), OpenWrt uses [libubox](/docs/techref/libubox)+[ubus](ubus)+[procd](/docs/techref/procd). This provides some pretty awesome functionality without requiring huge libraries with huge dependencies (\*cough\* glib).

<table>
<thead>
<tr class="header">
<th></th>
<th style="text-align: center;">Desktop Distributions</th>
<th></th>
<th style="text-align: center;">OpenWrt</th>
<th></th>
<th style="text-align: center;"><a href="https://en.wikipedia.org/wiki/Android (operating system)">Android</a></th>
<th><a href="https://en.wikipedia.org/wiki/Replicant (operating system)">Replicant</a></th>
<th><a href="https://en.wikipedia.org/wiki/Mer (software distribution)">mer-based</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Typical main memory size</td>
<td style="text-align: center;"><strong>&lt;color red&gt;128 MiB&lt;/color&gt;</strong> to 16 GiB (or more)</td>
<td></td>
<td style="text-align: center;"><strong>&lt;color red&gt;32 MiB&lt;/color&gt;</strong> to 512 MiB<a href="#fn1" class="footnote-ref" id="fnref1" role="doc-noteref"><sup>1</sup></a></td>
<td></td>
<td style="text-align: center;">min <strong>&lt;color red&gt;92 MiB&lt;/color&gt;</strong> for Android 2.1<br />
min <strong>&lt;color red&gt;340 MiB&lt;/color&gt;</strong> for Android 4.0</td>
<td></td>
<td>?</td>
</tr>
<tr class="even">
<td>Supported instruction sets</td>
<td style="text-align: center;">almost anything</td>
<td></td>
<td style="text-align: center;">almost anything</td>
<td></td>
<td style="text-align: center;">x86, 86-64, ARM, MIPS32</td>
<td></td>
<td></td>
</tr>
<tr class="odd">
<td>non-volatile storage space</td>
<td style="text-align: center;">100 MiB</td>
<td></td>
<td style="text-align: center;">8 MiB<a href="#fn2" class="footnote-ref" id="fnref2" role="doc-noteref"><sup>2</sup></a></td>
<td></td>
<td style="text-align: center;">150MiB for Android 2.1<br />
512MiB for Android 4.0</td>
<td></td>
<td>?</td>
</tr>
<tr class="even">
<td><a href="https://en.wikipedia.org/wiki/Kernel (computing)">kernel</a></td>
<td style="text-align: center;"><strong><code>Linux kernel</code></strong></td>
<td></td>
<td style="text-align: center;"></td>
<td></td>
<td style="text-align: center;"></td>
<td></td>
<td></td>
</tr>
<tr class="odd">
<td>:::</td>
<td style="text-align: center;">FOSS and binary drivers</td>
<td></td>
<td style="text-align: center;">FOSS drivers: e.g. <a href="https://en.wikipedia.org/wiki/Comparison of open-source wireless drivers">802.11</a>; <a href="/docs/techref/hardware/internet.access.technologies">Iaccess</a></td>
<td></td>
<td style="text-align: center;">Android binary drivers</td>
<td></td>
<td></td>
</tr>
<tr class="even">
<td><a href="https://en.wikipedia.org/wiki/C standard library">C standard library</a></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/GNU C Library">glibc</a></td>
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/uClibc">uClibc</a>, <a href="https://en.wikipedia.org/wiki/musl">musl</a></td>
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/Bionic (software)">bionic</a></td>
<td>glibc + <a href="https://en.wikipedia.org/wiki/Hybris (software)">libhybris</a></td>
<td>eglibc 2.15</td>
</tr>
<tr class="odd">
<td><a href="https://en.wikipedia.org/wiki/init">init</a></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/init">init</a><br />
<a href="https://en.wikipedia.org/wiki/Upstart">Upstart</a><br />
<a href="https://en.wikipedia.org/wiki/Initng">Initng</a></td>
<td><strong><code>systemd</code></strong></td>
<td style="text-align: center;">busybox-initd</td>
<td><strong><code>procd</code></strong></td>
<td style="text-align: center;">Android init-fork</td>
<td></td>
<td><code>systemd</code></td>
</tr>
<tr class="even">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/rsyslog">rsyslog</a> / <a href="https://en.wikipedia.org/wiki/syslog-ng">syslog-ng</a></td>
<td>:::</td>
<td style="text-align: center;">busybox-klogd, busybox-syslogd</td>
<td>:::</td>
<td style="text-align: center;"></td>
<td></td>
<td>:::</td>
</tr>
<tr class="odd">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/watchdog">watchdog</a></td>
<td>:::</td>
<td style="text-align: center;">busybox-watchdog</td>
<td>:::</td>
<td style="text-align: center;"></td>
<td></td>
<td>:::</td>
</tr>
<tr class="even">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/udev">udev</a></td>
<td>:::</td>
<td style="text-align: center;"><a href="/docs/techref/hotplug_legacy">hotplug2</a></td>
<td>:::</td>
<td style="text-align: center;"></td>
<td></td>
<td>:::</td>
</tr>
<tr class="odd">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/cron">cron</a></td>
<td>:::</td>
<td style="text-align: center;"><code>busybox-crond</code></td>
<td></td>
<td style="text-align: center;"></td>
<td></td>
<td>:::</td>
</tr>
<tr class="even">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/at (Unix)">atd</a></td>
<td>:::</td>
<td style="text-align: center;"><em>na</em></td>
<td></td>
<td style="text-align: center;"></td>
<td></td>
<td>:::</td>
</tr>
<tr class="odd">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/D-Bus">D-Bus</a></td>
<td></td>
<td style="text-align: center;"><a href="/docs/techref/ubus">ubus</a></td>
<td></td>
<td style="text-align: center;">Binder</td>
<td>?</td>
<td>D-Bus</td>
</tr>
<tr class="even">
<td>network configuration</td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/NetworkManager">NetworkManager</a> + GUI</td>
<td></td>
<td style="text-align: center;"><code>netifd</code></td>
<td></td>
<td style="text-align: center;">ConnectivityManager<br />
(not <a href="https://connman.net/">ConnMan = ConnectionManager</a>!)</td>
<td>?</td>
<td>ConnMan</td>
</tr>
<tr class="odd">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/GLib">GLib</a><br />
(GObject, Glib, GModule, GThread, GIO)</td>
<td></td>
<td style="text-align: center;"><a href="/docs/techref/libubox">libubox</a></td>
<td></td>
<td style="text-align: center;">?</td>
<td>?</td>
<td>Qt-based?</td>
</tr>
<tr class="even">
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/PulseAudio">PulseAudio</a></td>
<td></td>
<td style="text-align: center;"><a href="/docs/guide-user/hardware/audio/pulseaudio">pulseaudio</a> (optional)</td>
<td></td>
<td style="text-align: center;">PulseAudio</td>
<td>PulseAudio</td>
<td>PulseAudio</td>
</tr>
<tr class="odd">
<td><a href="https://en.wikipedia.org/wiki/Package management system">Package management system</a></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/dpkg">dpkg</a>/<a href="https://en.wikipedia.org/wiki/Advanced Packaging Tool">APT</a><br />
<a href="https://en.wikipedia.org/wiki/RPM Package Manager">RPM</a>/<a href="https://en.wikipedia.org/wiki/Yellowdog Updater, Modified">yum</a><br />
<a href="https://en.wikipedia.org/wiki/Portage (software)">portage</a><br />
<a href="https://en.wikipedia.org/wiki/pacman (package manager)">pacman</a><br />
...</td>
<td></td>
<td style="text-align: center;"><code>opkg</code></td>
<td></td>
<td style="text-align: center;"><a href="https://en.wikipedia.org/wiki/APK (file format)">apk</a></td>
<td>?</td>
<td><a href="https://en.wikipedia.org/wiki/RPM Package Manager">RPM</a></td>
</tr>
</tbody>
</table>
<aside id="footnotes" class="footnotes footnotes-end-of-document" role="doc-endnotes">
<hr />
<ol>
<li id="fn1"><p>yes, <em>heavily</em> stripped OpenWrt can run on 16 or even 8MiB<a href="#fnref1" class="footnote-back" role="doc-backlink">↩︎</a></p></li>
<li id="fn2"><p>yes, 4MiB and 2MiB possible<a href="#fnref2" class="footnote-back" role="doc-backlink">↩︎</a></p></li>
</ol>
</aside>

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

<!-- -->

- [PulseAudio does not depend on GLib](https://www.freedesktop.org/wiki/Software/PulseAudio/FAQ/#index2h3) and does not seem to depends on D-Bus neither: [LFS](http://www.linuxfromscratch.org/blfs/view/svn/multimedia/pulseaudio.html)
- [FOSDEM2013: Can Linux network configuration suck less?](https://archive.fosdem.org/2013/schedule/event/dist_network/)
