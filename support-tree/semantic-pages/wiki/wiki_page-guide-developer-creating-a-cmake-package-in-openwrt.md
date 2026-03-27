---
title: Create a Cmake package in OpenWrt
module: wiki
origin_type: wiki_page
token_count: 631
source_file: L1-raw/wiki/wiki_page-guide-developer-creating-a-cmake-package-in-openwrt.md
last_pipeline_run: '2026-03-27T07:16:36.403470+00:00'
source_url: https://openwrt.org/docs/guide-developer/creating-a-cmake-package-in-openwrt
language: text
ai_summary: This document provides a guide for creating a CMake package in OpenWrt, highlighting the differences from the Meson package creation process. It includes a basic `CMakeLists.txt` example for a simple 'Hello, World' application and details the structure of the corresponding `Makefile`. Key sections cover how to pass CMake options and how to build the package using OpenWrt's build system. The guide concludes with instructions on enabling the package through the configuration menu and locating the built package files.
ai_when_to_use: Use this guide when you need to create a CMake-based package for OpenWrt, especially when transitioning from Meson-based packages.
ai_related_topics:
- CMakeLists.txt
- Makefile
- CMAKE_OPTIONS
- BuildPackage
---
# Create a Cmake package in OpenWrt

In the [Meson tutorial](/docs/guide-developer/creating_a_meson_based_package), we learned how to create a Meson package with a detailed guide. Since Cmake and Meson have similar roots, this tutorial will only focus on their differences.

## CMakeLists.txt

To begin, let's create a CMake project. The `main.c` file for this project will be the same as the one in the Meson tutorial, which includes a single `"Hello, World"` program. However, in order to use CMake, we need to include a `CMakeLists.txt` file. The most basic CMake file is presented here for simplicity.

``` cmake
cmake_minimum_required(VERSION 3.1...3.27)

project(
  hellocmake
  VERSION 1.0
  LANGUAGES C)

add_executable(hellocmake main.c)
install(TARGETS hellocmake DESTINATION /usr/bin)
```

## Makefile

The `Makefile` is very similar to other OpenWrt-based makefiles. The only difference is that it includes `cmake.mk` instead of `meson.mk`:

``` Makefile
include $(TOPDIR)/rules.mk

PKG_NAME:=hellocmake
PKG_VERSION:=0.1
PKG_RELEASE:=1

SOURCE_DIR:=/media/workspace/packages/cmakepackages/hellocmake
PKG_BUILD_DIR:=$(BUILD_DIR)/hellocmake-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/hellocmake
    CATEGORY:=custom
    TITLE:=Simple Cmake package
    #DEPENDS:=+libstdcpp +ixwebsocket +libatomic
endef

define Package/hellocmake/description
    hellocmake is a simple application to demonstrate OpenWrt build system with cmake packages
endef

define Package/hellocmake/install
    $(INSTALL_DIR) $(1)/usr/bin
    $(INSTALL_BIN) $(PKG_BUILD_DIR)/hellocmake $(1)/usr/bin/
endef

$(eval $(call BuildPackage,hellocmake))
```

## Passing Cmake options

In order to pass `Cmake` options, we can use the following syntax in the `Makefile`

``` Makefile
CMAKE_OPTIONS+= \
    -D<OPTION>bool=OFF
```

For example:

``` Makefile
CMAKE_OPTIONS+= \
    -DBUILD_TESTING:bool=OFF
```

## Build

To enable this package, open the configuration menu by typing `make menuconfig` in the command line. From there, go to `custom` → `hellocmake` and select the package.

If everything goes smoothly, the package that is built will be located in `<BIN_DIR>/packages/<target>/cmakepackages/`.

For instance:

``` bash
hellocmake_0.1-1_arm_cortex-a7_neon-vfpv4.ipk
```
