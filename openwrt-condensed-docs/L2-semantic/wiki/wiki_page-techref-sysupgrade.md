---
title: "Sysupgrade \u2013 Technical Reference"
module: wiki
origin_type: wiki_page
token_count: 2609
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-sysupgrade.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
language: text
---
# Sysupgrade – Technical Reference

This information is based upon v21.02, last updated for [commit 6d266ef158 on 2022-02-10](https://github.com/openwrt/openwrt/tree/6d266ef158).

# Sysupgrade – Technical Reference

In contrast to `opkg`, `mtd` and others, `sysupgrade` is merely a shell script: `/sbin/sysupgrade` intended to facilitate easy updates.

## Usage

This page lists all `sysupgrade` command-line options. For the overall upgrade procedure and typical usage, please read [OpenWrt OS upgrade procedure (sysupgrade or LuCI)](/docs/guide-user/installation/generic.sysupgrade) instead.

## Options

sysupgrade supports the following options

    Usage: /sbin/sysupgrade [<upgrade-option>...] <image file or URL>
           /sbin/sysupgrade [-q] [-i] [-c] [-u] [-o] [-k] <backup-command> <file>

    upgrade-option:
            -f <config>  restore configuration from .tar.gz (file or url)
            -i           interactive mode
            -c           attempt to preserve all changed files in /etc/
            -o           attempt to preserve all changed files in /, except those
                         from packages but including changed confs.
            -u           skip from backup files that are equal to those in /rom
            -n           do not save configuration over reflash
            -p           do not attempt to restore the partition table after flash.
            -k           include in backup a list of current installed packages at
                         /etc/backup/installed_packages.txt
            -T | --test
                         Verify image and config .tar.gz but do not actually flash.
            -F | --force
                         Flash image even if image checks fail, this is dangerous!
            -q           less verbose
            -v           more verbose
            -h | --help  display this help

    backup-command:
            -b | --create-backup <file>
                         create .tar.gz of files specified in sysupgrade.conf
                         then exit. Does not flash an image. If file is '-',
                         i.e. stdout, verbosity is set to 0 (i.e. quiet).
            -r | --restore-backup <file>
                         restore a .tar.gz created with sysupgrade -b
                         then exit. Does not flash an image. If file is '-',
                         the archive is read from stdin.
            -l | --list-backup
                         list the files that would be backed up when calling
                         sysupgrade -b. Does not create a backup file.

WARNING: Trying to copy all files from `/etc` with the `-c` option in a sysupgrade may cause unwanted version-specific files like `/etc/apk/world` to be included. That may cause incompatibilities in the new version.

WARNING: Preserving files across sysupgrades [can be fatal](this>docs/techref/preinit_mount#mount_root_filesystem) (see '[NOTE](../wiki/wiki_page-techref-luci2.md): ...') on systems with weak cpu and exceptionally large rootfs_data partitions.

Files to be preserved depend on the following:

- `/etc/sysupgrade.conf` - customizable backup configuration.
- `/lib/upgrade/keep.d/*` - system configurations provided by specific packages preserved by default.
- `opkg list-changed-conffiles` - list of files derived by package manager.
- `-o` will cause the entire `/overlay` directory to be saved (with the `-u` caveat below).
- `-n` will cause *NO* files will be saved and all configuration settings will be initialized from default values.
- `-u` will prevent preservation of any file that has not been changed since the last sysupgrade. This prevents the need for programs to migrate an old configuration and reduces time needed for sysupgrade.
- `-f` will *COMPLETELY OVERRIDE* all behaviour described above. Instead, the exact files provided in the .tar.gz file will be extracted into `/overlay/upper` after the sysupgrade.

**Q:** Does this mean, I make an archive.tar.gz of /etc and /root for example and sysupgrade -f archive.tar.gz will flash the router and afterwards restores the configs from this archive?

**A:** That's what is says: 'restore configuration from .tar.gz (file or url)'. Anything archived in the tgz will be written to /overlay after the flash. This way you can hand-pick the files that will be the system after new firmware boot.

## How It Works

The `sysupgrade` process starts with the execution of `/sbin/sysupgrade`. The below list describes its behavior.

1.  Parse command line and validate no mutually exclusive options passed.
2.  At this point, sysupgrade calls `include /lib/upgrade` -- a function in `/lib/functions.sh` that will source all `*.sh` files in the given directory.
    1.  [NOTE](../wiki/wiki_page-techref-luci2.md): An optional, platform-specific `/lib/upgrade/platform.sh` can override behavior, so for a full understanding, you should examine this file. (See `target/linux/<arch>/<sub-arch>/base-files/lib/upgrade/platform.sh` in your source tree.)
    2.  The optional functions `platform_copy_config` and `platform_do_upgrade` are at the end of this list.
3.  Create list of files to preserve and store them in `/tmp/sysupgrade.tgz` (unless `-f` was supplied).
4.  If the image supplied is an http or https URL, `wget` is run to retrieve it.
5.  The firmware image is saved (if a URL) or copied to `/tmp/sysupgrade.img`.
6.  Validates the firmware image, and that the root `compatible` node in the device tree file matches the value in `/sys/firmware/devicetree/base/compatible` from the existing firmware's device tree. (May be overridden with `-F`).
7.  Copies `/sbin/upgraded` into `/tmp`
8.  Builds a [json message](https://git.openwrt.org/?p=project/procd.git;a=blob;f=system.c;h=83aea423ec6aaceedca54e42aea18ce90d7ddfa1;hb=37eed131e9967a35f47bacb3437a9d3c8a57b3f4#l627) and sends a message, via `ubus`, to `procd`, to initiate the upgrade. Among other things, the message specifies:
    1.  path: `/tmp/sysupgrade.img`,
    2.  backup: `/tmp/sysupgrade.tgz` if any files are being preserved, unset otherwise,
    3.  force: if `-F` was supplied,
    4.  and command: `/lib/upgrade/do_stage2`.
9.  The `sysupgrade` function in `procd` will unpack and validate the message, then validate the firmware image and such.
10. Notably, `procd` does not terminate any services here.
11. **This is where things get funky!** If all is well, we call [sysupgrade_exec_upgraded](https://git.openwrt.org/?p=project/procd.git;a=blob;f=sysupgrade.c;h=fc588b0248353137d4b81fce130d2d35d8dfa710;hb=37eed131e9967a35f47bacb3437a9d3c8a57b3f4#l28), which further parses the original json and then passes control to `/sbin/upgraded` via `execvp`.
    1.  Note that at boot time, the kernel passes control to `/sbin/init` as PID=1, which in turn `exec`s `/sbin/procd`. Thus, this results in `/tmp/upgraded` becoming the new PID=1 ("init") process.
    2.  At this point, service management is no longer possible.
12. `/sbin/upgraded` executes the command passed (`/lib/upgrade/stage2`) with parameters. The remaining sequence runs from this shell script.
    1.  `/bin/sh /lib/upgrade/stage2` is run via fork/exec, so is not PID1.
13. Terminate (`SIGKILL`) all `telnet`, `ash`, and `dropbear` processes.
14. Loop over all remaining processes, sending them the TERM signal.
15. Loop over all remaining processes, sending them the KILL signal.
16. Create a new RAM filesystem, mount it, and copy over a very small set of binaries into it.
17. Change root into the new RAM filesystem.
18. Remount `/overlay` read-only, and lazy-unmount it.
19. Write the upgraded firmware to disk. If `platform_do_upgrade` is defined then it is run. Otherwise, this is done via [default_do_upgrade](https://github.com/openwrt/openwrt/blob/6d266ef158/package/base-files/files/lib/upgrade/common.sh#L301), using `mtd` to flash the firmware.
20. If any files are being preserved, the tarball is passed via `mtd`'s `-j` option. This causes mtd to [write a raw jffs2 inode (with id = 1) and file data](https://github.com/openwrt/openwrt/blob/6d266ef158/package/system/mtd/src/jffs2.c#L163), resulting in the tarball to appearing as `/sysupgrade.tgz` once the jffs2 file system is mounted.
    1.  A consequence is that the mtd sources are intimately tied to the jffs2 implementation and can break if changes are made to jffs2 in the kernel (it should probably be using the uapi header from the kernel `make headers_install` instead of copying it into its source tree).
    2.  After reboot, this file will be extracted by `/lib/preinit/80_mount_root` (`/sbin/init` during [preinit](https://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;h=46411aa413a2a65614cfc765d3d6a42dee200532;hb=37eed131e9967a35f47bacb3437a9d3c8a57b3f4#l157) --\> `/bin/sh /etc/preinit` --\> `/lib/preinit/80_mount_root`)
    3.  and finally deleted by `/etc/rc.d/S95done` (`/sbin/procd` --\> at `STATE_INIT` --\> `procd_inittab_run("sysinit");` --\> `/etc/inittab`)
21. If a `platform_copy_config` is implemented, it is run at this point.
22. Unmount any remaining filesystems.
23. Reboot.

There are plenty of potential deficiencies in this process, among them:

- Hardcodes a list of "potentially-interfering" / interactive processes (`ash`, `telnet`, `dropbear`) to kill first; this is not exhaustive or up-to-date (e.g., `telnet` is no longer in the base install; `openssh` is not handled).
- Does not give processes much time in between TERM and KILL signals.
- Does not utilise `procd` to tear down services.
- Susceptible to fork bombs.
- Easily broken by open files on storage devices (e.g., for swap, or explicitly opened), as these can prevent unmounting `/overlay`.
- Does not handle errors (e.g., I/O) in writing the disk image, potentially leaving a partially-upgraded system upon reboot.
- Various error conditions are ignored in `mtd`, which can also result in preserved files not being written to the new jffs2 file system or and leaving the file system corrupted, but without reporting an error.

Many of these deficiencies are historical artifacts, remaining simply because no one has fixed them.

Thanks to Michael Jones for writing most of this down on the mailing list [\[OpenWrt-Devel\] Sysupgrade and Failed to kill all processes](http://lists.openwrt.org/pipermail/openwrt-devel/2020-May/029074.html).

TODO: Explain how this process works during failsafe mode.
