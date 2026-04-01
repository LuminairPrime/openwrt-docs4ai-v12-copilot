---
title: Create Meson-based packages in OpenWrt
module: wiki
origin_type: wiki_page
token_count: 1314
source_file: L1-raw/wiki/wiki_page-guide-developer-creating-a-meson-based-package.md
last_pipeline_run: '2026-04-01T13:49:08.540826+00:00'
source_url: https://openwrt.org/docs/guide-developer/creating_a_meson_based_package
language: text
ai_summary: This tutorial outlines the process of creating and installing Meson-based packages in OpenWrt, providing a comprehensive guide for developers. It details the necessary steps, including including `$(INCLUDE_DIR)/meson.mk` in the `Makefile`, and using `MESON_ARGS` to pass configuration options. Additionally, it covers how to define environment variables with `MESON_VARS` and provides a simple example of a 'Hello World' application. By following these instructions, developers can efficiently build and customize their software packages within the OpenWrt environment.
ai_when_to_use: Use this guide when you need to create a custom package using the Meson build system in OpenWrt, especially for applications that require specific build configurations.
ai_related_topics:
- meson.mk
- MESON_ARGS
- MESON_VARS
- Makefile
---

> **Source:** [https://openwrt.org/docs/guide-developer/creating_a_meson_based_package](https://openwrt.org/docs/guide-developer/creating_a_meson_based_package)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-04-01

# Create Meson-based packages in OpenWrt

This tutorial provides a step-by-step guide to creating and installing meson-based packages in OpenWrt. We assume that the source code is local, but the process is the same for other cases such as Git, SVN, etc.

## General instructions in building packages

The `include` directory in OpenWrt contains information about the build system for different types of packages. Here, For example, `meson.mk` in the `include` directory provides useful insights:

``` bash
# To build your package using meson:
#
# include $(INCLUDE_DIR)/meson.mk
# MESON_ARGS+=-Dfoo -Dbar=baz
#
# To pass additional environment variables to meson:
#
# MESON_VARS+=FOO=bar
#
.
.
.
#
# same for Build/Compile and Build/Install
#
# Host packages are built in the same fashion, just use these vars instead:
#
# MESON_HOST_ARGS+=-Dfoo -Dbar=baz
# MESON_HOST_VARS+=FOO=bar
```

To create a Meson package for OpenWrt, we need to perform a few steps. Firstly, we should include `$(INCLUDE_DIR)/meson.mk` in the `Makefile`, which will enable us to use Meson build system within the OpenWRT environment. Secondly, we can pass Meson arguments to specify various configuration options by using the `MESON_ARGS+=<arg>` syntax. This is especially useful when we want to customize build settings, such as choosing a specific compiler or setting optimization flags. Additionally, we can also pass environmental variables to Meson by using `MESON_VARS`. This allows us to define environment-specific settings or pass additional information to the build system. By following these steps, we can create a robust and flexible Meson package for OpenWRT that meets our specific requirements.

## A simple Meson package

Meson is a build system that is designed to optimize and simplify the process of building software. By creating a Meson package, we can take advantage of this build system to automate the process of building and installing our software package. To begin with, we will be creating a single Meson package. This package will be located in the directory path `/media/workspace/packages/mesonsexmpl/`.

``` bash
mkdir /media/workspace/packages/mesonsexmpl/helloworld
cd /media/workspace/packages/mesonsexmpl/helloworld
```

Next, we will create the required files. These files are `main.c` source file and `meson.build` configuration file.

``` bash
touch main.c  meson.build
```

### main.c

To demonstrate a basic scenario, we will be populating the `main.c` file with a straightforward yet classic `"Hello World!"` message.

``` c
// main.c
#include <stdio.h>

int main(int argc, char** argv)
{
    printf(“Hello World\n”);
    return 0;
}
```

### meson.build

For the `meson.build` file, we use the simple build file provided by the meson tutorial:

``` cmake
# meson.build
project('helloworld', 'c')
executable('helloworld', 'main.c')
```

### Makefile

The `Makefile` plays a crucial role in our `helloworld` package, as it provides instructions for compiling and building the software. Without it, the program would not be able to run properly. To ensure that our `helloworld` package is functional, we have created a `Makefile` that outlines the necessary steps for building the program. You can find the `Makefile` below.

``` makefile
include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/meson.mk
include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/nls.mk
# Name, version and release number
# The name and version of your package are used to define the variable to point to the build directory of your package: $(PKG_BUILD_DIR)
PKG_NAME:=helloworld
PKG_VERSION:=1.0
PKG_RELEASE:=1

# Source settings (i.e. where to find the source codes)
# This is a custom variable, used below
SOURCE_DIR:=/media/workspace/packages/mesonsexmpl/helloworld/src

# Package definition; instructs on how and where our package will appear in the overall configuration menu ('make menuconfig')
define Package/helloworld
  SECTION:=examples
  CATEGORY:=Examples
  TITLE:=Hello, World!
endef

# Package description; a more verbose description on what our package does
define Package/helloworld/description
  A simple "Hello, world!" -application.
endef

define Package/helloworld/install
    $(INSTALL_DIR) $(1)/usr/bin/
    $(INSTALL_BIN)  $(PKG_BUILD_DIR)/openwrt-build/helloworld $(1)/usr/bin

endef

$(eval $(call BuildPackage,helloworld))
```

In order to incorporate our new package, we will need to make some changes to the `feeds.conf` file that is located at the root directory of OpenWrt source code . By making these modifications, we can ensure that our new package is successfully added and integrated into the system.

``` bash
src-link mesonpackages /media/workspace/packages/mesonsexmpl
```

### feeds.conf

Next, we need to update the package feed.

    ./scripts/feeds update mesonpackages
    ./scripts/feeds install -a -p  mesonpackages

Once we have updated the necessary feeds, the next step is to select the correct package for building. To do this, we must open the configuration menu by typing `make menuconfig` in the command line. From there, we should look for the `helloworld` package and select it to proceed with the build process.

To finish building the package, we need to execute the build command. Running this command will compile all the necessary files and create the final package that can be used for deployment or distribution.

``` bash
make package/helloworld/compile
```

If everything goes smoothly, the package that is built will be located in ''\<BIN_DIR\>/packages/\<target\>/mesonpackages/packages'. For instance:

    helloworld_1.0-1_arm_cortex-a7_neon-vfpv4.ipk
