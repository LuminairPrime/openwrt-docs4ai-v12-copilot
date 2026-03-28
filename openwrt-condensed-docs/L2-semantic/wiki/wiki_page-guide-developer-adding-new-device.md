---
title: Adding a new device
module: wiki
origin_type: wiki_page
token_count: 3029
source_file: L1-raw/wiki/wiki_page-guide-developer-adding-new-device.md
last_pipeline_run: '2026-03-27T20:02:39.961617+00:00'
source_url: https://openwrt.org/docs/guide-developer/adding_new_device
language: text
ai_summary: The 'Adding a new device' module provides a comprehensive guide for developers looking to integrate new hardware into OpenWrt. It emphasizes the importance of examining recent commits and using local grep searches to identify necessary files for device integration. Key directories and their functions are outlined, including base-files for firmware integration, device tree source files, and image configuration. Additionally, it covers the process of making the new device visible in the make menuconfig and the organization of kernel patches.
ai_when_to_use: This module is useful when you need to add support for a new device in OpenWrt, particularly for custom or unsupported hardware.
ai_related_topics:
- target/linux/<arch_name>/base-files/etc/
- target/linux/<arch_name>/base-files/lib/
- target/linux/<arch_name>/dts/
- target/linux/<arch_name>/image/
- target/linux/<arch_name>/<board_name>/
- target/linux/<arch_name>/modules.mk
---
# Adding a new device

A good all-round advice would be to start by looking at recent commits about adding a new device, to see what files where changed and how. Many files try to be as self-explanatory as possible, most of the times just opening them will be enough to understand their function.

## Learn by example

### Search by grep locally

A good method is learn by example, so you can do:

    grep -lri mt300a target/

The result is minimal list of files required to add a new board:

    target/linux/ramips/base-files/etc/board.d/01_leds
    target/linux/ramips/base-files/etc/board.d/02_network
    target/linux/ramips/base-files/lib/upgrade/platform.sh
    target/linux/ramips/base-files/lib/ramips.sh
    target/linux/ramips/dts/GL-MT300A.dts
    target/linux/ramips/image/mt7620.mk

### Search by Git commit

[Browse the source filtered by "add support for"](https://git.openwrt.org/?p=openwrt%2Fopenwrt.git&a=search&h=HEAD&st=commit&s=add+support+for) and checkout the `diff` for newly added device

## Important files

This is a general map of where most important files are located:

### /target/linux/\<arch_name\>/base-files/etc/…

This folder contains files and folders that will be integrated in the firmware’s /etc folder.

These are its subfolders and files:

- **…board.d/** scripts for defining device-specific default hardware, like leds and network interfaces.
- **…hotplug.d/** scripts for defining device-specific actions to be done automatically on hotplugging of devices
- **…init.d/** scripts for defining device-specific actions to be done automatically on boot
- **…uci-defaults/** files for defining device-specific uci configuration items. Used e.g. for config migration after syntax changes.
- **…diag.sh** defines what is the led to use for error codes for each board

*Note that some of these functions are now done in the DTS for the board.*

### /target/linux/\<arch_name\>/base-files/lib/…

This folder contains files and folders that will be integrated in the firmware’s /lib folder.

These are its subfolders and files:

- **…\<arch_name\>.sh** human-readable full board name associated to script-safe board name
- **…preinit/** common \<arch_name\> preinit startup scripts
- **…upgrade/** common \<arch_name\> upgrade scripts

### /target/linux/\<arch_name\>/base-files/sbin

This folder contains files and folders that will be integrated in the firmware’s /sbin folder, usually common \<arch_name\> sbin scripts and tools.

### /target/linux/\<arch_name\>/dts/

Device tree source files, or dts for short.

*Certain architectures have the DTS directory deeper down. ARM devices, for example, typically have it located at `files-X.yy/arch/arm/boot/dts/`*

*If the DTS or DTSI file is already present in upstream Linux, they will usually not be present in the OpenWrt source. Configuring for the target and running `make target/linux/{clean,prepare}` will download and patch Linux, allowing the resulting file to be found in the `build_dir`*

### /target/linux/\<arch_name\>/image/

Configuration needed to build device-specific flashable images.

### /target/linux/\<arch_name\>/\<board_name\>/

Board-specific configuration.

### /target/linux/\<arch_name\>/modules.mk

Arch-specific kernel module config file for menuconfig

### Making new device appear in make menuconfig

After edit the files above, you need to touch the makefiles

    touch target/linux/*/Makefile

## Patches

The patches-\* subdirectories contain the kernel patches applied for every target.
All patches should be named 'NNN-lowercase_shortname.patch' and sorted into the following categories:

**0xx** - upstream backports
**1xx** - code awaiting upstream merge
**2xx** - kernel build / config / header patches
**3xx** - architecture specific patches
**4xx** - mtd related patches (subsystem and drivers)
**5xx** - filesystem related patches
**6xx** - generic network patches
**7xx** - network / phy driver patches
**8xx** - other drivers
**9xx** - uncategorized other patches
 All patches must be written in a way that they are potentially upstreamable, meaning:

1.  they must contain a **proper subject**
2.  they must contain a **proper commit message** explaining what they change
3.  they must contain a **valid Signed-off-by line**

## Testing images

Test firmware images without writing them to flash by using ramdisk images.

In **make menuconfig** select **Target Images** and then you can select the **ramdisk** option.

This will create an image with kernel + initramfs, that will have **initramfs** in the name. The resulting image can be loaded in the device through the bootloader's tftp function and should boot to a prompt without relying on flash/filesystem support.

## Tips and tricks

### Getting a shell on the target device

In order to collect relevant data for a port of OpenWrt to the device of interest one wants shell access. Most devices though do not offer a way to get a shell with telnet or ssh.

#### Abuse Unsanitized User Input

Some router offers ping test or NTP server configuration and may not properly sanitize user input. Try to enter shell script and see if you are lucky. You may need some `javascript` knowledges to disable client-side input validation.

##### Starting telnetd

``` bash
$( /bin/busybox telnetd -l/bin/sh -p23 & )
```

##### Obtain the password hash using HTTP or use `sed` to delete/change the default password if telnet login is required

``` bash
$( cp /etc/shadow /www )
$( cp /etc/passwd /www )
```

Then try to download them to your computer and crack the hash

#### Downgrade to older firmware

Some router may try to download a firmware file (e.g. [TP-Link Archer C2 AC750](/toh/tp-link/archer_c2_ac750)) from specific private IP at the beginning of booting, which allow user to downgrade to older firmware

#### Downgrade by Serial access

Serial access may allow you to enter console mode of u-boot for flashing/loading other firmware. Usually soldering is required. See [Generic flashing over the Serial port](/docs/guide-user/installation/generic.flashing.serial)

#### HTTP Server Vulnerability

Some routers may be running outdated/insecure HTTP server and may be vulnerable to buffer overflow or other attack

#### Netgear

With [netgear-telnetenable](/toh/netgear/telnet.console) many Netgear devices can be opened up for telnet access. Also see [GitHub: insanid/NetgearTelnetEnable](https://github.com/insanid/NetgearTelnetEnable). When such means cannot be used, one could try to flash an image build from the sources published by the vendor with telnetd enabled.

With [nmrpflash](https://github.com/jclehner/nmrpflash) many Netgear devices can be flashed. Devices that are compatible with this tool become effectively unbrickable.

### Collecting relevant data

On [WikiDevi](https://wikidevi.com/wiki/Main_Page) lots of information can be found, e.g. the FCC ID is very useful when searching for documentation, datasheets and internal photo's (to be able to distinguish used chips without having to open the casing).

Typically one can use the following commands:

``` bash
dmesg                          # log buffer might be to small, see note 1.
cat /proc/cmdline
cat /proc/cpuinfo
cat /proc/meminfo
cat /proc/devices
ls /sys/devices/platform
cat /proc/mtd
cat /sys/class/mtd/mtd*/offset # Linux 4.1 and newer, see note 2.
ifconfig -a
ls /sys/class/net
brctl show
cat /sys/kernel/debug/gpio     # GPIO information
```

**Note 1:** Often the log buffer is to small and the earliest messages may be missing from the information retrieved with `dmesg`. If one build a stock image from the sources the vendor has published, a larger buffer size can be set within the kernel config.

**Note 2:** <http://lxr.free-electrons.com/source/Documentation/ABI/testing/sysfs-class-mtd>

Another useful tool for getting information for setting LEDs might be [gpiodump](https://github.com/jclehner/gpiodump-mt7620), a MT7620 GPIOMODE register dumper (RAMIPS).

### Getting collected data from a device

Because of the limited space, common file transfer utilities such as rsync/curl/ssh/scp/ftp/http/tftp may not be available, a stripped down version/applet may be available from busybox.

Assume the router ip is `192.168.0.123`, and the file to be transfer located at `/tmp/important-data.txt`.

#### Use SCP to download

Your ssh server built into the device may have SCP capabilities without an sftp server. It may also only support legacy SCP (requiring the -O option) not scpv2.

i.e.

##### Receiver

    scp -O <source> <dest>

For example:

     scp -O root@192.168.1.1:/tmp/important-data.txt ~/

#### HTTP by `httpd` and `busybox mount`

If the web interface are served from `/www`.

##### Sender

``` bash
mount -o bind /tmp /www
```

##### Receiver

``` bash
wget http://192.168.0.123/important-data.txt
```

#### FTP by `busybox ftpput`

##### Receiver

Setup an FTP server. Add an anonymous account with write permission

``` bash
python -m pyftpdlib -w -p 21
```

##### Sender

``` bash
busybox ftpput 192.168.0.123 important-data.txt /tmp/important-data.txt
```

#### netcat by `busybox nc`

##### Receiver

``` bash
busybox nc -l -p 12345 > important-data.txt
```

##### Sender

``` bash
cat /tmp/important-data.txt | busybox nc 192.168.0.123:12345
```

#### TFTP by `busybox tftp`

##### Receiver

Setup a tftp server

##### Sender

``` bash
busybox tftp -p -l /tmp/important-data.txt -r important-data.txt 192.168.0.123
```

#### Use Curl to upload

Depending on what is compiled into your curl binary if available you may also be able to auth, use ftp/tftp etc. Extracts from curl man page:

    It supports these protocols: DICT, FILE, FTP, FTPS, GOPHER, GOPHERS,
           HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, MQTT, POP3, POP3S, RTMP, RTMPS, RTSP, SCP, SFTP, SMB, SMBS, SMTP, SMTPS, TELNET,  TFTP,  WS
           and WSS. The command is designed to work without user interaction.

           curl  offers  a busload of useful tricks like proxy support, user authentication, FTP upload, HTTP post, SSL connections, cookies,
           file transfer resume and more. As you will see below, the number of features will make your head spin.

           -T, --upload-file <file>
                  This transfers the specified local file to the remote URL. If there is no file part in the specified URL, curl will  append
                  the  local  file  name.  [NOTE](../wiki/wiki_page-techref-luci2.md) that you must use a trailing / on the last directory to really prove to Curl that there is no
                  file name or curl will think that your last directory name is the remote file name to use. That will most likely cause  the
                  upload operation to fail. If this is used on an HTTP(S) server, the PUT command will be used.

                  Use  the  file name "-" (a single dash) to use stdin instead of a given file.  Alternately, the file name "." (a single pe‐
                  riod) may be specified instead of "-" to use stdin in non-blocking mode to allow reading server output while stdin is being
                  uploaded.

                  You can specify one -T, --upload-file for each URL on the command line. Each -T, --upload-file + URL pair specifies what to
                  upload and to where. curl also supports "globbing" of the -T, --upload-file argument, meaning that you can upload  multiple
                  files to a single URL by using the same URL globbing style supported in the URL.

                  When  uploading  to  an SMTP server: the uploaded data is assumed to be RFC 5322 formatted. It has to feature the necessary
                  set of headers and mail body formatted correctly by the user as curl will not transcode nor encode it further in any way.

                  -T, --upload-file can be used several times in a command line

                  Examples:
                   curl -T file https://example.com
                   curl -T "img[1-1000].png" ftp://ftp.example.com/
                   curl --upload-file "{file1,file2}" https://example.com

                  See also -G, --get and -I, --head.

#### Copy from terminal

If all of the above tools/applets are unavailable, you may copy from telnet terminal but it may not work for binary file.

base64 would be a common choice to work around this limitation, but many routers lack such a command. You can first escape binary data to screen-safe hexadecimal by piping to busybox hexdump on the router:

``` bash
hexdump -v -e '/1 "%02x"'
```

You can then reverse it on the computer with the following command:

``` bash
xxd -r -p
```
