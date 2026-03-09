# Procd system init and daemon management

**See also: [procd-init-scripts#procd_init_scripts](/docs/guide-developer/procd-init-scripts#procd_init_scripts)**

`procd` is the OpenWrt [process](https://en.wikipedia.org/wiki/Process (computing)) management daemon written in [C](https://en.wikipedia.org/wiki/C (programming language)). It keeps track of processes started from init scripts (via ubus calls), and can suppress redundant service start/restart requests when the config/environment has not changed.

`procd` has replaced ... , e.g.

- `hotplug2`, a dynamic device management subsystem for embedded systems. Hotplug2 is a trivial replacement of some of the UDev functionality in a tiny pack, intended for Linux early userspace: Init RAM FS and InitRD.
- `busybox-klogd` and `busybox-syslogd`
- `busybox-watchdog`

`procd` is intended to stay compatible with the existing format of `/etc/config/`; exceptions ...

## Help with the development of procd

1.  test what has been ported
2.  review of the code

## Buttons with procd

:!: see commit in <https://dev.openwrt.org/log/trunk/package/base-files/files/etc/rc.button>

:!: see use case [hardware.button](/docs/guide-user/hardware/hardware.button)

## Init scripts with procd

see [procd-init-scripts](/docs/guide-developer/procd-init-scripts)

## early state and preinit

Before the real procd runs, a small init process is started. This process has the job of early system init. It will do the following things in the listed order

- bring up basic mounts such as /proc /sys/{,fs/cgroup} /dev/{,shm,pts}
- create some required folder, /tmp/{run,lock,state}
- bring up /dev/console and map the processes stdin/out/err to the console (this is the "Console is alive" message)
- setup the PATH environment variable
- check if "init_debug=" is set in the kernel command line and apply the debug level if set
- initialise the watchdog
- start kmodloader and load the modules listed in /etc/modules-boot.d/
- start hotplug with the preinit rules (/etc/hotplug-preinit.json)
- start preinit scripts found inside /lib/preinit/

Once preinit is complete the init process is done and will do an exec on the real procd. This will replace init as pid1 with an instance of procd running as the new pid 1. The watchdog file descriptor is not closed. Instead it is handed over to the new procd process. The debug_level will also be handed over to the new procd instance if it was set via command line or during preinit.

## procd start up

Procd will first do some basic process init such as setting itself to be owner of its own process group and setting up signals. We are now ready to bring up the userland in the following order

- find out if a watchdog file descriptor was passed by the init process and start up the watchdog
- setup /dev/console to be our stdin/out/err
- start the coldplug process using the full rule set (/etc/hotplug.json). This is done by manually triggering all events that have already happened using udevtrigger
- start ubus, register it as a service and connect to it.

The basic system bringup is now complete, procd is up and running and can start handling daemons and services

## /etc/inittab

Procd supports four commands inside inittab

- respawn - this works just like you expect it. It starts a process and will respawn it once it has completed.
- respawnlate - this works like the respawn but will start the process only when the procd init is completed.
- askfirst - this works just like respawn but will print the line "Please press Enter to activate this console." before starting the process
- askconsole - this works like askfirst but, instead of running on the tty passed as a parameter, it will look for the tty defined in the kernel command line using "console="
- askconsolelate - this works like the askconsole but will start the process only when the procd init is completed.
- sysinit - this will trigger procd to run the command, given as a parameter, only once. This is usually used to trigger execution of /etc/rc.d/

Once all items inside /etc/inittab are processed, procd enter its normal run mode and will handle messages coming in via ubus. It will stay in this state until a reboot/shutdown is triggered.

## ubus command interface

## hotplug

Hotplug scripts are located inside /etc/hotplug.d and are based on json_script. This is a json based if then else syntax. Procd hotplug service offers the following actions:

- makedev
- rm
- exec
- button
- load-firmware

![construction&noheader&nofooter&noeditbtn](/page>meta/infobox/construction&noheader&nofooter&noeditbtn)

## procd (process management daemon) – Technical Reference

- [Project's git](http://git.openwrt.org/?p=project/procd.git;a=summary)
- procd is available in OpenWrt since [r34865 (trunk)](https://dev.openwrt.org/changeset/34865). It consists of files under GPLv2, LGPLv2.1 and ISC licenses.
- [commits to OpenWrt trunk regarding procd](https://dev.openwrt.org/search?q=procd&noquickjump=1&changeset=on)

## OpenWrt – operating system architecture

![architecture&noheader&nofooter](/page>docs/techref/architecture&noheader&nofooter)

### History

Package history is available at:

- current history: <https://dev.openwrt.org/log/trunk/package/system/procd>
- old history pre r37007 <https://dev.openwrt.org/log/trunk/package/procd/Makefile?rev=36995>

<!-- -->

- [r34865: procd: add initial implementation](https://dev.openwrt.org/changeset/34865)
- [r34866: base-files: add basic procd integration, let procd start (and restart) ubus instead of having an ubus init script](https://dev.openwrt.org/changeset/34866)
- [r34867: dropbear: convert init script to procd](https://dev.openwrt.org/changeset/34867)
- [r36003: base-files: make basefiles aware of procd](https://dev.openwrt.org/changeset/36003)
- [r36005: busybox: make init and logread depend on !PROCD_INIT](https://dev.openwrt.org/changeset/36005)
- [r36446: hotplug2: make it depend on !PROCD_INIT](https://dev.openwrt.org/changeset/36446)
- [r36896: procd: make the preinit rules wildcard all buttons for failsafe](https://dev.openwrt.org/changeset/36896)
- [r36987: hotplug2: procd does the hotplugging now](https://dev.openwrt.org/changeset/36987)
- [r36998: base-files: procd is now the init process](https://dev.openwrt.org/changeset/36998)
- [r36999: base-files: diag does not need to insmod any drivers, procd already did it for us](https://dev.openwrt.org/changeset/36999)
- [r37000: base-files: input/button drivers get loaded before preinit by procd](https://dev.openwrt.org/changeset/37000)
- [r37002: base-files: /etc/init.d/rcS is no longer needed, procd handles this for us now](https://dev.openwrt.org/changeset/37002)
- [r37039: busybox: disable syslogd/klogd by default, procd replaces them](https://dev.openwrt.org/changeset/37039)
- [r37106: busybox: disable the watchdog utility by default (procd handles watchdog devices)](https://dev.openwrt.org/changeset/37106)
- [r37242, 37243, 37244: busybox: convert telnet, crond and sysntpd init scripts to procd](https://dev.openwrt.org/changeset/37242)
- [r37245: dropbear: register a config.change trigger: procd_add_config_trigger "dropbear" "/etc/init.d/dropbear" "restart"](https://dev.openwrt.org/changeset/37245)
- [r37429: procd: add proto and trigger support to the /etc/init.d/log](https://dev.openwrt.org/changeset/37249)
- [r37336: procd: make old button hotplug rules work until all packages are migrated](https://dev.openwrt.org/changeset/37336)
