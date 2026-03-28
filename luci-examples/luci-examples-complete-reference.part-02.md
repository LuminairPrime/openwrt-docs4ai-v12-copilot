---
module: luci-examples
total_token_count: 292
section_count: 1
is_monolithic: false
is_sharded_part: true
part_number: 2
part_count: 2
generated: '2026-03-28T12:00:00.596003+00:00'
---

# luci-examples Complete Reference (Part 2 of 2)

> **Contains:** 1 documents
> **Tokens:** ~292 (cl100k_base)
> **Index:** [./luci-examples-complete-reference.md](./luci-examples-complete-reference.md)

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
