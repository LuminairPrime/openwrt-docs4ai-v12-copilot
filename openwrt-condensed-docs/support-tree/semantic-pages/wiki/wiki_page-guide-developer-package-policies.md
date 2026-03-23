---
title: OpenWrt packages
module: wiki
origin_type: wiki_page
token_count: 5457
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-package-policies.md
last_pipeline_run: '2026-03-23T22:14:22.429226+00:00'
language: text
---
# OpenWrt packages

The OpenWrt system is maintained and distributed as a collection of *packages*.

Almost all pieces of software found in a typical OpenWrt firmware image are provided by such a package with a notable exception being the Linux kernel itself.

The term *OpenWrt package* may either refer to one of two things:

- an OpenWrt *source package* which essentially is a directory consisting of:
  - an *OpenWrt package Makefile* describing the acquisition, building and packaging procedures for a piece of software (required)
  - a supplemental directory with *OpenWrt package patches* which modify the acquired source code (optional)
  - other static files that go with the package, such as init script files, default configurations, scripts or other support files (optional)

- an OpenWrt *binary package*, which is a GNU tar compatible archive containing binary executable software artifacts and the accompanying *package control files* for installation on a running system, similar to the `.deb` or `.rpm` files used in other package managers

OpenWrt *binary packages* are almost exclusively produced from *source packages* by invoking either the *OpenWrt buildroot* or the *OpenWrt SDK* in order to translate the source package Makefile descriptions into executable binary artifacts tailored for a given target system.

Although it is possible to manually assemble binary packages by invoking tools such as *tar* and placing the appropriate control files in the correct directories, it is strongly discouraged to do so since such binary packages are usually not easily reproducible and verifiable.

Source packages are developed in multiple OpenWrt *package feeds* hosted in different locations and following different purposes. Each *package feed* is a collection of *source package* definitions residing within a publicly or privately reachable source code repository.

## Source packages

Source packages describe how a piece of software has to be *downloaded*, *patched*, *compiled* and *packaged* in order to form a binary software artifact suitable for use on a running target system. They also describe relations to other source packages required either at *build time* or at *run time*.

Each source package should have a *globally unique name* closely resembling the name of the software described by it. OpenWrt often follows the lead of other distributions when deciding about the naming of packages and sticks to the same naming conventions in many cases.

### Structure

A *source package* is a subdirectory within its corresponding *package feed* containing at least one Openwrt `Makefile` and optionally `src`, `files` or `patches` directories.

#### Makefile

An OpenWrt *source package Makefile* contains a series of header variable assignments, action recipes and one or multiple OpenWrt specific signature footer lines identifying it as OpenWrt specific package Makefile.

See [Creating packages](/docs/guide-developer/packages) for details on Makefile contents.

#### The files directory

Static files accompanying a source package, such as OpenWrt specific init scripts or configuration files, must be placed inside a directory called `files`, residing within the same subdirectory as the `Makefile`. There are no strict rules on how such static files are to be named and organized within the `files` directory but by convention, the extension `.conf` is used for OpenWrt UCI configration files and the extension `.init` is used to denote OpenWrt specific init scripts.

The actual placement and naming of the resources within the `files` directory on the target system is controlled by the source package Makefile and unrelated to the structure and naming within the `files` directory.

#### The patches directory

The `patches` directory must be placed in the same parent directory as the `Makefile` file and may only contain *patch files* used to modify the source code being packaged.

Patch files must be in *unified diff* format and carry the extension `.patch`. The file names must also carry a numerical prefix to denote the order in which the patch files must be applied. Patch file names should be concise and avoid characters other than ASCII alphanumerics and hyphens.

Suitable patch file names could look like:

- `000-patch-makefile.patch`
- `010-backport-frobnicate-crash-fix.patch`
- `999-add-local-hack-for-openwrt-compatibility.patch`

It is recommended to use [Quilt](/docs/guide-developer/toolchain/use-patches-with-buildsystem) to manage source package patch collections.

#### The src directory

Some packages do not actually fetch their program code from an external source but bundle the code to be compiled and packages directly within the package feed. This is usually done for packages which are specific to OpenWrt and do not exist outside of their respective package feed.

Sometimes the `src` directory may also be used to supply additional code to the compilation process, in addition to the program code fetched from external sources.

If present, the OpenWrt build system will automatically copy the contents of the `src` directory verbatim to the compilation scratch directory (*build directory*) of the package, retaining the structure and naming of the files.

### Feature Considerations

Many OpenWrt supported devices still have only a few megabytes of flash and RAM available which makes it important to shrink the packages as much as possible. Opt for the lowest common denominator whenever possible.

Some general considerations when packaging a new piece of software are:

- Do not ship man pages or documentation, a typical installation lacks both the infrastructure and the space to view and store man page databases
- Minimize external dependencies - try to avoid optional external dependencies whenever possible. An extreme example is `ICU` which weighs around 12MB and is an optional dependency for Unicode multi language support in various packages
- Modularize packages - if the software you're packaging supports and uses plugins then put those plugins into separate binary package declarations instead of lumping them all together along with the main program. This way you can externalize dependencies and move them into the plugin packages instead of having them in the main component, which makes the package usable on a wider range of targets because users can omit parts with large dependencies.
- Try to rely on standard facilities - instead of requiring extra programs to implement tasks like user context switching, use the `procd` facilities to run a service as a different user.

Often it is tempting to add various `menuconfig` configuration options to allow the customization of the package features by the users compiling their own variant of OpenWrt but it should be kept in mind that large parts of the userbase will use the package solely by installing binary archives from the OpenWrt repositories.

Binary packages in the official OpenWrt repositories are always built with the default settings of a package so a maintainer should ensure that the default feature selection represents a fair balance between resource requirements and most common user needs.

### Copyright statements

Historically, packages for OpenWrt used to contain a copyright notice at the top of the Makefile, stating something like:

    # Copyright (C) 2007-2010 OpenWrt.org
    This is free software, licensed under the GNU General Public License v2.
    See /[LICENSE](../openwrt-core/makefile_meta-category-utils.md) for more information.

Since contributors likely do not have a formal contract with OpenWrt to develop packages, they cannot disclaim their own copyrights and assign them to the project.

When adding new packages, please don't simply copy the statement from another package but add either your own in the form:

    # Copyright (C) 2016 Joe Random <joe@example.org>

or omit it entirely.

### Versioning

There are a number of Makefile variables influencing the visible version of the resulting packages. When packaging upstream release tarballs, the `PKG_VERSION` variable should be set to the version of the upstream software being packaged. For example, if the `openssl` package compiles the released `openssl-1.0.2q.tar.gz` archive, then `PKG_VERSION` variable should be set to the value `1.0.2q`.

When there are no upstream release tarballs available or when software is packaged straight from a source code repository, the `PKG_SOURCE_DATE` and `PKG_SOURCE_VERSION` variables should be used instead. The `PKG_SOURCE_DATE` value must correspond to the modification date in the format `YYYY-MM-DD` of the source repository revision being packaged and `PKG_SOURCE_VERSION` must be set to the corresponding revision identifier of the repository, e.g. the commit hash for Git or the revision number for SVN repositories. For example, if the `ubus` package clones from Git revision <https://git.openwrt.org/?p=project/ubus.git;a=commitdiff;h=221ce7e7ff1bd1a0c9995fa9d32f58e865f7207f>, then its Makefile should specify `PKG_SOURCE_DATE:=2018-10-06` and `PKG_SOURCE_VERSION:=221ce7e7ff1bd1a0c9995fa9d32f58e865f7207f`.

The build system will combine these variables into a common version identifier and truncate the revision identifier if needed. Given the values in the example, the resulting version identifier will be `2018-10-06-221ce7e7`. This is done to make repository revision identifiers comparable to each other since SCM systems like Git or Mercurial use SHA hashes to identify revisions which are no monotonically increasing numerical values.

#### Package Revisions

Source packages must specify a `PKG_RELEASE` value identifying the revision of the source package. In contrast to the `PKG_VERSION`, `PKG_SOURCE_DATE` and `PKG_SOURCE_VERSION` variables which are identifying the upstream version of the program code being packaged, the `PKG_RELEASE` variable denotes the revision of the package itself.

The package revision should start with the value `1` and must be increased whenever modifications are made to the package which might cause changes to the executables or other files contained within the resulting binary packages. When the package is updated to a newer `PKG_VERSION` or `PKG_SOURCE_VERSION`, the `PKG_RELEASE` must be reset back to `1`.

Some examples for dealing with the `PKG_RELEASE` are:

- Fixed a typo in the maintainer's mail address -\> `PKG_RELEASE` stays unchanged
- Added a `--disable-acl` to the configure arguments -\> `PKG_RELEASE` is incremented
- Updated `libfoo` from version `0.2.1` to `0.2.2` -\> `PKG_RELEASE` is reset to `1` and `PKG_VERSION` set to `0.2.2`

### Downloading

When declaring the source download method in the Makefile, direct tarball downloads via [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) or HTTPS are the preferred way to acquire package sources, Git or other SCM clones should be avoided, mainly to keep the locally cached source downloads reproducible.

If direct Git cloning is required (for example because there is no release tarballs available upstream) then Git via HTTPS is preferred over Git via [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) is preferred over Git via its native protocol. Many OpenWrt users are behind corporate firewalls which disallow Git native traffic (TCP 9418).

#### Mirror Sites

The use of mirror sites for tarball download locations is encouraged and helps to reduce the traffic load on upstream project sites. When choosing mirrors for a package, please try to ensure that the mirror is:

- officially endorsed by the upstream project (E.G. mentioned on their download page).
- well reachable by people from a wide range of different locations.
- using proper SSL certificates when using HTTPS.
- hosting the most current version of the software in question.

Multiple mirrors can be specified in a package Makefile by assigning a white-space separated list of URLs to the `PKG_SOURCE_URL` variable. It is a good convention to assign the upstream project site itself to the end of the mirror list. This provides a canonical fallback location in case a new version has not yet propagated to all mirrors and conveys the original download location to casual readers.

Try to limit the amount of mirror sites to 3 to 5 different locations, including the main download site.

### Building

The build recipes in a source package should adhere to the OpenWrt defaults as much as possible. This ensures that source package declarations remain compact and free of copy-pasted boilerplate code.

By default, the build system uses a set of standard `./configure` and `make` invocations to build packages in a refined manner. Most of these steps can be influenced through a number of variables to alter the way the actual commands are executed.

Please refer to [package-defaults.mk](https://git.openwrt.org/?p=openwrt/openwrt.git;a=blob;f=include/package-defaults.mk) to learn how the default recipes are implemented.

Whenever possible, try to avoid redefining the default macros but use the provided variables to encode functional differences.

Example for a bad redefinition:

    define Build/Compile
            (cd $(PKG_BUILD_DIR)/nonstandard/dir/; make)
    endef

Example for achieving the same using variable overrides:

    MAKE_PATH := nonstandard/dir/

Likewise, do not attempt to override `Build/Configure` but use `CONFIGURE_ARGS` to pass switches like `CONFIGURE_ARGS += --enable-acl` or `CONFIGURE_ARGS += --without-systemd` and `CONFIGURE_VARS` to pass environment variables to the configuration script, like `CONFIGURE_VARS += ac_cv_func_snprintf=yes`.

#### Hooks

In some cases it is possible to arrange things before e.g. the `./configure` script is invoked in order to touch files, remove things or echo values into stampfiles. In such cases, it is permissible to redefine the recipe in order to achieve the desired result. Use the default implementations of the macros to call the original behaviour after the custom work is done. Refer to the examples below for some common use cases.

##### Running custom commands after unpacking but before patching the sources:

    define Build/Prepare
      echo "1.2.3" > $(PKG_BUILD_DIR)/version.txt
      $(call Build/Prepare/Default)
    endef

##### Running custom commands after unpacking and patching the sources:

    define Build/Prepare
      $(call Build/Prepare/Default)
      rm -f $(PKG_BUILD_DIR)/m4/libtool.m4
      cp $(PKG_BUILD_DIR)/make/Makefile.linux $(PKG_BUILD_DIR)/Makefile
    endef

##### Running custom commands before invoking configure:

    define Build/Configure
      touch $(PKG_BUILD_DIR)/ChangeLog
      $(call Build/Configure/Default)
    endef

##### Running custom commands after executing make:

    define Build/Compile
      $(call Build/Compile/Default)
      cp $(PKG_BUILD_DIR)/src/libfoo.so.1.2 $(PKG_BUILD_DIR)/src/libfoo.so
    endef

#### Autotools

Many open source projects rely on GNU autoconf and automake as their build system which may lead to a number of problems in a cross compilation setting.

Usual problems revolve around:

- `configure` scripts attempting to call programs to test certain features which might fail if the called program has been built for another architecture
- Pregenerated `configure` scripts embedding faulty and possibly outdated versions of `libtool` causing runtime problems on the target system
- Macros in configure scripts probing host system details to configure the package for the target, like calling `uname` to figure out the kernel version or endianess
- Projects shipping convenience scripts like `autogen.`sh which make certain assumptions about the host system or try to call the improper version of utilities like `autopoint` or `autoconf,` leading to macro errors and version mismatches when executing the generated configure scripts and Makefiles

Due to the complex nature of the GNU autoconf/automake system there is no single set of solutions to a given problem but rather a general list of guidelines and best practices to adhere to.

- Never patch the generated / shipped `configure` script but fix the underlying `configure.ac` or `configure.in` files and rely on the `PKG_FIXUP:=autoreconf` facility to regenerate the config script. This also has the nice side-effect of updating the embedded `libtool` version and using a cross-compile-safe set of standard macros, replacing unsafe ones in many cases.
- Make `./configure` invocations as explicit as possible by forcibly disabling or enabling any feature which depends on the presence of an external library, e.g. `--disable-acl` to build a given package without `libacl` support on both systems having `libacl` in their staging directory and systems not providing this library. Failure to do so will result in errors like `Package example is missing dependencies for the following libraries: libfoo.so.1` on systems that happen to build `libfoo` before building example.
- Pre-seed `configure` tests that cannot be reliably determined in a cross-compile setting. Properly written autoconf test macros can be overridden by cache-variables in the form `ac_cv_somename=value` - use this facility to skip tests which would otherwise fail or result in host-system specific values. For example the `libpcap` package passes `ac_cv_linux_vers=$(LINUX_VERSION)` to prevent `./configure` from calling the host systems `uname` in order to figure out the kernel version. The names of the involved cache variables can be found in the `config.log` file within the package build directory or by inspecting the generated shell code of the `configure` program. Use the `CONFIGURE_VARS` variable to pass the cache variables down to the actual `./configure` invocation
- Never trust shipped `autogen.sh` and similar scripts, rather use `PKG_FIXUP:=autoreconf` to (re)generate the configure script and automake templates and encode additionally needed steps in the appropriate build recipes.

## Dependencies

A *source package* may depend on a number of other packages, either to satisfy compilation requirements or to enforce the presence of specific functionality, such as shared libraries or support programs at runtime on the target system.

There are two kinds of dependencies; *build dependencies*, specified by the `PKG_BUILD_DEPENDS` Makefile variable and *runtime dependencies*, declared in the `DEPENDS` variable of the corresponding `define Package/...` Makefile sections.

*Build dependencies* are resolved at package compilation time and instruct the build system to download, patch and compile each mentioned dependency before the source package itself is compiled. This is required when the compilation process of a package depends on resources such as header files from another package. *Build dependencies* are not transformed into *runtime dependencies* and should only be used when the resources of the packages being depended upon are solely required at compilation time. This usually is the case for header-only libraries such as the C++ Boost project or static `.a` library archives that result in no dynamic runtime requirements.

*Runtime dependencies*, on the other hand, specify the relation of *binary packages*, instructing the package manager to fetch and install the listed dependencies before installing the binary package itself. A *runtime dependency* automatically implies a *build dependency*, so if a `DEPENDS` variable within a `define Package/...` section of a given source package specifies the name of a `define Package/...` section of another source package, the build system will take care of compiling the other package before compiling the source package specifiying the runtime dependency.

Package dependencies, regardless of whether they're build-time or runtime ones, should only require packages within the same *package feed* or provided by the *base feed* located within the main OpenWrt `package/` directory.

Dependencies among packages in different, non-base feeds are strongly discouraged as it is not guaranteed that each build system has access to all feeds.

## Shared libraries

Packages providing shared libraries require additional care to ensure that software depending on these libraries remains functional and is not accidentally broken by incompatible updates, changed APIs, removed functionality and so on.

While the package dependency mechanisms will ensure that the build system compiles library packages before the program packages requiring them, they do not guarantee that such programs are getting rebuilt when the library package itself is updated.

Also, in the case of binary package repositories, installing a newer, incompatible version of library packages would break installed programs relying on this library unless an additional version constraint is applied to the dependency.

The OpenWrt build system introduced the concept of an `ABI_VERSION` to address the issue of program dependencies on specific versions of a shared library, requiring exactly the ABI the program was initially compiled and linked against. The `ABI_VERSION` value is supposed to reflect the `SONAME` of the library being packaged.

### SONAME

Most upstream libraries contain an [ELF SONAME](https://en.wikipedia.org/wiki/Soname) attribute denoting the canonical name of the library including a version suffix specifying the version of the exposed ABI. Changes breaking the exposed ABI usually result in a change to the `SONAME`.

When a program is linked against such a library, the linker will resolve the `SONAME` of the requested shared object and put it into the `DT_NEEDED` section of the resulting program executable. Upon starting the program, the dynamic linker on the target system will consult the `DT_NEEDED` section to find the required libraries within the standard library search path.

### ABI Version

Setting an `ABI_VERSION` variable on a library package definition will cause the build system to track the value of this variable and trigger recompilations in all packages depending on this library package whenever the value is incremented. This is useful to force re-linking of all programs after a library has been changed to an incompatible version.

The `ABI_VERSION` value is also appended to the binary package name and all dependencies mentioning the binary library package will be automatically expanded to contain the `ABI_VERSION` suffix. If for example a library package `libfoo` specifies `ABI_VERSION:=1.0`, the resulting binary package will be called `libfoo1.0` and when a package `bar` specifies `DEPENDS:=+libfoo`, the resulting runtime dependency will be `Depends: libfoo1.0`.

This ensures that incompatible updates to the `libfoo` library, denoted by an `ABI_VERSION` increase, will cause programs linked against it from then on to have a different runtime dependency, allowing the OpenWrt package manager to notice the change.

Example: when `libfoo` is updated to a new, incompatible version and its `SONAME` property changed from `libfoo.so.1.0` to `libfoo.so.1.1`, then `ABI_VERSION` should be increased from `1.0` to `1.1`, causing the resulting `libfoo` binary package to be called `libfoo1.1`. Source packages linking `libfoo` from then on, will have runtime dependencies on `libfoo1.1`.

When a shared library is packaged, the `ABI_VERSION` variable of the corresponding `define Package/lib...` section should be set to the `SONAME` of the `.so` library file contained within the binary package. The `SONAME` usually reflects the library's internal `ABI` version and is incremented whenever incompatible changes to the public APIs are made within the library, E.G. when changing a function call signature or when removing exported symbols.

The public [ABI tracker](https://abi-laboratory.pro/index.php?view=tracker) is useful to decide whether an `ABI_VERSION` change is required when updating an existing library package to a newer upstream version.

Some upstream library projects do not use a `SONAME` at all or do not properly version their libraries, in such cases, the `ABI_VERSION` must be set to a value in the form `YYYYMMDD`, reflecting the source code change date of the last incompatible change being made.

### Contents

In order to allow multiple versions of binary library packages to coexist on the same system, each library package should only contain shared object files specific to the `SONAME` version of the library getting packaged.

A typical upstream library `libbar` with version 1.2.3 and `SONAME` of `libbar.so.1` will usually provide these files after compilation:

    libbar.so       -> libbar.so.1.2.3 (symlink)
    libbar.so.1     -> libbar.so.1.2.3 (symlink)
    libbar.so.1.2.3      (shared library object)

The binary `libbar1` package should only contain `libbar.so.1` and `libbar.so.1.2.3` as the common `libbar.so` symlink would clash with a `libbar2` package providing version `2.0.0` of `libbar`.

Versionless symlinks are usually not needed for libraries using the `SONAME` attribute and are only used during the linking phase when compiling programs depending on the library.

#### NOTE

`$(INSTALL_DATA)` and `$(INSTALL_BIN)` will currently copy the file contents instead of the symlink itself, so prefer `$(CP)` when copying the library symlinks. Consider the example above, if you run

    $(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/lib/libbar.so.* $(1)/usr/lib/

it will result in two copies of the library in regular files:

    libbar.so.1               (regular file)
    libbar.so.1.2.3           (regular file)

Instead, use

    $(CP) $(PKG_INSTALL_DIR)/usr/lib/libbar.so.* $(1)/usr/lib/

and you'll get the intended result:

    libbar.so.1     -> libbar.so.1.2.3 (symlink)
    libbar.so.1.2.3                    (regular file)

While there has been a proposal to change `$(INSTALL_BIN)` behavior, `$(CP)` will continue to work.

### Development Files

Source packages defining binary packages that ship shared libraries should declare a `Build/InstallDev` recipe that copies all resources required to discover and link the shared libraries into the staging directory.

A typical `InstallDev` recipe usually copies all library symlinks (including the unversioned ones), header files and, in case they're provided, pkg-config (`*.pc`) files.
