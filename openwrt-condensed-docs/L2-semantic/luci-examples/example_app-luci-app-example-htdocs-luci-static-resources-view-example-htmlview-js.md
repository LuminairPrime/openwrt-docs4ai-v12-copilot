---
title: htmlview.js
module: luci-examples
origin_type: example_app
token_count: 318
version: unknown
source_file: L1-raw/luci-examples/example_app-luci-app-example-htdocs-luci-static-resources-view-example-htmlview-js.md
last_pipeline_run: '2026-03-09T21:35:51.010624+00:00'
upstream_path: applications/luci-app-example/htdocs/luci-static/resources/view/example/htmlview.js
language: javascript
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
