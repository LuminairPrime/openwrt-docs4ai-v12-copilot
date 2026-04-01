---
title: 'jshn: a JSON parsing and generation library in for shell scripts'
module: wiki
origin_type: wiki_page
token_count: 3692
source_file: L1-raw/wiki/wiki_page-guide-developer-jshn.md
last_pipeline_run: '2026-04-01T13:49:08.540826+00:00'
source_url: https://openwrt.org/docs/guide-developer/jshn
language: text
ai_summary: The `jshn` module is a JSON parsing and generation library designed for use in shell scripts within OpenWrt. It provides functions to initialize JSON structures, add various data types (like integers, strings, booleans, arrays, and objects), and parse JSON data from variables or files. Key functions include `json_init`, `json_add_int`, `json_load`, and `json_get_var`, which facilitate the creation and manipulation of JSON data in shell scripts. This library is particularly useful for developers needing to handle JSON in environments lacking native JSON support.
ai_when_to_use: Use `jshn` when you need to parse or generate JSON data in OpenWrt shell scripts, especially when working with APIs or configuration files that utilize JSON format.
ai_related_topics:
- json_init
- json_add_int
- json_add_string
- json_add_boolean
- json_add_array
- json_add_object
- json_load
- json_get_var
- json_get_vars
- json_select
- json_close_object
- json_close_array
- json_dump
- json_load_file
- json_is_a
---

> **Source:** [https://openwrt.org/docs/guide-developer/jshn](https://openwrt.org/docs/guide-developer/jshn)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-04-01

# jshn: a JSON parsing and generation library in for shell scripts

`jshn` (JSON SHell Notation), a small utility and shell library for parsing and generating [JSON](https://en.wikipedia.org/wiki/JSON) data.

Shell scripts (ash, bash, zsh) doesn't have built-in functions to work with JSON or other hierarchical structures so OpenWrt provides a shell library [/usr/share/libubox/jshn.sh](https://git.openwrt.org/?p=project/libubox.git;a=blob;f=sh/jshn.sh;hb=HEAD) from `libubox` package. You need to include it into your scripts and then you can call it's functions:

``` bash
#!/bin/sh

# source jshn shell library
. /usr/share/libubox/jshn.sh

# generating json data
json_init
json_add_int "code" "0"
json_add_string "msg" "Hello, world!"
json_add_object "test"
json_add_int "testdata" "1"
json_close_object
MSG_JSON=`json_dump`
# the MSG_JSON var now contains: { "code": 0, "msg": "Hello, world!", "test": { "testdata": 1 } }

# parsing json data from the MSG_JSON variable
local var1 code msg # declare local variables to load data into
json_load "$MSG_JSON"
json_select test # go into the object inside of the "test" field
json_get_var var1 testdata # first is var name "var1" then the JSON field name "testdata"
json_select .. # go back to the upper level
# load the "code" field into corresponding code var, and the "msg" field into the msg var
json_get_vars code msg

echo "code: $code, msg: $msg, testdata: $var1"
```

Another example:

``` bash
#!/bin/sh

# source jshn shell library
. /usr/share/libubox/jshn.sh

# initialize JSON output structure
json_init

# add a boolean field
json_add_boolean foo 0

# add an integer field
json_add_int code 123

# add a string, take care of escaping
json_add_string result "Some complex string\n with newlines\n and even command output: $(date)"

# add an array with three integers
json_add_array alist
json_add_int "" 1
json_add_int "" 2
json_add_int "" 3
json_close_array

# add an object (dictionary)
json_add_object adict
json_add_string foo bar
json_add_string bar baz
json_close_object

# build JSON object and print to stdout
json_dump

# will output something like this:
# { "foo": false, "code": 123, "result": "Some complex string\\n with newlines\\n and even command output: Fri Jul 13 07:11:39 CEST 2018", "alist": [ 1, 2, 3 ], "adict": { "foo": "bar", "bar": "baz" } }
```

### More complicated examples

#### Parse file example

Given the file:

``` yaml
{
  "status": 200,
  "msg": "ok",
  "result": {
    "number": "99",
    "mac": "d85d4c9c2f1a",
    "last_seen": 1363777473407
  }
}
```

Script to parse it:

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_init
json_load_file /data2.txt  ## Load JSON from file
## json_get_var <local_var> <json_var>
json_get_var status status    ## Get Value of status inside JSON string (i.e. MSG) into local "status" variable
json_get_var msg msg
json_select result            ## Select "result" object of JSON string (i.e. MSG)
json_get_var number number
json_get_var mac mac
json_get_var last_seen last_seen
```

#### Parse arrays example

Given the file:

``` yaml
{
  "ip_addrs": {
    "lan": ["192.168.0.100","192.168.0.101","192.168.0.200"]
  }
}
```

Script to parse it:

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_init
json_load_file /data2.json
json_select "ip_addrs"

if json_is_a lan array
then
  json_select lan
  idx=1 # note that array element position starts from 1 not, 0
  while json_is_a ${idx} string  ## iterate over data inside "lan" object
  do
    json_get_var ip_addr $idx
    echo "$ip_addr"
    idx=$(( idx + 1 ))
  done
fi
```

#### Parse list of objects

The example will download electricity hourly prices for Finland in JSON and parse it. The prices JSON looks like

``` yaml
{
  "prices": [
    {
      "date": "2024-08-03T11:00:00.000Z",
      "value": 6.41
    },
    {
      "date": "2024-08-03T12:00:00.000Z",
      "value": 4.1
    },
  ]
}
```

Script to parse it:

``` bash
#!/bin/sh
set -e
. /usr/share/libubox/jshn.sh
date=$(date -u +%Y-%m-%dT%H:00:00.000Z)

# download prices JSON via wget in quiet mode with output to stdout that will be saved to a variable PRICES_JSON
PRICES_JSON=$(wget -qO - "https://sahkotin.fi/prices?start=$date")
exit_status=$?
# check exit code: if any error then exit
if [ $exit_status -ne 0 ]; then
   >&2 echo "error $exit_status"
   exit $exit_status
fi

json_load "$PRICES_JSON"
json_select "prices"
idx=1 # note that array element position starts from 1 not, 0
# iterate over data inside "price" array until elements are objects
while json_is_a $idx object
do
  json_select  $idx
  # now parse {"date": "2024-08-04T21:00:00.000Z", "value": 22.58}
  json_get_var price_date "date"
  echo "price_date: $price_date"
  json_get_var price_value "value"
  echo "price_value: $price_value"
  idx=$(( idx + 1 ))
  json_select .. # go back to the upper level to the prices array
done

echo "Total parsed $idx"
```

## json_for_each_item

Function useful to iterate through the different elements of an array or object. The provided callback function is called for each element which is passed the value, key and user provided arguments. For field types different from array or object the callback is called with the retrieved value.

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_load_file /data2.json

dump_item() {
 echo "item: $1 '$2'"
}

json_for_each_item "dump_item" "ip_addrs"
```

## json_get_values

To get all values of an array use the `json_get_values`:

``` bash
#!/bin/sh
. /usr/share/libubox/jshn.sh

json_load '{"alist":[1,2]}'
json_get_values values "alist"
echo "${values}" #=> 1 2
# print comma separated
echo "${values// /, }" #=> 1, 2
```

## Get all fields into variables

Get all fields and declare variables for them:

``` bash
json_load '{"params":{"id": 1, "name": "Alice"}}'
json_select "params"
json_get_keys keys
for key in $keys
do
  json_get_var "$key" "$key"
done
echo "$id" #=> 1
echo "$name" #=> Alice
```

## jshn utility

Internally the `/usr/share/libubox/jshn.sh` is just a wrapper for [/usr/bin/jshn](https://git.openwrt.org/?p=project/libubox.git;a=blob;f=jshn.c;hb=HEAD) utility.

    root@OpenWrt:/# jshn
    Usage: jshn [-n] [-i] -r <message>|-R <file>|-o <file>|-p <prefix>|-w

Options:

- `-r <message>` parse from string `<message>`: called from `json_load()`
- `-R <file>` parse from file `<file>`: called from `json_load_file()`
- `-w` write the constructed object to stdout: called from `json_dump()`
- `-o <file>` write to file `<file>`
- `-p <prefix>` set prefix
- `-n` no newlines \n on formatting
- `-i` indent nested objects on formatting

You can call it directly:

``` bash
root@OpenWrt:/# jshn -R /etc/board.json
json_init;
json_add_object 'model';
json_add_string 'id' 'innotek-gmbh-virtualbox';
json_add_string 'name' 'innotek GmbH VirtualBox';
json_close_object;
json_add_object 'network';
json_add_object 'lan';
json_add_string 'ifname' 'eth0';
json_add_string 'protocol' 'static';
json_close_object;
json_add_object 'wan';
json_add_string 'ifname' 'eth1';
json_add_string 'protocol' 'dhcp';
json_close_object;
json_close_object;
```

The output is then evaluated inside of the shell script to create in memory structure as in file.

If you created an object like:

``` bash
json_init;
json_add_string 'username' 'root';
json_dump;
```

Then internally it will call `jshn -w` with the json obj passed via multiple env variables like

    root@OpenWrt:/# JSON_CUR=J_V T_J_V_username=string K_J_V=username J_V_username=root jshn -w
    { "username": "root" }

Here `J_V` stands for "JSON value":

- `JSON_CUR` means a name of var with root object to format
- `K_J_V` is a key name i.e. `username`
- `T_J_V_username` is a type of the `username` field
- `J_V_username=root` is a value of the the `username` field i.e. `root`

## Other examples

### Get bridge status

OpenWrt have a command `devstatus` to check network device status. E.g. `devstatus br-lan` prints:

``` yaml
{
        "external": false,
        "present": true,
        "type": "bridge",
        "up": true,
        "carrier": true,
        "bridge-members": [
                "eth0.1",
                "wlan0"
        ],
        "mtu": 1500,
        "mtu6": 1500,
        "macaddr": "84:16:f9:9b:e0:7a",
        "txqueuelen": 1000,
        "ipv6": true,
        "promisc": false,
        "rpfilter": 0,
        "acceptlocal": false,
        "igmpversion": 0,
        "mldversion": 0,
        "neigh4reachabletime": 30000,
        "neigh6reachabletime": 30000,
        "neigh4gcstaletime": 60,
        "neigh6gcstaletime": 60,
        "neigh4locktime": 100,
        "dadtransmits": 1,
        "multicast": true,
        "sendredirects": true,
        "statistics": {
                "collisions": 0,
                "rx_frame_errors": 0,
                "tx_compressed": 0,
                "multicast": 0,
                "rx_length_errors": 0,
                "tx_dropped": 0,
                "rx_bytes": 10609108786,
                "rx_missed_errors": 0,
                "tx_errors": 0,
                "rx_compressed": 0,
                "rx_over_errors": 0,
                "tx_fifo_errors": 0,
                "rx_crc_errors": 0,
                "rx_packets": 39594607,
                "tx_heartbeat_errors": 0,
                "rx_dropped": 0,
                "tx_aborted_errors": 0,
                "tx_packets": 91154927,
                "rx_errors": 0,
                "tx_bytes": 121051584071,
                "tx_window_errors": 0,
                "rx_fifo_errors": 0,
                "tx_carrier_errors": 0
        }
}
```

You can check the `devstatus` sources to see that internally it makes a [ubus call](/docs/techref/ubus) and uses the `jshn` to format output:

``` bash
cat /sbin/devstatus
#!/bin/sh
. /usr/share/libubox/jshn.sh
DEVICE="$1"

[ -n "$DEVICE" ] || {
    echo "Usage: $0 <device>"
    exit 1
}

json_init
json_add_string name "$DEVICE"
ubus call network.device status "$(json_dump)"
```

### Check if Link is up using devstatus and jshn

``` bash
#!/bin/sh

. /usr/share/libubox/jshn.sh

WANDEV="$(uci get network.wan.ifname)"

json_load "$(devstatus $WANDEV)"

json_get_var var1 speed
json_get_var var2 link

echo "Speed: $var1"
echo "Link: $var2"
```

## Additional JSON parsing tools

### jsonfilter

The [jsonfilter](commit>project/jsonpath.git) tool in included into OpenWrt. The help output:

    root@openwrt:~# jsonfilter --help
    == Usage ==

      # jsonfilter [-a] [-i <file> | -s "json..."] {-t <pattern> | -e <pattern>}
      -q            Quiet, no errors are printed
      -h, --help    Print this help
      -a            Implicitely treat input as array, useful for JSON logs
      -i path       Specify a JSON file to parse
      -s "json"     Specify a JSON string to parse
      -l limit      Specify max number of results to show
      -F separator  Specify a field separator when using export
      -t <pattern>  Print the type of values matched by pattern
      -e <pattern>  Print the values matched by pattern
      -e VAR=<pat>  Serialize matched value for shell "eval"

    == Patterns ==

      Patterns are JsonPath: http://goessner.net/articles/JsonPath/
      This tool implements $, @, [], * and the union operator ','
      plus the usual expressions and literals.
      It does not support the recursive child search operator '..' or
      the '?()' and '()' filter expressions as those would require a
      complete JavaScript engine to support them.

    == Examples ==

      Display the first IPv4 address on lan:
      # ifstatus lan | jsonfilter -e '@["ipv4-address"][0].address'

      Extract the release string from the board information:
      # ubus call system board | jsonfilter -e '@.release.description'

      Find all interfaces which are up:
      # ubus call network.interface dump | \
            jsonfilter -e '@.interface[@.up=true].interface'

      Export br-lan traffic counters for shell eval:
      # devstatus br-lan | jsonfilter -e 'RX=@.statistics.rx_bytes' \
            -e 'TX=@.statistics.tx_bytes'

Usage example:

``` bash
ubus call network.wireless status | jsonfilter -e '@[*]' | jsonfilter -a -e '@[1]'
```

The first jsonfilter call will output one radio JSON structure object per line, the second call then consumes this lines while using the -a flag to treat them like an array, this allows you to select the first or second radio regardless of the name.

### jq

[jq](https://stedolan.github.io/jq/) jq is a flexible command-line JSON processor that is very popular for scripting. It's not installed by default in OpenWRT because is too big (more than 200Kb) so to install use `opkg update; opkg install jq` By default it just colorize an output e.g. `cat /etc/board.json | jq`

### See also

- [Awesome JSON](https://github.com/burningtree/awesome-json) A curated list of awesome JSON libraries and resources.
- [OpenWrt script samples](https://github.com/yurt-page/openwrt-script-samples)
- [Writing shell scripts support forum topic](https://forum.openwrt.org/t/writing-shell-scripts-support-topic/206144)
