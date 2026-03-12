---
title: example.uc
module: luci-examples
origin_type: example_app
token_count: 292
version: 11ff260
source_file: L1-raw/luci-examples/example_app-luci-app-example-root-usr-share-rpcd-ucode-example-uc.md
last_pipeline_run: '2026-03-12T22:39:22.932543+00:00'
upstream_path: applications/luci-app-example/root/usr/share/rpcd/ucode/example.uc
language: ucode
ai_summary: 'The `example.uc` module provides a simple interface for accessing configuration data using the UCI (Unified Configuration Interface) in OpenWrt. It defines two methods: `get_sample1`, which retrieves the number of cats, dogs, and parakeets from the ''example'' configuration, and `get_sample2`, which returns predefined string and numeric values along with arrays of parakeets. This module leverages the `cursor` API to interact with UCI without directly parsing configuration files. It is designed to facilitate easy data retrieval for applications built on the LuCI framework.'
ai_when_to_use: Use this module when you need to access and manipulate configuration data in OpenWrt applications, particularly within the LuCI web interface.
ai_related_topics:
- cursor
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
