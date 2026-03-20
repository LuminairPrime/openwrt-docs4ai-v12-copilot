# procd (Skeleton Semantic Map)

> **Contains:** Headers and function signatures for procd.
> **Generated:** 2026-03-20T04:40:19.476369+00:00

---

> **Summary:** Defines the procd init script Bash API for service registration and supervised process lifecycle control. Exposes procd_open_service(), procd_close_service(), procd_open_instance(), procd_close_instance(), and procd_set_param() for declaring supervised processes with respawn rules, environment variables, limits, file triggers, and bound network devices. Also provides procd_add_reload_trigger() for UCI-based reload events.
> **Use Case:** Use in every /etc/init.d/ script that must integrate with the OpenWrt procd process supervisor for automatic respawn, controlled signal handling, and named trigger-based reload without manual service polling.
# procd init.d API Reference
# procd.sh
