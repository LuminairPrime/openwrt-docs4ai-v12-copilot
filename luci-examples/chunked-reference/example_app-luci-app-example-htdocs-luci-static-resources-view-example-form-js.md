---
title: form.js
module: luci-examples
origin_type: example_app
token_count: 476
source_file: L1-raw/luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-form-js.md
last_pipeline_run: '2026-04-01T11:39:34.127010+00:00'
source_commit: unknown
source_url: https://github.com/openwrt/luci/blob/unknown/applications/luci-app-example/htdocs/luci-static/resources/view/example/form.js
source_locator: applications/luci-app-example/htdocs/luci-static/resources/view/example/form.js
language: javascript
ai_summary: The `form.js` module is a JavaScript file used in the LuCI framework for creating a user interface form that interacts with UCI configuration files in OpenWrt. It defines a form structure that includes multiple sections and various input types, such as text fields, flags, and dynamic lists. The form is mapped to a configuration file named 'example' located at `/etc/config/example`, allowing users to read and write configuration settings. Each section can contain different types of options, including a password input and a select dropdown with predefined values.
ai_when_to_use: Use this module when you need to create a custom configuration form in a LuCI application that interacts with UCI settings in OpenWrt.
ai_related_topics:
- form.Map
- form.TypedSection
- form.Value
- form.Flag
- form.ListValue
- form.DynamicList
---

> **Source:** [https://github.com/openwrt/luci/blob/unknown/applications/luci-app-example/htdocs/luci-static/resources/view/example/form.js](https://github.com/openwrt/luci/blob/unknown/applications/luci-app-example/htdocs/luci-static/resources/view/example/form.js)
> **Kind:** example_app | **Commit:** unknown | **Method:** normalized
> **Normalized:** 2026-04-01

# form.js
```javascript
'use strict';
'require view';
'require form';

// Project code format is tabs, not spaces
return view.extend({
	render: function() {
		let m, s, o;

		/*
		The first argument to form.Map() maps to the configuration file available
		via uci at /etc/config/. In this case, 'example' maps to /etc/config/example.

		If the file is completely empty, the form sections will indicate that the
		section contains no values yet. As such, your package installation (LuCI app
		or software that the app configures) should lay down a basic configuration
		file with all the needed sections.

		The relevant ACL path for reading a configuration with UCI this way is
		read > uci > ["example"]

		The relevant ACL path for writing back the configuration is
		write > uci > ["example"]
		*/
		m = new form.Map('example', _('Example Form'),
			_('Example Form Configuration.'));

		s = m.section(form.TypedSection, 'first', _('first section'));
		s.anonymous = true;

		s.option(form.Value, 'first_option', _('First Option'),
			_('Input for the first option'));

		s = m.section(form.TypedSection, 'second', _('second section'));
		s.anonymous = true;

		o = s.option(form.Flag, 'flag', _('Flag Option'),
			_('A boolean option'));
		o.default = '1';
		o.rmempty = false;

		o = s.option(form.ListValue, 'select', _('Select Option'),
			_('A select option'));
		o.placeholder = 'placeholder';
		o.value('key1', 'value1');
		o.value('key2', 'value2');
		o.rmempty = false;
		o.editable = true;

		s = m.section(form.TypedSection, 'third', _('third section'));
		s.anonymous = true;
		o = s.option(form.Value, 'password_option', _('Password Option'),
			_('Input for a password (storage on disk is not encrypted)'));
		o.password = true;
		o = s.option(form.DynamicList, 'list_option', _('Dynamic list option'));

		return m.render();
	},
});

```
