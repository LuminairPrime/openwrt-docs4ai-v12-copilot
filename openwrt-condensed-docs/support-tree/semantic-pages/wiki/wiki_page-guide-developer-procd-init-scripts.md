---
title: Procd Init Scripts
module: wiki
origin_type: wiki_page
token_count: 5333
source_file: L1-raw/wiki/wiki_page-guide-developer-procd-init-scripts.md
last_pipeline_run: '2026-03-27T20:02:39.961617+00:00'
source_url: https://openwrt.org/docs/guide-developer/procd-init-scripts
language: text
ai_summary: Practical guide for writing procd-based /etc/init.d/ service scripts. Walks through USE_PROCD=1, procd_open_instance, procd_set_param command/respawn/stdout/stderr, procd_close_instance, and the service_triggers() callback for uci-change-triggered reloads; includes worked examples for a simple daemon, a daemon with multiple instances, and a service that reloads on UCI changes to a specific package.
ai_when_to_use: Reference when writing or debugging a procd init script; use this guide to correctly set respawn thresholds, wire stdout/stderr to logd, add UCI change triggers so the service restarts when its config file changes, and test reload without a full reboot using /etc/init.d/myservice reload.
ai_related_topics:
- procd_open_instance
- procd_set_param respawn
- service_triggers
- procd_add_config_trigger
- USE_PROCD
- start_service
- procd
---
# Procd Init Scripts

A procd init script is similiar to an old init script, but with a few differences:

- procd expects services to start as if they were to **run in the foreground**, but of course procd runs them the background from the user's perspective.
- Different shebang line: `#!/bin/sh /etc/rc.common`
- procd expects that shell variable (not environment variable) `initscript` is set to the path of the script that invoked it
- Explicitly use procd `USE_PROCD=1`

Example:

``` bash
#!/bin/sh /etc/rc.common

START=90
STOP=01
USE_PROCD=1

service_data() {
    /usr/sbin/mesh11sd -v
}

start_service() {
    procd_open_instance
    procd_set_param command /bin/sh "/usr/sbin/mesh11sd"
    procd_append_param command daemon
    procd_set_param pidfile /var/run/mesh11sd.pid
    procd_set_param term_timeout 1
    procd_set_param stdout 1
    procd_set_param respawn 150 10 10
    procd_close_instance
}

stop_service() {
    /sbin/uci revert mesh11sd
    /sbin/uci revert wireless
    /sbin/uci revert dhcp
    /sbin/uci revert network
    /usr/sbin/nft delete table bridge mesh11s 2> /dev/null
}

```

## How do these scripts work?

Init script has to handle two main tasks:

1.  Define current configuration (state) for service instance(s)
2.  Specify when (and optionally how) to reconfigure service

Defining configuration is handled in the `start_service()`. For each instance to be run it has to specify service command and all its parameters. All that info is stored internally by `procd`. On a single change (compared to the last used configuration) `procd` restarts a service.

Init script has to specify all possible `procd` events that may require service reconfiguration. Defining all triggers is done in the `service_triggers()` using `procd_add_*_trigger` helpers.

Optionally init script may handle service reconfiguration process on its own. It's useful for services that don't require complete restart to use new configuration. It can be handled by specifying custom `reload_service()` which prevents `start_service()` from being called and so stops `procd` from restarting service.

## Service Data

Service data is sent to `stdout` by the function `service_data()`. This would typically be the version of the service (see the example).

## Defining service instances

The purpose of `start_service()` (see next section to see when it's called) is to define instance(s) with:

1.  Command to execute to start service
2.  Information on what to observe for changes (e.g. files or devices) - optional
3.  Settings that `procd` should use (e.g. auto respawning, logging stdout, user to use) - optional

The above information is stored by `procd` as a service instance state. On every relevant system change (e.g. config change), `start_service()` is called by designed triggers. If it generates any different state (e.g. command will change) than the previous one, `procd` will detect it and restart the service.

Defining service instance details is handled by setting parameters. Some values are set directly in the `start_service()` (like `command`) while some are determined by `procd` (like `file` and file hash). There are two helpers for setting parameters:

1.  `procd_set_param()`
2.  `procd_append_param()`

The below example lists supported parameters and describes them. For implementation details see the [procd.sh](commit>?p=openwrt/openwrt.git;a=blob;f=package/system/procd/files/procd.sh).

``` bash
start_service() {
         procd_open_instance [instance_name]
         procd_set_param command /sbin/your_service_daemon -b -a --foo # service executable that has to run in **foreground**.
         procd_append_param command -bar 42 # append command parameters

         # respawn automatically if something died, be careful if you have an alternative process supervisor
         # if process exits sooner than respawn_threshold, it is considered crashed and after 5 retries the service is stopped
         # if process finishes later than respawn_threshold, it is restarted unconditionally, regardless of error code
         # notice that this is literal respawning of the process, not in a respawn-on-failure sense
         procd_set_param respawn ${respawn_threshold:-3600} ${respawn_timeout:-5} ${respawn_retry:-5}

         procd_set_param env SOME_VARIABLE=funtimes  # pass environment variables to your process
         procd_set_param limits core="unlimited"  # If you need to set ulimit for your process
         procd_set_param file /var/etc/your_service.conf # /etc/init.d/your_service reload will restart the daemon when these files have changed
         procd_set_param netdev dev # likewise, but for when dev's ifindex changes.
         procd_set_param data name=value ... # likewise, but for when this data changes.
         procd_set_param stdout 1 # forward stdout of the command to logd
         procd_set_param stderr 1 # same for stderr
         procd_set_param user nobody # run service as user nobody
         procd_set_param pidfile /var/run/somefile.pid # write a pid file on instance start and remove it on stop
         procd_set_param term_timeout 60 # wait before sending SIGKILL
         procd_close_instance
}
```

### Stopping services

`stop_service()` is only needed when you need special things to stop your service. `stop_service()` is called *before* procd killed the service.

If you want to add a check *after* procd has sent the terminate signal (e.g. wait for the process to be really gone), you can define an extra function `service_stopped()`.

### Init scripts during compilation

WARNING: initscripts **will run** while building OpenWrt images (when installing packages in what will become a ROM image) in the **host system** (right now, for actions "*enable*" and "*disable*"). **They must not fail, or have undesired side-effects in that situation.** When being run by the build system, environment variable **\${IPKG_INSTROOT}** will be set to the working directory being used. On the "target system", that environment variable will be empty/unset. Refer to "/lib/functions.sh" and also to "/etc/rc.common" in package "base-files" for the nasty details.

## Specifying triggers

While `start_service()` takes care of setting service instances states and submitting them to the `procd` (for a potential service restart), it has to be explicitly called to do so. In most cases it should happen on some related change.

That's where `service_triggers()` comes in handy and allows specifying triggers. Most system important changes result in generating events that `service_triggers()` can use for triggering various actions. There are multiple `procd_add_*_trigger()` helpers for that purpose.

Every configurable service has to specify what system changes should result in its reconfiguration. Those events should be defined in the `service_triggers()` using available helpers. When related `procd` `service` event occurs it will result in executing `/etc/init.d/<foo> reload`.

Example:

``` bash
service_triggers()
{
        procd_add_reload_trigger "<uci-file-name>" "<second-uci-file>"
        procd_add_reload_interface_trigger <interface>
        procd_add_reload_mount_trigger <path> [<path> ...]
}
```

| Function                           | Arguments            | Event used      | Description                                     |
|:-----------------------------------|:---------------------|:----------------|-------------------------------------------------|
| procd_add_reload_trigger           | list of config files | `config.change` | Uses `/etc/init.d/<foo> reload` as the handler  |
| procd_add_reload_interface_trigger | interface name       | `interface.*`   | Uses `/etc/init.d/<foo> reload` as the handler  |
| procd_add_reload_mount_trigger     | paths to watch for   | `mount.add`     | Uses `/etc/init.d/<foo> reload` as the handler  |
| procd_add_restart_mount_trigger    | paths to watch for   | `mount.add`     | Uses `/etc/init.d/<foo> restart` as the handler |

 When using `uci` from command line `uci commit` doesn't generate `config.change` event. It requires calling `reload_config` afterwards.

This does not apply to using `uci` over `rpcd` plugin.

 Adding `interface.*` trigger and having `/etc/init.d/<foo> reload` called won't automatically make `procd` notice any state change and won't make it restart a service.

Relevant interface has to be made part of service state using the `procd_set_param netdev`.

 Using mount triggers depends on mount notifications emitted by `blockd`. Hence `blockd` needs to be installed and the mount need to be configured in `/etc/config/fstab`.

See also [fstab](/docs/guide-user/storage/fstab)

See use cases of [procd_add_interface_trigger](https://github.com/openwrt/packages/search?q=procd_add_interface_trigger), [procd_add_reload_trigger](https://github.com/openwrt/packages/search?q=procd_add_reload_trigger), [procd_add_reload_mount_trigger](https://github.com/openwrt/packages/search?q=procd_add_reload_mount_trigger) in the OpenWrt packages repository.

### ucitrack

In older versions of OpenWrt, a system called "ucitrack" attempted to track UCI config files, and the processes that depended on each of them, and would restart them all as needed. This too, is replaced with ubus/procd, and expanded to allow notifying services when network interfaces change.

## Manual reload

Sometimes service state may depend on information that doesn't have any events related. This may happen e.g. with service native configuration files that don't get build using UCI config.

In such cases `procd` should be told to use relevant config file using `procd_set_param file /etc/foo.conf`. After every config file modification `/etc/init.d/foo reload` should be called manually.

## Custom service reload

By default (without `reload_service()` specified) calling `/etc/init.d/<foo> reload` results in running `start_service()` and `procd` comparing states. In some cases a more complete control over `reload` action may be needed thought.

### Forcing service restart

If some service requires a restart when `reload` is called, it can be implemented as follows:

``` bash
reload_service()
{
        echo "Explicitly restarting service, are you sure you need this?"
        stop
        start
}
```

j==== Reloading service setup ====

Some services may support reloading configuration without a complete restart. It's usually implemented using \`SIGHUP\` or similar signal.

OpenWrt comes with a `procd_send_signal()` helper that doesn't require passing PID directly. Example:

    reload_service() {
             procd_send_signal service_name [instance_name] [signal]
    }

The *signal* argument is `SIGHUP` by default and must be specified by NAME. You can get available signals using `kill -l`.

The *service_name* is the basename of the `init.d` script, e.g. `yourapp` for the `/etc/init.d/yourapp`.

The *instance_name* allows specifying custom instance name in case it was used like `procd_open_instance [instance_name]`. If *instance_name* is unspecified, or '' '\*' '' then the signal will be delivered to all instances of the service.

**Note** You can also send signals to named procd services from outside initscripts. Simply load the procd functions and send the signal as before.

    #!/bin/sh
    . /lib/functions/procd.sh
    procd_send_signal service_name [instance_name] [signal]

 You can also configure reload by signal with `procd_set_param reload_signal` service option.

## Service jails

procd can isolate services using various Linux features typically used for (slim-)containers: *chroot* and *namespaces* (and *limits*, *seccomp*, *capabilities* as well as setting `PR_SET_NO_NEW_PRIVS`, see [Service Parameters](#service_parameters)).

| Function                | Arguments        | Description                                                   |
|:------------------------|:-----------------|:--------------------------------------------------------------|
| procd_add_jail          | jail name, flags | Set up service jail (with features according to *flags*)      |
| procd_add_jail_mount    | read-only paths  | Read-only bind the paths listed to the jail's mount namespace |
| procd_add_jail_mount_rw | read-write paths | Bind the paths listed to the jail's mount namespace           |

| Flag        | Description                                                           |
|:------------|:----------------------------------------------------------------------|
| log         | Allow jailed service to log to syslog                                 |
| ubus        | Allow jailed service to access ubus                                   |
| procfs      | Mount /proc in jail                                                   |
| sysfs       | Mount /sys in jail                                                    |
| ronly       | Re-mount jail rootfs read-only                                        |
| requirejail | Do not fall back to run without jail in case jail could not be set up |
| netns       | Run jailed process in new network namespace                           |
| userns      | Run jailed process in new user namespace                              |
| cgroupsns   | Run jailed process in new cgroups namespace                           |
| console     | Set up console accessible with `ujail-console`                        |

See use cases of [procd_add_jail](https://github.com/openwrt/packages/search?q=procd_add_jail).

## Debugging

Set PROCD_DEBUG=1 to see debugging information when starting or stopping a procd init script. Also, `INIT_TRACE=1 /etc/init.d/mything $action` Where \$action is start/stop etc.

### A common gotcha with stopping a service

Keep in mind that `procd` only tracks the main process. For example, consider the following script that reads from log file and then performs an action:

``` sh
#!/usr/bin/sh

tail -f /var/log/messages |  while read -r match; do
    echo foo
done
```

Because this script uses a pipe a sub-process is spawned. Calling `/etc/init.d./<foo> stop` will only terminate the parent process. The sub-process will still be alive and continue running. This is also true if you call `kill` on the main process's PID manually. The program needs to keep track of its sub-processes and terminate them properly when it receives a `SIGTERM` signal.

For this case in particular, here is a working solution:

``` sh
#!/usr/bin/sh

pid=
_cleanup() {
    kill "$pid"
    exit
}

trap _cleanup TERM INT

tail -f /var/log/messages |  while read -r match; do
    echo foo
done & # Beware the &: In order to be able to receive signals at all, the above `while read`
       # needs to be run in the background.
pid=$!
wait $pid
```

## Examples

- [r39617 firewall3](https://dev.openwrt.org/changeset/39617)
- [r40635 radsecproxy](https://dev.openwrt.org/changeset/40635)
- [r40674 xupnpd](https://dev.openwrt.org/changeset/40674)
- [r40785 shairport](https://dev.openwrt.org/changeset/40785)
- [r40997 igmpproxy](https://dev.openwrt.org/changeset/40997)
- [Create a sample procd init script](/docs/guide-developer/procd-init-script-example)

## Service Parameters

The following table contains a listing of the possible values to `procd_set_param()` and a description of their effects. List values are passed space-separated, e.g. `procd_set_param env HOME=/root ENVIRONMENT=production FOO="bar baz"`. String values are implicitely concatenated, so `procd_set_param error An error occurred` is equivalent to `procd_set_param error "An error occurred"`.

| Parameter       | Data Type      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|-----------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `env`           | Key-Value-List | Sets a number of environment variables in `key=value` notation exported to the spawned process.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `data`          | Key-Value-List | Sets arbitrary user data in `key=value` notation to the ubus service state. This is mainly used to store additional meta data with spawned services, such as [mDNS](../wiki/wiki_page-guide-developer-mdns.md) announcements or firewall rules which may be picked up by other services.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `limits`        | Key-Value-List | Set ulimit values in `key=value` notation for the spawned process. The following limit names are recognized by *procd*: `as` (`RLIMIT_AS`), `core` (`RLIMIT_CORE`), `cpu` (`RLIMIT_CPU`), `data` (`RLIMIT_DATA`), `fsize` (`RLIMIT_FSIZE`), `memlock` (`RLIMIT_MEMLOCK`), `nofile` (`RLIMIT_NOFILE`), `nproc` (`RLIMIT_NPROC`), `rss` (`RLIMIT_RSS`), `stack` (`RLIMIT_STACK`), `nice` (`RLIMIT_NICE`), `rtprio` (`RLIMIT_RTPRIO`), `msgqueue` (`RLIMIT_MSGQUEUE`), `sigpending` (`RLIMIT_SIGPENDING`) **Two numeric values, separated by blank space, are expected for RLIMIT: the first value represents the soft limit and the other the hard limit; e.g.: [procd_set_param](../cookbook/procd-service-lifecycle.md) limits nofile="10000 20000"; the "unlimited" value can be used in cases where "ulimit -{parameter} unlimited" works, for example for the "core" parameter.**                                                                                               |
| `command`       | List           | Sets the command vector (`argv`) used to execute the process.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `netdev`        | List           | Passes a list of Linux network device names to *procd* to be monitored for changes. Upon starting a service, the interface index of each network device name is resolved and stored as part of *procd*'s in-memory service state. When a service reload request is processed and the interface index of any of the associated network devices changed or if the list itself changed, the running service state is invalidated and *procd* will restart the associated process or deliver a UNIX signal to it, depending on how the service was set up.                                                                                                                                                                                                                                                                                                                                                                                   |
| `file`          | List           | Passes a list of file names to *procd* to be monitored for changes. Upon starting a service, the content of each passed file is checksummed and stored as part of *procd*'s in-memory service state. When a service reload request is processed and the checksum of one of the associated files changed, or the list of files itself changed, the running service state is invalidated and *procd* will restart the associated process or deliver a UNIX signal to it, depending on how the service was set up.                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `respawn`       | List           | A series of three consecutive numbers which set the *respawn threshold*, the *respawn timeout* and the *respawn retry* respectively. The timeout specifies the amount of seconds to wait before a service restart attempt, the retry value controls how many restart attempts will be made before a service is considered crashed and the threshold value in seconds controls the time frame in which the restart attempts are counted towards the retry limit. For example a threshold of 300 with a retry value of 10 will cause *procd* to consider the service to be crashed if the associated UNIX process terminated more than 10 times within a time frame of 5 minutes. No further restart attempts will be made for such crashed services unless an explicit restart is performed. Setting the retry value to `0` will cause *procd* to try restarting the service indefinitely. The default value for `respawn` is `3600 5 5`. |
| `watch`         | List           | Passes a list of *ubus* namespaces to watch - *procd* will subcribe to each namespace and wait for incoming *ubus* events which are then forwarded to registered JSON script triggers for evaluation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `error`         | List           | Passes one or more free formed error strings to *procd*. The error strings are stored as part of the in-memory service state and are exposed verbatim in *ubus* for use by other tools. This facility is mainly useful to allow init scripts to signal configuration errors or other transient issues preventing a successful start up. If any error string is passed to *procd*, no attempt will be made to actually spawn the associated UNIX process of the service but the service instance itself is still registered in *procd*.                                                                                                                                                                                                                                                                                                                                                                                                   |
| `nice`          | Integer        | Set the scheduling priority of the spawned process. Valid values range from `-20` (most favorable) to `19` (least favorable).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `term_timeout`  | Integer        | Specifies the amount of seconds to wait for a clean process exit after delivering the `TERM` signal. If the process fails to completely exit within the specified time frame, the process is forcibly terminated using an uncatchable `KILL` signal. The default termination timeout value is 5 seconds. Services with expensive shutdown operations, such as database systems, should set the `term_timeout` parameter to sufficiently large value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `reload_signal` | String         | Instructs *procd* to handle process reloads by delivering a UNIX signal instead of terminating the running process and spawning it again. This is useful for programs that provide extensive native configuration reload handling which allows for updated configurations to be applied on the fly without the need to restart the process. Note that this parameter only makes sense in conjunction with fixed command lines. When a reload signal is specified, any updated command line will be ignored since the running process is retained and not executed again. Valid values for this parameter are UNIX signal names as listed by `kill -l`.                                                                                                                                                                                                                                                                                   |
| `pidfile`       | String         | Instructs *procd* to write the PID of the spawned process into the specified file path. While *procd* itself does not use or require PID files to track spawned processes, this option is useful for sitation where knowledge of the PID is required, e.g. for monitoring or control client software.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `user`          | String         | Specifies the name of the user to spawn the process as. *procd* will look up the given name in `/etc/passwd` and set the effective uid and primary gid of the spawned processaccordingly. If omitted, the process is spawned as `root` (uid 0, gid 0)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `seccomp`       | String         | Specifies file path to read seccomp filter rules from, the file should be JSON formatted like the [seccomp object of the OCI run-time spec](https://github.com/opencontainers/runtime-spec/blob/master/config-linux.md#seccomp)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `capabilities`  | String         | Specifies file path to read capability set, the file should be JSON formatted like the [capabilities object of the OCI run-time spec](https://github.com/opencontainers/runtime-spec/blob/master/config.md#linux-process)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `stdout`        | Boolean        | If set to `1`, instruct *procd* to relay the spawned process' stdout to the system log. The stdout will be fed line-wise to `syslog(3)` using the basename of the first command argument as identity, `LOG_INFO` as priority and `LOG_DAEMON` as facility.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `stderr`        | Boolean        | If set to `1`, instruct *procd* to relay the spawned process' stderr to the system log. The stderr will be fed line-wise to `syslog(3)` using the basename of the first command argument as identity, `LOG_ERR` as priority and `LOG_DAEMON` as facility.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `no_new_privs`  | Boolean        | Instructs *ujail* to not allow privilege elevation. Sets the *ujail* `-c` parameter when true.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
