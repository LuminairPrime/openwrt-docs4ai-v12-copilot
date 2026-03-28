---
title: 70_ddns.js
module: luci-examples
origin_type: example_app
token_count: 392
source_file: L1-raw/luci-examples/example_app-luci-app-ddns-htdocs-luci-static-resources-view-status-include-70-ddns-js.md
last_pipeline_run: '2026-03-28T11:37:47.626796+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/applications/luci-app-ddns/htdocs/luci-static/resources/view/status/include/70_ddns.js
source_locator: applications/luci-app-ddns/htdocs/luci-static/resources/view/status/include/70_ddns.js
language: javascript
ai_summary: The 70_ddns.js module is part of the luci-examples package in OpenWrt, designed to manage Dynamic DNS (DDNS) services through a web interface. It utilizes the RPC mechanism to fetch the status of configured DDNS services and displays this information in a structured table format. The module loads DDNS configurations using the UCI system and presents details such as the next update time, lookup hostname, registered IP address, and network type. It also handles cases where no services are configured by displaying an appropriate message.
ai_when_to_use: Use this module when you need to provide a user interface for monitoring and managing Dynamic DNS services in OpenWrt. It is particularly useful for users who require real-time updates on their DDNS configurations.
ai_related_topics:
- rpc
- uci
- baseclass
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/applications/luci-app-ddns/htdocs/luci-static/resources/view/status/include/70_ddns.js](https://github.com/openwrt/luci/blob/unknown/applications/luci-app-ddns/htdocs/luci-static/resources/view/status/include/70_ddns.js)
> **Kind:** example_app | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-28

# 70_ddns.js
```javascript
'use strict';
'require baseclass';
'require rpc';
'require uci';

return baseclass.extend({
	title: _('Dynamic DNS'),

	callDDnsGetServicesStatus: rpc.declare({
		object: 'luci.ddns',
		method: 'get_services_status',
		expect: {  }
	}),

	load: function() {
		return Promise.all([
			this.callDDnsGetServicesStatus(),
			uci.load('ddns')
		]);
	},

	render: function(data) {
		var services = data[0];

		var table = E('table', { 'class': 'table' }, [
			E('tr', { 'class': 'tr table-titles' }, [
				E('th', { 'class': 'th' }, _('Configuration')),
				E('th', { 'class': 'th' }, _('Next Update')),
				E('th', { 'class': 'th' }, _('Lookup Hostname')),
				E('th', { 'class': 'th' }, _('Registered IP')),
				E('th', { 'class': 'th' }, _('Network'))
			])
		]);

		cbi_update_table(table, Object.keys(services).map(function(key, index) {
			return [
				key,
				services[key].next_update ? _(services[key].next_update) : _('Unknown'),
				uci.get('ddns',key,'lookup_host'),
				services[key].ip ? services[key].ip : _('No Data'),
				(uci.get('ddns',key,'use_ipv6') == '1' ? 'IPv6' : 'IPv4') + ' / ' + uci.get('ddns',key,'interface')
			];
		}), E('em', _('There is no service configured.')));

		return E([table]);
	}
});

```
