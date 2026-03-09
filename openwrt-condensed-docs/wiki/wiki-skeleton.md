# wiki (Skeleton Semantic Map)

> **Contains:** Headers and function signatures for wiki.
> **Generated:** 2026-03-09T19:21:17.773812+00:00

---

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

# Building MPD-full with PulseAudio
### 18.06.02
#### The MPD Makefile

# MPD-full building from source
### Barrier Breaker and Chaos Calmer

# Building OpenWrt for Netgear WNDR3700
## Prerequisites
## Configuration
## Installation

# Building OpenWrt Kernel for Debian System
## Floating Point Unit (MIPS)
## udev
## SELinux
## IKConfig

# Setting up a build VM in VirtualBox
## Instructions
### 1. Get VirtualBox
### 2. Get a Debian image
### 3. Install the virtual machine
### 4. Initial Debian setup

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

# Create a Cmake package in OpenWrt
## CMakeLists.txt
## Makefile
## Passing Cmake options
## Build

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

# Debugging
## Serial Port
## JTAG
## GDB
## perf/oprofile cpu profiling
## Wireless
### Capture Management Traffic
### Logging hostapd behaviour
## Add and modify compiler debug flags

# Device Tree Usage in OpenWrt (DTS)
## References
## General
## Defining software partitions in all DTS targets

# Using Dependencies
## Topic
## Dependency types
### Special Notes
## Caveats
### Using boolean operators
## Bugs

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

# Drivers

## Learning more

# embedding-files-in-image

# External Toolchain
## Use OpenWrt as External Toolchain
### Step 1: Build Toolchain
### Step 2: Build Firmware

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

# Frequent PR mistakes or "How to prevent my PR from getting delayed for sure"
## 1. Add a commit message
## 2. Add a Signed-off-by with your real name
## 3. Do not multi-post or re-post PRs
## 4. Know the difference between the PR (Pull Request) and the commit
## 5. Answer questions
## 6. Do not resolve comment that are not resolved
## 7. Use checkpatch.pl
## 8. Address all issues

# GNU Debugger
## Compiling Tools
## Add debugging to a package
## Starting GNU Debugger

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

# Links to Libraries
## C standard library
## C++ standard library
## SSL/TLS




# Adding new elements to LuCI
## Adding a new top level tab
## Adding the cbi_tab code
## Adding the cbi_file
## Adding the view_tab code

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

# Overview
## How Packages are Compiled
## Package Feeds
## Package Versions
## Repeatable Builds

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

# Overriding Build Options
## Autotools: Autoconf
## Compiler flags
## Make
## CMake
## Scons

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

# RPC daemon
### Default plugins

# High-level security incident response handling process

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

# uBus IPC/RPC System
## uBus - IPC/RPC
### Reference documentation for ubus

# UCI defaults
## Integrating custom settings
## Ensuring scripts don’t overwrite custom settings: implementing checks
## Examples

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

# Sending patches by git send-email

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

# Write shell scripts in OpenWrt
## The default OpenWrt shell is ash: the Almquist shell
## OpenWrt, BusyBox, and the ash shell
## The shebang Operator and Shell Scripting for OpenWrt
### Can I change my default shell from ash to bash?
## Automated shell script checking
## Check if a tool is available

# OpenWrt – operating system architecture
### What's the difference between ubus vs dbus?

# Mounting Block Devices
## Overview
## block-mount (binary package)
### The new block-mount in Barrier Breaker
#### Usage: block \<info\|mount\|umount\|detect\>

### working/not working in Barrier Breaker as of 2015/01/30
## block-hotplug (binary package)

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

# OpenWrt Buildroot – Technical Reference
## Kernel related options
### CONFIG_EXTERNAL_KERNEL_TREE
### OpenWrt Buildroot – Build sequence
### Make sequence
### Warnings, errors and tracing

# BusyBox
## Identify OpenWrt version through udhcp

# DFS
## DFS support



## DFS status unknown

## No DFS support

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

# OpenWrt File System Hierarchy / Memory Usage
### Mount Points
## History

# Network Filesystems
## Supported Network Filesystems






## Embedded FS
## Security

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

# TRX vs. TRX2 vs. BIN
# The various headers
## TRX v1
## TRX v2
## BIN-Header
## TP-LINK BIN Header

# Hotplug -- Legacy
#### What is hotplug?
#### How it works
## Configuration
## Examples
## Coldplug
### Logs generated by Coldplug script below
## Troubleshoot
## Notes

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

# Init (User space boot) reference for Chaos Calmer: procd
## Procd replaces init
## Life and death of a Chaos Calmer system

# Internal Layout D-Link DIR-825

# libnl and libnl-tiny – Technical Reference
## libnl
## libnl-tiny

# libubox
## libubox/utils.h
## libubox/usock.h
## libubox/uloop.h
## libubox/blob.h
## libubox/blobmsg.h
## libubox/list.h
## libubox/safe-list.h
## libubox/kvlist.h

# lldpd
## Abstract
## Configuration
## Usage
## Known Issues

# LuCI – Technical Reference

## What is LuCI
## Dependencies
## Encompassed Packages

# LuCI2 (OpenWrt web user interface)
### NOTE: This page currently mixes the five+ years old abandoned original "luci2" and the new JavaScript based standard LuCI implementation. Information on this page can be partially misleading
## Implementation details
### Menu
### Templates
### Views
### Communication with ubus
### Dependencies of LuCI2


# mountd – Technical Reference

## What is mountd?
## Help with the development of mountd
## Why do we want mountd?
## Dependencies of mountd

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


# netifd (Network Interface Daemon) – Technical Reference

### What is netifd?
### Debugging
### Help with the development of netifd
### Why do we want netifd?

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

# rpcd: OpenWrt ubus RPC daemon for backend server
### Default plugins
## plugin executables
#!/bin/sh

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

# Sysupgrade – Technical Reference
# Sysupgrade – Technical Reference
## Usage
## Options

## How It Works



# ubox
## OpenWrt – operating system architecture

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

# EasyCwmp (CPE WAN Management Protocol daemon)
## EasyCwmp Presentation in Broadban Worl Forum
## Compliant Standards

## EasyCwmp design
## Benefits

## Interoperability





## Install
#### EasyCwmp
#### microxml

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

# Xenomai - real-time framework inside OpenWrt
# Xenomai - real-time framework inside OpenWrt
## Pre-condition
## Status
