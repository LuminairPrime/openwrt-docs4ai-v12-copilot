---
title: commands.js
module: luci-examples
origin_type: example_app
token_count: 247
source_file: L1-raw/luci-examples/example_app-luci-app-commands-htdocs-luci-static-resources-view-commands-js.md
last_pipeline_run: '2026-03-27T07:16:36.403470+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/applications/luci-app-commands/htdocs/luci-static/resources/view/commands.js
source_locator: applications/luci-app-commands/htdocs/luci-static/resources/view/commands.js
language: javascript
ai_summary: The `commands.js` module in the `luci-examples` application provides a web interface for configuring custom shell commands in OpenWrt. It allows users to create, modify, and delete commands, with options for adding descriptions, command lines, and custom arguments. Additionally, it includes a flag for public access, enabling commands to be executed without authentication. This module is built using JavaScript and leverages the LuCI framework for rendering forms and views.
ai_when_to_use: Use this module when you need to create a user-friendly interface for managing custom shell commands in OpenWrt. It is particularly useful for applications that require command execution from a web interface.
ai_related_topics:
- form.Map
- form.GridSection
- form.Value
- form.Flag
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/applications/luci-app-commands/htdocs/luci-static/resources/view/commands.js](https://github.com/openwrt/luci/blob/unknown/applications/luci-app-commands/htdocs/luci-static/resources/view/commands.js)
> **Kind:** example_app | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-03-27

# commands.js
```javascript
'use strict';

'require view';
'require form';

return view.extend({
	render: function(data) {
		let m, s, o;

		m = new form.Map('luci', _('Custom Commands'),
			_('This page allows you to configure custom shell commands which can be easily invoked from the web interface.'));

		s = m.section(form.GridSection, 'command');
		s.nodescriptions = true;
		s.anonymous = true;
		s.addremove = true;

		o = s.option(form.Value, 'name', _('Description'),
			_('A short textual description of the configured command'));

		o = s.option(form.Value, 'command', _('Command'), _('Command line to execute'));
		o.textvalue = function(section_id) {
			return E('code', [ this.cfgvalue(section_id) ]);
		};

		o = s.option(form.Flag, 'param', _('Custom arguments'),
			_('Allow the user to provide additional command line arguments'));

		o = s.option(form.Flag, 'public', _('Public access'),
			_('Allow executing the command and downloading its output without prior authentication'));

		return m.render();
	}
});

```
