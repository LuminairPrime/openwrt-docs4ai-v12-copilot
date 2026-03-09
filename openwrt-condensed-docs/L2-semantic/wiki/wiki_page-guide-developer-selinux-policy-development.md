---
title: OpenWrt SELinux policy development, customization, and testing
module: wiki
origin_type: wiki_page
token_count: 8662
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-selinux-policy-development.md
last_pipeline_run: '2026-03-09T18:12:55.650305+00:00'
language: text
---
# OpenWrt SELinux policy development, customization, and testing

⚠️ **WARNING: FOLLOWING THESE PROCEDURES MAY RESULT IN A BRICKED OR INACCESSIBLE DEVICE !!!** ⚠️

This article demonstrates OpenWrt SELinux policy customization/development and testing/deployment. If you intend to deploy your own customized version of **selinux-policy** to your device, or if you intend to help improve the selinux-policy models provided by OpenWrt, then you should familiarize yourself with this procedure.

## Introduction and Prerequisites

This example assumes using Fedora 34 GNU/Linux for image building, and that there is at least 20GB of storage available on the host system used for building these components. In this example workflow, the resulting SELinux policy will be deployed and tested on a Linksys WRT1900ACS wireless router. In addition to the above, we require access to a git repository that can be accessed using the HTTPS protocol. This can be a private git repository, or a repository hosted on public services such as GitLab or Github. Please make sure that you carefully review all example commands for plausibility before trying to execute them in your specific build environment - filenames, commit hashes, personal data, etc. will differ from environment to environment and over time!

### Goals

The purpose of this exercise is to help familiarize potential contributors with the procedure of SELinux policy development for OpenWrt. OpenWrt can be configured and assembled in many ways, and the more scenarios are tested and supported the better. Please see Wish List for a list of known configurations that are not yet currently addressed and that need attention. Also see Feedback Checklist for a list of requested information (and instructions to gather this information) to determine and test whether the policy configuration is accurate and comprehensive.

In this example we're going to start by assembling the OpenWrt SELinux policy. By default, OpenWrt provides a generic policy with the aim to include support for all known common functionality. The goal of this default policy is to cover as many aspects of OpenWrt as possible and to make it "just work" by default on as many devices and device configurations as possible. The downside of this default policy is that, because it is so generic, it is also somewhat inefficient: The policy might include rules for components and functionalitty that you may not have installed or use and thereby it may require more space than strictly needed. Ideally, you would pick and choose a selection of modules appropriate and relevant for your target device's setup. (The goal is to eventually make assembling OpenWrt SELinux policy from available modules as easy as assembling OpenWrt images with the OpenWrt Image Builder.) Once we have assembled and deployed OpenWrt SELinux policy appropriate to our target device, we are going to work on extending functionality by adding policy for a simple `Hello World` shell script. Once tested, we're going to build an image with the resulting policy integrated, and deploy that to our target device.

Eventually, when everything works as intended and the policy you created is useful to the general public, you may consider submitting a patch with your changes to OpenWrt, so that all interested parties can benefit from your hard work.

## Installing and setting up build requirements

We're going to start by creating an OpenWrt Image Builder (IB) archive that can be used to assemble OpenWrt factory and sysupgrade images with included SELinux support. We have to ensure that we have all required build dependencies installed on our build system. In addition to the usual required host packages, we also need the `secilc` program, so that we can compile SELinux policy written in [Common Intermediate Language (CIL)](https://github.com/SELinuxProject/selinux/blob/master/secilc/docs/README.md).

    [kcinimod@brutus ~]$ sudo dnf install gcc-c++ git make bc make patch wget unzip tar bzip2 gettext ncurses-devel perl-FindBin perl-Data-Dumper perl-Thread-Queue perl-base findutils which diffutils file perl-File-Copy openssl-devel flex libxslt intltool zlib-devel rsync secilc

### Clone OpenWrt source code using git

Now that we have the build requirements taken care of, we can get the sources for OpenWrt. In this example, we'll clone OpenWrt from its mirror on Github:

    [kcinimod@brutus ~]$ git clone https://github.com/openwrt/openwrt.git

#### Addressing feeds

We'll now update and install all available feeds:

    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds update -a
    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds install -a

#### Addressing build configuration

Now, we will create an OpenWrt Image builder archive that is (somewhat) tailored to our requirements. (Remember: It has to have support for both SELinux, and for our example Linksys WRT1900ACS target device.)

    [kcinimod@brutus ~]$ cd ~/openwrt
    [kcinimod@brutus openwrt]$ make -j$(($(nproc) + 1)) menuconfig

After a short while a menu appears. We will address the Linksys WRT1900ACS target requirement first. The first three entries in the menu are used for this:

      Target System (Marvell EBU Armada)  --->
      Subtarget (Marvell Armada 37x/38x/XP)  --->
      Target Profile (Linksys WRT1900ACS v1)  --->

Select the "Build OpenWrt Image Builder" option from the menu.

      [*] Build the OpenWrt Image Builder

Next, we'll enable SELinux in the "Global Build Settings" submenu.

      Global build settings  --->
          [*] Enable SELinux (NEW)

Save the configuration and then exit the configuration tool using the menu on the bottom of the screen.

### Building OpenWrt and its Image Builder

Now we are ready to compile OpenWrt and its Image Builder. This will take some time.

    [kcinimod@brutus openwrt]$ make -j$(($(nproc) + 1))

The procedure above will create various images with regular SELinux support and the default SELinux selinux-policy model, in addition to an SELinux enabled Image Builder. In this example we will do a clean factory install using the created `~/openwrt/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img` factory image to test and ensure that the unmodified defaults work. The procedure of doing a factory install is documented elsewhere, but here is a quick summary:

1.  My host Ethernet network interface with static IP address 192.168.1.15 is connected to my WRT1900ACS device
2.  I browse to the stock Linksys WRT1900ACS web interface at address <https://192.168.1.1>
3.  The interface provides an option to manually flash the device with a specified image, and I point that to `~/openwrt/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img` factory image
4.  The device reboots and I use `ssh root@192.168.1.1` to log in to the device now running OpenWrt

#### Applying basic customization

There is a good chance that the selinux-policy enclosed n this image is slightly outdated and there may have been changes to upstream since. If you want to contribute policy, it is probably best to build on top of upstream. As a base for this work, you probably want to use the default policy with all modules enabled, so that you can have a good idea of how things work in the default scenario.

As an example, we will however exclude an optional module that is not depended on by any other modules to give you an idea of how you would go about assembling and building the policy with a customized module selection. Picking and choosing modules to install can be tricky, as modules may have dependencies on other modules. It is advised that you test locally whether all dependencies of your selection of modules can be resolved.

Depending on how integrated the component you want to target is, it is wise to set the default SELinux mode to "permissive", at least during the policy development phase. Even though this reasoning does not really apply to this contrived example, we will default to permissive mode for now for illustrative purposes.

At this point, you are essentially forking the policy. Publish your forked Git repository and ensure that the forked Git repository is accessible with the HTTPS protocol. You can for example use GitLab or Github for this but we'll use Github in this example.

### Creating a new selinux-policy-myfork repository on Github

#### Forking selinux-policy

I created a new empty `override/selinux-policy-myfork.git` repository on Github. I then clone this into a local working directory, and also clone the upstream selinux-policy. After that, I consolidate the two, and push my changes to selinux-policy-myfork to its Github upstream.

    [kcinimod@brutus openwrt]$ cd ~
    [kcinimod@brutus ~]$ git clone git@github.com:doverride/selinux-policy-myfork.git
    [kcinimod@brutus ~]$ git clone https://git.defensec.nl/selinux-policy.git
    [kcinimod@brutus ~]$ rm -rf selinux-policy/.git
    [kcinimod@brutus ~]$ cp -r selinux-policy-myfork/.git selinux-policy/.git
    [kcinimod@brutus ~]$ rm -rf selinux-policy-myfork
    [kcinimod@brutus ~]$ mv selinux-policy selinux-policy-myfork
    [kcinimod@brutus ~]$ cd selinux-policy-myfork
    [kcinimod@brutus selinux-policy-myfork (master #)]$ git init .
    [kcinimod@brutus selinux-policy-myfork (master #)]$ git add .
    [kcinimod@brutus selinux-policy-myfork (master +)]$ git commit -am 'initial commit'
    [kcinimod@brutus selinux-policy-myfork (master)]$ git push

#### Adding a custom target to the Makefile

One of our goals has been achieved: We forked the OpenWrt selinux-policy straight from upstream, and are working with an up-to-date policy snapshot as of now. To continue, we would like to build the whole policy minus the sandbox.cil module. To that end, we will add a target to ~/selinux-policy-myfork/Makefile that can be used to achieve the desired effect. Before pushing the result to Github, we will ensure that the policy actually builds. Edit ~/selinux-policy-myfork/Makefile and make the following changes.

Add a "myfork" target - Change this line ...:

``` Makefile
.PHONY: all clean minimal policy check install
```

... to read like this instead:

``` Makefile
.PHONY: all clean minimal myfork policy check install
```

Define which modules to enclose - locate the following line in the file:

``` Makefile
polvers = 31
```

... and insert this block right **after** it:

``` Makefile
modulesmyfork = $(shell find src -type f -name '*.cil' \
        ! -name sandbox.cil -printf '%p ')
```

Now, define the "myfork" target - locate this line:

``` Makefile
policy: policy.$(polvers)
```

... and insert this block **right before**:

``` Makefile
myfork: myfork.$(polvers)
myfork.%: $(modulesmyfork)
        secilc -vvv --policyvers=$* $^
```

Now, see if it builds:

    [kcinimod@brutus ~]$ cd ~/selinux-policy-myfork
    [kcinimod@brutus selinux-policy-myfork]$ make myfork
    [kcinimod@brutus selinux-policy-myfork]$ echo $?

If the build failed, look carefully at the compiler output - it will report any dependency issues that you can then manually resolve. Iterate on this until you get a successful build. Now, commit the result and push your changes to the Github remote, like so:

    [kcinimod@brutus selinux-policy-myfork (master *=)]$ git commit -am "adds myfork target to makefile"
    [kcinimod@brutus selinux-policy-myfork (master>)]$ git push

#### Building a selinux-policy-myfork ipk package

Now we have to package the policy, so that it can be enclosed with a factory and sysupgrade image using our Image Builder. For this, we have to create a package manifest, which defines how an ipk package gets assembled. Lucky for us, our selinux-policy-myfork repository has a template for this at `~/selinux-policy-myfork/support` that can serve as a reference.

First, we create a local feeds directory (example ~/mypackages):

    [kcinimod@brutus selinux-policy-myfork]$ cd ~
    [kcinimod@brutus ~]$ mkdir mypackages

Now we recursively copy `~/selinux-policy-myfork/support/selinux-policy-XXXX` to the local feeds' `~/mypackages` directory and rename it to `selinux-policy-myfork`:

    [kcinimod@brutus ~]$ cp -r selinux-policy-myfork/support/selinux-policy-XXXX mypackages/selinux-policy-myfork

We will need to replace the PKG_NAME variable's value next, which will determine the name of the package that will be generated:

    [kcinimod@brutus ~]$ sed -i 's/PKG_NAME:=.*/PKG_NAME:=selinux-policy-myfork/' mypackages/selinux-policy-myfork/Makefile

We replace PKG_SOURCE (point to your repository HTTPS URL, as this is where the source will be retrieved from):

    [kcinimod@brutus ~]$ sed -i 's#PKG_SOURCE_URL:=.*#PKG_SOURCE_URL:=https://github.com/doverride/selinux-policy-myfork.git#' mypackages/selinux-policy-myfork/Makefile

We need to also change PKG_SOURCE_DATE (use the current date or the date of the last commit):

    [kcinimod@brutus ~]$ sed -i 's/PKG_SOURCE_DATE:=.*/PKG_SOURCE_DATE:=2020-10-19/' mypackages/selinux-policy-myfork/Makefile

And we alse replace PKG_SOURCE_VERSION (use the commit ID of your latest commit):

    [kcinimod@brutus ~]$ sed -i 's/PKG_SOURCE_VERSION:=.*/PKG_SOURCE_VERSION:=4b8d8c06c5f1dc8641b2b08b44d7fde955e2b9db/' mypackages/selinux-policy-myfork/Makefile

Replace PKG_MIRROR_HASH (we'll skip this during development):

    [kcinimod@brutus ~]$ sed -i 's/PKG_MIRROR_HASH:=.*/PKG_MIRROR_HASH:=skip/' mypackages/selinux-policy/myfork/Makefile

Replace PKG_MAINTAINER (use your name and e-mail address instead of mine):

    [kcinimod@brutus ~]$ sed -i 's/PKG_MAINTAINER:=.*/PKG_MAINTAINER:=Dominick Grift <dominick.grift@defensec.nl>/' mypackages/selinux-policy-myfork/Makefile

Replace PKG_CPE_ID (whatever):

    [kcinimod@brutus ~]$ sed -i 's#PKG_CPE_ID:=cpe:/a:XXXX:selinux-policy-XXXX#PKG_CPE_ID:=cpe:/a:myfork:selinux-policy-myfork#' mypackages/selinux-policy-myfork/Makefile

Replace define/Package:

    [kcinimod@brutus ~]$ sed -i 's#define Package/selinux-policy-XXXX#define Package/selinux-policy-myfork#' mypackages/selinux-policy-myfork/Makefile

Replace TITLE:

    [kcinimod@brutus ~]$ sed -i 's/TITLE:=XXXX SELinux policy for OpenWrt/TITLE:=Myfork SELinux policy for OpenWrt/' mypackages/selinux-policy-myfork/Makefile

Replace URL:

    [kcinimod@brutus ~]$ sed -i 's#URL:=https://XXXX/#URL:=https://whatever/#' mypackages/selinux-policy-myfork/Makefile

Replace define/Package/description:

    [kcinimod@brutus ~]$ sed -i 's/XXXX SELinux security policy designed specifically for OpenWrt/Myfork SELinux security policy designed specifically for OpenWrt/' mypackages/selinux-policy-myfork/Makefile

Replace Build/Compile/Default (we'll use our new "myfork" target):

    [kcinimod@brutus ~]$ sed -i 's#$(call Build/Compile/Default,policy)#$(call Build/Compile/Default,myfork)#' mypackages/selinux-policy-myfork/Makefile

Replace the final occurrence of selinux-policy-XXXX:

    [kcinimod@brutus ~]$ sed -i 's/selinux-policy-XXXX/selinux-policy-myfork/' mypackages/selinux-policy-myfork/Makefile

Change the "mode from config" to "permissive", and change the policy model to selinux-policy-myfork:

    [kcinimod@brutus ~]$ sed -i 's/SELINUX=.*/SELINUX=permissive/' mypackages/selinux-policy-myfork/files/selinux-config
    [kcinimod@brutus ~]$ sed -i 's/SELINUXTYPE=.*/SELINUXTYPE=selinux-policy-myfork/' mypackages/selinux-policy-myfork/files/selinux-config

Add/update the "mypackages" custom feed and selinux-policy-myfork:

    [kcinimod@brutus ~]$ echo "src-link custom ${HOME}/mypackages" >> openwrt/[feeds.conf](../wiki/wiki_page-guide-developer-creating-a-meson-based-package.md).default
    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds update custom
    [kcinimod@brutus ~]$ ./openwrt/scripts/feeds install selinux-policy-myfork

After these modifications have succeeded, we have to perform `menuconfig` again, to also select **selinux-policy-myfork** for being built:

    [kcinimod@brutus ~]$ cd ~/openwrt
    [kcinimod@brutus openwrt]$ make -j$(($(nproc) + 1)) menuconfig

Now we'll enable selinux-policy-myfork from the "Base system" submenu.

      Base system  --->
          <*> selinux-policy-myfork.................. Myfork SELinux policy for OpenWrt

Save the configuration first and then exit the menu using the menu on the bottom of the screen.

Now, we build the ipk package file:

    [kcinimod@brutus openwrt]$ make package/selinux-policy-myfork/compile

If this succeeds, the resulting ipk package can be found in `~/openwrt/bin/packages/*/custom`:

    [kcinimod@brutus openwrt]$ ls ~/openwrt/bin/packages/*/custom/*.ipk
    /home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-4b8d8c06_all.ipk

=== Creating installation and upgrade media with selinux-policy-myfork included using Image Builder

First, we will extract the Image Builder archive:

    [kcinimod@brutus openwrt]$ cd ~
    [kcinimod@brutus ~]$ mv ~/openwrt/bin/targets/*/*/openwrt-imagebuilder*.tar.xz ~
    [kcinimod@brutus ~]$ tar xf openwrt-imagebuilder*.tar.xz

Since we have a policy package, we can conveniently include it in firmware images generated by the Image Builder:

    [kcinimod@brutus ~]$ cd openwrt-imagebuilder*-x86_64
    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ make image PACKAGES="/home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-4b8d8c06_all.ipk"

This should yield **factory** and **sysupgrade** images which can be deployed onto a WRT1900ACS like any other OpenWrt image:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ ls bin/targets/*/*
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-linksys_wrt1900acs-linksys_wrt1900acs.manifest
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    sha256sums

#### Deploying sysupgrade image with customized selinux-policy-myfork

We should now be able to copy the resulting `openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin` image to the device using the `scp` utility (provided that the router is reachable on the network) and perform the upgrade:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ cd ~
    [kcinimod@brutus ~]$ scp /home/kcinimod/openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin root@192.168.1.1:/tmp/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    [kcinimod@brutus ~]$ ssh root@192.168.1.1
    root@OpenWrt:~# sysupgrade -F -n -v /tmp/*.bin

Give the device a moment to reboot and log back into it over ssh. Verify that your policy model is used and, again, follow the Feedback Checklist to see if all works well.

    [kcinimod@brutus ~]$ ssh root@192.168.1.1
    root@OpenWrt:~# sestatus
    SELinux status:           enabled
    SELinuxfs mount:          /sys/fs/selinux
    Current mode:             permissive
    Mode from config file:    permissive
    Policy version:           31
    Policy from config file:  selinux-policy-myfork

## Policy development overview

The next step will be to extend the policy by targeting a simple "Hello World" shell script. I will not get into the details of writing SELinux policy in this exercise. The policy is written in **Common Intermediate Language** and I am working on documenting that. You can try to find help in [\#selinux on the freenode IRC network](irc://irc.freenode.org/#selinux), but if you need assistance or have any questions related to OpenWrt selinux-policy and SELinux policy/CIL in particular, then I can be reached on the [OFTC IRC network in the \#openwrt-devel](irc://irc.oftc.net/#openwrt-devel) channel under the IRC nickname **grift**.

### Confining "Hello World"

We will be creating a simple script: `/root/helloworld`. It simply prints the output of `echo "Hello from: $(id -Z)"` to standard output and exits. Then, we will develop a policy for this script at runtime and test the result "on-device". Once the policy has been verified to work as intended, we will deploy a sysupgrade image with the resulting customization enclosed, and we will change the default SELinux mode back to "enforcing". This simple example will hopefully be illustrative enough to get you started. Please use the knowledge gained to help improve the policy, so that everyone can benefit.

#### Creating and testing the script

First, we need to create the script that our policy will interact with:

    root@OpenWrt:~# printf '#!/bin/sh\n echo "hello from: $(id -Z)\n"' > /root/helloworld
    root@OpenWrt:~# chmod +x /root/helloworld

To see what it does at this stage, let's run it:

    root@OpenWrt:~# /root/helloworld
    hello from: u:r:sys.subj

The script works, but the output of the script indicates that it currently operates within the "unconfined" `u:r:sys.subj` context. We would like the script to be contained, thereby applying the principle of least privilege to this process by subjecting it to our modified SELinux policy.

We can write a basic skeleton policy for this script off-device, using our cloned `selinux-policy-myfork` repository, then build and test that, and copy the compiled `policy.31` file (along with the updated `file_contexts` file) to the device. Then, we can run the `load_policy` command to apply the updated policy to the running system, and use that procedure to test and refine the policy until it works as we need it to.

#### Extend selinux-policy-myfork with basic skeleton for helloworld

    [kcinimod@brutus ~]$ cd selinux-policy-myfork
    [kcinimod@brutus selinux-policy-myfork]$ cat > src/agent/helloworld.cil <<EOF
    (block helloworld ;; declare a new container
    (blockinherit .agent.base_template) ;; this will declare types for both the process and executable file and associate some basic rules with them
    (filecon "/root/helloworld" file execfile_file_context)) ;; this will associate the file context with /root/helloworld and close container
    (in .sys (call .helloworld.subj_type_transition (subj))) ;; this macro was made available when we inherited the agent.base_template inside the helloworld container
    ;; it will cause selinux to automatically transition the context of any process associated with u:r:sys.subj to u:r:helloworld.subj when files with the u:r:helloworld.execfile context are executed
    EOF
    [kcinimod@brutus selinux-policy-myfork]$ make myfork

The compilation results in two files: `policy.31` and `file_contexts`, both found within `~/selinux-policy-myfork`. We copy these to the router using the `scp` command. The customized policy can then be loaded via `load_policy`, and the file context for `/root/helloworld` can be applied by running `restorecon`, like reproduced here:

    [kcinimod@brutus selinux-policy-myfork]$ scp policy.31 root@192.168.1.1:/etc/selinux/selinux-policy-myfork/policy/policy.31
    [kcinimod@brutus selinux-policy-myfork]$ scp file_contexts root@192.168.1.1:/etc/selinux/selinux-policy-myfork/contexts/files/file_contexts
    [kcinimod@brutus selinux-policy-myfork[$ ssh root@192.168.1.1
    root@OpenWrt:~# load_policy
    root@OpenWrt:~# restorecon -v /root/helloworld

Now it is time to test again - but before we do that, we will clear the kernel debug message ring buffer, so that we cannot get confused by any avc denials triggered by us copying the `policy.31` and `file_contexts` files over, because SELinux would not have permitted these operations if it had already been enforcing the policy.

A peculiar thing to be aware of is that SELinux will cache access vectors and events that occur in permissive mode, and that these will **only be printed once** to avoid flooding the logs. If you need to flush this cache, you can toggle the mode from permissive to enforcing, and then back again.

We perform both these operations here, before re-executing our script:

    root@OpenWrt:~# dmesg -c
    root@OpenWrt:~# setenforce 1 && setenforce 0
    root@OpenWrt:~# /root/helloworld
    hello from: u:r:helloworld.subj

The test concluded that the specified domain transition from `u:r:sys.subj` to `u:r:helloworld.subj` took place, due to our custom policy having taken effect. Since we are still operating in "permissive" mode for development purposes, we can use the `dmesg` command to see which permissions would have been denied if we had instead been operating in "enforcing" mode.

    root@OpenWrt:~# dmesg | grep -i denied

The resulting avc denials can be interpreted and translated to policy, that we can then append to our modifications, and then test again. Eventually, no new avc denials should be printed to dmesg when testing in "oermissive" mode, indicating that the resulting process has all the permissions and contexts assigned that it needs to function. Once we arrive at that point, the update should be ready for real-worl use.

We will now append some of the rules we were able to identify from the output of the `dmesg | grep -i` denied command. Some of these might not be obvious to you at this point. Suffice to say that rules can be (and in fact often are) grouped for common patterns, and with sufficient experience, you learn to recognise these patterns and how to correlate them to provided macros and templates commonly used to address these issues.

There is another gotcha you should be aware of: There are rules present in the policy that instruct SELinux to "silently" block specified events. This functionality can be useful if you want to block some access on purpose without SELinux printing avc denials. However, sometimes, knowing these events actually occurred (and were blocked) might actually be needed. The `secilc` compiler allows you to compile the policy with these "dontaudit" rules removed via the `-D` or `--disable-dontaudit` switches, but that's beyond the scope of this exercise. For now, suffice to say that `helloworld` wants to operate on the terminal (as it needs to print the output to a terminal) but the current policy has rules that tell SELinux to silently block this access. We need to change this to keep our policy-confined program working:

    [kcinimod@brutus selinux-policy-myfork]$ cat >> src/agent/helloworld.cil <<EOF
    (in .helloworld ;; insert into existing helloworld container
    (call .shell.execute_execfile_files (subj)) ;; executes /bin/sh which leads to busybox shell
    (call .selinux.linked.subj_type (subj)) ;; busybox links with libselinux which needs some access to determine selinux state
    (call .sys.readwriteinherited_ptydev_chr_files (subj)) ;; operate on pty, this was silently blocked
    (call .dev.readwriteinherited_ttydev_chr_files (subj))) ;; operate on tty. this was silently blocked
    ;; close helloworld container
    EOF
    [kcinimod@brutus selinux-policy-myfork]$ make myfork

Following the same procedure as before, copy over the `policy.31` and `file_contexts` files, reload policy, clear the ring buffer using `dmesg -c`, flush the SELinux log cache by toggling its state, retry running the script, and check dmesg again for avc messages, like so:

    [kcinimod@brutus selinux-policy-myfork]$ scp policy.31 root@192.168.1.1:/etc/selinux/selinux-policy-myfork/policy/policy.31
    [kcinimod@brutus selinux-policy-myfork]$ scp file_contexts root@192.168.1.1:/etc/selinux/selinux-policy-myfork/contexts/files/file_contexts
    [kcinimod@brutus selinux-policy-myfork[$ ssh root@192.168.1.1
    root@OpenWrt:~# load_policy
    root@OpenWrt:~# dmesg -c
    root@OpenWrt:~# setenforce 1 && setenforce 0
    root@OpenWrt:~# /root/helloworld
    hello from: u:r:helloworld.subj

    root@OpenWrt:~# dmesg | grep -i denied

The above dmesg invocation prints one more avc denial in permissive mode, so let's try this in enforcing mode:

    root@OpenWrt:~# dmesg -c
    root@OpenWrt:~# setenforce 1
    root@OpenWrt:~# /root/helloworld
    hello from: u:r:helloworld.subj

    root@OpenWrt:~# dmesg | grep -i denied
    root@OpenWrt:~# exit

This demonstrates that it works in enforcing mode. We can just add that last rule and then commit and push the policy to Github:

    [kcinimod@brutus selinux-policy-myfork]$ cat >> src/agent/helloworld.cil <<EOF
    (in .helloworld ;; insert into existing helloworld container
    (call .tmpfile.search_runtimetmpfile_dirs (subj))) ;; busybox traverses /tmp/run for some reason
    ;; close helloworld container
    EOF
    [kcinimod@brutus selinux-policy-myfork]$ make myfork
    [kcinimod@brutus selinux-policy-myfork]$ git add .
    [kcinimod@brutus selinux-policy-myfork]$ git commit -am "adds helloworld example"
    [kcinimod@brutus selinux-policy-myfork]$ git push

Next, we will build a new ipk package including our recent work, and also create a new sysupgrade image with our new policy package integrated, again using the Image Builder.

For that to work, we need to adjust two things in our local build artifacts:

\* The `~/mypackages/selinux-policy-myfork/Makefile` **PKG_SOURCE_VERSION** has to be updated to point to the new latest git commit ID \* The `~/mypackages/selinux-policy-myfork/files/selinux-config` has to be updated to change the mode from "permissive" to "enforcing".

Replace **PKG_SOURCE_VERSION** (use the commit ID of your latest commit):

    [kcinimod@brutus selinux-policy-myfork]$ cd ~
    [kcinimod@brutus ~]$ sed -i 's/PKG_SOURCE_VERSION:=4b8d8c06c5f1dc8641b2b08b44d7fde955e2b9db/PKG_SOURCE_VERSION:=c5e28890e61bed077477bcc526b8fb6639728c93/' mypackages/selinux-policy-myfork/Makefile

Change the "mode from config" to enforcing:

    [kcinimod@brutus ~]$ sed -i 's/SELINUX=.*/SELINUX=enforcing/' mypackages/selinux-policy-myfork/files/selinux-config

Now, we are ready to Create the updated ipk package:

    [kcinimod@brutus ~]$ cd openwrt
    [kcinimod@brutus openwrt]$ make package/selinux-policy-myfork/compile

If the operation succeeds, the resulting ipk package can be found in `~/openwrt/bin/packages/*/custom`:

    [kcinimod@brutus openwrt]$ ls ~/openwrt/bin/packages/*/custom/*.ipk
    /home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-c5e28890_all.ipk

Now that we have an updated ipk package, we can create new installation and upgrade images using Image Builder:

    [kcinimod@brutus openwrt]$ cd ~/openwrt-imagebuilder*-x86_64
    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ make image PACKAGES="/home/kcinimod/openwrt/bin/packages/arm_cortex-a9_vfpv3-d16/custom/selinux-policy-myfork_2020-10-19-c5e28890_all.ipk"

This should yield factory and sysupgrade images, just like before:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ ls bin/targets/*/*
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-linksys_wrt1900acs-linksys_wrt1900acs.manifest
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-factory.img
    openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    sha256sums

Again, we deploy the new sysupgrade image with our customized selinux-policy-myfork:

    [kcinimod@brutus openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64]$ cd ~
    [kcinimod@brutus ~]$ scp /home/kcinimod/openwrt-imagebuilder-mvebu-cortexa9.Linux-x86_64/bin/targets/mvebu/cortexa9/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin root@192.168.1.1:/tmp/openwrt-mvebu-cortexa9-linksys_wrt1900acs-squashfs-sysupgrade.bin
    [kcinimod@brutus ~]$ ssh root@192.168.1.1
    root@OpenWrt:~# sysupgrade -F -n -v /tmp/*.bin

After the device has booted up again, our policy should be enforcing least privileges for our hello world script.

## In closing

This wraps up the exercise. Remember that this is meant to illustrate the SELinux policy development (and deployment) workflow in broad strokes. To be able to contribute your work back your policy, you need to adhere to a number of established style rules. I suggest that you take a close look at the existing policy, to identify patterns and clues on how to make your policy feel familiar to someone who's already familiar with pre-existing upstream policy code. To help with that, see if you can find a module that closely resembles yours, and compare and contrast the two in order to find ways to improve and align your module with existing best practices. If you need help, feel free to just ask [on IRC](irc://irc.oftc.net/#openwrt-devel)! Happy policy hacking! :)