---
title: GNU Debugger
module: wiki
origin_type: wiki_page
token_count: 430
source_file: L1-raw/wiki/wiki_page-guide-developer-gdb.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_url: https://openwrt.org/docs/guide-developer/gdb
language: text
ai_summary: The GNU Debugger (GDB) guide provides instructions for using GDB on OpenWrt, focusing on compiling tools and adding debugging capabilities to packages. Users can enable GDB and gdbserver in the menuconfig and add CFLAGS to package Makefiles to include debugging information. The guide also outlines how to start gdbserver on the target device and connect to it from the host for debugging sessions. Key commands for setting breakpoints and running programs within GDB are also included.
ai_when_to_use: This guide is useful when developers need to debug applications running on OpenWrt devices. It is particularly applicable when recompiling packages with debugging information to troubleshoot issues.
ai_related_topics:
- gdb
- gdbserver
- TARGET_CFLAGS
- CONFIG_DEBUG
---

> **Source:** [https://openwrt.org/docs/guide-developer/gdb](https://openwrt.org/docs/guide-developer/gdb)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-04-01

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
