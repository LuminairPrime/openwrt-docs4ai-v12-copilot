---
title: OpenWrt Feeds
module: wiki
origin_type: wiki_page
token_count: 2736
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-feeds.md
last_pipeline_run: '2026-03-12T09:09:53.122488+00:00'
language: text
ai_summary: OpenWrt Feeds are collections of packages that can be sourced from various locations, including remote servers and version control systems. They are essential for managing additional package build recipes in OpenWrt Buildroot, allowing for customization through a feed configuration file. The configuration is typically done in the `feeds.conf` or `feeds.conf.default` files, where each feed is defined by its method, name, and source. Supported feed methods include `src-git`, `src-bzr`, `src-hg`, and others, enabling diverse ways to retrieve package data.
ai_when_to_use: Use OpenWrt Feeds when you need to manage and customize package sources for building OpenWrt images. This is particularly useful for integrating additional software or maintaining custom packages.
ai_related_topics:
- feeds.conf
- feeds.conf.default
- src-git
- src-bzr
- src-hg
- src-svn
- src-link
- src-darcs
- src-gitsvn
- src-git-full
- src-cpy
---
# OpenWrt Feeds

In OpenWrt, a "feed" is a collection of [packages](/docs/guide-developer/packages) which share a common location. Feeds may reside on a remote server, in a version control system, on the local filesystem, or in any other location addressable by a single name (path/URL) over a protocol with a supported feed method.

Feeds are additional predefined package build recipes for OpenWrt Buildroot. They may be configured to support custom feeds or non-default feed packages via a feed configuration file.

## Feed Configuration

The list of usable feeds is configured from either the `feeds.conf` file, if it exists, or otherwise the `feeds.conf.default` file. This file contains a list of feeds with each feed listed on a separate line. Each feed line consists of 3 whitespace-separated components: The feed method, the feed name, and the feed source. Blank lines, excessive white-space/newlines, and comments are ignored during parsing. Comments begin with \`#\` and extend to the end of a line.

Nowadays (AToW 2026-01-17) the `main` branch, the defaults contained within `feeds.conf.default` appear as follows. Note that the `#` prefixed lines are commented out and included for ease of configuration.

``` xml
src-git packages https://git.openwrt.org/feed/packages.git
src-git luci https://git.openwrt.org/project/luci.git
src-git routing https://git.openwrt.org/feed/routing.git
src-git telephony https://git.openwrt.org/feed/telephony.git
src-git video https://github.com/openwrt/video.git
#src-git targets https://github.com/openwrt/targets.git
#src-git oldpackages http://git.openwrt.org/packages.git
#src-link custom /usr/src/openwrt/custom-feed
```

The git method can specify a specific branch or commit using the following formats

    src-git local_feed_name https://example.com/repo_name/something.git;branch_name
    src-git local_feed_name https://example.com/repo_name/something.git^commit_hash

As of this writing, the following feed methods are supported:

| Method       | Function                                                                                                                  |
|:-------------|---------------------------------------------------------------------------------------------------------------------------|
| src-bzr      | Data is downloaded from the source path/URL using `bzr`                                                                   |
| src-cpy      | Data is copied from the source path. The path can be specified as either relative to OpenWrt repository root or absolute. |
| src-darcs    | Data is downloaded from the source path/URL using `darcs`                                                                 |
| src-git      | Data is downloaded from the source path/URL using `git` as a shallow (depth of 1) clone                                   |
| src-git-full | Data is downloaded from the source path/URL using `git` as a full clone                                                   |
| src-gitsvn   | Bidirectional operation between a Subversion repository and git                                                           |
| src-hg       | Data is downloaded from the source path/URL using `hg`                                                                    |
| src-link     | A symlink to the source path is created. The path must be absolute.                                                       |
| src-svn      | Data is downloaded from the source path/URL using `svn`                                                                   |

Feed names are used to identify feeds and serve as the basis for several file and directory names that are created to hold information about the feeds. The feed source is the location from which the feed data is downloaded.

For the methods listed above which rely on version control systems that support a "limited history" option (such as `--depth=1` for git and `--lightweight` for bzr) the smallest available history is downloaded. This is a good default, but developers who are actively committing to a feed and/or using the commit history may want to change this behavior. This can be done by editing `scripts/feeds` to use `src-git-full` or by checking out the feed without using `scripts/feeds`. A shallow git clone can be updated to a "full" clone through use of `git fetch --unshallow`

## Working with Feeds

As of December, 2018, feeds are retrieved and managed by the script `scripts/feeds` within the `openwrt/openwrt.git` repository. The `feeds` script incorporates packages from a variety of feed sources into the OpenWrt build system. This is a two step process done by the developer before building an image by updating a feed followed by installing packages from specific to that feed.

During the `update` step, the feeds are obtained from their sources listed within a [feed configuration](/docs/guide-developer/feeds#feed_configuration) and then copied into the `feeds` directory. After a successful update, each package recipe within a feed is represented within a folder in `feeds/<feed_name>/<package_name>/`, but they are not currently incorporated into the OpenWrt build system as they are not contained within the \`package/\` directory.

During the `install` step, packages from the feeds obtained during an \`update\` are then linked into the `package/feeds/<feed_name>` folder, where `<feed_name>` is replaced by the name of the feed in the feed configuration. After this step, it is then possible to perform package specific make operations by utilizing their path within the `package/` folder. For example:

`make package/feeds/<feed_name>/<package_name>`

    $ ./scripts/feeds
    Usage: ./scripts/feeds <command> [options]

    Commands:
            list [options]: List feeds, their content and revisions (if installed)
            Options:
                -n :            List of feed names.
                -s :            List of feed names and their URL.
                -r <feedname>:  List packages of specified feed.
                -d <delimiter>: Use specified delimiter to distinguish rows (default: spaces)
                -f :            List feeds in opkg [feeds.conf](../wiki/wiki_page-guide-developer-creating-a-meson-based-package.md) compatible format (when using -s).

            install [options] <package>: Install a package
            Options:
                -a :           Install all packages from all feeds or from the specified feed using the -p option.
                -p <feedname>: Prefer this feed when installing packages.
                -d <y|m|n>:    Set default for newly installed packages.
                -f :           Install will be forced even if the package exists in core OpenWrt (override)

            search [options] <substring>: Search for a package
            Options:
                -r <feedname>: Only search in this feed

            uninstall -a|<package>: Uninstall a package
            Options:
                -a :           Uninstalls all packages.

            update -a|<feedname(s)>: Update packages and lists of feeds in [feeds.conf](../wiki/wiki_page-guide-developer-creating-a-meson-based-package.md) .
            Options:
                -a :           Update all feeds listed within [feeds.conf](../wiki/wiki_page-guide-developer-creating-a-meson-based-package.md). Otherwise the specified feeds will be updated.
                -r :           Update by rebase. (git only. Useful if local commits exist)
                -s :           Update by rebase and autostash. (git only. Useful if local commits and uncommited changes exist)
                -i :           Recreate the index only. No feed update from repository is performed.
                -f :           Force updating feeds even if there are changed, uncommitted files.

            clean:             Remove downloaded/generated files.

### Feed Commands

Feeds can be utilized through the `scripts/feeds` script. A list of the available commands is generated by invoking `scripts/feeds` without any arguments. Most commands require the feed information to be available locally, so running update first is usually necessary. In the following discussion the term "applicable packages" usually refers to the package names given on the command line or all packages in a feed when the -a option is used.

#### Clean

The clean command removes the locally stored feed data, including the feed indexes and data for all packages in the feed (but not the symlinks created by the install command, which will be dangling until the feeds are re-downloaded by the update command). This is done by removing the `feeds` directory and all subdirectories.

#### Install

The install command installs the applicable packages and any packages on which the applicable packages depend (both direct dependencies and build dependencies). The installation process consists of creating a symbolic link from `package/feeds/$feed_name/$package_name` to `feeds/$feed_name/$package_name` so that the package will be included in the configuration process when the directory hierarchy under `packages` is searched.

| Command                            | Description                                                                                                  |
|:-----------------------------------|--------------------------------------------------------------------------------------------------------------|
| ./scripts/feeds install -a         | Install all packages (not required; packages can be installed on an as-needed basis for slow build machines) |
| ./scripts/feeds install luci       | Install only the package LuCI                                                                                |
| ./scripts/feeds install -a -p luci | Install the complete LuCI WebUI by installing all (-a) packages from the preferred feed (-p) luci            |

See the above section for a list of the feeds available by default.

|                                                                   |                                                                                                                                               |
|-------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|
| ![48px-outdated.svg.png](/meta/icons/tango/48px-outdated.svg.png) | Please note that this replaces the old method of creating symlinks, which can be still found on-line in many old forum and user-group entries |

#### List

The list command reads and displays the list of packages in each feed from the index file for the applicable feeds. The index file is stored in the `feeds` directory with the name of the feed suffixed with `.index`. The file is generated by the update command.

#### Search

The search command reads through the feed metadata and lists packages which match the given search criteria.

#### Uninstall

The uninstall command does the opposite of the install command (although it does not address dependent packages in any way). It simply removes any symlinks to the package from the subdirectories of `package/feeds`.

#### Update

When `scripts/feeds update` is invoked, each of the applicable feeds are downloaded from their source location into a subdirectory of `feeds` with the feed name. It then parses the package information from the feed into an index file used by the list and search commands.

| Command                              | Description                          |
|:-------------------------------------|--------------------------------------|
| ./scripts/feeds update packages luci | Checkout the packages and luci feeds |

Note that update also stores the configured location of the feed in `feeds/$feed_name.tmp/location` such that changes to the configuration can be detected and handled appropriately.

After retrieval the downloaded packages need to be *"installed"*. Only after installation will they be available in the configuration interface!

## Custom Feeds

Ok, you've developed your package, and now you want to use it via make menuconfig, OR you are developing a package and you want to test it in a build before you try to get it included in OpenWrt.

The solution is a custom feed. You can either create an entirely new feed, or use a modified version of one of the standard ones.

### Creating the package directory

For this example we assume that your are in `/home/user/openwrt` as your base directory.

#### Adding your package to an existing feed

FIXME

#### Adding your package to your own feed

For this example we assume that you name your feed `custom` and your project is called `helloworld` and its openwrt Makefile is located at `/usr/src/openwrt/custom-feed/helloworld/Makefile`.

1.  Edit `/home/user/openwrt/feeds.conf.default`
2.  Add a new line for your feed. `src-link custom /usr/src/openwrt/custom-feed/`

1.  Update the feed: from the `<buildroot dir>` (e.g. `/home/user/openwrt`) do: `./scripts/feeds update custom`
2.  And then install it `./scripts/feeds install -a -p custom`

### Using the feed

1.  Now your package(s) should be available when you do `make menuconfig`

## Explanations

The downloaded sources (referenced in package Makefiles) are not there... The downloads go first to \<buildroot\>/dl as gzipped .gz files. And there they are stored and then they get unzipped to /build_dir. See e.g. \<buildroot\>/build_dir/target-\*/ and below it you will find subdirectories for each package's sources.

### Documentation

1.  [OpenWrt Buildroot – About](/docs/guide-developer/toolchain/start)
2.  [OpenWrt Buildroot – Installation](/docs/guide-developer/toolchain/install-buildsystem)
3.  [OpenWrt Buildroot – Usage](/docs/guide-developer/toolchain/use-buildsystem)
4.  OpenWrt Buildroot – Feeds
5.  [OpenWrt Buildroot – Technical Reference](/docs/techref/buildroot)  this article needs *your* attention.

## Links
