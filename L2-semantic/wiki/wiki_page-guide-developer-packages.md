---
title: Creating packages
module: wiki
origin_type: wiki_page
token_count: 11047
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-packages.md
last_pipeline_run: '2026-03-20T04:40:03.869041+00:00'
language: text
ai_summary: Step-by-step guide for creating a new OpenWrt package from scratch. Covers directory layout under package/mypackage/, the minimal Makefile skeleton (include $(TOPDIR)/rules.mk, Package/define, Build/Compile, Package/install), adding dependencies via DEPENDS:=, using PKG_INSTALL=1 vs. custom Build/Compile, creating conffiles, installing init scripts, and submitting packages to the upstream feed.
ai_when_to_use: 'Reference when porting a new open-source application to OpenWrt or creating a first-party package: follow the Makefile skeleton to define metadata, set the correct PKG_RELEASE, and use $(INSTALL_BIN)/$(INSTALL_CONF) macros in Package/install to place files in the correct image paths.'
ai_related_topics:
- Package/define
- Build/Compile
- Package/install
- DEPENDS
- PKG_INSTALL
- conffiles
- feeds
---
# Creating packages

**See also -\> [Package Policy Guide](package-policies)**, which contains a wealth of extra technical information not covered here.

One of the things that we've attempted to do with OpenWrt's template system is make it incredibly easy to port software to OpenWrt. If you look at a typical package directory in OpenWrt you'll find three things:

- package/Makefile
- package/patches
- package/files

The patches directory is optional and typically contains bug fixes or optimizations to reduce the size of the executable. The files directory is optional. It typically includes default config or init files.

The package `Makefile` is the important item because it provides the steps actually needed to download and compile the package.

Looking at one of the package makefiles, you'd hardly recognize it as a makefile. Through what can only be described as blatant disregard and abuse of the traditional make format, the `Makefile` has been transformed into an object oriented template which simplifies the entire ordeal.

Here, for example, is package/bridge/Makefile:

``` make
include $(TOPDIR)/rules.mk

PKG_NAME:=bridge
PKG_VERSION:=1.0.6
PKG_RELEASE:=1

PKG_BUILD_DIR:=$(BUILD_DIR)/bridge-utils-$(PKG_VERSION)
PKG_SOURCE:=bridge-utils-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=@SF/bridge
PKG_HASH:=9b7dc52656f5cbec846a7ba3299f73bd

include $(INCLUDE_DIR)/package.mk

define Package/bridge
  SECTION:=base
  CATEGORY:=Network
  TITLE:=Ethernet bridging configuration utility
  URL:=http://bridge.sourceforge.net/
endef

define Package/bridge/description
 Ethernet bridging configuration utility
 Manage ethernet bridging; a way to connect networks together to
 form a larger network.
endef

define Build/Configure
  $(call Build/Configure/Default,--with-linux-headers=$(LINUX_DIR))
endef

define Package/bridge/install
        $(INSTALL_DIR) $(1)/usr/sbin
        $(INSTALL_BIN) $(PKG_BUILD_DIR)/brctl/brctl $(1)/usr/sbin/
endef

$(eval $(call BuildPackage,bridge))
```

## BuildPackage variables

As you can see, there's not much work to be done; everything is hidden in other makefiles and abstracted to the point where you only need to specify a few variables.

- `PKG_NAME` - The name of the package, as seen via menuconfig and ipkg. Avoid using underscores in the package name, to avoid build failures--for example, the underscore separates name from version information, and may confuse the build system in hard-to-spot places.
- `PKG_VERSION` - The upstream version number that we're downloading
- `PKG_RELEASE` - The version of this package Makefile. Should be initially set to 1, and reset to 1 whenever the `PKG_VERSION` is changed. Increment it when `PKG_VERSION` stays the same, but when there are functional changes to the installed artifacts.
- `PKG_LICENSE` - The license(s) the package is available under, [SPDX](https://spdx.org/licenses/) form.
- `PKG_LICENSE_FILES`- file containing the license text
- `PKG_BUILD_DIR` - Where to compile the package
- `PKG_SOURCE` - The filename of the original sources
- `PKG_SOURCE_URL` - Where to download the sources from (directory)
- `PKG_HASH` - A checksum to validate the download. It can be either a MD5 or SHA256 checksum, but SHA256 should be used, see [scripts/download.pl](commit>?p=openwrt/openwrt.git;a=blob;f=scripts/download.pl;h=676c6e9e6b10b6a44ed2bbc03a7ba3c983aaf639;hb=HEAD#l66)
- `PKG_CAT` - How to decompress the sources (zcat, bzcat, unzip)
- `PKG_URL`. - Upstream project homepage
- `PKG_BUILD_DEPENDS` - Packages that need to be built before this package. Use this option if you need to make sure that your package has access to includes and/or libraries of another package at build time. Specify the directory name (i.e. openssl) rather than the binary package name (i.e. libopenssl). This build variable only establishes the build time dependency. Use `DEPENDS` to establish the runtime dependencies. This variable uses the same syntax as `DEPENDS` below.
- `PKG_CONFIG_DEPENDS` - specifies which config options influence the build configuration and should trigger a rerun of Build/Configure on change
- `PKG_INSTALL` - Setting it to "1" will call the package's original "make install" with prefix set to `PKG_INSTALL_DIR`
- `PKG_INSTALL_DIR` - Where "make install" copies the compiled files
- `PKG_FIXUP` - See below
- `PKG_CPE_ID` - Variable defining Common Platform Enumeration (CPE) identifier, which uniquely identifies application usually in vulnerability tracking. The CPE standard itself is maintained by NIST and documented at[Official Common Platform Enumeration (CPE) Dictionary](https://nvd.nist.gov/products/cpe)
- `PKG_CVE_IGNORE` - Variable for defining CVEs that don't apply to this version of the package due to features not enabled, or affecting other platforms (e.g. Windows issues or features that are not used and so not relevant)
- `PKG_CVE_FIXED` - Variable for defining CVEs that are patches in the current version, but aren't properly marked as fixed at cve.org in the current version

Optional support for fetching sources from a VCS (git, bzr, svn, etc), see [Use source repository](#use_source_repository) below for more information:

- `PKG_SOURCE_PROTO` - the protocol to use for fetching the sources (git, svn, etc).
- `PKG_SOURCE_URL` - source repository to fetch from. The URL scheme must be consistent with `PKG_SOURCE_PROTO` (e.g. `git://`), but most VCS accept `http://` or `https://` URLs nowadays.
- `PKG_SOURCE_VERSION` - must be specified, the commit hash or SVN revision to check out.
- `PKG_SOURCE_DATE` - a date like `2017-12-25`, will be used in the name of generated tarballs.
- `PKG_MIRROR_HASH` - SHA256 checksum of the tarball generated from the source repository checkout (previously named `PKG_MIRROR_MD5SUM`). See [below](#use_source_repository) for details.
- `PKG_SOURCE_SUBDIR` - where the temporary source checkout should be stored, defaults to `$(PKG_NAME)-$(PKG_VERSION)`

The `PKG_*` variables define where to download the package from; @SF is a special keyword for downloading packages from sourceforge. The md5sum is used to verify the package was downloaded correctly and PKG_BUILD_DIR defines where to find the package after the sources are uncompressed into \$(BUILD_DIR). PKG_INSTALL_DIR defines where the files will be copied after calling "make install" (set with the PKG_INSTALL variable), and after that you can package them in the install section.

At the bottom of the file is where the real magic happens, "BuildPackage" is a macro setup by the earlier include statements. BuildPackage only takes one argument directly -- the name of the package to be built, in this case "bridge". All other information is taken from the define blocks. This is a way of providing a level of verbosity, it's inherently clear what the DESCRIPTION variable in Package/bridge is, which wouldn't be the case if we passed this information directly as the Nth argument to BuildPackage.

Avoid reuse of PKG_NAME in call, define and eval lines for consistency and readability. Write the full name instead.

## Testing a package Makefile

There is [support for a range of sanity checks](commit>?p=openwrt/openwrt.git;a=commit;h=7a315b0b5d6aa91695853a8647383876e4b49a7a) like mismatched checksums.

To check your package:

    make package/nlbwmon/download
    make package/nlbwmon/check V=s

To automatically attempt to fix the Makefile:

    make package/nlbwmon/check V=s FIXUP=1

Note: despite the similar name, this has nothing to do with the `PKG_FIXUP` variable presented below.

## PKG_FIXUP

Some packages that use autotools end up needing fixes to work around autotools using host tools instead of the build environment tools. OpenWrt defines some PKG_FIXUP rules to help work around this.

``` make
PKG_FIXUP:=autoreconf
PKG_FIXUP:=patch-libtool
PKG_FIXUP:=gettext-version
```

Any variations of this you see in the wild are simply aliases for these.

##### autoreconf

This fixup performs

- autoreconf -f -i
- touch required but maybe missing files
- ensures that openwrt-libtool is linked
- suppresses autopoint/gettext

##### patch-libtool

If the shipped automake recipes are broken beyond repair, then simply find instances of libtool, detect their version and apply OpenWrt fix patches to it.

##### gettext-version

This fixup suppresses version mismatch errors in automake's gettext support.

#### Tips

Packages that are using Autotools should work with simply "PKG_FIXUP:=autoreconf". However there might be issues with required versions.

:!: Instead of patching `./configure`, one should fix the file from which `./configure` is generated in autotools: `configure.ac` (or `configure.in`, for very old packages). Another important file is `Makefile.am` from which `Makefile`s (with `configure` output) are generated.

## Package Sourcecode

OpenWrt Buildroot supports many different ways to download external source code.

### Use packed source code archive

Most packages use a packed .tar.gz, .tar.bz2, .tar.xz or similar source code file.

### Use source repository

`PKG_SOURCE_PROTO` supports download from various repositories to integrate development versions:

``` make
PKG_SOURCE_PROTO:=bzr
PKG_SOURCE_PROTO:=cvs
PKG_SOURCE_PROTO:=darcs
PKG_SOURCE_PROTO:=git
PKG_SOURCE_PROTO:=hg
PKG_SOURCE_PROTO:=svn
```

Besides the source repository `PKG_SOURCE_URL`, you also need to specify which exact version you are building using `PKG_SOURCE_VERSION` e.g. a commit hash for git, or a revision number for svn. The `PKG_SOURCE_VERSION` can be a git tag and specified like `PKG_SOURCE_VERSION:=v$(PKG_VERSION)`.

Buildroot will first clone the source repository, and then generate a tarball from the source repository, with a name like `dl/odhcpd-2017-08-16-94e65ee0.tar.xz`.

You should also define `PKG_MIRROR_HASH` with the SHA256 checksum of this generated tarball. This way, users building OpenWrt will directly download the generated tarball from a buildbot and verify its checksum, thus avoiding a clone of the source repository.

:!: The tarballs generated from svn checkouts are not reproducible, so you should avoid defining `PKG_MIRROR_HASH` when building from svn!

To generate `PKG_MIRROR_HASH` automatically, use the following (replace `package/odhcpd` by your package):

    # First add "PKG_MIRROR_HASH:=skip" to the package Makefile and/or "HASH:=skip", if required.
    make package/odhcpd/download V=s
    make package/odhcpd/check FIXUP=1 V=s

:!: `PKG_MIRROR_HASH:=skip` does not currently work, see [GitHub issue \#19757](https://github.com/openwrt/openwrt/issues/19757)

Complete git example:

``` make
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/jow-/nlbwmon.git
PKG_SOURCE_DATE:=2017-08-02
PKG_SOURCE_VERSION:=32fc0925cbc30a4a8f71392e976aa94b586c4086
PKG_MIRROR_HASH:=caedb66cf6dcbdcee0d1525923e203d003ef15f34a13a328686794666f16171f
```

History: `PKG_MIRROR_MD5SUM` was [introduced in 2011](commit>?p=openwrt/openwrt.git;a=commitdiff;h=b568a64f8c1f7c077c83d8c189d4c84ca270aeb4) and [renamed to `PKG_MIRROR_HASH` in 2016](commit>?p=openwrt/openwrt.git;a=commitdiff;h=7416d2e046b87b262b407f8af70b8dd9b2927c70).

### Bundle source code with OpenWrt Makefile

It is also possible to have the source code in the package/\<packagename\> directory. Often a ./src/ subdirectory is used.

    Examples: px5g , px5g-standalone

### Download override

Bundled source code does not need overriding.

You can download additional data from external sources.

``` make
USB_IDS_VER:=0.321
USB_IDS_FILE:=usb.ids.$(USB_IDS_VER)
define Download/usb_ids
  FILE:=$(USB_IDS_FILE)
  URL_FILE:=usb.ids
  URL:=@GITHUB/vcrhonek/hwdata/v$(USB_IDS_VER)
  HASH:=00aa21766bb078186d2bc2cca9a2ae910aa2b787a810e97019b1b3f94c9453f2
endef
$(eval $(call Download,usb_ids))
```

and unpack it or integrate it into the build process

``` make
define Build/Prepare
        $(Build/Prepare/Default)
        $(CP) $(DL_DIR)/$(USB_IDS_FILE) $(PKG_BUILD_DIR)/usb.ids
endef
```

You can modify UNPACK_CMD or call/modify PKG_UNPACK manually in your Build/Prepare section.

``` make
UNPACK_CMD=ar -p "$(DL_DIR)/$(PKG_SOURCE)" data.tar.xz | xzcat | tar -C $(1) -xf -
```

``` make
define Build/Prepare
        $(PKG_UNPACK)
#       we have to download additional stuff before patching
        (cd $(PKG_BUILD_DIR) && ./contrib/download_prerequisites)
        $(Build/Patch)
endef
```

    Examples: px5g, px5g-standalone, usbutils, debootstrap, gcc,

## BuildPackage defines

##### Package/

matches the argument passed to buildroot, this describes the package the menuconfig and ipkg entries. Within Package/ you can define the following variables:

-  SECTION - The type of package (currently unused)
-  CATEGORY - Which menu it appears in menuconfig
-  TITLE - A short description of the package
-  URL - Where to find the original software
-  MAINTAINER - (required for new packages) Who to contact concerning the package
-  DEPENDS - (optional) Which packages must be built/installed before this package. See [below](#dependency_types) for the syntax
-  EXTRA_DEPENDS - (optional) Runtime dependencies, don't get built, only added to package `control` file
-  PROVIDES - (optional) allow to define a virtual package that might be provided by multiple real-packages
-  PKGARCH - (optional) Set this to "all" to produce a package with "Architecture: all" (See below)
-  USERID - (optional) a username:groupname pair to create at package installation time.

##### PKGARCH (optional)

By default, packages are built for the target architecture, and the ipk files generated are tagged that way. This is normally correct, for any compiled code, but if a package only contains scripts or resources, marking it with PKGARCH:=all will make a single ipk file that can be installed on any target architecture. (It will still be compiled into `bin/packages/arch/`, however.)

##### Package/conffiles (optional)

A list of config files installed by this package, one file per line. The file list section should not be indented: no leading tabs or spaces in the section.

##### Package/description

A free text description of the package

##### Build/Prepare (optional)

A set of commands to unpack and patch the sources. You may safely leave this undefined.

##### Build/Configure (optional)

You can leave this undefined if the source doesn't use configure or has a normal config script, otherwise you can put your own commands here or use "\$(call Build/Configure/Default,)" as above to pass in additional arguments for a standard configure script.

##### Build/Compile (optional)

How to compile the source; in most cases you should leave this undefined, because then the default is used, which calls make. If you want to pass special arguments to make, use e.g. "\$(call Build/Compile/Default,FOO=bar)"

##### Build/Install (optional)

How to install the compiled source. The default is to call "make install". Again, to pass special arguments or targets, use "\$(call Build/Install/Default,install install-foo)". Note that you need put all the needed make arguments here. If you just need to add something to the "install" argument, don't forget the "install" itself.

##### Build/InstallDev (optional)

For things needed to compile packages against it (static libs, header files), but that are of no use on the target device.

##### Build/Clean (optional)

For things needed to be wiped out during cleanup procedure.

##### Package/install

A set of commands to copy files into the ipkg which is represented by the \$(1) directory. As source you can use relative paths which will install from the unpacked and compiled source, or \$(PKG_INSTALL_DIR) which is where the files in the Build/Install step above end up.

##### Package/preinst

The actual text of the script which is to be executed before installation. Don't forget to include the `#!/bin/sh`. If you need to abort installation, have the script return `false`.

##### Package/postinst

The actual text of the script which is to be executed after installation. Don't forget to include the `#!/bin/sh`. Alternatively you can also use an [uci-default script](/docs/guide-developer/uci-defaults) which will be executed automatically on runtime installations by opkg or embedding into an image.

##### Package/prerm

The actual text of the script which is to be executed before removal. Don't forget to include the `#!/bin/sh`. If you need to abort removal, have the script return `false`.

##### Package/postrm

The actual text of the script which is to be executed after removal. Don't forget to include the `#!/bin/sh`.

The reason that some of the defines are prefixed by "Package/" and others are simply "Build" is because of the possibility of generating multiple packages from a single source. OpenWrt works under the assumption of one source per package `Makefile`, but you can split that source into as many packages as desired. Since you only need to compile the sources once, there's one global set of "Build" defines, but you can add as many "Package/" defines as you want by adding extra calls to BuildPackage -- see the dropbear package for an example.

## Building in a subdirectory of the source

Some software has no Makefile directly at the root of the tarball. For instance, it is common to have a `src/` directory with all source files and a Makefile. The problem is that OpenWRT's build system will try to run `make` in `PKG_BUILD_DIR`; this will fail if there is no Makefile there. To solve this problem, use the `MAKE_PATH` variable, for instance:

    MAKE_PATH:=src

This path is relative to `PKG_BUILD_DIR` and defaults to `.`. Alternatively, you can override `Build/Compile` (see above), though this is more work.

## Dependency Types

Various types of dependencies can be specified, which require a bit of explanation for their differences. More documentation is available at [Using Dependencies](/docs/guide-developer/dependencies)

|              |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|:-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| +\<foo\>     | Package will depend on package \<foo\> and will select it when selected.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| \<foo\>      | Package will depend on package \<foo\> and will be invisible until \<foo\> is selected.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| @FOO         | Package depends on the config symbol CONFIG_FOO and will be invisible unless CONFIG_FOO is set. This usually used for depending on certain Linux versions or targets, e.g. @TARGET_foo will make a package only available for target foo. You can also use boolean expressions for complex dependencies, e.g. @(!TARGET_foo&&!TARGET_bar) will make the package unavailable for foo and bar.                                                                                                                                                                                                                                                                       |
| +FOO:\<bar\> | Package will depend on \<bar\> if CONFIG_FOO is set, and will select \<bar\> when it is selected itself. The typical use case would be if there are compile time options for this package toggling features that depend on external libraries. :!: Note that the + replaces the @. :!: There is limited support for boolean operators here compared to the @ type above. Negation ! is only supported to negate the whole condition. Parentheses are ignored, so use them only for readability. Like C, && has a higher precedence than \|\|. So +(YYY\|\|FOO&&BAR):package will select package if CONFIG_YYY is set or if both CONFIG_FOO and CONFIG_BAR are set. |
| @FOO:\<bar\> | Package will depend on \<bar\> if CONFIG_FOO is set, and will be invisible until \<bar\> is selected when CONFIG_FOO is set.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

Some typical config symbols for (conditional) dependencies are:

|                                   |                                                                                                                                                                                 |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TARGET\_\<foo\>                   | Target \<foo\> is selected                                                                                                                                                      |
| TARGET\_\<foo\>\_\<bar\>          | If the target \<foo\> has subtargets, subtarget \<foo\> is selected. If not, profile \<foo\> is selected. This is in addition to TARGET\_\<foo\>                                |
| TARGET\_\<foo\>\_\<bar\>\_\<baz\> | Target \<foo\> with subtarget \<bar\> and profile \<baz\> is selected.                                                                                                          |
| LINUX_3_X                         | Linux version used is 3.x.\*                                                                                                                                                    |
| LINUX_2_6_X                       | Linux version used is 2.6.x.\* (:1: only used for backfire and earlier)                                                                                                         |
| LINUX_2_4                         | Linux version is 2.4 (:!: only used in backfire and earlier, and only for target brcm-2.4)                                                                                      |
| USE_UCLIBC, USE_GLIBC, USE_EGLIBC | To (not) depend on a certain libc.                                                                                                                                              |
| BROKEN                            | Package doesn't build or work, and should only be visible if "Show broken targets/packages" is selected. Prevents the package from failing builds by accidentally selecting it. |
| IPV6                              | IPv6 support in packages is selected.                                                                                                                                           |

Note that the syntax above applies to the `DEPENDS` field only.

`PKG_BUILD_DEPENDS` does not use `+` or `@`, but otherwise uses the same syntax. You can write `FOO:bar` to build `bar` if `CONFIG_FOO` is defined (if you want to build bar if package FOO is selected, use `PACKAGE_FOO:bar`). You may use `!`, `||` and `&&` as explained above. `PKG_BUILD_DEPENDS` uses the name from the `PKG_NAME`, not the individual packages. For example, if you want to have openssl to be a build-dependency, you would write `PKG_BUILD_DEPENDS:=openssl`, whereas if your package depends and selects the openssl library, you'd have `DEPENDS:=+libopenssl`. Notice that there's no installable package named `openssl`: the library is `libopenssl`, the utility is `openssl-util`, but their `PKG_NAME` is `openssl`. If you need a host-built package, append `/host` to the `PKG_NAME`, e.g. `PKG_BUILD_DEPENDS:=openssl/host`. A package listed in `PKG_BUILD_DEPENDS` will be built even if it is not selected in `make menuconfig`.

`EXTRA_DEPENDS` does not accept the conditional or select dependency syntax. However, unlike `DEPENDS` and `PKG_BUILD_DEPENDS`, it is generated at package-build-time, so you may use Makefile functions to add them conditionally. For example, to get the equivalent of `DEPENDS:=@SOMESYMBOL:foo +PACKAGE_somepkg:bar`, you can write `EXTRA_DEPENDS:=$(if $(CONFIG_SOMESYMBOL),foo) $(if $(CONFIG_PACKAGE_somepkg),bar)`. :!: Note that neither `foo` or `bar` will be selected in menuconfig, or guaranteed to be built before your package, even if selected somewhere else. For this reason, it is seldom used in packages.

`EXTRA_DEPENDS` is more often used to depend on specific versions, by adding the desired version specification in parentheses, using \>=,\>,\<,\<=,=. Make sure you add the `PKG_RELEASE` number if you're using '=', such as `EXTRA_DEPENDS:=foo (=2.0.0-1)`: where foo's `PKG_VERSION` is 2.0.0, and `PKG_RELEASE` is 1.

## Configure a package source

Example:

``` make
CONFIGURE_ARGS += \
        --disable-native-affinity \
        --disable-unicode \
        --enable-hwloc

CONFIGURE_VARS += \
        ac_cv_file__proc_stat=yes \
        ac_cv_file__proc_meminfo=yes \
        ac_cv_func_malloc_0_nonnull=yes \
        ac_cv_func_realloc_0_nonnull=yes

```

To set variables (autoconfig internal ones or CPPFLAGS,CFLAGS, CXXFLAGS, LDFLAGS for example) or configure arguments. Setting configure arguments is common. Setting VARS is needed when the configure.ac autoconf source script does not work well on cross compilation or finding libraries.

:!: The article [packages.flags](/docs/guide-developer/packages.flags) contains more information and examples about overriding and setting these.

### Host tools required

In order to build your package, you may require some extra build tools or libraries that are not already in the standard OpenWrt toolchain. These must be built as part of the OpenWrt build process ie. you cannot rely on them being installed via the build system's package manager (or manually by the user or administrator). This is so that OpenWrt can be built reliably and repeatably on a wide variety of machines. These are referred to as *host tools* because they run on (or are compiled for) the host, not the target.

If your package requires host tools in order to be built for the target machine, these should go in `PKG_BUILD_DEPENDS` and will end with `/host`. For example, the `json-glib` package requires the [Meson build system](https://mesonbuild.com/) to generate build files, as well as Glib2 on the host, so it has:

``` make
PKG_BUILD_DEPENDS:=glib2/host meson/host
```

A package might itself provide host tools, and building or using *those* might require *other* host tools to be built first. These other tools go in `HOST_BUILD_DEPENDS`. For example, the host tool that the Meson package provides requires another build tool, [Ninja](https://ninja-build.org/), so it has this line:

``` make
HOST_BUILD_DEPENDS:=ninja/host
```

The makefile for a package that provides host tools will:

- Include `$(INCLUDE_DIR)/host-build.mk`. You can look at this makefile for the details of the host tool build process.
- Have sections similar to the `Build/...` sections of other packages, but they will start with `Host/`. For example, `Host/Configure`, `Host/Compile` and `Host/Install` are common.
- Call `$(eval $(call HostBuild))` at the end.

Some examples of packages that *provide* host tools (and their makefiles):

- [Meson](https://github.com/openwrt/packages/blob/master/devel/meson/Makefile)
- [Samba 4](https://github.com/openwrt/packages/blob/master/net/samba4/Makefile) - note that the Samba 4 *target* package actually depends on the Samba 4 *host* package provided in the same makefile
- [Go (golang)](https://github.com/openwrt/packages/blob/master/lang/golang/golang/Makefile) - this is a much more complex example, and useful if you're thinking of adding support for a new language in OpenWrt.

##### BUILD

If you want to build only the host tool to test or check a compilation error for host compilation, then you could also build only the host tool with the following command.

- Compile:
  make ./package/\<package_name\>/**host**/compile
- Clean:
  make ./package/\<package_name\>/**host**/clean
- Update:
  make ./package/\<package_name\>/**host**/update

The make arguments **QUILT=1** and **V=s** are also valid.

##### PATCHES

If you want to patch the host and target tool separately, then you have to add `HOST_PATCH_DIR:=./<directory>`. For example, add `HOST_PATCH_DIR:=./patches-host` to the `Makefile` so the host tool has its own patch directory. The target tool will still use the standard patch directory `./patches` in its package directory.

##### NOTES

All variables in your pre/post install/removal scripts should have double (\$\$) instead of a single (\$) string characters. This will inform "make" to not interpret the value as a variable, but rather just ignore the string and replace the double \$\$ by a single \$ -- [More Info](https://forum.openwrt.org/viewtopic.php?pid=85197#p85197)

After you've created your package Makefile, the new package will automatically show in the menu the next time you run "make menuconfig" and if selected will be built automatically the next time "make" is run.

DESCRIPTION is obsolete, use Package/PKG_NAME/description.

## Adding configuration options

If you would like to configure your package installation/compilation in the menuconfig you can do the following: Add MENU:=1 to your package definition like this:

``` make
define Package/mjpg-streamer
  SECTION:=multimedia
  CATEGORY:=Multimedia
  TITLE:=MJPG-streamer
  DEPENDS:=@!LINUX_2_4 +libpthread-stubs +jpeg
  URL:=http://mjpg-streamer.wiki.sourceforge.net/
  MENU:=1
endef
```

Create a config key in the Makefile:

``` make
define Package/mjpg-streamer/config
    source "$(SOURCE)/Config.in"
endef
```

Create a Config.in file directory where the Makefile is located with the content like this:

``` make
    # Mjpg-streamer configuration
    menu "Configuration"
        depends on PACKAGE_mjpg-streamer

    config MJPEG_STREAMER_AUTOSTART
        bool "Autostart enabled"
        default n

        menu "Input plugins"
            depends on PACKAGE_mjpg-streamer
            config MJPEG_STREAMER_INPUT_FILE
                bool "File input plugin"
                help
                    You can stream pictures from jpg files on the filesystem
                default n

            config MJPEG_STREAMER_INPUT_UVC
                bool "UVC input plugin"
                help
                    You can stream pictures from an Universal Video Class compatible webcamera
                default y

            config MJPEG_STREAMER_FPS
                depends MJPEG_STREAMER_INPUT_UVC
                int "Maximum FPS"
                default 15

            config MJPEG_STREAMER_PICT_HEIGHT
                depends MJPEG_STREAMER_INPUT_UVC
                int "Picture height"
                default 640

            config MJPEG_STREAMER_PICT_WIDTH
                depends MJPEG_STREAMER_INPUT_UVC
                int "Picture width"
                default 480

            config MJPEG_STREAMER_DEVICE
                depends MJPEG_STREAMER_INPUT_UVC
                string "Device"
                default /dev/video0

            config MJPEG_STREAMER_INPUT_GSPCA
                bool "GSPCA input plugin"
                help
                    You can stream pictures from a gspca supported webcamera Note this module is deprecated, use the UVVC plugin instead
                default n
        endmenu

        # ......

    endmenu
```

Above, you can see examples for various types of config parameters. Finally, you can check your configuration parameters in your Makefile in the following way (note that you can reference the parameter's value with its name prefixed with `CONFIG_`):

``` make
ifeq ($(CONFIG_MJPEG_STREAMER_INPUT_UVC),y)
    $(CP) $(PKG_BUILD_DIR)/input_uvc.so $(1)/usr/lib
endif
```

## Working on local application source

If you are still working on the application, itself, at the same time as you are working on the packaging, it can be very useful to have OpenWrt build your work in progress code, rather than a specific version+md5sum combination checked out of revision control, or downloaded from your final "release" location. There are a few ways of doing this.

### CONFIG_SRC_TREE_OVERRIDE

This is an option in menuconfig. See "Advanced configuration options (for developers)" -\> "Enable package source tree override"

This allows you to point to a local git tree. (And only git) Say your package is defined in my_cool_feed/awesome_app.

    ln -s /path/to/local/awesome_app_tree/.git feeds/my_cool_feed/awesome_app/git-src
    make package/awesome_app/{clean,compile} V=s

Benefits of this approach are that you don't need any special infrastructure in your package makefiles, they stay completely as they would be for a final build. The downside is that it only builds whatever is currently **committed** in HEAD of your local tree. (This could be a private testing branch, but everything you want to include in the package must be committed: uncommitted local changes will not be included in the build.) This will also use a **separate** directory for building and checking out the code. So, any built objects in your local git tree (for example, a build targeting a different architecture) will be left alone, but whichever **branch** is checked out in your tree determines where HEAD is.

### USE_SOURCE_DIR

As part of deprecating `package-version-override.mk` (below), a method to point directly to local source was introduced.

    make package/awesome_app/clean V=s
    make package/awesome_app/prepare USE_SOURCE_DIR=~/src/awesome_src V=s
    make package/awesome_app/clean V=s

(`V=s` is optional above)

This doesn't require any config change to enable rules, doesn't require that you have a local git tree, and doesn't require any files to be committed.

At least at present, however, this has the following problems:

- make clean doesn't clean the source link directory, but still seems to be removing a link
- make prepare needs to be run every time
- make package/awesome_app/{clean,compile} USE_SOURCE_DIR=~blah doesn't work
- Seems to have bad interactions with leaving USE_SOURCE_DIR set for other (dependent?) packages.

See <http://www.mail-archive.com/openwrt-devel@lists.openwrt.org/msg23122.html> for the original discussion of this new feature

:!: Since OpenWrt 19.07.5, `USE_SOURCE_DIR` only works with packages that have a valid `PKG_MIRROR_HASH`. For packages under development, hash checking can be disabled by setting `PKG_MIRROR_HASH=skip`. This allows using `USE_SOURCE_DIR` for packages pulling sources from a developer branch (e.g. having `PKG_SOURCE_VERSION:=branchname`) without updating `PKG_MIRROR_HASH` every time.

### (Deprecated) package-version-override.mk

:!: \*\* Don't use this anymore! \*\*

Support for this style of local source building was removed. This style required a permanent modification to your package makefile, and then entering a path via menuconfig to where the source was found. It was fairly easy to use, and didn't care whether your local source was in git or svn or visual source safe even, but it had the major downside that the "clean" target simply didn't work (as it simply removed a symlink for cleaning).

If you build a current OpenWrt tree, with packages that still attempt to use this style of local building, you **will** receive errors like so: ERROR: please fix package/feeds/feed_name/application_name/Makefile - see logs/package/feeds/feed_name/application_name/dump.txt for details

If you need/want to keep using this style, where it's available, make sure you include without failing if it was missing:

    -include $(INCLUDE_DIR)/package-version-override.mk

## Creating packages for kernel modules

A [kernel module](https://wiki.archlinux.org/title/Kernel_module) is an installable program which extends the behavior of the linux kernel. A kernel module gets loaded after the kernel itself, E.G. using `insmod`.

Many kernel programs are included in the Linux source distribution; typically the kernel build may be configured to, for each program,

- compile it into the kernel as a built-in,
- compile it as a loadable kernel module, or
- ignore it.

See ***FIX:Customizingthekerneloptions customizing the kernel options*** for including it in the kernel.

To include one of these programs as a loadable module, select the corresponding kernel option in the OpenWrt configuration (see [Build Configuration](/docs/guide-developer/toolchain/use-buildsystem#image_configuration)). If your favorite kernel module does not appear in the OpenWrt configuration menus, you must add a stanza to one of the files in the package/kernel/linux/modules directory. Here is an example extracted from .../modules/block.mk:

``` make
define KernelPackage/loop
  SUBMENU:=$(BLOCK_MENU)
  TITLE:=Loopback device support
  KCONFIG:= \
        CONFIG_BLK_DEV_LOOP \
        CONFIG_BLK_DEV_CRYPTOLOOP=n
  FILES:=$(LINUX_DIR)/drivers/block/loop.ko
  AUTOLOAD:=$(call AutoLoad,30,loop)
endef

define KernelPackage/loop/description
 Kernel module for loopback device support
endef

$(eval $(call KernelPackage,loop))
```

Changes to the \*.mk files are not automatically picked up by the build system. To force re-reading the metadata, either touch the kernel package Makefile using `touch package/kernel/linux/Makefile` (on older revisions `touch package/kernel/Makefile`) or to delete the `tmp/` directory of the buildroot.

You can also add kernel modules which are *not* part of the linux source distribution. In this case, a kernel module appears in the package/ directory, just as any other package does. The package/Makefile uses `KernelPackage/xxx` definitions in place of `Package/xxx`.

For example, here is `package/madwifi/Makefile`:

``` make
#
# Copyright (C) 2006 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#
# $Id$

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=madwifi
PKG_VERSION:=0.9.2
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.bz2
PKG_SOURCE_URL:=@SF/$(PKG_NAME)
PKG_HASH:=a75baacbe07085ddc5cb28e1fb43edbb
PKG_CAT:=bzcat

PKG_BUILD_DIR:=$(KERNEL_BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

RATE_CONTROL:=sample

ifeq ($(ARCH),mips)
  HAL_TARGET:=mips-be-elf
endif
ifeq ($(ARCH),mipsel)
  HAL_TARGET:=mips-le-elf
endif
ifeq ($(ARCH),i386)
  HAL_TARGET:=i386-elf
endif
ifeq ($(ARCH),armeb)
  HAL_TARGET:=xscale-be-elf
endif
ifeq ($(ARCH),powerpc)
  HAL_TARGET:=powerpc-be-elf
endif

BUS:=PCI
ifneq ($(CONFIG_LINUX_2_4_AR531X),)
  BUS:=AHB
endif
ifneq ($(CONFIG_LINUX_2_6_ARUBA),)
  BUS:=PCI AHB  # no suitable HAL for AHB yet.
endif

BUS_MODULES:=
ifeq ($(findstring AHB,$(BUS)),AHB)
  BUS_MODULES+=$(PKG_BUILD_DIR)/ath/ath_ahb.$(LINUX_KMOD_SUFFIX)
endif
ifeq ($(findstring PCI,$(BUS)),PCI)
  BUS_MODULES+=$(PKG_BUILD_DIR)/ath/ath_pci.$(LINUX_KMOD_SUFFIX)
endif

MADWIFI_AUTOLOAD:= \
    wlan \
    wlan_scan_ap \
    wlan_scan_sta \
    ath_hal \
    ath_rate_$(RATE_CONTROL) \
    wlan_acl \
    wlan_ccmp \
    wlan_tkip \
    wlan_wep \
    wlan_xauth

ifeq ($(findstring AHB,$(BUS)),AHB)
    MADWIFI_AUTOLOAD += ath_ahb
endif
ifeq ($(findstring PCI,$(BUS)),PCI)
    MADWIFI_AUTOLOAD += ath_pci
endif

define KernelPackage/madwifi
  SUBMENU:=Wireless Drivers
  DEFAULT:=y if LINUX_2_6_BRCM |  LINUX_2_6_ARUBA |  LINUX_2_4_AR531X |  LINUX_2_6_XSCALE, m if ALL
  TITLE:=Driver for Atheros wireless chipsets
  DESCRIPTION:=\
    This package contains a driver for Atheros 802.11a/b/g chipsets.
  URL:=http://madwifi.org/
  VERSION:=$(LINUX_VERSION)+$(PKG_VERSION)-$(BOARD)-$(PKG_RELEASE)
  FILES:= \
        $(PKG_BUILD_DIR)/ath/ath_hal.$(LINUX_KMOD_SUFFIX) \
        $(BUS_MODULES) \
        $(PKG_BUILD_DIR)/ath_rate/$(RATE_CONTROL)/ath_rate_$(RATE_CONTROL).$(LINUX_KMOD_SUFFIX) \
        $(PKG_BUILD_DIR)/net80211/wlan*.$(LINUX_KMOD_SUFFIX)
  AUTOLOAD:=$(call AutoLoad,50,$(MADWIFI_AUTOLOAD))
endef

MADWIFI_MAKEOPTS= -C $(PKG_BUILD_DIR) \
        PATH="$(TARGET_PATH)" \
        ARCH="$(LINUX_KARCH)" \
        CROSS_COMPILE="$(TARGET_CROSS)" \
        TARGET="$(HAL_TARGET)" \
        TOOLPREFIX="$(KERNEL_CROSS)" \
        TOOLPATH="$(KERNEL_CROSS)" \
        KERNELPATH="$(LINUX_DIR)" \
        LDOPTS=" " \
        ATH_RATE="ath_rate/$(RATE_CONTROL)" \
        DOMULTI=1

ifeq ($(findstring AHB,$(BUS)),AHB)
  define Build/Compile/ahb
    $(MAKE) $(MADWIFI_MAKEOPTS) BUS="AHB" all
  endef
endif

ifeq ($(findstring PCI,$(BUS)),PCI)
  define Build/Compile/pci
    $(MAKE) $(MADWIFI_MAKEOPTS) BUS="PCI" all
  endef
endif

define Build/Compile
    $(call Build/Compile/ahb)
    $(call Build/Compile/pci)
endef

define Build/InstallDev
    $(INSTALL_DIR) $(STAGING_DIR)/usr/include/madwifi
    $(CP) $(PKG_BUILD_DIR)/include $(STAGING_DIR)/usr/include/madwifi/
    $(INSTALL_DIR) $(STAGING_DIR)/usr/include/madwifi/net80211
    $(CP) $(PKG_BUILD_DIR)/net80211/*.h $(STAGING_DIR)/usr/include/madwifi/net80211/
endef

define KernelPackage/madwifi/install
    $(INSTALL_DIR) $(1)/etc/init.d
    $(INSTALL_DIR) $(1)/lib/modules/$(LINUX_VERSION)
    $(INSTALL_DIR) $(1)/usr/sbin
    $(INSTALL_BIN) ./files/madwifi.init $(1)/etc/init.d/madwifi
    $(CP) $(PKG_BUILD_DIR)/tools/{madwifi_multi,80211debug,80211stats,athchans,athctrl,athdebug,athkey,athstats,wlanconfig} $(1)/usr/sbin/
endef

$(eval $(call KernelPackage,madwifi))
```

------------------------------------------------------------------------

#### The use of MODPARAMS

If a module require some special param to be passed on Autoload, it's available MODPARAMS using the following syntax:

    MODPARAMS.module_ko:=example_param1=example_value example_param2=example_value2

For example here is `package/kernel/cryptodev-linux/Makefile`:

``` make
define KernelPackage/cryptodev
    SUBMENU:=Cryptographic API modules
    TITLE:=Driver for cryptographic acceleration
    URL:=http://cryptodev-linux.org/
    VERSION:=$(LINUX_VERSION)+$(PKG_VERSION)-$(BOARD)-$(PKG_RELEASE)
    DEPENDS:=+kmod-crypto-authenc +kmod-crypto-hash
    FILES:=$(PKG_BUILD_DIR)/cryptodev.$(LINUX_KMOD_SUFFIX)
    AUTOLOAD:=$(call AutoLoad,50,cryptodev)
    MODPARAMS.cryptodev:=cryptodev_verbosity=-1
endef
```

------------------------------------------------------------------------

#### Make a Kernel Module required for boot

Some modules may be required for the correct operation of the device. One example would be an ethernet driver required for the correct operation of the switch on the device.
To flag a Kernel Module this way it's needed to append `1` to `AUTOLOAD` at the end.
This cause the module file to get placed in /etc/modules-boot.d/ instead of /etc/modules.d/, modules-boot.d is processed by procd init before launching preinit and correctly works both in a normal boot and in a failsafe boot. All of this is with the assumption that the module is installed in the firmware and not with OPKG on a loaded system as **it needs to be present before /overlay is mounted**. (OPKG installed module are present only in after /overlay is mounted)

For example here is `phy-realtek` in `package/kernel/linux/modules/netdevices.mk`:

``` make
define KernelPackage/phy-realtek
   SUBMENU:=$(NETWORK_DEVICES_MENU)
   TITLE:=Realtek Ethernet PHY driver
   KCONFIG:=CONFIG_REALTEK_PHY
   DEPENDS:=+kmod-libphy
   FILES:=$(LINUX_DIR)/drivers/net/phy/realtek.ko
   AUTOLOAD:=$(call AutoLoad,18,realtek,1)
endef
```

## File installation macros

INSTALL_DIR, INSTALL_BIN, INSTALL_DATA are used for creating a directory, copying an executable, or copying a data file. +x is set on the target file for INSTALL_BIN, independent of its mode on the host.

From the big document:

Package/\<name\>/install:

A set of commands to copy files out of the compiled source and into the ipkg which is represented by the \$(1) directory. Note that there are currently 4 defined install macros:

    INSTALL_DIR
    install -d -m0755
    INSTALL_BIN
    install -m0755
    INSTALL_DATA
    install -m0644
    INSTALL_CONF
    install -m0600

## Packaging a service

If you want to install a service (something that should start/stop at boot time, that has a /etc/init.d/blah script), read the [Init Scripts](/docs/techref/initscripts) section of the Technical Reference and the [Procd init scripts](/docs/guide-developer/procd-init-scripts) section of the Developer's Guide. A key point is to make sure that the init.d script can be run on the host. At image build time, all init.d scripts found are run on the host, looking for the START=20/STOP=99 lines. This is what installs the symlinks in /etc/rc.d.

Packages have default postinst/prerm scripts that will run `/etc/init.d/foo enable` (creating the symlinks) or `/etc/init.d/foo disable` (removing the symlinks) when they are installed/removed by opkg.

Very basic example of a suitable init.d script. Please note that the newer style version does not work properly with interpreted executables (i.e. scripts). That is because start-stop-daemon is used by service_stop() in a way that it makes it confuse the script name with the interpreter name.

:!: **procd** style init is used in some init.d scripts since [this commit](commit>?p=openwrt/openwrt.git;a=commit;h=f87409440298121ae1fbd718a17267cc180438e4). See [procd-init-scripts](/docs/guide-developer/procd-init-scripts) for more details on that.

``` bash
#!/bin/sh /etc/rc.common
# "new(er)" style init script
# Look at /lib/functions/service.sh on a running system for explanations of what other SERVICE_
# options you can use, and when you might want them.

START=80
APP=mrelay
SERVICE_WRITE_PID=1
SERVICE_DAEMONIZE=1

start() {
        service_start /usr/bin/$APP
}

stop() {
        service_stop /usr/bin/$APP
}
```

``` bash
#!/bin/sh /etc/rc.common
###########################################
# NOTE - this is an old style init script #
###########################################

START=80
APP=mrelay
PID_FILE=/var/run/$APP.pid

start() {
        start-stop-daemon -S -x $APP -p $PID_FILE -m -b
}

stop() {
        start-stop-daemon -K -n $APP -p $PID_FILE -s TERM
        rm -rf $PID_FILE
}
```

See [Configuration in scripts](/docs/guide-developer/config-scripting) for details on how to access UCI configuration information from an init.d script, for instance to set command-line parameters or to generate a config file for your service.

## How To Submit Patches to OpenWrt

Packages are maintained in a separate repository to reduce maintenance overhead. The general guidelines for OpenWrt still apply, but see the README in the packages repository for latest information.

- <https://github.com/openwrt/packages>
- [https://dev.openwrt.org/wiki/SubmittingPatches](/submitting-patches)

See [the original announcement](https://web.archive.org/web/20170629071358/https://lists.openwrt.org/pipermail/openwrt-devel/2014-June/025810.html) of this change.
