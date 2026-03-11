---
title: 'ucode module: nl80211'
module: ucode
origin_type: c_source
token_count: 3950
version: 591d1f6
source_file: L1-raw/ucode/c_source-api-module-nl80211.md
last_pipeline_run: '2026-03-11T14:46:50.602050+00:00'
upstream_path: lib/nl80211.c
language: c
ai_summary: Provides netlink 802.11 wireless configuration API bindings for ucode. Implements request() to send and receive nl80211 commands including NL80211_CMD_GET_INTERFACE, NL80211_CMD_GET_STATION, NL80211_CMD_TRIGGER_SCAN, and regulatory domain queries. Returns structured attribute dictionaries parsed from kernel nl80211 netlink messages.
ai_when_to_use: Use in ucode-based wireless management handlers that need direct kernel-level 802.11 interface control, station enumeration, or scan triggering beyond what iwinfo or standard UCI wireless config expose.
ai_related_topics:
- nl80211.request
- NL80211_CMD_GET_INTERFACE
- NL80211_CMD_GET_STATION
- NL80211_CMD_TRIGGER_SCAN
---
# ucode module: nl80211

> **Live docs:** https://ucode.mein.io/module-nl80211.html

---

## Wireless Netlink

The `nl80211` module provides functions for interacting with the nl80211 netlink interface
for wireless networking configuration and management.

Functions can be individually imported and directly accessed using the
[named import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#named_import)
syntax:

  ```ucode
  import * as nl80211 from 'nl80211';

  // Send a nl80211 request
  let response = nl80211.request(nl80211.const.NL80211_CMD_GET_WIPHY, 0, { wiphy: 0 });

  // Create a listener for wireless events
  let wifiListener = nl80211.listener((msg) => {
      print('Received wireless event:', msg, '\n');
  }, [nl80211.const.NL80211_CMD_NEW_INTERFACE, nl80211.const.NL80211_CMD_DEL_INTERFACE]);

  // Wait for a specific nl80211 event
  let event = nl80211.waitfor([nl80211.const.NL80211_CMD_NEW_SCAN_RESULTS], 5000);
  if (event)
      print('Received scan results:', event.msg, '\n');
  ```

Alternatively, the module namespace can be imported
using a wildcard import statement:

  ```ucode
  import * as nl80211 from 'nl80211';

  // Send a nl80211 request
  let response = nl80211.request(nl80211.const.NL80211_CMD_GET_WIPHY, 0, { wiphy: 0 });

  // Create a listener for wireless events
  let listener = nl80211.listener((msg) => {
      print('Received wireless event:', msg, '\n');
  }, [nl80211.const.NL80211_CMD_NEW_INTERFACE, nl80211.const.NL80211_CMD_DEL_INTERFACE]);
  ```

Additionally, the nl80211 module namespace may also be imported by invoking
the `ucode` interpreter with the `-lnl80211` switch.

### nl80211.listener
**Kind**: static class of [`nl80211`](#module_nl80211)  
**See**: [listener()](module:nl80211#listener)  

### nl80211~Netlink message flags
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NLM_F_ACK | `number` | Request for acknowledgment |
| NLM_F_ACK_TLVS | `number` | Request for acknowledgment with TLVs |
| NLM_F_APPEND | `number` | Append to existing list |
| NLM_F_ATOMIC | `number` | Atomic operation |
| NLM_F_CAPPED | `number` | Request capped |
| NLM_F_CREATE | `number` | Create if not exists |
| NLM_F_DUMP | `number` | Dump request |
| NLM_F_DUMP_FILTERED | `number` | Dump filtered request |
| NLM_F_DUMP_INTR | `number` | Dump interrupted |
| NLM_F_ECHO | `number` | Echo request |
| NLM_F_EXCL | `number` | Exclusive creation |
| NLM_F_MATCH | `number` | Match request |
| NLM_F_MULTI | `number` | Multi-part message |
| NLM_F_NONREC | `number` | Non-recursive operation |
| NLM_F_REPLACE | `number` | Replace existing |
| NLM_F_REQUEST | `number` | Request message |
| NLM_F_ROOT | `number` | Root operation |

### nl80211~nl80211 commands
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_CMD_GET_WIPHY | `number` | Get wireless PHY attributes |
| NL80211_CMD_SET_WIPHY | `number` | Set wireless PHY attributes |
| NL80211_CMD_NEW_WIPHY | `number` | Create new wireless PHY |
| NL80211_CMD_DEL_WIPHY | `number` | Delete wireless PHY |
| NL80211_CMD_GET_INTERFACE | `number` | Get interface information |
| NL80211_CMD_SET_INTERFACE | `number` | Set interface attributes |
| NL80211_CMD_NEW_INTERFACE | `number` | Create new interface |
| NL80211_CMD_DEL_INTERFACE | `number` | Delete interface |
| NL80211_CMD_GET_KEY | `number` | Get key |
| NL80211_CMD_SET_KEY | `number` | Set key |
| NL80211_CMD_NEW_KEY | `number` | Add new key |
| NL80211_CMD_DEL_KEY | `number` | Delete key |
| NL80211_CMD_GET_BEACON | `number` | Get beacon |
| NL80211_CMD_SET_BEACON | `number` | Set beacon |
| NL80211_CMD_NEW_BEACON | `number` | Set beacon (alias) |
| NL80211_CMD_STOP_AP | `number` | Stop AP operation |
| NL80211_CMD_DEL_BEACON | `number` | Delete beacon |
| NL80211_CMD_GET_STATION | `number` | Get station information |
| NL80211_CMD_SET_STATION | `number` | Set station attributes |
| NL80211_CMD_NEW_STATION | `number` | Add new station |
| NL80211_CMD_DEL_STATION | `number` | Delete station |
| NL80211_CMD_GET_MPATH | `number` | Get mesh path |
| NL80211_CMD_SET_MPATH | `number` | Set mesh path |
| NL80211_CMD_NEW_MPATH | `number` | Add new mesh path |
| NL80211_CMD_DEL_MPATH | `number` | Delete mesh path |
| NL80211_CMD_SET_BSS | `number` | Set BSS attributes |
| NL80211_CMD_SET_REG | `number` | Set regulatory domain |
| NL80211_CMD_REQ_SET_REG | `number` | Request regulatory domain change |
| NL80211_CMD_GET_MESH_CONFIG | `number` | Get mesh configuration |
| NL80211_CMD_SET_MESH_CONFIG | `number` | Set mesh configuration |
| NL80211_CMD_GET_REG | `number` | Get regulatory domain |
| NL80211_CMD_GET_SCAN | `number` | Get scan results |
| NL80211_CMD_TRIGGER_SCAN | `number` | Trigger scan |
| NL80211_CMD_NEW_SCAN_RESULTS | `number` | New scan results available |
| NL80211_CMD_SCAN_ABORTED | `number` | Scan aborted |
| NL80211_CMD_REG_CHANGE | `number` | Regulatory domain change |
| NL80211_CMD_AUTHENTICATE | `number` | Authenticate |
| NL80211_CMD_ASSOCIATE | `number` | Associate |
| NL80211_CMD_DEAUTHENTICATE | `number` | Deauthenticate |
| NL80211_CMD_DISASSOCIATE | `number` | Disassociate |
| NL80211_CMD_MICHAEL_MIC_FAILURE | `number` | Michael MIC failure |
| NL80211_CMD_REG_BEACON_HINT | `number` | Beacon regulatory hint |
| NL80211_CMD_JOIN_IBSS | `number` | Join [IBSS](../wiki/wiki_page-techref-wireless-modes.md) |
| NL80211_CMD_LEAVE_IBSS | `number` | Leave [IBSS](../wiki/wiki_page-techref-wireless-modes.md) |
| NL80211_CMD_TESTMODE | `number` | Test mode |
| NL80211_CMD_CONNECT | `number` | Connect |
| NL80211_CMD_ROAM | `number` | Roam |
| NL80211_CMD_DISCONNECT | `number` | Disconnect |
| NL80211_CMD_SET_WIPHY_NETNS | `number` | Set wireless PHY network namespace |
| NL80211_CMD_GET_SURVEY | `number` | Get survey data |
| NL80211_CMD_NEW_SURVEY_RESULTS | `number` | New survey results |
| NL80211_CMD_SET_PMKSA | `number` | Set PMKSA |
| NL80211_CMD_DEL_PMKSA | `number` | Delete PMKSA |
| NL80211_CMD_FLUSH_PMKSA | `number` | Flush PMKSA |
| NL80211_CMD_REMAIN_ON_CHANNEL | `number` | Remain on channel |
| NL80211_CMD_CANCEL_REMAIN_ON_CHANNEL | `number` | Cancel remain on channel |
| NL80211_CMD_SET_TX_BITRATE_MASK | `number` | Set TX bitrate mask |
| NL80211_CMD_REGISTER_FRAME | `number` | Register frame |
| NL80211_CMD_REGISTER_ACTION | `number` | Register action frame |
| NL80211_CMD_FRAME | `number` | Frame |
| NL80211_CMD_ACTION | `number` | Action frame |
| NL80211_CMD_FRAME_TX_STATUS | `number` | Frame TX status |
| NL80211_CMD_ACTION_TX_STATUS | `number` | Action TX status |
| NL80211_CMD_SET_POWER_SAVE | `number` | Set power save |
| NL80211_CMD_GET_POWER_SAVE | `number` | Get power save |
| NL80211_CMD_SET_CQM | `number` | Set CQM |
| NL80211_CMD_NOTIFY_CQM | `number` | Notify CQM |
| NL80211_CMD_SET_CHANNEL | `number` | Set channel |
| NL80211_CMD_SET_WDS_PEER | `number` | Set WDS peer |
| NL80211_CMD_FRAME_WAIT_CANCEL | `number` | Cancel frame wait |
| NL80211_CMD_JOIN_MESH | `number` | Join mesh |
| NL80211_CMD_LEAVE_MESH | `number` | Leave mesh |
| NL80211_CMD_UNPROT_DEAUTHENTICATE | `number` | Unprotected deauthenticate |
| NL80211_CMD_UNPROT_DISASSOCIATE | `number` | Unprotected disassociate |
| NL80211_CMD_NEW_PEER_CANDIDATE | `number` | New peer candidate |
| NL80211_CMD_GET_WOWLAN | `number` | Get WoWLAN |
| NL80211_CMD_SET_WOWLAN | `number` | Set WoWLAN |
| NL80211_CMD_START_SCHED_SCAN | `number` | Start scheduled scan |
| NL80211_CMD_STOP_SCHED_SCAN | `number` | Stop scheduled scan |
| NL80211_CMD_SCHED_SCAN_RESULTS | `number` | Scheduled scan results |
| NL80211_CMD_SCHED_SCAN_STOPPED | `number` | Scheduled scan stopped |
| NL80211_CMD_SET_REKEY_OFFLOAD | `number` | Set rekey offload |
| NL80211_CMD_PMKSA_CANDIDATE | `number` | PMKSA candidate |
| NL80211_CMD_TDLS_OPER | `number` | TDLS operation |
| NL80211_CMD_TDLS_MGMT | `number` | TDLS management |
| NL80211_CMD_UNEXPECTED_FRAME | `number` | Unexpected frame |
| NL80211_CMD_PROBE_CLIENT | `number` | Probe client |
| NL80211_CMD_REGISTER_BEACONS | `number` | Register beacons |
| NL80211_CMD_UNEXPECTED_4ADDR_FRAME | `number` | Unexpected 4-address frame |
| NL80211_CMD_SET_NOACK_MAP | `number` | Set no-ack map |
| NL80211_CMD_CH_SWITCH_NOTIFY | `number` | Channel switch notify |
| NL80211_CMD_START_P2P_DEVICE | `number` | Start P2P device |
| NL80211_CMD_STOP_P2P_DEVICE | `number` | Stop P2P device |
| NL80211_CMD_CONN_FAILED | `number` | Connection failed |
| NL80211_CMD_SET_MCAST_RATE | `number` | Set multicast rate |
| NL80211_CMD_SET_MAC_ACL | `number` | Set MAC ACL |
| NL80211_CMD_RADAR_DETECT | `number` | Radar detect |
| NL80211_CMD_GET_PROTOCOL_FEATURES | `number` | Get protocol features |
| NL80211_CMD_UPDATE_FT_IES | `number` | Update FT IEs |
| NL80211_CMD_FT_EVENT | `number` | FT event |
| NL80211_CMD_CRIT_PROTOCOL_START | `number` | Start critical protocol |
| NL80211_CMD_CRIT_PROTOCOL_STOP | `number` | Stop critical protocol |
| NL80211_CMD_GET_COALESCE | `number` | Get coalesce |
| NL80211_CMD_SET_COALESCE | `number` | Set coalesce |
| NL80211_CMD_CHANNEL_SWITCH | `number` | Channel switch |
| NL80211_CMD_VENDOR | `number` | Vendor command |
| NL80211_CMD_SET_QOS_MAP | `number` | Set QoS map |
| NL80211_CMD_ADD_TX_TS | `number` | Add TX TS |
| NL80211_CMD_DEL_TX_TS | `number` | Delete TX TS |
| NL80211_CMD_GET_MPP | `number` | Get MPP |
| NL80211_CMD_JOIN_OCB | `number` | Join OCB |
| NL80211_CMD_LEAVE_OCB | `number` | Leave OCB |
| NL80211_CMD_CH_SWITCH_STARTED_NOTIFY | `number` | Channel switch started notify |
| NL80211_CMD_TDLS_CHANNEL_SWITCH | `number` | TDLS channel switch |
| NL80211_CMD_TDLS_CANCEL_CHANNEL_SWITCH | `number` | Cancel TDLS channel switch |
| NL80211_CMD_ABORT_SCAN | `number` | Abort scan |

### nl80211~Scan flags
Constants for NL80211_ATTR_SCAN_FLAGS bitmask.

**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_SCAN_FLAG_LOW_PRIORITY | `number` | Low priority scan |
| NL80211_SCAN_FLAG_FLUSH | `number` | Flush scan results before returning |
| NL80211_SCAN_FLAG_AP | `number` | Force AP mode scan |
| NL80211_SCAN_FLAG_RANDOM_ADDR | `number` | Randomize source MAC address |
| NL80211_SCAN_FLAG_FILS_MAX_CHANNEL_TIME | `number` | FILS max channel time |
| NL80211_SCAN_FLAG_ACCEPT_BCAST_PROBE_RESP | `number` | Accept broadcast probe responses |
| NL80211_SCAN_FLAG_OCE_PROBE_REQ_HIGH_TX_RATE | `number` | OCE high TX rate probe requests |
| NL80211_SCAN_FLAG_OCE_PROBE_REQ_DEFERRAL_SUPPRESSION | `number` | OCE probe request deferral suppression |
| NL80211_SCAN_FLAG_LOW_SPAN | `number` | Low span scan |
| NL80211_SCAN_FLAG_LOW_POWER | `number` | Low power scan |
| NL80211_SCAN_FLAG_HIGH_ACCURACY | `number` | High accuracy scan |
| NL80211_SCAN_FLAG_RANDOM_SN | `number` | Randomize sequence number |
| NL80211_SCAN_FLAG_MIN_PREQ_CONTENT | `number` | Minimize probe request content |
| NL80211_SCAN_FLAG_FREQ_KHZ | `number` | Report scan results with frequency in KHz |
| NL80211_SCAN_FLAG_COLOCATED_6GHZ | `number` | Scan colocated 6GHz BSS |

### nl80211~BSS status constants
Constants for BSS status values.

**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_BSS_STATUS_AUTHENTICATED | `number` | Authenticated with BSS |
| NL80211_BSS_STATUS_ASSOCIATED | `number` | Associated with BSS |
| NL80211_BSS_STATUS_IBSS_JOINED | `number` | Joined [IBSS](../wiki/wiki_page-techref-wireless-modes.md) |

### nl80211~BSS use-for and cannot-use-reasons constants
Constants for BSS use-for and cannot-use-reasons bitmasks.

**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_BSS_USE_FOR_NORMAL | `number` | Use BSS for normal connection |
| NL80211_BSS_USE_FOR_MLD_LINK | `number` | Use BSS as MLD link |
| NL80211_BSS_CANNOT_USE_NSTR_NONPRIMARY | `number` | NSTR nonprimary link not usable |
| NL80211_BSS_CANNOT_USE_6GHZ_PWR_MISMATCH | `number` | 6GHz power mode mismatch |

### nl80211~HWSIM commands
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| HWSIM_CMD_REGISTER | `number` | Register radio |
| HWSIM_CMD_FRAME | `number` | Send frame |
| HWSIM_CMD_TX_INFO_FRAME | `number` | Send TX info frame |
| HWSIM_CMD_NEW_RADIO | `number` | Create new radio |
| HWSIM_CMD_DEL_RADIO | `number` | Delete radio |
| HWSIM_CMD_GET_RADIO | `number` | Get radio information |
| HWSIM_CMD_ADD_MAC_ADDR | `number` | Add MAC address |
| HWSIM_CMD_DEL_MAC_ADDR | `number` | Delete MAC address |
| HWSIM_CMD_START_PMSR | `number` | Start peer measurement |
| HWSIM_CMD_ABORT_PMSR | `number` | Abort peer measurement |
| HWSIM_CMD_REPORT_PMSR | `number` | Report peer measurement |

### nl80211~Interface types
**Kind**: inner typedef of [`nl80211`](#module_nl80211)  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| NL80211_IFTYPE_ADHOC | `number` | [IBSS](../wiki/wiki_page-techref-wireless-modes.md)/ad-hoc interface |
| NL80211_IFTYPE_STATION | `number` | Station interface |
| NL80211_IFTYPE_AP | `number` | Access point interface |
| NL80211_IFTYPE_AP_VLAN | `number` | AP VLAN interface |
| NL80211_IFTYPE_WDS | `number` | WDS interface |
| NL80211_IFTYPE_MONITOR | `number` | Monitor interface |
| NL80211_IFTYPE_MESH_POINT | `number` | Mesh point interface |
| NL80211_IFTYPE_P2P_CLIENT | `number` | P2P client interface |
| NL80211_IFTYPE_P2P_GO | `number` | P2P group owner interface |
| NL80211_IFTYPE_P2P_DEVICE | `number` | P2P device interface |
| NL80211_IFTYPE_OCB | `number` | Outside context of BSS (OCB) interface |