---
title: Write shell scripts in OpenWrt
module: wiki
origin_type: wiki_page
token_count: 1431
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-write-shell-script.md
last_pipeline_run: '2026-03-09T18:39:45.812572+00:00'
language: text
---
# Write shell scripts in OpenWrt

## The default OpenWrt shell is ash: the Almquist shell

The default [shell](https://en.wikipedia.org/wiki/Command-line_interface) provided with *OpenWrt* is the [Almquist shell](https://en.wikipedia.org/wiki/Almquist_shell), which is better known as the *ash shell* and is also the default [Busybox](https://en.wikipedia.org/wiki/BusyBox) shell. Most [Linux distros](https://en.wikipedia.org/wiki/Linux_distribution), such as [Ubuntu](https://en.wikipedia.org/wiki/Ubuntu) or [Debian](https://en.wikipedia.org/wiki/Debian), will use the [Bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)) shell, which is much bigger and more complex than *ash*. For example, a typical *bash* implementation requires approximately 1 MB of disk space, which is an extravagant waste of memory/space in an embedded device.

By contrast, *BusyBox* fits in less than 512 KB of space, and, in addition to providing the *ash* shell, it also provides many other tools you will need to manage your OpenWrt device. Some examples of the other very useful tools provided by *BusyBox* include [awk](https://en.wikipedia.org/wiki/AWK), [grep](https://en.wikipedia.org/wiki/grep), [sed](https://en.wikipedia.org/wiki/sed), and [vi/vim](https://en.wikibooks.org/wiki/Learning_the_vi_Editor/BusyBox_vi). Note that the stock (*i.e.* factory) firmware that ships with many routers also uses *BusyBox* for the reasons outlined here.

## OpenWrt, BusyBox, and the ash shell

OpenWrt firmware uses [BusyBox](https://en.wikipedia.org/wiki/Busybox) because it is extremely efficient with respect to 1) the size required to install it and run it in RAM, and 2) the amount of functionality it provides. Please be aware that many of the *BusyBox* implementations of common Linux/Unix tools might be more limited than their full desktop counterparts. However, *Bash* and *Busybox* shell are similar enough for the majority of daily use cases. If your script is using the [POSIX](https://en.wikipedia.org/wiki/POSIX) features of the *Bash* shell, then it will work in the *Ash* shell, too.

------------------------------------------------------------------------

**Q: Can I install a full version of Bash or other Linux CLI tools, including my favorite editor?**

**A: Yes!** *(but there is a catch)*

If your router supports USB storage and you choose to [install and configure a USB drive](/docs/guide-user/storage/usb-drives-quickstart) with your OpenWrt device, you will have much more storage space for installing programs. If you choose to go this route, then you can install the [bash package](/packages/pkgdata/bash) very easily. Also, OpenWrt contains many packages for installing the full versions of core Linux shell utilities, such as [basename](/packages/pkgdata/coreutils-basename), [cat](/packages/pkgdata/coreutils-cat), [rm](/packages/pkgdata/coreutils-rm), [sort](/packages/pkgdata/coreutils-sort), or [sleep](/packages/pkgdata/coreutils-sleep). To get an idea of the full list of available CLI packages, visit the web page for the OpenWrt packages in the [Utilities](/packages/index/utilities) category and search for all packages that start with *coreutils*. Also, OpenWrt contains many full sized versions of popular [Linux editors](/packages/index/utilities---editors) such as [nano](/packages/pkgdata/nano) and vim (see [vim](/packages/pkgdata/vim), [vim-full](/packages/pkgdata/vim-full), [vim-fuller](/packages/pkgdata/vim-fuller)).

**WARNING: DO NOT INSTALL ANY OF THE vim PACKAGES LINKED HERE UNLESS YOU HAVE INSTALLED A USB DRIVE.**

To illustrate the reason for this warning, as of v19.0x, the [vim-fuller](/packages/pkgdata/vim-fuller) package binary is ~2.8 MB, and it will be even larger when installed.

------------------------------------------------------------------------

## The shebang Operator and Shell Scripting for OpenWrt

Scripts in OpenWrt should have the shebang `#!/bin/sh` at the first line.

A shebang of `#!/bin/bash` can be used, but of course, only if the bash package is installed.

For more information, refer to the [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) operator.

------------------------------------------------------------------------

### Can I change my default shell from ash to bash?

The short answer is "*yes*", but this practice is not recommended.

**WARNING: If you update */etc/passwd* to change the *root* account's default shell to anything other than `#!/bin/sh`, there is a good chance you will be unable to log in to your router via SSH**.

If you've installed the [OpenWrt bash](/packages/pkgdata/bash) package on your router and then changed your default shell to `#!/bin/bash`, you will be able to login to your device via SSH. However, the risk in doing so is that you may still lock yourself out of your device inadvertently, for example, by upgrading. The working assumption for OpenWrt is that *ash* will be the default shell. If you want to use the *bash* shell regularly, then simply run the *bash* command each time you login to your device.

In the event you are having difficulty accessing your device via SSH, refer to the OpenWrt [failsafe process](/docs/guide-user/troubleshooting/failsafe_and_factory_reset).

------------------------------------------------------------------------

## Automated shell script checking

Write your bash scripts with `#!/bin/sh` first line in <https://www.shellcheck.net/> and it will check for features you cannot use in OpenWrt shell. see the <https://github.com/koalaman/shellcheck/blob/master/README.md#portability>

## Check if a tool is available

You may need to install additional command line tools in OpenWrt, as the default installation is very minimal. A Desktop PC Linux like Ubuntu has much more command line tools in default install.

Check if a tool is available by writing **type tool-name** and it will answer you where this tool is, or an error if there is no such tool installed. Use the package table or index (Packages link in the sidebar to the left of this article) to find the package with the tool you need.

    # type time
    time is /usr/bin/time

See also: [Configuration in scripts](config-scripting)