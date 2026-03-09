---
title: example.uc
module: luci-examples
origin_type: example_app
token_count: 292
version: unknown
source_file: L1-raw/luci-examples/example_app-luci-app-example-root-usr-share-rpcd-ucode-example-uc.md
last_pipeline_run: '2026-03-09T19:21:03.362055+00:00'
upstream_path: applications/luci-app-example/root/usr/share/rpcd/ucode/example.uc
language: ucode
---
# example.uc
```ucode
#!/usr/bin/env ucode

'use strict';

import { cursor } from 'uci';

// Rather than parse files in /etc/config, we can use `cursor`.
const uci = cursor();

const methods = {
	get_sample1: {
		call: function() {
			const num_cats = uci.get('example', 'animals', 'num_cats');
			const num_dogs = uci.get('example', 'animals', 'num_dogs');
			const num_parakeets = uci.get('example', 'animals', 'num_parakeets');
			const result = {
				num_cats,
				num_dogs,
				num_parakeets,
				is_this_real: false,
				not_found: null,
			};

			uci.unload();
			return result;
		}
	},

	get_sample2: {
		call: function() {
			const result = {
				option_one: {
					name: "Some string value",
					value: "A value string",
					parakeets: ["one", "two", "three"],
				},
				option_two: {
					name: "Another string value",
					value: "And another value",
					parakeets: [3, 4, 5],
				},
			};
			return result;
		}
	}
};

return { 'luci.example': methods };

```
