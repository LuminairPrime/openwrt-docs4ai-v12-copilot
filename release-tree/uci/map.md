# uci Navigation Map

> **Contains:** Headers and function signatures for uci.
> **Generated:** 2026-03-20T04:40:19.476369+00:00

---

> **Summary:** Defines the default UCI configuration schema for the OpenWrt qos-scripts traffic-shaping system. Specifies interface sections with classgroup, enabled, upload (kbit/s), and download (kbit/s) options, and classify sections mapping port ranges, protocols, and address patterns to priority classes (Priority, Express, Normal, Bulk) used by the HFS+ queue discipline.
> **Use Case:** Reference when configuring per-interface bandwidth limits and traffic prioritization rules to ensure UCI key names, section types, and option values match what the qos-scripts daemon expects.
# UCI Default Schema: qos
# qos
# QoS configuration for OpenWrt
# INTERFACES:
# RULES:
# Don't change the stuff below unless you
# really know what it means :)
