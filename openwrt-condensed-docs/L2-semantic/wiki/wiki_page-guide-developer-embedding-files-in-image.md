---
title: embedding-files-in-image
module: wiki
origin_type: wiki_page
token_count: 503
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-embedding-files-in-image.md
last_pipeline_run: '2026-03-09T18:12:55.650305+00:00'
language: text
---
# embedding-files-in-image

\<WRAP center round help 90%\> UPDATE: This functionality was [removed in April 2017](https://git.lede-project.org/?p=source.git;a=commit;h=b044bd5921e9644c9df9655bef10cee0af730724).

The easy way is to include the files as [custom files](/docs/guide-developer/toolchain/use-buildsystem#custom_files) \</WRAP\>

This is a plain copy-paste from mailing list, if you have some time to turn it in a proper wiki article please do so.

Hi Karl,  
let me introduce a not strictly new way but another heavily under documented buildroot feature which you can use to implement custom modifications to packages which do not require source code edits.  
For every processed package Makefile, the buildroot tries to include a a Makefile fragment in \$(TOPDIR)/overlay/\*/\$(PKG_DIR_NAME).mk which one can use to monkey-patch internals without directly touching the package recipes.  
For example to amend "base-files" to include a custom banner and inittab, you could create an overlay file called  

    "overlay/my-example-organization/base-files.mk"\\

which extends the default Package/base-files/install recipe to copy your custom files in the end.  
Assuming a directory structure like this  
\* overlay/my-example-organization/banner  
\* overlay/my-example-organization/inittab  
\* overlay/my-example-organization/base-files.mk  
the base-files.mk would need to include something like the following code to splicy your custom files into the packaging procedure:

    --- 8< ---
    # Figure out the containing dir of this Makefile
    OVERLAY_DIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

    # Declare custom installation commands
    define custom_install_commands
            @echo "Installing extra files from $(OVERLAY_DIR)"
            $(INSTALL_DIR) $(1)/etc/config
            $(INSTALL_DATA) $(OVERLAY_DIR)/banner $(1)/etc/banner
            $(INSTALL_DATA) $(OVERLAY_DIR)/inittab $(1)/etc/inittab
    endef

    # Append custom commands to install recipe,
    # and make sure to include a newline to avoid syntax error
    Package/base-files/install += $(newline)$(custom_install_commands)
    --- >8 ---

HTH, Jo