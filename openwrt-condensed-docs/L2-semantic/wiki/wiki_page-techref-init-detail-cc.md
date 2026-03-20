---
title: 'Init (User space boot) reference for Chaos Calmer: procd'
module: wiki
origin_type: wiki_page
token_count: 5589
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-init-detail-cc.md
last_pipeline_run: '2026-03-12T22:39:22.932543+00:00'
language: text
ai_summary: The Init (User space boot) reference for Chaos Calmer details the implementation of the user space boot sequence in OpenWrt, specifically focusing on the role of procd as the primary process. Procd, which replaces the traditional init system, is responsible for managing services and handling hotplug events after the initial preinit steps are completed by `/sbin/init`. The document outlines the boot process, including filesystem mounting and kernel module loading, as well as the source code paths followed during execution. It serves as a technical reference for developers looking to understand or contribute to the procd implementation in the Chaos Calmer release.
ai_when_to_use: This documentation is useful for developers working on the boot process of OpenWrt in the Chaos Calmer release, particularly those interested in modifying or extending the functionality of procd.
ai_related_topics:
- procd
- init
- kmodloader
- procd_coldplug
- mount_root
---
# Init (User space boot) reference for Chaos Calmer: procd

Analysis of how the user space part of the boot sequence is implemented in OpenWrt, Chaos Calmer release.

## Procd replaces init

On a fully booted Chaos Calmer system, pid 1 is `/sbin/procd`:

    root@openwrt:~# ps
      PID USER       VSZ STAT COMMAND
        1 root      1440 S    /sbin/procd
        ...

At boot, Linux kernel starts `/sbin/init` as the first user process. In Chaos Calmer, `/sbin/init` does the preinit/failsafe steps, those that depend only on the read-only partition in flashed image, then execs (that is: is replaced by) `/sbin/procd` to continue boot as specified by the configuration in writable flash partition. Procd started as pid 1 assumes several roles: service manager, hotplug events handler; this as of February 2016, when this research was done. [Procd techref wiki page](/docs/techref/procd) at this point in time is a design document and work in progress, if you are reading here and know/understand procd's semantics and API, please update that page.

Procd sources:
<http://git.openwrt.org/?p=project/procd.git;a=tree;hb=0da5bf2ff222d1a499172a6e09507388676b5a08>
at the commit used to build the procd package in Chaos Calmer release:
`PKG_SOURCE_VERSION:=0da5bf2ff222d1a499172a6e09507388676b5a08`

`/sbin/init` source:
<http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/init.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l71>

## Life and death of a Chaos Calmer system

This is the source code path followed in logical order of execution by the processor in user space while booting Chaos Calmer.

:!: All links to source repositories should show the code at the commit used in Chaos Calmer release.
:!: Pathnames evaluated at preinit time when / is read only have "(/rom)" prepended, to signify the path where the file is found on a fully booted system.

1.  `main(int argc, char **argv)` in /sbin/init, line 71
    User space life begins here. OpenWrt calls this phase "preinit".
    1.  `early()` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/early.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l92)
        Mount filesystems: `/proc`, `/sys`, `/sys/fs/cgroup`, `/dev` (a tmpfs), `/dev/pts`
        Populate `/dev` with entries from `/sys/dev/{char;block}`
        Open `/dev/console` as STDIN/STDOUT/STDERR
        Make directories `/tmp` (optionally on zram), `/tmp/run`, `tmp/lock`, `/tmp/state`

        This accounts for most of the filesystem layout, observed that `/etc/fstab` is a [broken symlink, line 161](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/Makefile;hb=483dac821788b457d349233e770329186a0aa860#l161), with the following additions:
        - `procd_coldplug()` [invoked at hotplug setup time](http://git.openwrt.org/?p=project/procd.git;a=blob;f=state.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l105) will recreate `/dev` from scratch.
        - `/etc/rc.d/S10boot` will invoke `mount_root` to setup a writable filesystem based on extroot or jffs2 overlay or a tmpfs backed [snapshot capable](/docs/guide-user/installation/snapshot) overlay, add some directories and files, and mount debugfs.
    2.  `cmdline()` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/init.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l56)
        Check kernel cmdline for boot parameter "`init_debug={1,2,3,4}`".
    3.  Fork `/sbin/kmodloader (/rom)/etc/modules-boot.d/` [kmodloader source](http://git.openwrt.org/?p=project/ubox.git;a=blob;f=kmodloader.c;hb=907d046c8929fb74e5a3502a9498198695e62ad8#l830)
        Wait up to 120 seconds for `/sbin/kmodloader` to probe the kernel modules declared in `(/rom)/etc/modules-boot.d/`
        At this point in the boot sequence, '/etc/modules-boot.d' is the one from the rom image (`/rom/etc/...` when boot is done). The overlay filesystem is mounted later.

        kmodloader is a multicall binary, invoked as
        '' kmodloader` does ` [main_loader()](http://git.openwrt.org/?p=project/ubox.git;a=blob;f=kmodloader.c;hb=907d046c8929fb74e5a3502a9498198695e62ad8#l732)''
        which reads files in `(/rom)/etc/modules-boot.d/`, looking for lines starting with the name of a module to load, optionally followed by a space and module parameters. There appear to be [special treatment for files with names beginning with a number](http://git.openwrt.org/?p=project/ubox.git;a=blob;f=kmodloader.c;hb=907d046c8929fb74e5a3502a9498198695e62ad8#l788): the modules they list are immediately loaded, then modules from files with name beginning with an ascii char greater than "9" are loaded all together in a final load_modprobe call.
    4.  `uloop_init()` line 116 [(definition)](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l211)
        [Documentation of libubox/uloop.h](/docs/techref/libubox#libuboxulooph) says:
        *Uloop is a loop runner for i/o. Gets in charge of polling the different file descriptors you have added to it, gets in charge of running timers, and helps you manage child processes. Supports epoll and kqueue as event running backends.*
        [uloop.c source in libubox](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l666) says uloop's process management duty is assigned by a call to
        '' [int uloop_process_add(struct uloop_process \*p)](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l492)` `p-\>pid'' is the process id of a child process to monitor and `p->cb` a pointer to a callback function.
        When the managed child process will exit, uloop_run, running in parent context to receive SIGCHLD signal, will trigger execution of the callback.
    5.  `preinit()` line 117 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l86)
        1.  [Forks a "plugd instance"](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l94), line 94
            '' /sbin/procd -h [(/rom)/etc/hotplug-preinit.json](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/system/procd/files/hotplug-preinit.json;hb=483dac821788b457d349233e770329186a0aa860)''
            to listen to kernel uevents for any required firmware or for notification of button pressed, handled by '' [(/rom)/etc/rc.button/failsafe](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/files/etc/rc.button/failsafe;hb=483dac821788b457d349233e770329186a0aa860)''
            as the request to enter failsafe mode. A flag file `/tmp/failsafe_button` containing the value of `${BUTTON}` is created if failsafe has been requested.
        2.  Forks, [at lines 106-111](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l106),
            '' PREINIT=1 /bin/sh [(/rom)/etc/preinit](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/files/etc/preinit;hb=483dac821788b457d349233e770329186a0aa860)''
            a shell to execute `(/rom)/etc/preinit` with `PREINIT=1` in its environment. Submits the child process to uloop management with the callback
            '' [spawn_procd()](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l51)''
            that will exec procd to replace init as pid 1 at completion of `(/rom)/etc/preinit`.
            1.  `/etc/preinit`
                A shell script, fully documented here [preinit_mount#preinit_operation](/docs/techref/preinit_mount#preinit_operation). In short, parse files in `(/rom)/lib/preinit` to build 5 lists of hooks and an environment, then run the hooks from some of the lists depending on the state of the environment.
                One of the steps in a successful boot sequence is to mount the overlay file system with a hook setup by
                '' [(/rom)/lib/preinit/80_mount_root](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/files/lib/preinit/80_mount_root;hb=483dac821788b457d349233e770329186a0aa860)` to call ` [mount_root](http://git.openwrt.org/?p=project/fstools.git;a=blob;f=mount_root.c;hb=09027fc86babc3986027a0e677aca1b6999a9e14)''
                which if extroot is not configured, mounts the writable data partition "rootfs_data" as overlay over the / partition "rootfs". If the data partition is being prepared, overlays a tmpfs in ram.
                Filesystem snapshots are supported; this is a feature listed in Barrier Breaker announce, shell wrapper is `/sbin/snapshot` script. The "`SNAPSHOT=magic`" environment variable is set in `mount_snapshot()` line 330.
    6.  `uloop_run()`, line 118
        At exit of the `(/rom)/etc/preinit` shell script, invokes the callback spawn_procd()
    7.  `spawn_procd()`
        As a callback by uloop_run in pid 1, this is pid 1; execs `/sbin/procd`

2.  `/sbin/procd`
    Execed by pid 1 `/sbin/init`, `/sbin/procd` replaces it as pid 1.
    1.  `setsid()`, line 67
        *The process group ID and session ID of the calling process are set to the PID of the calling process: [man 2 setsid](http://man7.org/linux/man-pages/man2/setsid.2.html)* See also [man 7 credentials](http://man7.org/linux/man-pages/man7/credentials.7.html).
    2.  `uloop_init()`, line 68
        The uloop instance set up before by `/sbin/init` is gone. Creates a new one.
    3.  `procd_signal()`, line 69 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=signal.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l82), line 82.
        Setup signal handlers. Reboot on SIGTERM or SIGINT, poweroff on SIGUSR2 or SIGUSR2.
    4.  `trigger_init()`, line 70 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=service/trigger.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l319)
        Procd triggers on config file/network interface changes, see [procd-init-scripts#procd_triggers_on_config_filenetwork_interface_changes](/docs/guide-developer/procd-init-scripts#procd_triggers_on_config_filenetwork_interface_changes)
        Initialise a run queue. An [example](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=examples/runqueue-example.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8) is the sole documentation. A queued task has an uloop callback invoked when done, here sets the empty queue callback to do nothing.
    5.  `procd_state_next()`, line 74 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=state.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l179)
        Transitions from NONE to EARLY the state of a state machine implemented in `state_enter(void)` used to sequence the remaining boot steps.
    6.  `STATE_EARLY` in `state_enter()`
        1.  Emits "- early -" to syslog,
        2.  Initialise the watchdog,
        3.  `hotplug("/etc/hotplug.json")` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/hotplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l568)
            User space device hotplugging handler setup.
            Static variables in file scope are important. The filename of the script to execute is kept in hotplug.c global scope: `static char * rule_file;`.
            Opens a netlink socket ([man 7 netlink](http://man7.org/linux/man-pages/man7/netlink.7.html)) and handles the file descriptor to uloop, to listen to uevents: kernel messages informing **u**serspace of kernel **events**. See <https://www.kernel.org/doc/pending/hotplug.txt>
            The uloop instance in pid 1 [uses epoll_wait](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l259) to monitor file descriptors, the kernel netlink socket FD is one of them, and is instructed to invoke the callback `hotplug_handler()` on uevent arrival.
            This `hotplug_handler` callback stays active after coldplug, and will handle all uevents the kernel will emit.
        4.  `procd_coldplug()` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/coldplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l40)
            Umounts `/dev/pts` and `/dev`, mounts a tmpfs on `/dev`, creates directories `/dev/shm` and `/dev/pts`, forks `udevtrigger` to reconstruct kernel uevents went unheard before netlink socket opening ("coldplug").
            1.  `udevtrigger`
                Scans `/sys/bus/*/devices`, `/sys/class`; and `/sys/block` if it isn't a subdir of `/sys/class`, writing "add" to the uevent file of all devices. Then the kernel synthesizes an "add" uevent message on netlink. See Injecting events into hotplug via "uevent" in <https://www.kernel.org/doc/pending/hotplug.txt>

                A callback chain, `udevtrigger_complete()` followed by `coldplug_complete()` is attached to completion of the child udevtrigger process, such that the still to be reached `uloop_run()` in procd `main()` function, after all uevents will have been processed, will advance procd state to STATE_UBUS, [line 31](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/coldplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l31).
    7.  `uloop_run`, line 75
        Solicited by udevtrigger in another process, the kernel emits uevents and uloop invokes the user space hotplug handler: the callback
        1.  `hotplug_handler`
            to run `/etc/hotplug.json`.
            1.  The `/etc/hotplug.json` script
                - creates and removes devices files, assigns them permissions,
                - loads firmware,
                - handles buttons by calling scripts in `/etc/rc.button/%BUTTON%` if the uevent has the "`BUTTON`" value,
                - and invokes `/sbin/hotplug-call "%SUBSYSTEM%"` to handle all other subsystem related actions.
                Subystems are: "platform" "net", "input", "usb", "usbmisc", "ieee1394", "block", "atm", "zaptel", "tty", "button" (without BUTTON value, possible?), "usb-serial". "usb-serial" is aliased to "tty" in hotplug.json.
                Documentation of json script syntax? Offline. [Use the source](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=json_script.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8). It is the json representation of the abstract syntax tree of a script in a fairly intuitive scripting language.
                There are 2 levels at which decisions are taken: hotplug.json acts as fast path executor or lightweight dispatcher, the subsystem scripts in /etc/hotplug.d/%SUBSYSTEM%/ do the heavy lifting.
                Uevent messages from the kernel contain key-value pairs passed as environment variables to the scripts. The kernel function
                '' [int add_uevent_var(struct kobj_uevent_env \*env, const char \*format, ...)](http://lxr.free-electrons.com/source/lib/kobject_uevent.c?v=3.18#L387)''
                creates them. This link <http://lxr.free-electrons.com/ident?v=3.18;i=add_uevent_var> provides a list of all places in the Linux kernel where it is used. It is an authoritative reference of the upstream defined uevent variables. Button events are generated by the out of tree kernel modules `button-hotplug` `gpio-button-hotplug` specific to OpenWrt.
                1.  `/sbin/hotplug-call "%SUBSYSTEM%"`
                    is a shell script that scans `/etc/hotlug.d/%SUBSYSTEM%/*` and sources all scripts assigned to a subsystem. "button" subsystem is handled here if the uevent lacks the "BUTTON" value, unlikely or impossible?.
        2.  `STATE_UBUS`
            At end of coldplug uevents processing, the callback [coldplug_complete calls](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/coldplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l34) `procd_state_next` which results in advancing procd to STATE_UBUS.
            "- ubus -" is logged to console, the services infrastructure is initialised, then procd schedules connect to after 1" ([line 67](http://git.openwrt.org/?p=project/procd.git;a=blob;f=ubus.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l64)) and starts `/sbin/ubus` as the system [ubus](/docs/techref/ubus) service.
            Transition to next state is triggered by the callback `ubus_connect_cb` that at the end, line 118, calls `procd_state_ubus_connect()`, line 186, that calls `procd_state_next` to transition to
        3.  `STATE_INIT`
            "- init -" is logged, `/etc/inittab` is parsed and entries
            '' ::askconsole:/bin/ash --login` ` ::sysinit:/etc/init.d/rcS S boot` executed. inittab format is the same as the one from busybox (Busybox example inittab). The "`sysinit'' action" handler
            1.  `runrc`
                instantiates a queue, whose empty handler `rcdone` will advance procd state.
                `runrc` [ignores](http://git.openwrt.org/?p=project/procd.git;a=blob;f=inittab.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l151) the process specification "`/etc/init.d/rcS`" (there is no such a script!), and runs
                1.  `rcS(pattern="S" , param="boot", rcdone)` (line 159)
                    that invokes the equivalent of
                    `_rc(&q, *path="/etc/rc.d", *file="S", *pattern="*", *param="boot")`
                    to enqueue in glob sort order the scripts
                    '' /etc/rc.d/S\* boot` with "`boot''" as the action. `/etc/rc.d/S*` are [symlinks made by rc.common enable](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/Makefile;hb=483dac821788b457d349233e770329186a0aa860#l117) to files in `/etc/init.d`, that are shell scripts with the shebang `#!/bin/sh /etc/rc.common`.
                    Invoking a `/etc/rc.d/S*` script runs `rc.common` that sources the /etc/rc.d/S\* script to set up a context, then invokes the function named as the action parameter ("`boot()`"), in that context.
        4.  `STATE_RUNNING`
            Execution arrives here after rcS scripts are done.
            "- init complete -" is logged.
            This is a stable state, keeping uloop_run in procd.c main() running, mostly waiting on epoll_wait. [Upon receipt of a signal](http://git.openwrt.org/?p=project/procd.git;a=blob;f=signal.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l33) in SIGTERM, SIGINT (reboot), or SIGUSR2, SIGUSR2 (poweroff), procd transitions to
        5.  `STATE_SHUTDOWN`
            "- shutdown -" is logged, /etc/inittab shutdown entry is executed, and procd sleeps [at line 169](http://git.openwrt.org/?p=project/procd.git;a=blob;f=state.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l169) while the kernel does poweroff or reboot.
    8.  `uloop_done`
        `return 0`
        lines 75 & 76 are never reached by pid 1, kernel would panic if init exited.
