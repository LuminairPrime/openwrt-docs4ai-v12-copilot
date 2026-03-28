# OpenWrt Development Slices (Alpha Batch)

**Instructions:**
Read the following OpenWrt development scenarios. Execute each scenario sequentially. Output the requested code snippet for each scenario, clearly separated by headers (e.g. `### Result for Scenario 01`). Provide a brief explanation of the libraries or architecture you chose for each, and what difficulties and debates you experienced.

---

## Scenario 01
Write an OpenWrt startup script that runs at boot. It needs to start 'my_daemon' which is installed in the standard location for a daemon installed from a package on the official OpenWRT repository. Restart it if it crashes. It should read the 'hostname' variable from a configuration file named after the daemon stored in the standard config file folder and apply the new hostname to the system.

---

## Scenario 05
Write an OpenWrt web view file snippet that fetches a list of connected wifi clients from the system bus and displays their MAC addresses in a simple HTML table.

---

## Scenario 07
Consider an OpenWrt C plugin daemon. Write the C method handler function snippet for an incoming RPC call that replies with a JSON object containing `{"status": "ok"}`.

---

## Scenario 10
Write an OpenWrt script snippet to execute exactly once on the router's very first boot that sets the default timezone to UTC and permanently saves the change, and then tell me where to place the script on the file system.

---

## Scenario 13
Write an OpenWrt script snippet that safely reads an external JSON file from '/etc/my_app/config.json', parses the data natively, and prints the value of the 'startup_delay' key.

---

## Scenario 16
Write an OpenWrt script that runs two continuous `ping` commands to two different IP addresses like 10.10.10.2 and 10.10.10.3simultaneously (in parallel, not sequentially). It must capture their output asynchronously and print both ping results live to the screen, prefixing each output line with the target IP address so the two distinct streams are easily identifiable.
