---
title: 'OpenWrt Buildroot: libs packages'
module: openwrt-core
origin_type: makefile_meta
token_count: 5273
version: unknown
source_file: L1-raw/openwrt-core/makefile_meta-category-libs.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
upstream_path: package/libs
language: makefile
---
# OpenWrt Buildroot: libs packages

> **Source:** https://github.com/openwrt/openwrt/tree/master/package/libs
---

## argp-standalone

GNU libc hierarchial argument parsing library broken out from glibc.

| Field | Value |
|---|---|
| Version | 1.3 |
| License | LGPL-2.1 |
| Maintainer | Ted Hess <thess@kitschensync.net> |
| Source URL | https://www.lysator.liu.se/~nisse/misc/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/argp-standalone
---

## elfutils

| Field | Value |
|---|---|
| Version | 0.192 |
| License | GPL-2.0-or-later LGPL-3.0-or-later |
| Maintainer | Luiz Angelo Daros de Luca <luizluca@gmail.com> |
| Source URL | https://sourceware.org/$(PKG_NAME)/ftp/$(PKG_VERSION) https://mirrors.kernel.org/sourceware/$(PKG_NAME)/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/elfutils
---

## gettext-full

| Field | Value |
|---|---|
| Version | 0.24.1 |
| License | LGPL-2.1-or-later |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | @GNU/gettext |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/gettext-full
---

## gmp

GMP is a free library for arbitrary precision arithmetic, operating on signed integers, rational numbers, and floating point numbers.

| Field | Value |
|---|---|
| Version | 6.3.0 |
| License | GPL-2.0-or-later |
| Source URL | @GNU/gmp/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/gmp
---

## gnulib-l10n

Localizations (translations) of messages for GNU gnulib code.

| Field | Value |
|---|---|
| Version | 20241231 |
| Source URL | @GNU/gnulib |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/gnulib-l10n
---

## jansson

Jansson is a C library for encoding, decoding and manipulating JSON data

| Field | Value |
|---|---|
| Version | 2.15.0 |
| License | MIT |
| Source URL | https://codeload.github.com/akheron/$(PKG_NAME)/tar.gz/v$(PKG_VERSION)? |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/jansson
---

## libbpf

libbpf is a library for loading eBPF programs and reading and manipulating eBPF objects from user-space.

| Field | Value |
|---|---|
| Version | 1.6.2 |
| Maintainer | Tony Ambardar <itugrok@yahoo.com> |
| Source URL | https://github.com/libbpf/libbpf |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libbpf
---

## libbsd

This library provides useful functions commonly found on BSD systems, and lacking on others like GNU systems, thus making it easier to port projects with strong BSD origins, without needing to embed the same code over and over again on each project.

| Field | Value |
|---|---|
| Version | 0.12.2 |
| License | BSD-4-Clause |
| Source URL | https://libbsd.freedesktop.org/releases |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libbsd
---

## libcap

$(call Package/libcap/description/Default) . This package contains the libcap utilities.

| Field | Value |
|---|---|
| Version | 2.69 |
| License | GPL-2.0-only |
| Maintainer | Paul Wassi <p.wassi@gmx.at> |
| Source URL | @KERNEL/linux/libs/security/linux-privs/libcap2 |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libcap
---

## libevent2

$(call Package/libevent2/Default/description) This package contains the libevent shared library historically containing both the core & extra libraries.

| Field | Value |
|---|---|
| Version | 2.1.12 |
| License | BSD-3-Clause |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | https://github.com/libevent/libevent/releases/download/release-$(PKG_VERSION)-stable |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libevent2
---

## libiconv-full

| Field | Value |
|---|---|
| Version | 1.18 |
| License | LGPL-2.1-or-later |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | @GNU/libiconv |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libiconv-full
---

## libjson-c

This package contains a library for javascript object notation backends.

| Field | Value |
|---|---|
| Version | 0.18 |
| License | MIT |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://s3.amazonaws.com/json-c_releases/releases/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libjson-c
---

## libmd

This library provides message digest functions found on BSD systems either on their libc or libmd libraries and lacking on others like GNU systems, thus making it easier to port projects with strong BSD origins, without needing to embed the same code over and over again on each project.

| Field | Value |
|---|---|
| Version | 1.1.0 |
| License | BSD-3-Clause |
| Source URL | https://archive.hadrons.org/software/libmd/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libmd
---

## libmnl

libmnl is a minimalistic user-space library oriented to Netlink developers. There are a lot of common tasks in parsing, validating, constructing of both the Netlink header and TLVs that are repetitive and easy to get wrong. This library aims to provide simple helpers that allows you to re-use code and to avoid re-inventing the wheel. The main features of this library are: . * Small: the shared library requires around 30KB for an x86-based computer. . * Simple: this library avoids complexity and elaborated abstractions that tend to hide Netlink details. . * Easy to use: the library simplifies the work for Netlink-wise developers. It provides functions to make socket handling, message building, validating, parsing and sequence tracking, easier. . * Easy to re-use: you can use the library to build your own abstraction layer on top of this library. . * Decoupling: the interdependency of the main bricks that compose the library is reduced, i.e. the library provides many helpers, but the pro

| Field | Value |
|---|---|
| Version | 1.0.5 |
| License | LGPL-2.1+ |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | http://www.netfilter.org/projects/libmnl/files ftp://ftp.netfilter.org/pub/libmnl |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libmnl
---

## libnetfilter-conntrack

libnetfilter_conntrack is a userspace library providing a programming interface (API) to the in-kernel connection tracking state table. The library libnetfilter_conntrack has been previously known as libnfnetlink_conntrack and libctnetlink. This library is currently used by conntrack-tools among many other applications.

| Field | Value |
|---|---|
| Version | 1.1.0 |
| License | GPL-2.0-or-later |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | https://www.netfilter.org/projects/libnetfilter_conntrack/files |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnetfilter-conntrack
---

## libnfnetlink

libnfnetlink is is the low-level library for netfilter related kernel/userspace communication. It provides a generic messaging infrastructure for in-kernel netfilter subsystems (such as nfnetlink_log, nfnetlink_queue, nfnetlink_conntrack) and their respective users and/or management tools in userspace.

| Field | Value |
|---|---|
| Version | 1.0.2 |
| License | GPL-2.0+ |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | http://www.netfilter.org/projects/libnfnetlink/files/ ftp://ftp.netfilter.org/pub/libnfnetlink/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnfnetlink
---

## libnftnl

libnftnl is a userspace library providing a low-level netlink programming interface (API) to the in-kernel nf_tables subsystem.

| Field | Value |
|---|---|
| Version | 1.3.1 |
| License | GPL-2.0-or-later |
| Maintainer | Steven Barth <steven@midlink.org> |
| Source URL | https://netfilter.org/projects/$(PKG_NAME)/files |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnftnl
---

## libnl

Common code for all netlink libraries

| Field | Value |
|---|---|
| Version | 3.12.0 |
| License | LGPL-2.1 |
| Source URL | https://github.com/thom311/libnl/releases/download/libnl$(subst .,_,$(PKG_VERSION)) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnl
---

## libnl-tiny

This package contains a stripped down version of libnl

| Field | Value |
|---|---|
| License | LGPL-2.1 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/libnl-tiny SECTION:=libs CATEGORY:=Libraries TITLE:=netlink socket library ABI_VERSION:=1  |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libnl-tiny
---

## libpcap

This package contains a system-independent library for user-level network packet capture.

| Field | Value |
|---|---|
| Version | 1.10.6 |
| License | BSD-3-Clause |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://www.tcpdump.org/release/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libpcap
---

## libselinux

libselinux is the runtime SELinux library that provides interfaces (e.g. library functions for the SELinux kernel APIs like getcon(), other support functions like getseuserbyname()) to SELinux-aware applications. libselinux may use the shared libsepol to manipulate the binary policy if necessary (e.g. to downgrade the policy format to an older version supported by the kernel) when loading policy.

| Field | Value |
|---|---|
| Version | 3.9 |
| License | libselinux-1.0 |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libselinux
---

## libsemanage

libsemanage is the policy management library. It uses libsepol for binary policy manipulation and libselinux for interacting with the SELinux system. It also exec's helper programs for loading policy and for checking whether the file_contexts configuration is valid (load_policy and setfiles from policycoreutils) presently, although this may change at least for the bootstrapping case (for rpm).

| Field | Value |
|---|---|
| Version | 3.9 |
| License | LGPL-2.1 |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libsemanage
---

## libsepol

Libsepol is the binary policy manipulation library. It doesn't depend upon or use any of the other SELinux components.

| Field | Value |
|---|---|
| Version | 3.9 |
| Maintainer | Thomas Petazzoni <thomas.petazzoni@bootlin.com> |
| Source URL | https://github.com/SELinuxProject/selinux/releases/download/$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libsepol
---

## libtool

| Field | Value |
|---|---|
| Version | 2.5.4 |
| License | GPL-2.0+ |
| Source URL | @GNU/libtool |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libtool
---

## libtraceevent

The libtraceevent library provides APIs to access kernel tracepoint events, located in the tracefs file system under the events directory.

| Field | Value |
|---|---|
| Version | 1.9.0 |
| Maintainer | Nick Hainke <vincent@systemli.org> |
| Source URL | https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/snapshot/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libtraceevent
---

## libtracefs

The libtracefs library provides APIs to access kernel trace file system.

| Field | Value |
|---|---|
| Version | 1.8.3 |
| Maintainer | Nick Hainke <vincent@systemli.org> |
| Source URL | https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/snapshot/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libtracefs
---

## libubox

Library for parsing and generating JSON from shell scripts

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libubox
---

## libunistring

This library provides functions for manipulating Unicode strings and for manipulating C strings according to the Unicode standard.

| Field | Value |
|---|---|
| Version | 1.4.2 |
| License | GPL-3.0 |
| Source URL | @GNU/$(PKG_NAME) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libunistring
---

## libunwind

Libunwind defines a portable and efficient C programming interface (API) to determine the call-chain of a program.

| Field | Value |
|---|---|
| Version | 1.8.3 |
| License | X11 |
| Maintainer | Yousong Zhou <yszhou4tech@gmail.com> |
| Source URL | https://github.com/libunwind/libunwind/releases/download/v$(PKG_VERSION)/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libunwind
---

## libusb

libusb is a C library that gives applications easy access to USB devices on many different operating systems.

| Field | Value |
|---|---|
| Version | 1.0.29 |
| License | LGPL-2.1-or-later |
| Maintainer | Felix Fietkau <nbd@nbd.name> |
| Source URL | https://github.com/libusb/libusb/releases/download/v$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libusb
---

## libxml2

A library for manipulating XML and HTML resources.

| Field | Value |
|---|---|
| Version | 2.15.1 |
| License | MIT |
| Source URL | @GNOME/libxml2/$(basename $(PKG_VERSION)) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/libxml2
---

## mbedtls

$(call Package/mbedtls/Default/description) This package contains the mbedtls library.

| Field | Value |
|---|---|
| Version | 3.6.5 |
| License | GPL-2.0-or-later |
| Source URL | https://github.com/Mbed-TLS/$(PKG_NAME)/releases/download/$(PKG_NAME)-$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/mbedtls
---

## mpfr

MPFR is a portable library written in C for arbitrary precision arithmetic on floating-point numbers. It is based on the GNU MP library. It aims to provide a class of floating-point numbers with precise semantics.

| Field | Value |
|---|---|
| Version | 4.2.2 |
| License | LGPL-3.0-or-later |
| Maintainer | Jeffery To <jeffery.to@gmail.com> |
| Source URL | @GNU/mpfr http://www.mpfr.org/mpfr-$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/mpfr
---

## musl-fts

The musl-fts package implements the fts(3) functions fts_open, fts_read, fts_children, fts_set and fts_close, which are missing in musl libc.

| Field | Value |
|---|---|
| Version | 1.2.7 |
| License | LGPL-2.1 |
| Maintainer | Lucian Cristian <lucian.cristian@gmail.com> |
| Source URL | https://github.com/pullmoll/musl-fts.git |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/musl-fts
---

## ncurses

| Field | Value |
|---|---|
| Version | 6.4 |
| License | MIT |
| Source URL | @GNU/$(PKG_NAME) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/ncurses
---

## nettle

| Field | Value |
|---|---|
| Version | 3.10.2 |
| License | GPL-2.0-or-later |
| Source URL | @GNU/nettle |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/nettle
---

## openssl

$(call Package/openssl/Default/description) This package contains the OpenSSL shared libraries, needed by other programs.

| Field | Value |
|---|---|
| Version | 3.5.5 |
| License | Apache-2.0 |
| Maintainer | Eneas U de Queiroz <cotequeiroz@gmail.com> |
| Source URL | https://www.openssl.org/source/ https://www.openssl.org/source/old/$(PKG_BASE)/ https://github.com/openssl/openssl/relea |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/openssl
---

## pcre2

| Field | Value |
|---|---|
| Version | 10.47 |
| License | BSD-3-Clause |
| Maintainer | Shane Peelar <lookatyouhacker@gmail.com> |
| Source URL | https://github.com/PCRE2Project/pcre2/releases/download/$(PKG_NAME)-$(PKG_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/pcre2
---

## popt

| Field | Value |
|---|---|
| Version | 1.19 |
| License | MIT |
| Source URL | http://ftp.rpm.org/popt/releases/popt-1.x/ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/popt
---

## readline

The Readline library provides a set of functions for use by applications that allow users to edit command lines as they are typed in. Both Emacs and vi editing modes are available. The Readline library includes additional functions to maintain a list of previously-entered command lines, to recall and perhaps reedit those lines, and perform csh-like history expansion on previous commands.

| Field | Value |
|---|---|
| Version | 8.3 |
| License | GPL-3.0-or-later |
| Source URL | @GNU/readline |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/readline
---

## sysfsutils

The library's purpose is to provide a consistant and stable interface for querying system device information exposed through sysfs.

| Field | Value |
|---|---|
| Version | 2.1.0 |
| License | LGPL-2.1 |
| Maintainer | Jo-Philipp Wich <jo@mein.io> |
| Source URL | @SF/linux-diag |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/sysfsutils
---

## toolchain

| Field | Value |
|---|---|
| License | GPL-3.0-with-GCC-exception |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/toolchain
---

## uclient

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/uclient
---

## udebug

| Field | Value |
|---|---|
| License | GPL-2.0 |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/libudebug SECTION:=libs CATEGORY:=Libraries TITLE:=udebug client library DEPENDS:=+libubox |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/udebug
---

## ustream-ssl

| Field | Value |
|---|---|
| License | ISC |
| Maintainer | Felix Fietkau <nbd@nbd.name> include $(INCLUDE_DIR)/[package.mk](../openwrt-core/makefile_meta-include-mk.md) include $(INCLUDE_DIR)/cmake.mk define Package/libustream/default SECTION:=libs CATEGORY:=Libraries TITLE:=ustream SSL Library DEPENDS:=+ |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/ustream-ssl
---

## wolfssl

wolfSSL (formerly CyaSSL) is an SSL library optimized for small footprint, both on disk and for memory use.

| Field | Value |
|---|---|
| Version | 5.8.4 |
| License | GPL-3.0-or-later |
| Maintainer | Eneas U de Queiroz <cotequeiroz@gmail.com> |
| Source URL | https://github.com/wolfSSL/wolfssl/archive/v$(PKG_REAL_VERSION) |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/wolfssl
---

## zlib

zlib is a lossless data-compression library. This package includes the shared library.

| Field | Value |
|---|---|
| Version | 1.3.1 |
| License | Zlib |
| Source URL | https://github.com/madler/zlib |


> Source: https://github.com/openwrt/openwrt/tree/master/package/libs/zlib
---
