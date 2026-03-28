---
title: Overriding Build Options
module: wiki
origin_type: wiki_page
token_count: 695
source_file: L1-raw/wiki/wiki_page-guide-developer-packages-flags.md
last_pipeline_run: '2026-03-28T11:59:43.422282+00:00'
source_url: https://openwrt.org/docs/guide-developer/packages.flags
language: text
ai_summary: The Overriding Build Options module in OpenWrt provides developers with the ability to customize build configurations for packages, particularly when cross-compiling. It details how to use various configuration variables such as **CONFIGURE_VARS** and **CONFIGURE_ARGS** to adjust settings during the autoconf process, as well as how to manage compiler flags through **TARGET_CFLAGS** and related variables. Additionally, it covers the use of **MAKE_VARS** for Makefile configurations and options for CMake and Scons. This flexibility allows developers to specify additional options and flags to meet specific package requirements.
ai_when_to_use: This module is particularly useful when you need to modify build options for packages that do not provide standard configuration flags or when cross-compiling for different architectures in OpenWrt.
ai_related_topics:
- CONFIGURE_VARS
- CONFIGURE_ARGS
- TARGET_CFLAGS
- MAKE_VARS
- CMAKE_OPTIONS
- SCONS_VARS
---
# Overriding Build Options

Some packages might require overriding certain build options because we are cross compiling.

The build system allows for several entries under **Advanced configuration options (for developers) \> Kernel extra CFLAGS** and **Advanced configuration options (for developers) \> Target Options** which will pass the defined flags onto the kernel and packages respectively.

## Autotools: Autoconf

**CONFIGURE_VARS**

1.  Override ac_cv\_\* variables that are normally set during autoconf ./configure phase.
2.  override pkgconfig configure vars

Example: Some packages check for features (header files) and do not offer -enable/-with or -disable/-without configure options (to be written into \_ARGS). Search for the configure variable in config.log and preset it in CONFIGURE_VARS.

          CONFIGURE_VARS += \
                  ac_cv_header_regex_h=no

**CONFIGURE_ARGS**

1.  Add options/test after ./configure

:!: Looking into config.log can help

## Compiler flags

Available compiler flags are handled in rules.mk

    TARGET_CFLAGS:=$(TARGET_OPTIMIZATION)$(if $(CONFIG_DEBUG), -g3) $(EXTRA_OPTIMIZATION)
    TARGET_CXXFLAGS = $(TARGET_CFLAGS)
    TARGET_ASFLAGS_DEFAULT = $(TARGET_CFLAGS)
    TARGET_ASFLAGS = $(TARGET_ASFLAGS_DEFAULT)
    TARGET_CPPFLAGS:=-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/include
    TARGET_LDFLAGS:=-L$(STAGING_DIR)/usr/lib -L$(STAGING_DIR)/lib

Typically you should only add additional options to compile flags.

    TARGET_CFLAGS+= -Wall

Example: Support multiple library versions via .../usr/lib/libname-v1/ or .../usr/lib/libname-v2/ and select them.

:!: BUG CXXFLAGS can contain wrong options because GCC/G++ accept different ones.

## Make

MAKE_VARS in include/package-defaults.mk

    MAKE_VARS = \
            CFLAGS="$(TARGET_CFLAGS) $(EXTRA_CFLAGS) $(TARGET_CPPFLAGS) $(EXTRA_CPPFLAGS)" \
            CXXFLAGS="$(TARGET_CXXFLAGS) $(EXTRA_CXXFLAGS) $(TARGET_CPPFLAGS) $(EXTRA_CPPFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) $(EXTRA_LDFLAGS)"

MAKE_FLAGS

    MAKE_FLAGS = \
            $(TARGET_CONFIGURE_OPTS) \
            CROSS="$(TARGET_CROSS)" \
            ARCH="$(ARCH)"

## CMake

include/cmake.mk

CMAKE_OPTIONS

CMAKE_HOST_OPTIONS

## Scons

SCONS_VARS are set in include/scons.mk

    SCONS_VARS = \
            CC="$(TARGET_CC_NOCACHE)" \
            CXX="$(TARGET_CXX_NOCACHE)" \
            CFLAGS="$(TARGET_CFLAGS) $(EXTRA_CFLAGS)" \
            CXXFLAGS="$(TARGET_CFLAGS) $(EXTRA_CFLAGS)" \
            CPPFLAGS="$(TARGET_CPPFLAGS) $(EXTRA_CPPFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) $(EXTRA_LDFLAGS)" \
            DESTDIR="$(PKG_INSTALL_DIR)"

SCONS_OPTIONS have no default set.

scons is only used by a few packages: [iotivity](https://github.com/openwrt/packages/blob/master/net/iotivity/Makefile) smartsnmpd
