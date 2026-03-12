---
title: htmlview.js
module: luci-examples
origin_type: example_app
token_count: 318
version: e08008c
source_file: L1-raw/luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-htmlview-js.md
last_pipeline_run: '2026-03-12T09:09:53.122488+00:00'
upstream_path: applications/luci-app-example/htdocs/luci-static/resources/view/example/htmlview.js
language: javascript
ai_summary: The `htmlview.js` module is a JavaScript component for the LuCI framework in OpenWrt, designed to create a dynamic HTML view based on UCI configuration data. It includes functions for loading UCI configurations, rendering HTML elements, and displaying specific configuration options. The `load` function retrieves the 'example' configuration, while the `render` function constructs an HTML structure that presents the configuration data. This module is particularly useful for developers looking to create custom web interfaces for managing OpenWrt settings.
ai_when_to_use: Use `htmlview.js` when you need to build a web interface that displays and interacts with UCI configuration data in OpenWrt.
ai_related_topics:
- uci
- view
---
# htmlview.js
```javascript
'use strict';
'require uci';
'require view';

return view.extend({
	handleSaveApply: null,
	handleSave: null,
	handleReset: null,
	load: function () {
		return Promise.all([
			// The relevant ACL path for reading a configuration with UCI this way is
			// read > uci > ["example"]
			uci.load('example')
		]);
	},
	render: function (data) {
		var body = E([
			E('h2', _('Example HTML Page'))
		]);
		var sections = uci.sections('example');
		var listContainer = E('div');
		var list = E('ul');
		// Note that this is pretty error-prone, because sections might be missing
		// etcetera.
		list.appendChild(E('li', {
			'class': 'css-class'
		}, ['First Option in first section: ', E('em', {}, [sections[0]
			.first_option])]));
		list.appendChild(E('li', {
			'class': 'css-class'
		}, ['Flag in second section: ', E('em', {}, [sections[1].flag])]));
		list.appendChild(E('li', {
			'class': 'css-class'
		}, ['Select in second section: ', E('em', {}, [sections[1].select])]));
		listContainer.appendChild(list);
		body.appendChild(listContainer);
		console.log(sections);
		return body;
	}
});
```
