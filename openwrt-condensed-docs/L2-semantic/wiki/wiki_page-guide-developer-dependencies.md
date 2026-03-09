---
title: Using Dependencies
module: wiki
origin_type: wiki_page
token_count: 1488
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-dependencies.md
last_pipeline_run: '2026-03-09T19:21:03.362055+00:00'
language: text
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

<!-- -->

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