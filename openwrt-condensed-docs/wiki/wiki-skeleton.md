# wiki (Skeleton Semantic Map)

> **Contains:** Headers and function signatures for wiki.
> **Generated:** 2026-03-20T01:28:16.926497+00:00

---

> **Summary:** The 21.02 release of OpenWrt introduces significant cosmetic changes, particularly in the naming conventions for devices and targets. This update aims to standardize device/image names using a vendor_model-variant scheme, enhancing consistency across various components such as Makefiles and DTS files. Key changes include the renaming of targets like ar71xx to ath79 and the systematic application of compatible names for board identification. Developers must adapt their scripts and configurations to reflect these new naming conventions to ensure compatibility with the updated system.
> **Use Case:** This module is essential for developers maintaining or adapting OpenWrt builds, especially those transitioning from older versions like 19.07 to 21.02. It is particularly relevant when updating device configurations and scripts to align with the new naming standards.
# 21.02: Major cosmetic changes
## Device/target renames



### arc770
### archs38
### ath79/ar71xx


### bcm27xx/brcm2708
### bcm47xx/brcm47xx
### bcm63xx/brcm63xx


### imx6
### layerscape
### mediatek
### mpc85xx
### octeon
### ramips
### samsung
### sunxi
## DEVICE_TITLE split and tidy-up
## Label MAC address
## Support of Ed25519 SSH keys

> **Summary:** The 'Adding new device support' module provides a comprehensive guide for developers looking to add support for new devices within the OpenWrt ecosystem. It outlines a general approach that includes listing device chips, ensuring access to the bootloader, and verifying hardware components such as flash partitioning and GPIOs. The document also details specific methods for testing GPIOs for LEDs and buttons, including example scripts for automation. Developers are encouraged to refer to related resources for device support policies and platform addition guidelines.
> **Use Case:** Use this module when you need to add support for a new device that is based on an already supported platform in OpenWrt.
# Adding new device support
## General Approach
## GPIOs
### GPIO LEDs
#!/bin/sh
### GPIO buttons
#!/bin/sh
### KSEG1ADDR() and accessing NOR flash
## Examples
### Brcm63xx Platform


### Ramips Platform
## Tips

> **Summary:** The 'Adding new platform support' module provides guidance for developers looking to add new platform support to OpenWrt. It emphasizes the importance of Linux in embedded devices and outlines the need for open-source firmware to enhance functionality and security. The document includes methods for verifying if a device runs Linux, particularly through OS fingerprinting and port scanning using tools like *nmap*. Specific command examples illustrate how to gather information about the device's operating system and running services.
> **Use Case:** This module is useful when you want to extend OpenWrt support to new hardware platforms or verify the Linux compatibility of existing devices. It is particularly relevant for developers aiming to create custom firmware for routers and other embedded devices.
# Adding new platform support
## Which Operating System does this device run?
### Operating System fingerprinting and port scanning
### Wireless Communications Fingerprinting
### Web server security exploits
### Native Telnet/SSH access
### Analyzing a binary firmware image
### Amount of flash memory
### Plugging a serial port
## Finding and using the manufacturer SDK
### GPL violations
### Using the SDK
### Creating a hardware specific kernel patch
### Using the device bootloader

### Making binary drivers work
### Understanding the firmware format
### Writing a flash map driver

> **Summary:** The 'Adding a new device' module provides a comprehensive guide for developers looking to integrate new hardware into OpenWrt. It emphasizes the importance of examining recent commits and using local grep searches to identify necessary files for device integration. Key directories and their functions are outlined, including base-files for firmware integration, device tree source files, and image configuration. Additionally, it covers the process of making the new device visible in the make menuconfig and the organization of kernel patches.
> **Use Case:** This module is useful when you need to add support for a new device in OpenWrt, particularly for custom or unsupported hardware.
# Adding a new device
## Learn by example
### Search by grep locally
### Search by Git commit
## Important files
### /target/linux/\<arch_name\>/base-files/etc/…
### /target/linux/\<arch_name\>/base-files/lib/…
### /target/linux/\<arch_name\>/base-files/sbin
### /target/linux/\<arch_name\>/dts/
### /target/linux/\<arch_name\>/image/
### /target/linux/\<arch_name\>/\<board_name\>/
### /target/linux/\<arch_name\>/modules.mk
### Making new device appear in make menuconfig
## Patches
## Testing images
## Tips and tricks
### Getting a shell on the target device
#### Abuse Unsanitized User Input
##### Starting telnetd
##### Obtain the password hash using HTTP or use `sed` to delete/change the default password if telnet login is required
#### Downgrade to older firmware
#### Downgrade by Serial access
#### HTTP Server Vulnerability
#### Netgear
### Collecting relevant data
### Getting collected data from a device
#### Use SCP to download
##### Receiver
#### HTTP by `httpd` and `busybox mount`
##### Sender
##### Receiver
#### FTP by `busybox ftpput`
##### Receiver
##### Sender
#### netcat by `busybox nc`
##### Receiver
##### Sender
#### TFTP by `busybox tftp`
##### Receiver
##### Sender
#### Use Curl to upload
#### Copy from terminal

> **Summary:** This module provides a comprehensive guide for building an OpenWrt image with support for 3G/4G connectivity and USB tethering. It outlines the necessary steps to prepare the build environment, including cloning the OpenWrt git repository and synchronizing package feeds. The configuration process involves selecting the target architecture and profile, as well as enabling specific kernel modules for USB networking support, such as kmod-usb-net for USB networking interfaces and kmod-usb-serial for legacy 3G dongles. Detailed instructions are provided for selecting various kernel modules to ensure compatibility with different devices and connection types.
> **Use Case:** Use this guide when you need to create a custom OpenWrt image that supports 3G/4G modems and USB tethering for network connectivity.
# Building image with support for 3g/4g and usb tethering
## Preparing build environment
## Configuring packages
### Selecting target architecture and profile
### Selecting kernel modules for usb networking support.
### Additional packages required for 3g functionality
#### ppp, chat, and uqmi
#### mbim
#### comgt and usb-modeswitch
#### minicom, picocom, and screen
### Web Interface Support

> **Summary:** This document provides a guide for building MPD-full with PulseAudio on OpenWrt. It outlines the necessary modifications to the Makefile, including adding dependencies for PulseAudio and adjusting compilation flags. Key changes include adding `+pulseaudio-daemon` to DEPENDS and enabling PulseAudio in the configuration. Additionally, it specifies the need to modify the EXTRA_LDFLAGS to include the correct library path for PulseAudio.
> **Use Case:** Use this guide when you need to build MPD-full with PulseAudio support on OpenWrt, particularly when customizing audio playback capabilities.
# Building MPD-full with PulseAudio
### 18.06.02
#### The MPD Makefile

> **Summary:** The MPD-full building from source guide provides instructions for enabling the full version of the Music Player Daemon (MPD) in OpenWrt by modifying the Makefile. Users must edit the MPD Makefile located in the OpenWrt feeds directory to change the dependency from `+libffmpeg` to `+libffmpeg-full`. After saving the changes, the full MPD version will be available in the `make menuconfig` interface alongside the mini version. This process is particularly relevant for users building from source who want access to the full feature set of MPD.
> **Use Case:** This guide is useful when you need to build the full version of MPD from source in OpenWrt, particularly if you require additional audio features not available in the mini version.
# MPD-full building from source
### Barrier Breaker and Chaos Calmer

> **Summary:** This document provides a comprehensive guide on building OpenWrt for the Netgear WNDR3700, detailing the steps required to create a functional firmware image from scratch. It includes prerequisites for setting up the OpenWrt Buildroot, instructions for pulling the latest code, and configuration steps necessary for a successful build. Additionally, it covers how to unbrick the device without a serial cable and offers optional guidance for creating one. The instructions are based on the trunk revision 19064 and emphasize the importance of specific configuration settings for network access.
> **Use Case:** Use this guide when you need to build a custom OpenWrt image for the Netgear WNDR3700, especially if you are facing issues with the default firmware or need specific features not available in the standard release.
# Building OpenWrt for Netgear WNDR3700
## Prerequisites
## Configuration
## Installation

> **Summary:** This document provides guidance on building OpenWrt kernels for use with the Debian operating system, highlighting key compatibility issues and configuration settings. It discusses the implications of using soft-FPU instructions in OpenWrt versus hard FPU instructions in Debian, and how to enable FPU emulation in the kernel. Additionally, it covers the requirements for udev and SELinux support, as well as the potential discrepancies in kernel configuration options. Finally, it suggests enabling IKConfig to save the kernel configuration within the kernel itself for easier reference.
> **Use Case:** Use this guide when you need to compile an OpenWrt kernel that is compatible with Debian, especially when addressing issues related to FPU instructions, udev, and SELinux support.
# Building OpenWrt Kernel for Debian System
## Floating Point Unit (MIPS)
## udev
## SELinux
## IKConfig

> **Summary:** This guide provides detailed instructions for setting up a build virtual machine (VM) for OpenWrt using VirtualBox on a Debian OS. It outlines the necessary prerequisites, including a 64-bit OS and at least 8 GB of free disk space. The steps include downloading VirtualBox, obtaining a Debian image, configuring the VM settings, and performing initial Debian setup tasks such as updating the system and installing required packages. Additionally, it covers configuring shared folders and enabling sudo access for the user, ensuring a functional development environment for OpenWrt.
> **Use Case:** Use this guide when you need to create a development environment for building OpenWrt on a Debian-based VM. It is particularly useful for developers who prefer working in a virtualized setup.
# Setting up a build VM in VirtualBox
## Instructions
### 1. Get VirtualBox
### 2. Get a Debian image
### 3. Install the virtual machine
### 4. Initial Debian setup

> **Summary:** The Configuration in scripts module provides a set of shell procedures for interacting with UCI (Unified Configuration Interface) to read and process configuration files within shell scripts in OpenWrt. It allows developers to load configuration files using `config_load name`, define callbacks for handling sections and options through `config_cb`, `option_cb`, and `list_cb`, and reset callbacks with `reset_cb`. This functionality is particularly useful for writing startup scripts located in `/etc/init.d/` that require configuration management.
> **Use Case:** Use this module when you need to read and manipulate UCI configuration files within shell scripts, especially for startup scripts in OpenWrt.
# Configuration in scripts
## Loading
#!/bin/sh /etc/rc.common
## Callbacks
### `config_cb` callback
### `option_cb` callback
### `list_cb` callback
## Iterating (config_foreach)
## Reading options (config_get)
#...
# read the value of "option ifname" into the "iface" variable
# $config contains the ID of the current section
#...
## Setting options (config_set)
# set the value of "option auto" to "0"
# $config contains the ID of the current section

## Direct access
## Reading lists
# handle list items in a callback
# $config contains the ID of the section
## Reading booleans
## Should I use callbacks or explicit access to options?
### Use case and example for callbacks
### Use case and example for direct access
### Mixing the two styles

> **Summary:** This document provides a guide for creating a CMake package in OpenWrt, highlighting the differences from the Meson package creation process. It includes a basic `CMakeLists.txt` example for a simple 'Hello, World' application and details the structure of the corresponding `Makefile`. Key sections cover how to pass CMake options and how to build the package using OpenWrt's build system. The guide concludes with instructions on enabling the package through the configuration menu and locating the built package files.
> **Use Case:** Use this guide when you need to create a CMake-based package for OpenWrt, especially when transitioning from Meson-based packages.
# Create a Cmake package in OpenWrt
## CMakeLists.txt
## Makefile
## Passing Cmake options
## Build

> **Summary:** This tutorial outlines the process of creating and installing Meson-based packages in OpenWrt, providing a comprehensive guide for developers. It details the necessary steps, including including `$(INCLUDE_DIR)/meson.mk` in the `Makefile`, and using `MESON_ARGS` to pass configuration options. Additionally, it covers how to define environment variables with `MESON_VARS` and provides a simple example of a 'Hello World' application. By following these instructions, developers can efficiently build and customize their software packages within the OpenWrt environment.
> **Use Case:** Use this guide when you need to create a custom package using the Meson build system in OpenWrt, especially for applications that require specific build configurations.
# Create Meson-based packages in OpenWrt
## General instructions in building packages
# To build your package using meson:
#
# include $(INCLUDE_DIR)/meson.mk
# MESON_ARGS+=-Dfoo -Dbar=baz
#
# To pass additional environment variables to meson:
#
# MESON_VARS+=FOO=bar
#
#
# same for Build/Compile and Build/Install
#
# Host packages are built in the same fashion, just use these vars instead:
#
# MESON_HOST_ARGS+=-Dfoo -Dbar=baz
# MESON_HOST_VARS+=FOO=bar
## A simple Meson package
### main.c
#include <stdio.h>
### meson.build
# meson.build
### Makefile
# Name, version and release number
# The name and version of your package are used to define the variable to point to the build directory of your package: $(PKG_BUILD_DIR)
# Source settings (i.e. where to find the source codes)
# This is a custom variable, used below
# Package definition; instructs on how and where our package will appear in the overall configuration menu ('make menuconfig')
# Package description; a more verbose description on what our package does
### feeds.conf

> **Summary:** The Debugging module in OpenWrt provides essential tools and techniques for diagnosing issues related to hardware, kernel, and driver development. It covers methods such as adding a serial console, utilizing JTAG for debugging, and employing GDB for code analysis. Additionally, it offers guidance on capturing wireless management traffic using tools like tcpdump and iwcap, as well as adjusting the logging level for hostapd to facilitate troubleshooting. These resources are crucial for developers working on embedded network devices to effectively identify and resolve issues.
> **Use Case:** Use this module when developing or debugging drivers and kernel code on OpenWrt devices, especially when dealing with wireless connectivity issues.
# Debugging
## Serial Port
## JTAG
## GDB
## perf/oprofile cpu profiling
## Wireless
### Capture Management Traffic
### Logging hostapd behaviour
## Add and modify compiler debug flags

> **Summary:** The Device Tree Usage in OpenWrt (DTS) module outlines the transition from older 'mach' files to Device Tree (DT) files, which include .dts, .dtsi, and .dtb formats. It provides guidelines for defining software partitions in DTS targets, emphasizing the importance of proper partition naming and read-only settings for critical components like boot loader binaries and firmware. The document also highlights the need for specific 'compatible' labels to ensure correct partition parsing by the OpenWrt kernel, thereby avoiding the use of certain configuration options. Additionally, it includes references to external resources for further understanding of Device Tree conventions.
> **Use Case:** This module is essential when developing or modifying device support in OpenWrt, particularly for defining firmware partitions in DTS files. It is useful for developers working on architecture-specific or board-specific device trees.
# Device Tree Usage in OpenWrt (DTS)
## References
## General
## Defining software partitions in all DTS targets

> **Summary:** The 'Using Dependencies' module provides guidance on how to define package dependencies in OpenWrt Makefiles. It explains various dependency types, such as mandatory dependencies, conditional selections, and negations, using examples like 'DEPENDS:=+libpcap' and 'DEPENDS:=@USB_SUPPORT'. The module also highlights the importance of correctly structuring dependencies to avoid issues when packages are installed on a running system. Additionally, it mentions special notes on selecting packages outside the usual 'DEPENDS' definition.
> **Use Case:** This module is useful when developing OpenWrt packages that require specific dependencies to be managed correctly. It helps ensure that all necessary packages are available during the build process.
# Using Dependencies
## Topic
## Dependency types
### Special Notes
## Caveats
### Using boolean operators
## Bugs

> **Summary:** The Device support policies / best practices document outlines guidelines for developers submitting device support patches in OpenWrt. It emphasizes the importance of clear commit messages, including specifications and flashing instructions, and provides recommendations for structuring DTS files, such as using consistent naming conventions and proper licensing. Additional tips are offered for enhancing readability and organizing device properties, particularly regarding LED configurations. Following these guidelines can improve the submission experience for both developers and reviewers.
> **Use Case:** Use this document when preparing to submit device support patches to ensure compliance with OpenWrt's best practices and to facilitate a smoother review process.
# Device support policies / best practices
## Commit message
## DTS files
### License
### dts-v1
### Model/device name
### General style
### LEDs
## base-files
### No wildcards
## MAC addresses
### Documentation
### Data source
## Backports
### Device support backports

> **Summary:** The Drivers module in OpenWrt provides an overview of how drivers operate within the Linux kernel, emphasizing that they can be compiled into the kernel or loaded as modules. It highlights the different types of driver source code, including Open Source, partially Open Source, and Closed Source (Binary Blobs). The document also notes that all kernel module package filenames in OpenWrt begin with 'kmod-' and that the modprobe command may not be available, recommending the use of insmod instead. Additionally, it suggests various resources for further learning and contacting developers.
> **Use Case:** Use this module when developing or managing drivers in OpenWrt, especially when dealing with kernel modules and understanding driver source code types.
# Drivers

## Learning more

> **Summary:** The 'embedding-files-in-image' module describes a method for embedding custom files into OpenWrt images using buildroot features. Although this functionality was removed in April 2017, it previously allowed users to create overlay files that could modify package installations without altering source code. Users could create a Makefile fragment in the overlay directory to append custom installation commands to existing package recipes, such as adding a custom banner or inittab to the 'base-files' package. The documentation provides an example of how to structure the overlay and the necessary Makefile commands for this process.
> **Use Case:** This method was useful for developers needing to customize package installations without modifying the original package source. It is relevant for historical context and understanding past customization techniques in OpenWrt.
# embedding-files-in-image

> **Summary:** The External Toolchain module allows developers to use an external toolchain to reduce build time when compiling OpenWrt from a cleaned-up source tree. This is particularly beneficial when integrating with automated build systems like Hudson or Tinderbox. To utilize this feature, developers must first build the toolchain by selecting 'Package the OpenWrt-based Toolchain' in the `make menuconfig` interface or by downloading a precompiled toolchain from the OpenWrt download page. After setting up the toolchain, developers can configure their buildroot and compile their firmware using standard OpenWrt build commands.
> **Use Case:** Use this module when you need to speed up the build process of OpenWrt, especially in automated environments.
# External Toolchain
## Use OpenWrt as External Toolchain
### Step 1: Build Toolchain
### Step 2: Build Firmware

> **Summary:** OpenWrt Feeds are collections of packages that can be sourced from various locations, including remote servers and version control systems. They are essential for managing additional package build recipes in OpenWrt Buildroot, allowing for customization through a feed configuration file. The configuration is typically done in the `feeds.conf` or `feeds.conf.default` files, where each feed is defined by its method, name, and source. Supported feed methods include `src-git`, `src-bzr`, `src-hg`, and others, enabling diverse ways to retrieve package data.
> **Use Case:** Use OpenWrt Feeds when you need to manage and customize package sources for building OpenWrt images. This is particularly useful for integrating additional software or maintaining custom packages.
# OpenWrt Feeds
## Feed Configuration
#src-git targets https://github.com/openwrt/targets.git
#src-git oldpackages http://git.openwrt.org/packages.git
#src-link custom /usr/src/openwrt/custom-feed
## Working with Feeds
### Feed Commands
#### Clean
#### Install
#### List
#### Search
#### Uninstall
#### Update
## Custom Feeds
### Creating the package directory
#### Adding your package to an existing feed
#### Adding your package to your own feed
### Using the feed
## Explanations
### Documentation
## Links

> **Summary:** This document outlines common mistakes that developers make when submitting Pull Requests (PRs) to OpenWrt, aiming to help them avoid delays in the review process. Key points include the necessity of a commit message, the importance of using a real name and email in the Signed-off-by line, and the distinction between a PR and its commits. Developers are also advised to respond to reviewer questions, avoid multi-posting PRs, and use the checkpatch.pl script for code quality checks.
> **Use Case:** Refer to this guide when preparing a PR for OpenWrt to ensure a smooth review process and to avoid common pitfalls that can lead to delays.
# Frequent PR mistakes or "How to prevent my PR from getting delayed for sure"
## 1. Add a commit message
## 2. Add a Signed-off-by with your real name
## 3. Do not multi-post or re-post PRs
## 4. Know the difference between the PR (Pull Request) and the commit
## 5. Answer questions
## 6. Do not resolve comment that are not resolved
## 7. Use checkpatch.pl
## 8. Address all issues

> **Summary:** The GNU Debugger (GDB) guide provides instructions for using GDB on OpenWrt, focusing on compiling tools and adding debugging capabilities to packages. Users can enable GDB and gdbserver in the menuconfig and add CFLAGS to package Makefiles to include debugging information. The guide also outlines how to start gdbserver on the target device and connect to it from the host for debugging sessions. Key commands for setting breakpoints and running programs within GDB are also included.
> **Use Case:** This guide is useful when developers need to debug applications running on OpenWrt devices. It is particularly applicable when recompiling packages with debugging information to troubleshoot issues.
# GNU Debugger
## Compiling Tools
## Add debugging to a package
## Starting GNU Debugger

> **Summary:** The 'Hardware Hacking First Steps' module provides guidance for users looking to install OpenWrt on unsupported routers. It outlines essential steps such as gaining access to the device via Unix shell, bootloader console, or JTAG port, and emphasizes the importance of gathering hardware information to identify compatible drivers. Users are encouraged to research available GNU/Linux drivers and learn programming languages like C for further development. The module also references various resources for deeper understanding and assistance in hardware hacking.
> **Use Case:** This module is useful when attempting to install OpenWrt on a router that is not officially supported, guiding users through the initial steps of hardware hacking.
# Hardware Hacking First Steps
## Gain Access

## Gather Information about Hardware
## Gather Information about Software
## Gather Information about Flash Layout
### Overall Flash Layout

### Precise Flash Layout
## Software Development
### Add Device
### Add Platform
## Software Development

> **Summary:** The Image Builder frontends module provides a collection of software tools designed to simplify and automate the generation of OpenWrt images. It includes various frontends such as the OpenWrt Firmware Selector for locating images, Chef Online Imagebuilder for customizing images via an API, and Gluon for creating firmware for wireless mesh nodes. Additionally, it features tools like Temba for generating custom firmware files and openwrt-tools for image generation using YAML templates. These tools cater to different user needs, from simple image downloads to complex custom firmware builds.
> **Use Case:** Use this module when you need to generate or customize OpenWrt firmware images without setting up a full build environment. It is particularly useful for community networks or users looking to automate the image creation process.
# Image Builder frontends
### OpenWrt Firmware Selector
### Chef Online Imagebuilder / Attended Sysupgrade(asu)
## Gluon
## Freifunk Berlin firmware
## Temba (TEMplate BAsed firmware)
## imagebuilder.sh
## openwrt-tools
## openwrt-auto-extroot
## lime-sdk cooker
## openwrt-linksys8450-ubi-installer
## openwrt-metabuilder
## openwrt_autobuild
## Mesh testbed generator
## Meshkit

> **Summary:** The `jshn` module is a JSON parsing and generation library designed for use in shell scripts within OpenWrt. It provides functions to initialize JSON structures, add various data types (like integers, strings, booleans, arrays, and objects), and parse JSON data from variables or files. Key functions include `json_init`, `json_add_int`, `json_load`, and `json_get_var`, which facilitate the creation and manipulation of JSON data in shell scripts. This library is particularly useful for developers needing to handle JSON in environments lacking native JSON support.
> **Use Case:** Use `jshn` when you need to parse or generate JSON data in OpenWrt shell scripts, especially when working with APIs or configuration files that utilize JSON format.
# jshn: a JSON parsing and generation library in for shell scripts
#!/bin/sh
# source jshn shell library
# generating json data
# the MSG_JSON var now contains: { "code": 0, "msg": "Hello, world!", "test": { "testdata": 1 } }
# parsing json data from the MSG_JSON variable
# load the "code" field into corresponding code var, and the "msg" field into the msg var
#!/bin/sh
# source jshn shell library
# initialize JSON output structure
# add a boolean field
# add an integer field
# add a string, take care of escaping
# add an array with three integers
# add an object (dictionary)
# build JSON object and print to stdout
# will output something like this:
# { "foo": false, "code": 123, "result": "Some complex string\\n with newlines\\n and even command output: Fri Jul 13 07:11:39 CEST 2018", "alist": [ 1, 2, 3 ], "adict": { "foo": "bar", "bar": "baz" } }
### More complicated examples
#### Parse file example
#!/bin/sh
## json_get_var <local_var> <json_var>
#### Parse arrays example
#!/bin/sh
#### Parse list of objects
#!/bin/sh
# download prices JSON via wget in quiet mode with output to stdout that will be saved to a variable PRICES_JSON
# check exit code: if any error then exit
# iterate over data inside "price" array until elements are objects
## json_for_each_item
#!/bin/sh
## json_get_values
#!/bin/sh
# print comma separated
## Get all fields into variables
## jshn utility



## Other examples
### Get bridge status
#!/bin/sh
### Check if Link is up using devstatus and jshn
#!/bin/sh
## Additional JSON parsing tools
### jsonfilter
### jq
### See also

> **Summary:** The 'Links to Libraries' module provides a curated list of lightweight libraries suitable for linking in OpenWrt development. It includes various C standard libraries like uClibc, which is currently used by OpenWrt, and alternatives such as dietlibc and Newlib. Additionally, it offers links to SSL/TLS libraries, including OpenSSL and PolarSSL, along with their licensing information. This resource is essential for developers looking to integrate specific libraries into their OpenWrt projects.
> **Use Case:** Use this module when selecting libraries for embedded development in OpenWrt, particularly when considering lightweight options for C and SSL/TLS functionalities.
# Links to Libraries
## C standard library
## C++ standard library
## SSL/TLS




> **Summary:** The 'Adding new elements to LuCI' module provides a guide for developers to enhance the LuCI interface by adding new tabs and forms. It outlines two primary methods for integration: using CBI (Configuration Binding Interface) and templates for views. The tutorial details the creation of a new top-level tab, its associated sub-tabs, and the necessary Lua scripts and configuration files. Examples are provided for both the controller and the model, demonstrating how to structure the code and where to place the files within the LuCI directory hierarchy.
> **Use Case:** This module is useful when developers want to customize the LuCI interface for specific applications or functionalities within OpenWrt. It is particularly applicable for creating user-friendly forms and navigation elements in the web interface.
# Adding new elements to LuCI
## Adding a new top level tab
## Adding the cbi_tab code
## Adding the cbi_file
## Adding the view_tab code

> **Summary:** The 'Device Support: MAC address setup' module provides guidance on retrieving and setting MAC addresses for devices running OpenWrt. It outlines methods for extracting MAC addresses from stock firmware and flash locations, including using commands like 'hexdump' and 'get_mac_binary'. The module also discusses how to merge data from stock firmware with research findings to create a comprehensive list of MAC addresses, and it highlights the importance of using the correct location for each interface. Additionally, it covers the automatic retrieval of MAC addresses by drivers and the use of label MAC addresses for device identification.
> **Use Case:** This module is useful when configuring MAC addresses for network interfaces on OpenWrt-supported devices, particularly when transitioning from stock firmware. It is applicable during the device support development process.
# Device Support: MAC address setup
## Retrieve addresses from stock firmware
## Find out about flash locations
## Merge your data
## Set MAC addresses
### MAC address pulled by driver

## Label MAC address
### label-mac-device DTS file
### Set label MAC address via 02_network
### Using the label MAC address
## Common MAC address locations

> **Summary:** The umdns package provides local DNS name resolution for OpenWrt routers, allowing services to be accessed via *hostname.local* instead of an IP address. It utilizes mDNS (multicast DNS), enabling automatic discovery of devices and services on the local network without requiring complex configuration. Installation is straightforward, available through the LuCI web interface or via `opkg install umdns`. Configuration options include setting the hostname, local domain, and specifying network interfaces for mDNS advertisement.
> **Use Case:** Use umdns when you want to simplify access to your OpenWrt router and its services on a local network without needing to remember IP addresses.
# umdns for Local Device Discovery
## Installation
### Configuration
### Firewall
### mDNS Alternatives
## For Developers
### Browsing announced services
### Issues/Bugs
### Announcing local services
### Service description files in /etc/umdns
### Testing
### Links

> **Summary:** The Network scripts module in OpenWrt provides a framework for implementing protocol handlers that enable various network configurations through the netifd daemon. Each protocol handler is a shell script located in `/lib/netifd/proto/` and must define at least two functions: `proto_protocolname_init_config` for parameter validation and monitoring, and `proto_protocolname_setup` for executing the protocol-specific setup logic. The handlers are invoked with configuration parameters in JSON format, allowing for dynamic updates to network interfaces. Changes to the protocol handlers require a restart of the netifd daemon to take effect.
> **Use Case:** Use this module when you need to implement custom network protocols such as PPPoE or 3G in OpenWrt, allowing for dynamic configuration and management of network interfaces.
# Network scripts
## Writing protocol handlers
#!/bin/sh
### init_config
### Setup
### renew
### Teardown
### Coldplug
### Keep config
### Debugging
### Available proto flags
### Error codes
### How does it work internally?
## API
### netifd functions
#### initialization functions
#### notification functions

### common functions
## Examples
### Get LAN address
# Runtime configuration
### Get WAN interface
# Runtime configuration
### Get WAN L2 device
# Runtime configuration
### Get WAN L3 device
# Runtime configuration
# Persistent configuration
### Get WAN address
# Runtime configuration
# Persistent static configuration
### Get WAN gateway
# Runtime configuration
# Persistent static configuration
### Get WAN prefix
# Runtime configuration
# Persistent static configuration
### Get WAN gateway for unmanaged default route
# Runtime configuration

> **Summary:** The SDK (Software Development Kit) for OpenWrt is a relocatable, precompiled toolchain designed for cross-compiling single userspace packages for specific targets without the need to compile the entire system. It allows developers to compile custom software for specific releases, update certain packages, or recompile existing packages with custom patches. To use the SDK, one can download a precompiled version or compile it themselves using 'make menuconfig'. After setting up the SDK, package definitions must be obtained and the desired packages can be compiled using standard buildroot commands.
> **Use Case:** Use the SDK when you need to create custom packages for OpenWrt or modify existing ones without rebuilding the entire system.
# Using the SDK
## Obtain SDK
#### Prerequisites
### Download
### Package Feeds
## Usage
### Obtain Definitions
### Compile Packages
### Example: existing package
### Build your own packages
## Troubleshooting

> **Summary:** The OpenWrt API module provides an overview of how the OpenWrt GNU/Linux distribution is structured, focusing on package management and compilation. OpenWrt is designed for embedded devices, utilizing a package manager called opkg to handle software packages, which are compressed archives containing programs, libraries, and configuration files. The build process involves compiling packages separately and assembling them into a firmware image that can be installed on devices. Additionally, the module explains the role of Makefiles in specifying source downloads and integrity checks for packages.
> **Use Case:** This module is useful for developers looking to understand the OpenWrt build system and how to create or modify packages for embedded devices.
# Overview
## How Packages are Compiled
## Package Feeds
## Package Versions
## Repeatable Builds

> **Summary:** OpenWrt packages are essential components of the OpenWrt system, providing software in the form of source and binary packages. A source package includes a Makefile, optional patches, and other static files, while a binary package is a tar archive containing executable artifacts and control files. Binary packages are typically generated from source packages using the OpenWrt buildroot or SDK, ensuring proper compilation and packaging. Manual assembly of binary packages is discouraged due to reproducibility and verification issues.
> **Use Case:** Use OpenWrt packages when developing or customizing firmware for embedded devices, ensuring that software components are properly managed and integrated. This is particularly relevant when creating new features or modifying existing functionalities in OpenWrt.
# OpenWrt packages
## Source packages
### Structure
#### Makefile
#### The files directory
#### The patches directory
#### The src directory
### Feature Considerations
### Copyright statements
### Versioning
#### Package Revisions
### Downloading
#### Mirror Sites

### Building
#### Hooks
##### Running custom commands after unpacking but before patching the sources:
##### Running custom commands after unpacking and patching the sources:
##### Running custom commands before invoking configure:
##### Running custom commands after executing make:
#### Autotools
## Dependencies
## Shared libraries
### SONAME
### ABI Version
### Contents
#### NOTE
### Development Files

> **Summary:** The Overriding Build Options module in OpenWrt provides developers with the ability to customize build configurations for packages, particularly when cross-compiling. It details how to use various configuration variables such as **CONFIGURE_VARS** and **CONFIGURE_ARGS** to adjust settings during the autoconf process, as well as how to manage compiler flags through **TARGET_CFLAGS** and related variables. Additionally, it covers the use of **MAKE_VARS** for Makefile configurations and options for CMake and Scons. This flexibility allows developers to specify additional options and flags to meet specific package requirements.
> **Use Case:** This module is particularly useful when you need to modify build options for packages that do not provide standard configuration flags or when cross-compiling for different architectures in OpenWrt.
# Overriding Build Options
## Autotools: Autoconf
## Compiler flags
## Make
## CMake
## Scons

> **Summary:** Step-by-step guide for creating a new OpenWrt package from scratch. Covers directory layout under package/mypackage/, the minimal Makefile skeleton (include $(TOPDIR)/rules.mk, Package/define, Build/Compile, Package/install), adding dependencies via DEPENDS:=, using PKG_INSTALL=1 vs. custom Build/Compile, creating conffiles, installing init scripts, and submitting packages to the upstream feed.
> **Use Case:** Reference when porting a new open-source application to OpenWrt or creating a first-party package: follow the Makefile skeleton to define metadata, set the correct PKG_RELEASE, and use $(INSTALL_BIN)/$(INSTALL_CONF) macros in Package/install to place files in the correct image paths.
# Creating packages
## BuildPackage variables





## Testing a package Makefile
## PKG_FIXUP
##### autoreconf
##### patch-libtool
##### gettext-version
#### Tips
## Package Sourcecode
### Use packed source code archive
### Use source repository
### Bundle source code with OpenWrt Makefile
### Download override
#       we have to download additional stuff before patching
## BuildPackage defines
##### Package/







##### PKGARCH (optional)
##### Package/conffiles (optional)
##### Package/description
##### Build/Prepare (optional)
##### Build/Configure (optional)
##### Build/Compile (optional)
##### Build/Install (optional)
##### Build/InstallDev (optional)
##### Build/Clean (optional)
##### Package/install
##### Package/preinst
##### Package/postinst
##### Package/prerm
##### Package/postrm
## Building in a subdirectory of the source
## Dependency Types
## Configure a package source
### Host tools required


##### BUILD
##### PATCHES
##### NOTES
## Adding configuration options
## Working on local application source
### CONFIG_SRC_TREE_OVERRIDE
### USE_SOURCE_DIR

### (Deprecated) package-version-override.mk
## Creating packages for kernel modules
#
# Copyright (C) 2006 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#
# $Id$
#### The use of MODPARAMS
#### Make a Kernel Module required for boot
## File installation macros
## Packaging a service
#!/bin/sh /etc/rc.common
# "new(er)" style init script
# Look at /lib/functions/service.sh on a running system for explanations of what other SERVICE_
# options you can use, and when you might want them.
#!/bin/sh /etc/rc.common
###########################################
# NOTE - this is an old style init script #
###########################################
## How To Submit Patches to OpenWrt

> **Summary:** This document provides a comprehensive guide on creating a sample procd init script for OpenWrt, illustrating how to set up a simple shell script as a service. It includes detailed instructions on configuring the script to accept parameters for a message and timeout, as well as how to create the corresponding init script in `/etc/init.d/`. The guide emphasizes the use of procd features such as service lifecycle management and configuration handling through UCI. Additionally, it explains how to enable the service and manage its startup and shutdown order.
> **Use Case:** Use this guide when you need to create a lightweight service on OpenWrt that can be configured and managed through the procd system. It is particularly useful for simple tasks that require periodic execution.
# Create a sample procd init script
## Setting up
#!/bin/sh
#these if statements will check input and place default values if no input is given
#they will also check if input is a number so you can call
#this script with just a time and it will still work correctly
#endless loop, will print the message every X seconds as indicated in the $every variable
## Creating a basic procd script
#!/bin/sh /etc/rc.common
## Enabling the service
#!/bin/sh /etc/rc.common
## Service configuration
## Loading service configuration
#!/bin/sh /etc/rc.common
## Advanced options

> **Summary:** Practical guide for writing procd-based /etc/init.d/ service scripts. Walks through USE_PROCD=1, procd_open_instance, procd_set_param command/respawn/stdout/stderr, procd_close_instance, and the service_triggers() callback for uci-change-triggered reloads; includes worked examples for a simple daemon, a daemon with multiple instances, and a service that reloads on UCI changes to a specific package.
> **Use Case:** Reference when writing or debugging a procd init script; use this guide to correctly set respawn thresholds, wire stdout/stderr to logd, add UCI change triggers so the service restarts when its config file changes, and test reload without a full reboot using /etc/init.d/myservice reload.
# Procd Init Scripts

#!/bin/sh /etc/rc.common
## How do these scripts work?
## Service Data
## Defining service instances
### Stopping services
### Init scripts during compilation
## Specifying triggers
### ucitrack
## Manual reload
## Custom service reload
### Forcing service restart
## Service jails
## Debugging
### A common gotcha with stopping a service
#!/usr/bin/sh
#!/usr/bin/sh
## Examples
## Service Parameters

> **Summary:** The RPC daemon (`rpcd`) in OpenWrt serves as a lightweight solution for enabling communication between various software components that do not have their own persistent daemons. It utilizes the `ubus` system for information exchange and action requests, allowing for efficient management without the overhead of multiple independent daemons. `rpcd` supports plugins through a simple API, loading shared library files and invoking their initialization functions. Default plugins include `session` and `uci`, while additional plugins can be developed and integrated from other projects.
> **Use Case:** Use `rpcd` when you need to facilitate communication for command-line tools like `uci` and `opkg` that do not run as background processes. It is particularly useful for integrating additional functionalities through plugins.
# RPC daemon
### Default plugins

> **Summary:** The High-level security incident response handling process outlines the steps necessary for effectively managing security incidents within OpenWrt. It emphasizes the importance of awareness, identification, and collaboration among team members to address security issues promptly. Key tasks include making the security team aware of incidents and analyzing reports for validity and severity. This structured approach ensures that security responses are handled efficiently and effectively.
> **Use Case:** This process should be utilized whenever a security incident is reported to ensure a swift and organized response. It is particularly relevant for developers and security teams working on OpenWrt.
# High-level security incident response handling process

> **Summary:** The Security module of OpenWrt outlines the processes, tools, and mechanisms utilized to ensure the security of the OpenWrt distribution and its official package feeds. It includes guidelines for vulnerability reporting, emphasizing confidentiality and the appropriate channels for communication, such as contacting <contact@openwrt.org> or the public mailing list <openwrt-adm@lists.openwrt.org>. Additionally, the module provides information on security advisories specifically for components maintained by OpenWrt, while noting that third-party components are not covered. The support status of various OpenWrt releases is also detailed, indicating their current status and projected end-of-life dates.
> **Use Case:** Use this module when you need to understand the security protocols and reporting mechanisms for OpenWrt. It is particularly relevant for developers and users who want to report vulnerabilities or stay informed about security advisories.
# Security
## Vulnerability reporting
## Security advisories
## Support Status
#### Notes
## Identifying problems
### uscan
### Coverity Scan
## Reproducible builds
## Deliver to users
## Hardening build options

> **Summary:** The OpenWrt SELinux policy development module provides guidance on customizing, developing, and testing SELinux policies for OpenWrt devices. It outlines the prerequisites, including the use of Fedora 34 for building images and the necessity of a git repository for accessing policy components. The module emphasizes the importance of tailoring the SELinux policy to specific device configurations to enhance efficiency and reduce unnecessary resource usage. Additionally, it encourages contributors to submit patches for improvements once their policies are tested and deemed beneficial for the community.
> **Use Case:** Use this module when you need to develop or customize SELinux policies for OpenWrt devices, particularly if you aim to optimize the policy for specific hardware configurations.
# OpenWrt SELinux policy development, customization, and testing
## Introduction and Prerequisites
### Goals
## Installing and setting up build requirements
### Clone OpenWrt source code using git
#### Addressing feeds
#### Addressing build configuration
### Building OpenWrt and its Image Builder
#### Applying basic customization
### Creating a new selinux-policy-myfork repository on Github
#### Forking selinux-policy
#### Adding a custom target to the Makefile
#### Building a selinux-policy-myfork ipk package
#### Deploying sysupgrade image with customized selinux-policy-myfork
## Policy development overview
### Confining "Hello World"
#### Creating and testing the script
#### Extend selinux-policy-myfork with basic skeleton for helloworld
## In closing

> **Summary:** Practical guide for using ubus from shell scripts, C code, and Lua/ucode. Covers the ubus CLI (ubus call, ubus listen, ubus wait_for), calling ubus from C (ubus_lookup_id, ubus_invoke, ubus_send_event), registering a new ubus object in a C daemon (ubus_add_object, ubus_method definitions), and the ACL permission file format for granting rpcd access to specific ubus paths.
> **Use Case:** Reference when calling an existing ubus service from a shell script (ubus call system board), writing a C daemon that needs to expose methods over ubus, or configuring rpcd ACL files to allow a LuCI JavaScript view to invoke a ubus path without root privileges.
# uBus IPC/RPC System
## uBus - IPC/RPC
### Reference documentation for ubus

> **Summary:** The UCI defaults module in OpenWrt allows for the preconfiguration of system settings using the Unified Configuration Interface (UCI) during the initial boot of a device. By placing scripts in the `/etc/uci-defaults` directory, these scripts are executed automatically by the boot service, with successful scripts being deleted after execution. This module supports the integration of custom settings through batch scripts that can be included in firmware builds, ensuring that configurations are applied after flashing. Additionally, it is recommended to implement checks in scripts to prevent overwriting existing configurations.
> **Use Case:** Use UCI defaults when you want to set initial configuration values for a device upon its first boot or after an upgrade. This is particularly useful for automating the setup of network parameters and other essential settings.
# UCI defaults
## Integrating custom settings
## Ensuring scripts don’t overwrite custom settings: implementing checks
## Examples

> **Summary:** The OpenWrt module for UEFI based x86 systems provides guidance on generating UEFI bootable images for x86-64 architecture. It outlines the necessary steps to build these images using the OpenWrt build system, including configuring the menu options and running the build command. Additionally, it covers the process for creating UEFI secure boot images, detailing the required tools and commands to sign EFI binaries. The module also references a development repository for secure boot capabilities and provides instructions for importing signing certificates.
> **Use Case:** Use this module when you need to create UEFI bootable images for x86-64 systems in OpenWrt, especially when targeting modern hardware that requires UEFI support.
# OpenWrt on UEFI based x86 systems
## Introduction
## Status
## Building UEFI bootable OpenWrt image
## UEFI Secure Boot
# Add the development git repository
# Configure the corresponding package repository
# Now, configure the build system
# Select x86 as Target, x86_64 as Subtarget
# make sure to select 'Sign EFI executable binaries' under 'Target Images'
# UEFI related tools are available under Utilities section,
# which consist of efitools, efibootmgr, efivar, and sbsigntool
# The certificate and key need to be generated
# to perform uefi binary signing
# run make to generate UEFI secure bootable OpenWrt image

> **Summary:** The 'Sending patches by git send-email' module provides guidance on how to properly send patches to the OpenWrt development mailing list using the 'git send-email' command. It emphasizes the importance of adhering to the format specified on the patchwork site to ensure that patches are processed correctly. Additionally, it warns against using standard email clients due to potential formatting issues that could arise. The recommended command for sending a patch includes specifying the sender's email and the recipient mailing list.
> **Use Case:** Use this module when you need to submit patches to the OpenWrt development mailing list to ensure they are correctly formatted and processed.
# Sending patches by git send-email

> **Summary:** The 'Working with GitHub' module provides a comprehensive guide for developers on how to interact with the OpenWrt source repository using GitHub. It covers essential steps such as forking the repository, cloning it locally, creating branches for changes, and submitting pull requests. Additionally, it explains how to configure Git settings, manage commits, and squash commits for cleaner pull requests. This module is particularly useful for developers looking to contribute to the OpenWrt project through GitHub.
> **Use Case:** Use this module when you want to contribute code to the OpenWrt project via GitHub, especially if you are unfamiliar with Git workflows.
# Working with GitHub
## Squashing commits
### Alternative squashing advice
## Reopen closed PR
# Get the hash yyyyyyyyyyyyyyy of the current state of "testbranch" (we will move the branch head later)
# Checkout the latest state of the PR (commit hash xxxxxxxxxxx)
# Delete old testbranch
# Label current state as testbranch
# Push old state to GitHub
# Checkout the desired hash yyyyyyyyy (or branch)
# Delete intermediate testbranch
# Label current state as testbranch
# Push new state to GitHub

> **Summary:** The OpenWrt operating system utilizes the Almquist shell (ash), which is part of the BusyBox suite, to provide a lightweight and efficient command-line interface for embedded devices. Unlike the more resource-intensive Bash shell used in many Linux distributions, ash is designed to minimize memory and storage usage, making it ideal for routers and similar hardware. While BusyBox offers a range of essential tools such as awk, grep, and sed, users should note that these implementations may be more limited than their full desktop counterparts. Scripts written using POSIX features of Bash are generally compatible with ash, allowing for effective scripting within OpenWrt's environment.
> **Use Case:** This module is particularly useful when developing shell scripts for OpenWrt devices, especially when memory and storage constraints are a concern.
# Write shell scripts in OpenWrt
## The default OpenWrt shell is ash: the Almquist shell
## OpenWrt, BusyBox, and the ash shell
## The shebang Operator and Shell Scripting for OpenWrt
### Can I change my default shell from ash to bash?
## Automated shell script checking
## Check if a tool is available

> **Summary:** OpenWrt's operating system architecture is designed to be lightweight and efficient, utilizing components like libubox, ubus, and procd instead of the larger libraries commonly found in desktop distributions. This architecture allows OpenWrt to function effectively on devices with limited resources, such as 32 MiB to 512 MiB of RAM. Key features include a custom init system (procd), a package management system (opkg), and a unique network configuration tool (netifd). The system is built on the Linux kernel, providing essential functionalities without the overhead of traditional desktop environments.
> **Use Case:** This architecture is particularly useful for embedded network devices that require a minimal footprint while still delivering robust networking capabilities. Use OpenWrt when developing firmware for routers or IoT devices with constrained hardware resources.
# OpenWrt – operating system architecture
### What's the difference between ubus vs dbus?

> **Summary:** The Mounting Block Devices module in OpenWrt provides advanced details on how block devices are managed through the `block-mount` package. This package includes functionalities for mounting devices at boot via `/etc/init.d/fstab` and handling hotplug events with `block-hotplug`. Key scripts included are `block.sh`, `mount.sh`, and `fsck.sh`, which facilitate various mounting operations. The `block` executable allows users to run commands such as `block info`, `block mount`, and `block detect` for managing block devices effectively.
> **Use Case:** Use this module when you need to manage block device mounting in OpenWrt, especially for configuring devices to mount automatically on boot or when they are hotplugged.
# Mounting Block Devices
## Overview
## block-mount (binary package)
### The new block-mount in Barrier Breaker
#### Usage: block \<info\|mount\|umount\|detect\>

### working/not working in Barrier Breaker as of 2015/01/30
## block-hotplug (binary package)

> **Summary:** The Bootloader is a critical piece of software executed upon powering up a hardware device, responsible for initializing low-level hardware details and passing a hardware description to the Kernel. It is typically stored on flash storage and is device-specific, though it is not part of OpenWrt itself. While not strictly necessary for booting Linux, bootloaders provide additional functionalities such as firmware flashing and device recovery options. Limitations may exist based on OEM designs, affecting kernel size and firmware formats.
> **Use Case:** Use the bootloader when you need to initialize hardware or perform tasks like flashing new firmware or recovering a device in OpenWrt.
# The Bootloader
## Main Function
### Why this is necessary?
## Features
### Limitations

### Additional Functions

## Boot Procedure
## Individual Bootloaders
### PC
### Embedded Devices

## Bootloader Pages

> **Summary:** The BCM63xx Firmware Image Information module provides tools and details for analyzing firmware image tags specific to Broadcom 63xx devices. It includes a program called `analyzetag` that can be compiled to extract information from firmware image files using various command-line options. Users can specify the input file, tag ID, flash start address, and firmware offset to retrieve detailed metadata about the firmware image. The documentation also outlines the structure of the Broadcom imagetag format, detailing the fields and their purposes for different versions of the imagetag.
> **Use Case:** This module is useful when working with firmware images for Broadcom 63xx devices in OpenWrt, especially for developers needing to analyze or modify firmware images.
# BCM63xx Firmware Image Information
## BCM63xx Firmware Image Analyzer
## Information about the Broadcom 63xx imagetag format
### Broadcom Generic CFE
### Broadcom Code Version 2.2x
### Broadcom Code Version 3.00 - 3.08
### Broadcom Code Version 3.06, Pirelli Modifed Version
### Broadcom Code Version 3.10+
### TP-Link custom CFE
## OpenWRT Broadcom 63xx Firmware Image README
### Old imagetag routers
### Redboot routers
## Table of Broadcom Version for Various Routers

> **Summary:** Explains the OpenWrt build system (buildroot), covering the directory layout (package/, target/, toolchain/, staging_dir/), the package Makefile structure (PKG_NAME, PKG_BUILD_DIR, Package/install, Build/Compile targets), the feeds system for third-party packages, the menuconfig workflow for selecting packages and target configs, and DL_DIR/TOPDIR conventions for reproducible builds.
> **Use Case:** Reference when creating a new OpenWrt package Makefile, adding a new package to a feed, configuring a cross-compilation toolchain for a specific target board, or troubleshooting why a package fails to compile in the buildroot environment.
# OpenWrt Buildroot – Technical Reference
## Kernel related options
### CONFIG_EXTERNAL_KERNEL_TREE
### OpenWrt Buildroot – Build sequence
### Make sequence
### Warnings, errors and tracing

> **Summary:** BusyBox is a crucial component in OpenWrt that consolidates various system utilities into a single binary, providing lightweight alternatives to many standard Unix tools. It includes essential commands such as `ash`, `cp`, `ls`, `echo`, and `ping`, which are compiled as 'applets' within `/bin/busybox`. This allows for a more efficient use of system resources on embedded devices. Additionally, BusyBox helps identify the OpenWrt version through the Vendor-Class option in DHCP requests, which includes the BusyBox version number.
> **Use Case:** Use BusyBox when you need lightweight command-line utilities in OpenWrt or when diagnosing the OpenWrt version via DHCP requests.
# BusyBox
## Identify OpenWrt version through udhcp

> **Summary:** The DFS (Dynamic Frequency Selection) module in OpenWrt manages the use of 5GHz WLAN channels that may overlap with weather radar frequencies, ensuring compliance with regulations such as those outlined in 802.11h. It is utilized during Automatic Channel Selection (ACS) in hostapd to identify and select available channels. Different hardware drivers provide varying levels of DFS support, including ath9k, ath10k, and mt76, with some limitations based on regulatory schemes like DFS-FCC and DFS-ETSI. Users should be aware of potential interoperability issues due to changing hardware and regulatory compliance, as well as the availability of proprietary drivers that may offer additional DFS functionality.
> **Use Case:** Use the DFS module when configuring 5GHz WLAN channels in OpenWrt to ensure compliance with local regulations and optimize channel selection. It is particularly relevant for environments where radar interference is a concern.
# DFS
## DFS support



## DFS status unknown

## No DFS support

> **Summary:** The External Documentation module for OpenWrt provides links to various upstream documentation relevant to the components used within the OpenWrt Linux distribution. It includes resources for bootloaders like Das U-Boot and RedBoot, as well as the Linux Kernel and GNU/Linux drivers. Additionally, it covers libraries such as µClibc and BusyBox, which are integral to the OpenWrt environment. Other topics include package management with Opkg, networking with Netfilter, and server options like µHTTPd and lighttpd.
> **Use Case:** Use this module when you need to reference external documentation for components integrated into OpenWrt, especially during development or troubleshooting. It is particularly useful for understanding the underlying systems and libraries that support OpenWrt functionalities.
# External Documentation
## Bootloader
### Das U-Boot (GPLv2)
### RedBoot (modified GPL)
### CFE (BSD like)
## Linux Kernel (GPLv2)
## GNU/Linux Drivers (diverse)
## C standard library
### µClibc (LGPL)
### EGLIBC (LGPL)
### newlib (LGPL)
### diet libc (GPLv2)
## Opkg (GPLv2)
## BusyBox (GPLv2)
## Netfilter (GPLv2+)
## Dropbear (MIT-style license)
## Dnsmasq (GPL)
## Samba (GPLv3)
## Web servers
### µHTTPd (New BSD License)
### httpd (Busybox) (GPLv2)
### lighttpd (revised BSD)
### mini-httpd (GPLv3+)
### Audio Servers

> **Summary:** The OpenWrt File System Hierarchy and Memory Usage module provides a detailed overview of how flash storage is partitioned and utilized in OpenWrt devices, specifically using the TP-Link WR1043ND as an example. It outlines the different memory layers, including hardware specifications, kernel space, and user space allocations. Key components such as u-boot, firmware, kernel, and root filesystem are identified along with their respective sizes. Additionally, it highlights the usage of overlay filesystems and the distribution of main memory.
> **Use Case:** This module is useful when configuring or troubleshooting memory usage and filesystem layout on OpenWrt devices. It is particularly relevant for developers working on embedded systems that require efficient memory management.
# OpenWrt File System Hierarchy / Memory Usage
### Mount Points
## History

> **Summary:** The Network Filesystems module in OpenWrt allows the system to mount various filesystems over an IP network, functioning as both a client and a server. Supported filesystems include ftp, sshfs, sftp, nfs, cifs, iscsi, remotefs, tftp, and webdav, each with specific configurations and capabilities. This module facilitates file sharing and storage solutions across networked devices. Security features vary by filesystem, with some supporting tcp-wrappers and authentication mechanisms.
> **Use Case:** Use this module when you need to access or share files over a network in OpenWrt, such as setting up a NAS or connecting to remote storage solutions.
# Network Filesystems
## Supported Network Filesystems






## Embedded FS
## Security

> **Summary:** The Filesystems module in OpenWrt provides an overview of various file systems utilized for device built-in flash storage. It covers common file systems such as OverlayFS, tmpfs, SquashFS, and JFFS2, detailing their characteristics, advantages, and limitations. OverlayFS is used to merge read-only and writable file systems, while tmpfs operates like a RAM-Disk for temporary storage. SquashFS is a read-only compressed file system, and JFFS2 is a writable compressed file system with journaling and wear leveling features.
> **Use Case:** This module is useful when configuring storage solutions for OpenWrt devices, particularly when selecting the appropriate file system for specific use cases such as temporary storage or read-only environments.
# Filesystems
## Common File System
### OverlayFS
### tmpfs
### SquashFS
### JFFS2
### UBIFS
### ext2
## Other filesystems
### mini_fo

## Implementation in OpenWrt
### Boot process
### Explanations
#### Explanations 1
#### Explanation 2
### Technical Details

#### Can we switch the filesystem to be entirely JFFS2?
## Notes

> **Summary:** The OpenWrt Flash Layout module provides an overview of the flash memory types used in embedded devices targeted by OpenWrt, specifically focusing on the distinctions between raw flash and FTL flash, as well as NOR and NAND flash types. It explains the implications of non-mechanical wear on flash memory, the differences in management between host-managed and self-managed flash, and the characteristics of NOR and NAND flash. The document also highlights the default file system setups for these flash types and their reliability considerations.
> **Use Case:** This module is useful when configuring or troubleshooting storage options in OpenWrt-based embedded devices, particularly when selecting the appropriate flash memory type for firmware and configuration storage.
# The OpenWrt Flash Layout
## Types of flash memory
### Non-mechanical wear
### Host-managed vs. self-managed
### NOR flash vs NAND flash
### MLC vs. SLC flash
## Partitioning of NOR flash-based devices
### Sysupgrade and `rootfs_data`
### Example NOR flash partitioning
#### Another Flash layout example
### Explanations
#### Mount Points
#!/bin/sh
# shows all overlay-whiteout symlinks
# 2018: overlay-whiteouts are a character device on CC 'find /overlay -type c' seems to work
#  https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt  put me on the right track
#### Example 2: Hoo Too HT-TM02
#### Example 3: D-Link DIR-300
## Partitioning of NAND flash-based devices
### Reserving UBI partition space for user-defined UBI volumes
### Example: Creating a UBI volume for persistent storage across sysupgrades
## MTD (Memory Technology Device) and MTDSPLIT
### MTD partitions

### MTDSPLIT
## UBI (Unsorted Block Images)
## Discovery (How to find out)
## Details
### generic
### broadcom with CFE
## Explanations
### What is an Image File?



> **Summary:** The Flash memory module in OpenWrt provides comprehensive insights into the considerations and types of flash memory used in embedded devices. It discusses critical factors such as read/write cycles, the choice between NOR and NAND flash, and the implications of SLC versus MLC flash types. The module also explains the structure of flash storage, including erase blocks, pages, and the out-of-band area for metadata. Understanding these concepts is essential for making informed decisions about flash memory in various projects.
> **Use Case:** Use this module when evaluating flash memory options for embedded devices in OpenWrt, particularly when considering performance, reliability, and storage requirements.
# Flash memory

## Erase blocks and erase cycles
### Hardware vs. Software
### NAND vs. NOR

## Bad blocks
### Hardware vs. Software
### NAND vs. NOR
## Flash memory lifetime
## Innocent mtdblock I/O errors
## NAND memory and bitflips
## NAND-specific tools for reading and writing to raw NAND

> **Summary:** The TRX, TRX2, and BIN firmware formats are used in various OpenWrt devices, each having distinct header structures despite containing similar content. TRX v1 and v2 both start with a magic number and include fields for header length, CRC value, flags, version, and multiple partition offsets, with TRX v2 adding an additional partition offset. The BIN header format is less defined, but it also begins with a magic number and includes reserved fields. Understanding these formats is crucial for firmware development and modification in OpenWrt.
> **Use Case:** Use this information when developing or modifying firmware for OpenWrt devices that utilize TRX or BIN formats.
# TRX vs. TRX2 vs. BIN
# The various headers
## TRX v1
## TRX v2
## BIN-Header
## TP-LINK BIN Header

> **Summary:** The Hotplug -- Legacy module describes the functionality of the deprecated Hotplug2 daemon, which was a lightweight alternative to UDev for managing device events in early Linux userspace. It executed scripts located in `/etc/hotplug.d/` in response to events such as interface status changes or button presses, making it particularly useful for managing PPPoE connections or handling unstable networks. Hotplug2 was removed in 2013 and replaced by the procd system. Configuration involved editing `/etc/hotplug2.rules` to specify which scripts to execute based on device types.
> **Use Case:** This module is relevant for users maintaining legacy OpenWrt systems that still utilize Hotplug2 for device management. It may also be of interest for understanding historical context in device event handling.
# Hotplug -- Legacy
#### What is hotplug?
#### How it works
## Configuration
## Examples
## Coldplug
### Logs generated by Coldplug script below
## Troubleshoot
## Notes

> **Summary:** The Image formats module provides an overview of various firmware types and their respective file extensions used in OpenWrt. It categorizes these formats into standard and specific types, detailing their usage scenarios such as factory images for OEM flashing and sysupgrade images for upgrading existing OpenWrt installations. Additional formats like ext4, squashfs, and initramfs are explained, highlighting their characteristics and typical applications. The document also includes information on developer files and example firmware image names for different targets.
> **Use Case:** This module is useful when determining the correct firmware image format to use for flashing or upgrading OpenWrt on various devices. It is particularly relevant for developers and users looking to understand the implications of different firmware types.
# Image formats
## Standard formats
### factory (.img/.bin)
### sysupgrade ( or trx )
## Specific formats
### ext4
### squashfs

### initramfs
### sdcard.img.gz
### rootfs
### kernel
### ubifs
### ubi
### tftp
### u-boot
### ubinized.bin
### uImage
### zImage
## Subformats
### bin, img, elf, dtb, chk, dlf
### xz, gz, tar, lzma
## Developer files
### sdk
### Imagebuilder
### vmlinux
# Example Firmware image names
## Firmware types
# Image Formats General
## Known Formats
## Other Formats



> **Summary:** The image/Makefile module in OpenWrt defines how to create and manage images for different platforms using the buildroot system. It provides functions such as Image/Prepare for data manipulation and Image/Build for invoking various image formats like jffs2 and squashfs. Additionally, it outlines the structure for platform-specific configurations and kernel options necessary for building device images. This module is essential for developers looking to customize or add new platforms to the OpenWrt build system.
> **Use Case:** Use this module when you need to create or modify image files for new or existing platforms in OpenWrt. It is particularly useful for developers adding support for new devices or customizing existing builds.
# image/Makefile Details

## image/Makefile from scratch or modify
## Basic Function
### Image/Prepare
### Image/Build/Initramfs
### Image/Build/jffs2-64k
### Image/Build/jffs2-128k
### Image/Build/squashfs
### Image/Build
## Example
#
# Copyright (C) 2010 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#
## See also
# Platform/Device configuration files
## config-4.x
## files-4.x
## patches-4.x
## Makefile
## image/Makefile
## base-files
## profiles/00-default.mk

> **Summary:** The Init (User space boot) reference for Chaos Calmer details the implementation of the user space boot sequence in OpenWrt, specifically focusing on the role of procd as the primary process. Procd, which replaces the traditional init system, is responsible for managing services and handling hotplug events after the initial preinit steps are completed by `/sbin/init`. The document outlines the boot process, including filesystem mounting and kernel module loading, as well as the source code paths followed during execution. It serves as a technical reference for developers looking to understand or contribute to the procd implementation in the Chaos Calmer release.
> **Use Case:** This documentation is useful for developers working on the boot process of OpenWrt in the Chaos Calmer release, particularly those interested in modifying or extending the functionality of procd.
# Init (User space boot) reference for Chaos Calmer: procd
## Procd replaces init
## Life and death of a Chaos Calmer system

> **Summary:** Documents the OpenWrt /etc/init.d/ procd init script system, including the required START/STOP priority numbers, the USE_PROCD=1 flag, mandatory shell functions (start_service, stop_service, reload, status), and the boot sequence ordering enforced by procd. Covers how to enable/disable services via symlinks in /etc/rc.d/, reload semantics, and the difference between restart and reload.
> **Use Case:** Reference when writing or debugging an /etc/init.d/ script: ensure the script sets USE_PROCD=1 and defines at minimum start_service(); use the START= and STOP= priority numbers to control boot ordering relative to netifd (START 20), dnsmasq (START 60), and other system services.
# Init Scripts
## Example Init Script
# Example script
# Copyright (C) 2007 OpenWrt.org
### Other functions
### Custom commands
## Enable and disable

> **Summary:** The Internal Layout D-Link DIR-825 module provides detailed information about the hardware configuration of the D-Link DIR-825 router, which includes two physical network interfaces (`eth0` and `eth1`) and two wireless interfaces (`wlan0` and `wlan1`). It describes the internal connections, including a Gigabit Switch and WAN port for `eth0` and `eth1`, respectively. The module also outlines the default configuration for various interfaces, including loopback, LAN, and WAN, along with the switch configuration for VLANs. Additionally, it highlights the default settings for network interfaces and the potential for configuring wireless access.
> **Use Case:** This module is useful when setting up or troubleshooting the D-Link DIR-825 router in an OpenWrt environment, particularly for understanding its network interface layout and configuration options.
# Internal Layout D-Link DIR-825

> **Summary:** The `libnl` library facilitates communication with the kernel through netlink sockets, allowing applications to manage routing information and interface settings. It is a comprehensive library but is not included by default in OpenWrt due to its size; instead, `libnl-tiny` serves as a lightweight alternative for basic functionalities. The `libnl` package has been modularized into components like `libnl-core`, `libnl-genl`, `libnl-nf`, and `libnl-route`, each serving specific purposes. In contrast, `libnl-tiny` is a compact version that replaces essential parts of `libnl-core` and `libnl-genl`, making it suitable for most applications while maintaining compatibility.
> **Use Case:** Use `libnl` when full netlink functionalities are required for complex applications. Opt for `libnl-tiny` for lightweight applications that can operate with its limited API.
# libnl and libnl-tiny – Technical Reference
## libnl
## libnl-tiny

> **Summary:** Documents libubox, the OpenWrt utility library that underpins ubus, procd, and netifd. Covers the blob/blobmsg API for binary/JSON message encoding (blob_buf_init, blobmsg_add_*), the uloop event loop (uloop_run, uloop_fd_add, uloop_timeout_*), avl/list data structures, and the json_script policy-based configuration evaluator used by procd.
> **Use Case:** Reference when implementing a C daemon that needs event-loop integration (uloop), binary message serialization for ubus calls (blobmsg), or efficient key-value lookup (avl_tree); most OpenWrt C programs link against libubox and use blobmsg_parse() to decode incoming ubus method arguments.
# libubox
## libubox/utils.h
## libubox/usock.h
## libubox/uloop.h
## libubox/blob.h
## libubox/blobmsg.h
## libubox/list.h
## libubox/safe-list.h
## libubox/kvlist.h

> **Summary:** The lldpd module implements the Link Layer Discovery Protocol (LLDP), an industry-standard protocol that provides a mechanism for network devices to discover each other and share information. It is designed to replace proprietary protocols like Extreme's EDP and Cisco's CDP. Configuration is done through the `/etc/config/lldpd` file, allowing users to set device classes and descriptions. The daemon must be running to utilize the `lldpcli` command for viewing neighbors and statistics.
> **Use Case:** Use lldpd when you need to discover adjacent network devices in a multi-vendor environment. It is particularly useful for network management and monitoring in OpenWrt setups.
# lldpd
## Abstract
## Configuration
## Usage
## Known Issues

> **Summary:** Provides a technical overview of the LuCI web interface framework for OpenWrt. Covers the three-tier architecture (controller/model/view), the CBI/form module system, Lua vs. JavaScript view types, the rpcd permission model, package Makefile conventions for registering menu entries and ACL files, and the workflow for developing and testing LuCI packages locally.
> **Use Case:** Reference when starting development of a new LuCI package: understand how to register menu items in the luci-base po/ACL system, choose between Lua CBI and JavaScript form views, and set up a local test environment using the LuCI development toolchain.
# LuCI – Technical Reference

## What is LuCI
## Dependencies
## Encompassed Packages

> **Summary:** LuCI2 is an experimental web user interface for OpenWrt, designed to replace the older Lua-based LuCI. It utilizes static HTML and JavaScript XHR for client-side rendering, significantly reducing resource consumption on devices with limited CPU and RAM. Communication with OpenWrt subsystems is handled through `ubus`, and a custom `rpcd` plugin extends `ubus` namespaces for additional functionality. The menu and views are dynamically generated, allowing for a flexible and user-specific interface.
> **Use Case:** Use LuCI2 when developing or testing web interfaces on OpenWrt devices, especially when resource efficiency is a concern. It is suitable for environments where the traditional LuCI interface may be too demanding.
# LuCI2 (OpenWrt web user interface)
### NOTE: This page currently mixes the five+ years old abandoned original "luci2" and the new JavaScript based standard LuCI implementation. Information on this page can be partially misleading
## Implementation details
### Menu
### Templates
### Views
### Communication with ubus
### Dependencies of LuCI2


> **Summary:** The mountd module is an automount daemon for OpenWrt, configured through the `/etc/config/mountd` file. It has been part of OpenWrt since version r17853 and is licensed under GPLv2. Although mountd was designed for embedded devices, it has since been replaced by blockd in newer versions. The module requires dependencies such as +uci, +kmod-usb-storage, and +kmod-fs-autofs4 to function properly.
> **Use Case:** Use mountd when you need an automount daemon specifically tailored for embedded devices in OpenWrt. However, consider using blockd for newer implementations.
# mountd – Technical Reference

## What is mountd?
## Help with the development of mountd
## Why do we want mountd?
## Dependencies of mountd

> **Summary:** The `mtd` utility is designed for writing to Memory Technology Devices (MTD) in OpenWrt. It provides a variety of commands such as `unlock`, `refresh`, `erase`, and `write`, allowing users to manage MTD partitions effectively. Additional functionalities include appending files to jffs2 partitions and fixing checksums in trx headers. Various options are available to customize the behavior of these commands, including quiet mode and forced writes.
> **Use Case:** Use the `mtd` utility when you need to manage firmware images or data stored on MTD devices in OpenWrt. It is particularly useful for tasks like erasing partitions or writing new firmware.
# MTD
# MTD
## Invocation
### Writing to MTD
### Options
## Examples
## Example (flash u-boot from OpenWrt)
## mtd vs dd
## mtd on vendor-firmware
## Notes


> **Summary:** Documents netifd, the OpenWrt network interface daemon responsible for managing network interfaces based on UCI config. Explains the interface/device/proto handler model, the /etc/config/network schema (interface, device, bridge, route, rule sections), protocol handler shell scripts in /lib/netifd/proto/, ifup/ifdown/ifupdate hotplug event flow, and the ubus network API exposed by netifd.
> **Use Case:** Reference when diagnosing why an interface fails to come up, implementing a custom protocol handler (proto script in /lib/netifd/proto/), writing hotplug scripts that react to ifup/ifdown events, or calling netifd ubus methods like network.interface.status or network.interface.up.
# netifd (Network Interface Daemon) – Technical Reference

### What is netifd?
### Debugging
### Help with the development of netifd
### Why do we want netifd?

> **Summary:** odhcpd is a daemon designed for managing DHCP, DHCPv6, Router Advertisements (RA), and Neighbor Discovery Protocol (NDP) in embedded systems, particularly for IPv6 home routers. It supports both stateless and stateful DHCPv4 and DHCPv6, as well as prefix delegation and dynamic reconfiguration. The module can operate in server or relay modes for both DHCPv6 and Router Discovery, enabling seamless IP management across routed interfaces. Configuration is handled via a UCI file located at `/etc/config/dhcp`.
> **Use Case:** Use odhcpd when you need to manage IP address assignments and routing information for IPv6 clients and routers in a network, especially in scenarios where prefix delegation is required.
# odhcpd
## Abstract
## Features
### Router Discovery (RD)
### DHCPv6
### DHCPv4
### Neighbor Discovery Proxy (NDP)
## Configuration
### odhcpd section
### dhcp section
### host section
## ubus API
## Compiling
# Prepare
# Build/install
# Build DEB/RPM packages

> **Summary:** The OpenWrt preinit and root mount system is responsible for the initial boot sequence and firstboot scripts that prepare the system for multiuser operation. It details the boot process from the moment the bootloader loads the kernel, through the execution of the `/etc/preinit` script, to the initialization of the root filesystem. The document outlines how various scripts are executed during this phase, including those for failsafe and external root filesystem configurations. Additionally, it provides an overview of available preinit scripts and their configurations.
> **Use Case:** This module is useful when configuring the boot sequence of OpenWrt devices, especially for custom setups involving external storage or enhanced failsafe mechanisms.
# Abstract
# Abstract
# Context: Boot Sequence
# Overview
## Preinit
## Failsafe
## Mount Root Filesystem
## First Boot
### Common
### Sourced rather than executed
### Executed with no parameters
### Executed with parameter 'switch2jffs'
### hook no_fo
# Preinit Operation
## Main Preinit Script
## Variables
## Hooks
### Development
### preinit_essentials
### preinit_main
### failsafe
### preinit_mount_root
### initramfs
# Firstboot Operation
## Main Firstboot Script
## Hooks
### switch2jffs
### no_fo
### jffs2reset
# Customizing the system
## Overriding Example
## Adding Example
# Architecture-specific notes

> **Summary:** Describes procd, the OpenWrt process manager and init system that replaces busybox init. Covers the procd init script lifecycle (start_service, stop_service, reload), the procd_add_instance/procd_set_param API for declaring managed processes, service watchdog behavior, instance respawn limits, stdio/logging configuration, trigger-based reload via ubus events, and the /etc/init.d/ enable/disable mechanism.
> **Use Case:** Reference when writing an /etc/init.d/ procd init script to manage a daemon: use procd_open_instance to declare the process, procd_set_param command/respawn/limits to configure it, and procd_close_instance to register it; also covers how to wire ubus triggers for config-change reloads.
# Procd system init and daemon management
## Help with the development of procd
## Buttons with procd
## Init scripts with procd
## early state and preinit


## procd start up
## /etc/inittab
## ubus command interface
## hotplug
## procd (process management daemon) – Technical Reference
## OpenWrt – operating system architecture
### History

> **Summary:** The Boot Process module provides a comprehensive overview of the sequence of operations that occur when an OpenWrt device is powered on, starting from the bootloader to the initialization of user space. It details the roles of the bootloader, kernel, and init processes, including specific actions like kernel decompression, filesystem mounting, and the execution of startup scripts. Key components such as [kexec], [extroot_configuration], and [OpenWrt FailSafe] are mentioned to illustrate their relevance during the boot process. Additionally, it highlights the importance of various scripts and configurations that influence system startup.
> **Use Case:** This module is useful for developers and system integrators who need to understand the boot sequence of OpenWrt for troubleshooting or customizing the boot process. It is particularly relevant when configuring boot parameters or debugging startup issues.
# The Boot Process

## Process Trinity
### Bootloader
### Kernel
### Init
#### Vanilla Startup Scripts
## Detailed boot sequence
### Boot loader
### /etc/preinit script
### Busybox init
## /etc/init.d/rcS Script At Startup
## Notes




> **Summary:** The Boot/Init Requirements document outlines the necessary functions and goals for initscripts in the new OpenWrt init system. It describes the boot process, which includes the kernel bootstrap, preinit, and init stages, emphasizing the importance of preinit in preparing the system for the init stage. Key goals include minimizing preinit functionality, ensuring failsafe access, and supporting configurable root filesystem mounts. The document also highlights the need for compatibility with /opt deployments and the proper handling of file descriptors during the transition to the target root filesystem.
> **Use Case:** This document is useful for developers working on the OpenWrt boot process, particularly those involved in creating or modifying initscripts for system initialization. It provides guidance on managing race conditions and maintaining system functionality during boot.
# Boot/Init Requirements
# Boot/Init Requirements
## Boot/Preinit
### Goals


#### Notes
### Must-do's
### 0) Before failsafe


### 1) Allow Failsafe
#### Configuration at Compile-time not Run-time
### 2) Mount swap and 3) Mount rootfs

#### 2) Mount swap



#### 3) Mount rootfs




### 4) Mount marked fses other rootfs




### 5) Start Init or Kexec
## Init
### Goals
### Wants

> **Summary:** Documents rpcd, the OpenWrt RPC daemon that exposes ubus methods over HTTP for LuCI. Explains the plugin architecture (/usr/lib/rpcd/*.so), ACL JSON files that grant LuCI views permission to call specific ubus paths, the session management API (rpcd-mod-session), the file plugin for proxied filesystem reads/writes, and how LuCI RPC calls are authenticated via the uhttpd session cookie.
> **Use Case:** Reference when a LuCI JavaScript view calls LuCI.rpc.declare() to invoke a ubus method, when writing an rpcd ACL file to grant a non-root package permission to call specific ubus paths, or when implementing a custom C rpcd plugin that exposes new ubus objects.
# rpcd: OpenWrt ubus RPC daemon for backend server
### Default plugins
## plugin executables
#!/bin/sh

> **Summary:** The `swconfig` program is used for configuring Ethernet network switches in OpenWrt. It supports various hardware switches through specific drivers and allows users to view and manage switch configurations. Although `swconfig` is considered legacy, it remains functional for supported devices, enabling commands like `swconfig list` and `swconfig dev switch0 show` to display current settings. Users should transition to the DSA framework for new switch drivers to utilize standard tools like `ip` for configuration.
> **Use Case:** Use `swconfig` when managing legacy Ethernet switches in OpenWrt that are compatible with its drivers. It is particularly useful for troubleshooting or configuring network settings on older hardware.
# swconfig
## Supported hardware
## Usage examples
## Show
### Example switch port on/off per port (ex: on/off port 4)
## Change
### Design and rationale
## Introduction
## Scope and rationale

## Distributed Switch Architecture vs. swconfig
## Switch configuration API






## References

> **Summary:** The Sysupgrade module in OpenWrt is a shell script located at `/sbin/sysupgrade` designed to facilitate system updates. It provides various command-line options for upgrading the system, creating backups, and restoring configurations. Key options include `-f` for restoring configurations from a tarball, `-c` for preserving changed files in `/etc/`, and `-n` to skip saving configurations during a reflash. Users should be cautious with certain options, as preserving files can lead to incompatibilities in new versions.
> **Use Case:** Use Sysupgrade when you need to update your OpenWrt device or restore configurations from a backup. It is particularly useful for maintaining system settings across upgrades.
# Sysupgrade – Technical Reference
# Sysupgrade – Technical Reference
## Usage
## Options

## How It Works



> **Summary:** The `ubox` package is a component of the OpenWrt operating system that facilitates the management of UCI configurations and block devices. Introduced in revision r36427, it includes features for generating fstab configurations and detecting block devices. Users can utilize the `block detect` command to create a sample UCI configuration file, which is particularly useful for setting up extroot if the target is set to '/'. Additionally, the `block info` command can be employed to retrieve the UUID of block devices.
> **Use Case:** Use the `ubox` package when configuring block devices and UCI settings in OpenWrt, especially for generating fstab entries. It is particularly relevant during the initial setup of storage devices.
# ubox
## OpenWrt – operating system architecture

> **Summary:** Explains the OpenWrt ubus inter-process communication bus, which provides a Unix-socket-based RPC mechanism for daemons to expose services and receive method calls. Covers ubus object and method registration, the ubusd broker, ubus_context lifecycle, blob_buf message encoding, ubus_lookup, ubus_invoke, ubus_register_event_handler, and the acl JSON permission system.
> **Use Case:** Reference when implementing a new daemon that needs to expose RPC methods to other processes or to LuCI via rpcd, or when a script needs to call an existing ubus service using the ubus CLI or the ubus ucode/Lua binding.
# ubus (OpenWrt micro bus architecture)
## Command-line ubus tool
### Help output
### list
### call
# ubus call network.interface.wan status
# ubus call network.device status '{ "name": "eth0" }'
### listen
# ubus listen &
# ubus call network.interface.wan down
# ubus call network.interface.wan up
### send
# ubus listen &
# ubus send foo '{ "bar": "baz" }'
## Access to ubus over HTTP
### ACLs
### Authentication
### Session management
### Actually making calls
## Lua module for ubus
## Namespaces & Procedures
### procd
### netifd
### rpcd
## What's the difference between ubus vs dbus?
## Examples
### FHEM
#### User mapping
# /etc/config/rpcd
#### User ACL
### Getting firmware version

> **Summary:** Documents the OpenWrt Unified Configuration Interface (UCI) — the standard system for storing and modifying router configuration. Explains the /etc/config/ text file format, section and option syntax, the uci CLI (uci set/get/add/delete/commit/revert), the C library API (uci_load, uci_set, uci_commit), and batch-change semantics where changes stay staged in memory until commit.
> **Use Case:** Reference when reading or modifying OpenWrt configuration from a shell script (uci CLI), a C daemon (libuci), a Lua script (luci.model.uci), or a ucode script (import('uci').cursor()); always call uci commit after changes or they will be lost on next read by other processes.
# UCI (Unified Configuration Interface) – Technical Reference
### What is UCI?
### Dependencies of UCI

## Packages
### Installed Files
#### uci
#### libuci
#### libuci-lua
## CLI behaviour
## CLI Usage
# delete a section 'guest_zone' if any to start from scratch
# creates a section called 'guest_zone'
# specify the section type
# set enabled option
# add a list option
# get the enabled option of the guest_zone section
# show the new added section
# show the full firewall config before commit
# save the changes to /etc/config/firewall
## ubus interface (rpcd)
## LuCI



## Lua Bindings for UCI
## API
### top level entry point
### on that you can call the usual operations
#### About uci structure
## Usage outside of OpenWrt
## See also

> **Summary:** EasyCwmp is a client implementation of the TR-069 CPE WAN Management Protocol for OpenWrt, developed by PIVA Software and licensed under GPL 2. It consists of two main components: the EasyCwmp core, which handles communication with the ACS server, and the EasyCwmp DataModel, which adheres to various TR-069 DataModel standards. The design allows for easy updates to DataModel parameters and supports multiple protocols including HTTP, HTTPS, and FTP, as well as SSL and IPv6. EasyCwmp is designed for flexibility, making it easy to install on Linux and POSIX systems while providing comprehensive documentation for users.
> **Use Case:** Use EasyCwmp when you need to manage CPE devices in compliance with TR-069 standards in an OpenWrt environment.
# EasyCwmp (CPE WAN Management Protocol daemon)
## EasyCwmp Presentation in Broadban Worl Forum
## Compliant Standards

## EasyCwmp design
## Benefits

## Interoperability





## Install
#### EasyCwmp
#### microxml

> **Summary:** unetd is a WireGuard based VPN daemon designed for OpenWrt routers, facilitating the creation and management of fully-meshed VPN connections. It separates network setup into shared network configurations and local configurations, ensuring secure and encrypted data replication among network members. Features include automatic peer IP address replication, VXLAN setup, and support for direct connections through double-NAT. Additionally, it offers a simple CLI for network management and generates IPv6 addresses based on host public keys.
> **Use Case:** Use unetd when you need to establish a secure, fully-meshed VPN network between multiple OpenWrt routers, especially in environments with NAT configurations.
# unetd
## Features
## Building
### OpenWrt
### Linux
## Example setup
#### Preparation
#### Example
## Configuration
### UCI network interface
### Network config data
##### Example:
##### Config properties:
##### Host properties:
##### Service properties
### CLI usage
### DHT support

> **Summary:** The Wireless Modes module in OpenWrt outlines various wireless operation modes supported by the system, including Access Point (AP), Ad-Hoc (IBSS), and Mesh Point (802.11s). Each mode serves specific networking purposes, such as AP for creating a wireless network, P2P for peer-to-peer connections, and Monitor for packet analysis. The module also references dynamic VLAN tagging and other advanced configurations. For detailed setup, users are directed to the relevant documentation and commands like 'iw list' to explore supported interface modes.
> **Use Case:** This module is useful when configuring wireless interfaces in OpenWrt to meet specific networking requirements, such as setting up a home network or creating a mesh network.
# Wireless Modes
# Wireless Modes
## AP
## AP/vlan
## IBSS (Ad-Hoc)
## MESH POINT (802.11s)
## MONITOR
## OCB
## P2P Client
## P2P-GO
## Station (Client)
## WDS
## Links

> **Summary:** The Wireless Standards module in OpenWrt provides an overview of various wireless communication standards relevant to the operating system. It covers standards such as 802.11a, 802.11b, 802.11g, 802.11n, 802.11ac, 802.11ad, and 802.11ax, detailing their frequency bands and characteristics. Additionally, it discusses features in drivers that can be queried using the `iw phy <phy interface> info` command, highlighting the importance of compatibility for optimal data transfer rates. The module also introduces concepts like MIMO, HT, VHT, HE, MCS, RSDB, and WOW, which are essential for understanding wireless performance and capabilities.
> **Use Case:** This module is useful when configuring or troubleshooting wireless settings in OpenWrt, especially when selecting hardware or optimizing performance based on supported standards and features.
# Wireless Standards
## 802.11a
## 802.11b
## 802.11g
## 802.11n
## 802.11ac
## 802.11ad
## 802.11ax
### Features in Drivers
#### MIMO multiple-input and multiple-output
#### HT, VHT, HE
#### MCS Modulation and Coding Scheme
#### RSDB DBDC
#### WOW Wake On Wlan
## Links

> **Summary:** The Xenomai module provides a real-time framework within OpenWrt, allowing for the handling of interrupts in a prioritized manner through Adeos. It facilitates the development of applications that can transition between the real-time Xenomai environment and the standard Linux system, utilizing a set of APIs known as 'skins' that emulate traditional RTOSes. This module is currently a work in progress and is not fully supported, with specific architecture and kernel version requirements for proper functionality. Users are advised to refer to the Xenomai website for examples and further guidance.
> **Use Case:** Use Xenomai in OpenWrt when real-time processing is critical for your application, particularly in embedded systems requiring precise timing and responsiveness.
# Xenomai - real-time framework inside OpenWrt
# Xenomai - real-time framework inside OpenWrt
## Pre-condition
## Status
