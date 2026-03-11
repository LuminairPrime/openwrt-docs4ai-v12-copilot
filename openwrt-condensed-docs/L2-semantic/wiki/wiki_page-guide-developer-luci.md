---
title: Adding new elements to LuCI
module: wiki
origin_type: wiki_page
token_count: 833
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-luci.md
last_pipeline_run: '2026-03-11T12:37:15.044626+00:00'
language: text
---
# Adding new elements to LuCI

This is a sample to show how to add a new element to the LuCI interface

[NOTE](../wiki/wiki_page-techref-luci2.md): Some of the information provided in this Wiki might be redundant from <https://github.com/openwrt/luci/wiki/ModulesHowTo>

As the examples show in the LuCI wiki, here are 2 ways to do this:

1.  CBI
2.  View (Template)

## Adding a new top level tab

First we are going to add a new tab to the top navigation. Normally one can see: Freifunk \| Status \| System \| Services \| Network, etc

One can do this by adding a file to the controller directory in your `<luci-path>/applications/luci-myapplication/luasrc/controller/myapp`

**\<luci-path\>** is the path of your LuCI source files

**luci-myapplication** is a new directory created for these examples. The name of the directory has to start with *luci-* so that it is recognized by `make menuconfig` and show up as a module to be compiled.

**controller** is the default directory for any UI control (i.e. new tab)

**myapp** is also a custom directory for this particular application

We will call this file `new_tab.lua`

The content is as follows:

``` lua
module("luci.controller.myapp.new_tab", package.seeall)  --notice that new_tab is the name of the file new_tab.lua
 function index()
     entry({"admin", "new_tab"}, firstchild(), "New tab", 60).dependent=false  --this adds the top level tab and defaults to the first sub-tab (tab_from_cbi), also it is set to position 30
     entry({"admin", "new_tab", "tab_from_cbi"}, cbi("myapp-mymodule/cbi_tab"), "CBI Tab", 1)  --this adds the first sub-tab that is located in <luci-path>/luci-myapplication/model/cbi/myapp-mymodule and the file is called cbi_tab.lua, also set to first position
     entry({"admin", "new_tab", "tab_from_view"}, template("myapp-mymodule/view_tab"), "View Tab", 2)  --this adds the second sub-tab that is located in <luci-path>/luci-myapplication/view/myapp-mymodule and the file is called view_tab.htm, also set to the second position
end
```

------------------------------------------------------------------------

## Adding the cbi_tab code

As specified above, we need to create a file called `cbi_tab.lua` in `<luci-path>/luci-myapplication/model/cbi/myapp-mymodule`

We will include the following code:

``` lua
m = Map("cbi_file", translate("First Tab Form"), translate("Please fill out the form below")) -- cbi_file is the config file in /etc/config
d = m:section(TypedSection, "info", "Part A of the form")  -- info is the section called info in cbi_file
a = d:option(Value, "name", "Name"); a.optional=false; a.rmempty = false;  -- name is the option in the cbi_file
return m
```

------------------------------------------------------------------------

## Adding the cbi_file

From the code above, we know we need a config file that has the appropriate sections and options. In our case, we will create the file *cbi_file* in `/etc/config` which looks like this:

    config 'info' 'A'
        option 'name' 'OpenWRT'

------------------------------------------------------------------------

## Adding the view_tab code

The *view_tab.htm* file needs to go in `<luci-path>/applications/luci-myapplication/luasrc/view/myapp-mymodule/`

Here are the contents of the file:

    <%+header%>
    <h1><%:Hello World%></h1>
    <%+footer%>
