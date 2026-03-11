---
title: The Boot Process
module: wiki
origin_type: wiki_page
token_count: 3243
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-process-boot.md
last_pipeline_run: '2026-03-11T14:46:50.602050+00:00'
language: text
---
# The Boot Process

 As noted below, this page is woefully out of date

> [![NOTE](../wiki/wiki_page-techref-luci2.md)]
> Please also see [requirements.boot.process](/docs/techref/requirements.boot.process)
>
> This guide it not up-to-date! It does not mention [procd](/docs/techref/procd)

This guide shall help you understand, e.g.

- When is it time for [kexec](/docs/guide-user/advanced/kexec) and when for [extroot_configuration](/docs/guide-user/additional-software/extroot_configuration) (see particularly [extroot.theory](/docs/guide-user/additional-software/extroot_configuration/extroot.theory))?
- How does the [OpenWrt FailSafe](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) work?
- the [flash.layout](/docs/techref/flash.layout) and the combination of [Utilization of file systems in OpenWrt](/docs/techref/filesystems#implementation_in_openwrt)
- When does the tmpfs get mounted and `/tmp` symlinked to it and `/var` symlinked to `/tmp`?

- [Preinit mount](/docs/techref/preinit_mount) Preinit, Mount Root, and First Boot Scripts
- [Init Scripts](/docs/techref/initscripts) Init script implementation reference
- [Block Mount](/docs/techref/block_mount) Block Device Mounting

## Process Trinity

The Machine gets powered on and some very very basic very low level hardware stuff gets done. You could connect to it over the [JTAG Port](/docs/techref/hardware/port.jtag) and issue commands.

### Bootloader

1.  the [bootloader](bootloader) on the flash gets executed
2.  the bootloader performs the [POST](https://en.wikipedia.org/wiki/Power-on self-test), which is a low-level hardware initialization
3.  the bootloader decompresses the Kernel image from its (known!) location on the flash storage into main memory (=RAM)
4.  the bootloader executes the Kernel with `init=...` option (default is ~~`/etc/preinit`~~ `/sbin/init`)

### Kernel

1.  the Kernel further bootstraps itself (sic!)
2.  issues the command/op-code `start_kernel`
3.  kernel scans the mtd partition *rootfs* for a valid superblock and mounts the SquashFS partition (which contains `/etc`) once found. (More info at [filesystems#technical_details](/docs/techref/filesystems#technical_details))
4.  `/etc/preinit` does pre-initialization setups (create directories, mount fs, /proc, /sys, ... )
5.  the Kernel `mounts` any other partition (e.g. jffs2 partition) under *rootfs (root file system)*. see [flash.layout](/docs/techref/flash.layout), [preinit and root mount](/docs/techref/preinit_mount#mount.root.filesystem), and also [udev](https://en.wikipedia.org/wiki/udev) FIXME **make sure**
6.  if "INITRAMFS" is not defined, calls `/sbin/init` (the mother of all processes)
7.  finally some *kernel thread* becomes the userspace `init` process

### Init

The user space starts when kernel mounts *rootfs* and the very first program to run is (by default) `/sbin/init`. Please remember, that the interface between application and kernel is the `clib` and the syscalls it offers.

1.  init reads `/etc/inittab` for the "sysinit" entry (default is "::sysinit:/etc/init.d/rcS S boot")
2.  init calls `/etc/init.d/rcS S boot`
3.  `rcS` executes the symlinks to the actual startup scripts located in `/etc/rc.d/S##xxxxxx` with option `"start"`:
4.  after rcS finishes, system should be up and running

#### Vanilla Startup Scripts

***[NOTE](../wiki/wiki_page-techref-luci2.md):*** [](/Packages/) you install with `opkg` will likely add additional scripts!

|              |                                                                                                                                                                                                                 |
|:-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| S05defconfig | create config files with default values for platform (if config file is not exist), really does this on first start after OpenWrt installed (copy unexisted files from /etc/defconfig/\$board/ to /etc/config/) |
| S10boot      | starts hotplug-script, mounts filesystesm, starts .., starts syslogd, ...                                                                                                                                       |
| S39usb       | `mount -t usbfs none /proc/bus/usb`                                                                                                                                                                             |
| S40network   | start a network subsystem (run /sbin/netifd, up interfaces and wifi                                                                                                                                             |
| S45firewall  | create and implement firewall rules from /etc/config/firewall                                                                                                                                                   |
| S50cron      | starts `crond`, see -\> `/etc/crontabs/root` for configuration                                                                                                                                                  |
| S50dropbear  | starts `dropbear`, see -\> `/etc/config/dropbear` for configuration                                                                                                                                             |
| S50telnet    | checks for root password, if non is set, `/usr/sbin/telnetd` gets started                                                                                                                                       |
| S60dnsmasq   | starts `dnsmasq`, see -\> `/etc/config/dhcp` for configuration                                                                                                                                                  |
| S95done      | executes `/etc/rc.local`                                                                                                                                                                                        |
| S96led       | load a LED configuration from /etc/config/system and set up LEDs (write values to /sys/class/leds/\*/\*)                                                                                                        |
| S97watchdog  | start the watchdog daemon (/sbin/watchdog)                                                                                                                                                                      |
| S99sysctl    | interprets `/etc/sysctl.conf`                                                                                                                                                                                   |

The `init` daemon will run all the time. On a shutdown command, `init`

1.  reads `/etc/inittab` for shutdown (default is "::shutdodwn:/etc/init.d/rcS K stop")
2.  `init` calls `/etc/init.d/rcS K stop`
3.  rcS executes the shutdown scripts located in /etc/rc.d/K##xxxxxx with option "stop"
4.  system halts/reboots

|             |                                                    |
|-------------|----------------------------------------------------|
| K50dropbear | kill all instances of dropbear                     |
| K90network  | down all interfaces and stop netifd                |
| K98boot     | stop logger daemons: /sbin/syslogd and /sbin/klogd |
| K99umount   | writes caches to disk, unmounts all filesystems    |

## Detailed boot sequence

- [boot process example for blackfin devices](http://docs.blackfin.uclinux.org/doku.php?id=bootloaders)

### Boot loader

After the bootloader (grub, in this example) initializes and parses any options that are presented at the boot menu, the bootloader loads the kernel.

Example from the openwrt-x86-ext2-image.kernel file entry for normal boot:

- "kernel /boot/vmlinuz root=/dev/hda2 init=/etc/preinit \[rest of options\]"

This entry in the boot/grub/menu.lst file tells grub that the kernel is located under the /boot directory and the filename is vmlinuz. The rest of the lines are the options that are passed to the kernel. To see how the kernel was started, you can view the options by reading the /proc/cmdline file. You can see what options were passed from grub by logging into the device and typing "cat /proc/cmdline".

For my test system, the options that were passed to the kernel at load time was:

- "root=/dev/hda2 rootfstype=ext2 init=/etc/preinit noinitrd console=ttyS0,38400,n,8,1 reboot=bios"

The options are:

1.  **root**: root device/partition where the rest of the OpenWrt system is located
2.  **rootfstype**: Format for the root partition - ext2 in this example
3.  **init**: The first program to call after the kernel is loaded and initialized
4.  **noinitrd**: All drivers for access to the rest of the system are built into the kernel, so no need to load an initial ramdisk with extra drivers
5.  **console**: Which device to accept console login commands from - talk to ttyS0 (first serial port) at 38400 speed using no flow control, eight data bits and one stop bit. See the kernel documentation for other options
6.  **reboot**: Not sure, but I believe that this option tells the kernel how to perform a reboot

The first program called after the kernel loads is located at the kernel options entry of the boot loader. For grub, the entry is located in the openwrt--.image.kernel.image file in the /boot/grub/menu.lst file.

\[ [NOTE](../wiki/wiki_page-techref-luci2.md): See the man page on grub for all of the grub parameters \] In this example, the entry "init=/etc/preinit" tells the kernel that the first program to run after initializing is "preinit" found in the "/etc" directory located on the disk "/dev/hda" and partition "hda2".

### /etc/preinit script

The preinit script's primary purpose is initial checks and setups for the rest of the startup scripts. One primary job is to mount the /proc and /sys pseudo filesystems so access to status information and some control functions are made available. Another primary function is to prepare the /dev directory for access to things like console, tty, and media access devices. The final job of preinit is to start the init daemon process itself.

### Busybox init

Init is considered the "Mother Of All Processes" since it controls things like starting daemons, changing runlevels, setting up the console/pseudo-consoles/tty access daemons, as well as some other housekeeping chores.

Once init is started, it reads the /etc/inittab configuration file to tell it what process to start, monitor for certain activities, and when an activity is triggered to call the relevant program.

The init program used by busybox is a minimalistic daemon. It does not have the knowledge of runlevels and such, so the config file is somewhat abbreviated from the normal init config file. If you are running a full linux desktop, you can "man inittab" and read about the normal init process and entries. Fields are separated by a colon and are defined as:

- \[ID\] : \[Runlevel(s)\] : \[Action\] : \[Process to execute \]

For busybox init, the only fields needed are the "ID" (1st), "Action" (3rd) and "Process" (4th) entries. Busybox init has several caveats from a normal init: the ID field is used for controlling TTY/Console, and there are no defined runlevels. A minimalistic /etc/inittab would look like:

1.  ::sysinit:/etc/init.d/rcS S boot
2.  ::shutdown:/etc/init.d/rcS K stop
3.  tts/0::askfirst:/bin/ash --login
4.  ttyS0::askfirst:/bin/ash --login
5.  tty1::askfirst:/bin/ash --login

Lines 1 and 2 with a blank ID field indicate they are not specific to any terminal or console. The other lines are directed to specific terminals/consoles.

Notice that both the "sysinit" and "shutdown" actions are calling the same program (the "/etc/init.d/rcS" script). The only difference is the options that are passed to the rcS script. This will become clearer later on.

At this point, init has parsed the configuration file and is looking for what to do next. So, now we get to the "sysinit" entry: call /etc/init.d/rcS with the options "S" and "boot"

## /etc/init.d/rcS Script At Startup

At this point, all basic setup has been done, all programs and system/configuration files are accessible, and we are now ready to start the rest of the processes.

The rcS script is pretty simplistic in it's function - it's sole purpose is to execute all of the scripts in the /etc/rc.d directory with the appropriate options. if you paid attention to the sysinit entry, the rcS script was called with the "S" and "boot" options. Since we called rcS with 2 options ("S" and "boot"), the rcS script will substitute \$1 with "S" and \$2 with "boot". The relevant lines in rcS are:

       -  for i in /etc/rc.d/$1* ; do
      2.      [ -x $i ] && $i $2
      3.  done

The basic breakdown is:

1.  Execute the following line once for every entry (file/link) in the /etc/rc.d directory that begins with "S"
2.  If the file is executable, execute the file with the option "boot"
3.  Repeat at step 1, replacing \$i with the next filename until there are no more files to check

Unlike Microsoft programs, Linux uses file permissions rather than filename extensions to tell it if this entry is executable or not. For an explanation of file permissions, see "man chmod" on a Linux/Unix machine on explanations for permissions and executable files.

If you look at the /etc/rc.d directory, you may notice that some scripts have relevant links for startup, but no shutdown (i.e., /etc/init.d/httpd), while some others have no startup script, but do have a shutdown script (i.e., /etc/init.d/umount).

In the case of httpd (the webserver), it doesn't matter if it dies or not, there's nothing to clean up before quitting.

On the other hand, the umount script MUST be executed before shutdown to ensure that all data is flushed to the media before unmounting of any relevant storage media, otherwise data corruption could occur. There's no need to call unmount at startup, since storage media mounting is handled somewhere else (like /etc/preinit), so there's no startup script for this one.

After the last startup script is executed, you should have a fully operational OpenWrt system.

## Notes

- See also [Booting](https://en.wikipedia.org/wiki/Booting) on the boot process in general.
- [log.essentials](/docs/guide-user/base-system/log.essentials) busybox-klogd and busybox-syslogd
- watchdog: <http://www.google.com/search?sclient=psy&hl=en&source=hp&q=openwrt+watchdog&btnG=Search>
- `pppd` is configured only in [network](/doc/uci/network), need this for you [internet.connection](/docs/guide-user/network/wan/internet.connection)
- see [init](https://en.wikipedia.org/wiki/init), [init manpage](http://linux.die.net/man/8/init), <http://linux.die.net/sag/init-intro.html>
