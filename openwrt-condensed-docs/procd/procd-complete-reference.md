---
module: procd
total_token_count: 352
section_count: 1
is_monolithic: true
generated: '2026-03-20T01:28:16.926497+00:00'
---

# procd Complete Reference

> **Contains:** 1 documents concatenated
> **Tokens:** ~352 (cl100k_base)

---

# procd init.d API Reference

> **Extracted from:** `procd.sh` block comments

# procd.sh
```bash
procd API:
procd_open_service(name, [script]):
Initialize a new procd command message containing a service with one or more instances
procd_close_service()
Send the command message for the service
procd_open_instance([name]):
Add an instance to the service described by the previous procd_open_service call
procd_set_param(type, [value...])
Available types:
command: command line (array).
respawn info: array with 3 values $fail_threshold $restart_timeout $max_fail
env: environment variable (passed to the process)
data: arbitrary name/value pairs for detecting config changes (table)
file: configuration files (array)
netdev: bound network device (detects ifindex changes)
limits: resource limits (passed to the process)
user: $username to run service as
group: $groupname to run service as
pidfile: file name to write pid into
stdout: boolean whether to redirect commands stdout to syslog (default: 0)
stderr: boolean whether to redirect commands stderr to syslog (default: 0)
facility: syslog facility used when logging to syslog (default: daemon)
No space separation is done for arrays/tables - use one function argument per command line argument
procd_close_instance():
Complete the instance being prepared
procd_running(service, [instance]):
Checks if service/instance is currently running
procd_kill(service, [instance]):
Kill a service instance (or all instances)
procd_send_signal(service, [instance], [signal])
Send a signal to a service instance (or all instances)
```
