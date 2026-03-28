---
title: LuCI – Technical Reference
module: wiki
origin_type: wiki_page
token_count: 1499
source_file: L1-raw/wiki/wiki_page-techref-luci.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_url: https://openwrt.org/docs/techref/luci
language: text
ai_summary: Provides a technical overview of the LuCI web interface framework for OpenWrt. Covers the three-tier architecture (controller/model/view), the CBI/form module system, Lua vs. JavaScript view types, the rpcd permission model, package Makefile conventions for registering menu entries and ACL files, and the workflow for developing and testing LuCI packages locally.
ai_when_to_use: 'Reference when starting development of a new LuCI package: understand how to register menu items in the luci-base po/ACL system, choose between Lua CBI and JavaScript form views, and set up a local test environment using the LuCI development toolchain.'
ai_related_topics:
- LuCI.cbi
- LuCI.form
- rpcd ACL
- luci-mod-admin-full
- luci-base
- LuCI.ui
- LuCI.uci
---
# LuCI – Technical Reference

- See also the [LuCI Essentials](/docs/guide-user/luci/luci.essentials) page
- [LuCI Wiki](https://github.com/openwrt/luci/wiki)
- [LuCI Documentation](https://github.com/openwrt/luci/wiki/Documentation)
- [LuCI Github](https://github.com/openwrt/luci)

## What is LuCI

[Lua](https://en.wikipedia.org/wiki/Lua_(programming_language)) Control Interface (LuCI) was founded in 2008 as "FFLuCI" as part of the efforts to port the Freifunk-Firmware from [White Russian](/about/history) code branch to its successor [Kamikaze](/about/history).

The initial reason for this project was the absence of a free, clean, extensible and easily maintainable [web user interface](/docs/guide-user/luci/webinterface.overview) for embedded devices. While most similar configuration interfaces make heavy use of the Shell-scripting language, LuCI:

- uses the Lua programming language and
- splits the interface up into logical parts like models and views, uses object-oriented libraries and templating.

That ensures better performance, smaller installation size, faster runtimes, and simple maintainability.

Meanwhile LuCI evolved from a MVC-Webframework to a collection of libraries, applications and user interfaces with general purpose for Lua programmers while the focus still remains on the [web user interface](/docs/guide-user/luci/webinterface.overview) which became an official part of OpenWrt since 'Kamikaze' 8.09.

## Dependencies

- [uci](/docs/techref/uci) (including libuci-lua)

## Encompassed Packages

`luci` and `luci-ssl` are meta-packages. Here you see what they comprise, the sizes are in Bytes compiled for the ar71xx platform. They shouldn't differ much from binaries compiled for other architectures. Also note, that with JFFS2 it is not possible to precisely predict the occupied space.

In case you want to use a different web server than [uhttpd](/docs/guide-user/services/webserver/http.uhttpd) and not install uhttpd at all, do not install the meta-package because it includes it. Install the individual components instead and a web server of your choice. The article [start](/docs/guide-user/services/webserver/start) shows you some choices from the repos.

|                      Name                      | Size  | Description                                                                                                                                                                                                                                                                                   |
|:----------------------------------------------:|:-----:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                      luci                      |  779  | Meta package. Standard OpenWrt set including full and mini admin and the standard theme                                                                                                                                                                                                       |
|                     uhttpd                     | 23778 | uHTTPd is a tiny single threaded [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) server with TLS, CGI and Lua support. It is intended as a drop-in replacement for the Busybox [HTTP](../wiki/wiki_page-guide-developer-adding-new-device.md) daemon.                                                                                                                                              |
|              luci-mod-admin-full               | 60827 | LuCI Administration - full-featured for full control                                                                                                                                                                                                                                          |
|              luci-mod-admin-core               | 5257  | Web UI Core module                                                                                                                                                                                                                                                                            |
|              luci-theme-bootstrap              | 13801 | Bootstrap theme (default)                                                                                                                                                                                                                                                                     |
|               luci-theme-openwrt               | 7756  | OpenWrt.org theme                                                                                                                                                                                                                                                                             |
|               luci-i18n-english                | 1252  | English                                                                                                                                                                                                                                                                                       |
|               luci-app-firewall                | 16630 | Firmware and Portforwarding application                                                                                                                                                                                                                                                       |
|                    firewall                    | 11603 | UCI based firewall for OpenWrt /etc/config/firewall /etc/firewall.user. Dependencies: iptables, iptables-mod-conntrack, iptables-mod-nat                                                                                                                                                      |
|                luci-app-initmgr                | 5713  | LuCI Initscript Management                                                                                                                                                                                                                                                                    |
|                   libiwinfo                    | 25362 | Wireless information library with consistent interface for proprietary Broadcom, madwifi, nl80211 and wext driver interfaces.                                                                                                                                                                 |
|                 luci-lib-ipkg                  | 2846  | LuCI IPKG/OPKG call abstraction library                                                                                                                                                                                                                                                       |
|                luci-theme-base                 | 25065 | Common base for all themes                                                                                                                                                                                                                                                                    |
|                   libnl-tiny                   | 14390 | This package contains a stripped down version of libnl                                                                                                                                                                                                                                        |
|                     liblua                     | 81477 | Lua is a powerful light-weight programming language designed for extending applications. Lua is also frequently used as a general-purpose, stand-alone language. Lua is free software. This package contains the Lua shared libraries, needed by other programs.                              |
|                      lua                       | 9069  | Lua is a powerful light-weight programming language designed for extending applications. Lua is also frequently used as a general-purpose, stand-alone language. Lua is free software. This package contains the Lua language interpreter. (5.1.4-7)                                          |
|                  luci-lib-web                  | 59695 | MVC Webframework                                                                                                                                                                                                                                                                              |
|                  luci-lib-sys                  | 15795 | LuCI Linux/POSIX system library                                                                                                                                                                                                                                                               |
|                 luci-lib-nixio                 | 31683 | NIXIO POSIX library                                                                                                                                                                                                                                                                           |
|                 luci-lib-core                  | 28096 | LuCI core libraries                                                                                                                                                                                                                                                                           |
|                  luci-sgi-cgi                  | 2420  | CGI Gateway behind existing Webserver                                                                                                                                                                                                                                                         |
|                  luci-lib-lmo                  | 4714  | LuCI LMO I18N library                                                                                                                                                                                                                                                                         |
|        Additionally Required for HTTPS         |       |                                                                                                                                                                                                                                                                                               |
|                    luci-ssl                    |  782  | Meta package. Standard OpenWrt set including full admin, the standard theme + HTTPS support. Installs px5g and libustream-mbedtls by default (since Dec2016)                                                                                                                                  |
|                (uhttpd-mod-tls)                | 5825  | The TLS plugin adds HTTPS support to uHTTPd. Note: Not needed since r35295 in Jan2013 as uhttpd is always built ready to utilize SSL library via a libustream- library                                                                                                                        |
|                 uhttpd-mod-lua                 | 9178  | The Lua plugin adds a CGI-like Lua runtime interface to uHTTPd.                                                                                                                                                                                                                               |
|                      px5g                      | 28480 | Px5g is a tiny standalone X.509 certificate generator. It's suitable to create key files and certificates in [DER](https://en.wikipedia.org/wiki/Distinguished Encoding Rules) and [PEM](https://en.wikipedia.org/wiki/Privacy Enhanced Mail) format for use with stunnel, uhttpd and others. |
| Internationalization and localization packages |       |                                                                                                                                                                                                                                                                                               |
|                 luci-i18n-xxx                  | ????? | Please refer to <https://github.com/openwrt/luci/wiki/i18n> for an overview of the translation progress.                                                                                                                                                                                      |
