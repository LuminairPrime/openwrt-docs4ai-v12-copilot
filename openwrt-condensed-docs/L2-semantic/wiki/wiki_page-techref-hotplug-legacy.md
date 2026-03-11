---
title: Hotplug -- Legacy
module: wiki
origin_type: wiki_page
token_count: 3404
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-hotplug-legacy.md
last_pipeline_run: '2026-03-11T14:18:13.562842+00:00'
language: text
---
# Hotplug -- Legacy

![historic&noheader&nofooter&noeditbtn](/page>meta/infobox/historic&noheader&nofooter&noeditbtn)

> [!WARNING]
> See the [Hotplug article](/docs/guide-user/base-system/hotplug) for information on the current approach.
>
> The "hotplug2" daemon was removed in 2013 ([r36987](https://dev.openwrt.org/changeset/36987)) and replaced with [procd](/docs/techref/procd).

Hotplug2 was a trivial replacement of some of the UDev functionality in a tiny pack, intended for Linux early userspace: Init RAM FS and InitRD. Hotplug executes scripts located in the respective hotplug directory: `/etc/hotplug.d/` on certain events, like when an interface goes up or down or when a button gets pressed. It can be very useful with [PPPoE](https://en.wikipedia.org/wiki/Point-to-Point Protocol over Ethernet)-connection or in an unstable network. Hotplug has been available since OpenWrt 'Kamikaze' 7.06 and was removed in 2013, prior to the release of "Attitude Adjustment".

- <https://dev.openwrt.org/browser/trunk/package/hotplug2?rev=36446>

|                                                                   |                                                                                                                                           |
|-------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| ![48px-outdated.svg.png](/meta/icons/tango/48px-outdated.svg.png) | Example: See [r37336: procd: make old button hotplug rules work until all packages are migrated](https://dev.openwrt.org/changeset/37336) |

It is also used by [hardware.button](/docs/guide-user/hardware/hardware.button)

#### What is hotplug?

Best answer to this question is found on [Chris Lumens's website](http://www.bangmoney.org/presentations/hotplug/).

#### How it works

Every time an interface goes up or down, all scripts in the `/etc/hotplug.d/iface/` directory are executed, in alphabetical order. According to an informal convention a numeric prefix is added to each script name to set the correct order of running. That's why the scripts there are named like this: `/etc/hotplug.d/iface/<nn>-<scriptname>` e.g.: 10-routes, 20-firewall

Kernel module: `button-hotplug`

## Configuration

Modify `/etc/hotplug2.rules` to enable Hotplug execute your script(s) in `/etc/hotplug.d/<type>`. `<type>` is a kind of hotplug device; such as usb. In /etc/hotplug2.rules, remove '^' before `<type>` which can be net, input, button, usb etc.

    $include /etc/hotplug2-common.rules

    SUBSYSTEM ~~ (^net$|^input$|^button$|^usb$|^ieee1394$|^block$|^atm$|^zaptel$|^tty$) {
        exec /sbin/hotplug-call %SUBSYSTEM%
    }

    DEVICENAME == watchdog {
        exec /sbin/watchdog -t 5 /dev/watchdog
        next-event
    }

Simply place your script(s) into the respective hotplug subdirectory. Script looks like this:

There are three main environment variables that are passed to each iface hotplug-script:

| Variable name | Description                                                                      |
|---------------|----------------------------------------------------------------------------------|
| ACTION        | Either "ifup" or "ifdown"                                                        |
| INTERFACE     | Name of the interface which went up or down (e.g. "wan" or "ppp0")               |
| DEVICE        | Physical device name which interface went up or down (e.g. "eth0.1" or "br-lan") |

## Examples

Save the example script at `/etc/hotplug.d/iface/99-my-action`.

\| ''#!/bin/sh

\[ "\$ACTION" = ifup \] && {

    logger -t button-hotplug Device: $DEVICE / Action: $ACTION

}'' \|

Every time an interface goes up then the if/fi statement will be executed.

-\> [hardware.button](/docs/guide-user/hardware/hardware.button) makes ample use of hotplug.

Niii has posted this quick example for a USB WiFi device hotplug event to trigger an init.d network restart wlan0 script.

For determine RTL8188SU_PRODID variable, use "lsusb -v":

    idVendor           0x0bda Realtek Semiconductor Corp.
    idProduct          0x8171 RTL8188SU 802.11n WLAN Adapter
    bcdDevice            2.00

**/etc/hotplug.d/usb/20-rtl8188su**

\| ''#!/bin/sh

BINARY="/sbin/wifi up" RTL8188SU_PRODID="bda/8171/200"

if \[ "\${PRODUCT}" = "\${RTL8188SU_PRODID}" \]; then

      if [ "${ACTION}" = "add" ]; then
          ${BINARY}
      fi

fi'' \|

**`/etc/hotplug.d/usb/20-cp210x`**

An other script to create a symlink instead of renaming the device.
I test if DEVICE_NAME is empty because when I plug usb device I retrieve two add event, and the first come before created device, so symlink fails.

\| ''#!/bin/sh

CP210_PRODID="10c4/ea60/100" SYMLINK="my_link"

if \[ "\${PRODUCT}" = "\${CP210_PRODID}" \];

     then if [ "${ACTION}" = "add" ];
        then
           DEVICE_NAME=$(ls /sys/$DEVPATH | grep tty)
           if [ -z ${DEVICE_NAME} ];
              then logger -t Hotplug Warning DEVICE_NAME is empty
              exit
           fi
           logger -t Hotplug Device name of cp210 is $DEVICE_NAME
           ln -s /dev/$DEVICE_NAME /dev/${SYMLINK}
           logger -t Hotplug Symlink from /dev/$DEVICE_NAME to /dev/${SYMLINK} created
     fi

fi

if \[ "\${PRODUCT}" = "\${CP210_PRODID}" \];

     then if [ "${ACTION}" = "remove" ];
           then
           rm /dev/${SYMLINK}
           logger -t Hotplug Symlink /dev/${SYMLINK} removed
     fi

fi'' \|

Script that detects if plugged usb device is bluetooth or not.

\| ''#!/bin/sh BT_PRODID="a12/1/" BT_PRODID_HOT=\`echo \$PRODUCT \| cut -c 1-6\`

\#logger -t HOTPLUG "PRODUCT ID is" \$BT_PRODID_HOT

if \[ "\$BT_PRODID_HOT" = "\$BT_PRODID" \]; then

      if [ "$ACTION" = "add" ]; then
          logger -t HOTPLUG "bluetooth device has been plugged in!"
          if [ "$BSBTID_NEW" = "$BSBTID_OLD" ]; then
              logger -t HOTPLUG "bluetooth device hasn't changed"
          else
              logger -t HOTPLUG "bluetooth device has changed"
          fi
      fi
      if [ "$ACTION" = "remove" ]; then
          logger -t HOTPLUG "bluetooth device has been removed!"
      fi

else

      logger -t HOTPLUG "USB device is not bluetooth"

fi'' \|

Auto start mjpg-streamer when an usb camera is plugged in. Firstly, remove '^' before 'input' in `/etc/hotplug2.rules` to enable Hotplug execute script(s) in `/etc/hotplug.d/input`. Secondly, add `/etc/hotplug.d/input/30-mjpg-streamer`

    case "$ACTION" in
        add)
                # start process
            /etc/init.d/mjpg-streamer start
                ;;
        remove)
                # stop process
            /etc/init.d/mjpg-streamer stop
                ;;
    esac

## Coldplug

If you had notice the udev and eudev were removed in the openwrt 18.0.\* release, don't be afraid because you still can make the things works.
**Using hotplug scripts as coldplug**
You just need to pay atention at the ACTION env var, at the boot are executed 'bind' actions.
So, just add this option to hotplug run accordinly. In my case I used this:

Take a look into file `/etc/hotplug.d/usb/22-symlinks`

    #!/bin/sh
    # Description: Action executed on boot (bind) and with the system on the fly
    if [ "$ACTION" = 'bind' ] ; then
      case "${PRODUCT}" in
        1bc7*) # Telit HE910 3g modules product id prefix
          DEVICE_NAME=$(ls /sys/$DEVPATH | grep tty)
          DEVICE_TTY=$(ls /sys/$DEVPATH/tty/)
          # Module Telit HE910-* connected to minipciexpress slot MAIN
          if [ ${DEVICENAME} = '1-1.3:1.0' ] ; then
            ln -s /dev/$DEVICE_TTY /dev/ttyMODULO1_DIAL
            logger -t Hotplug Symlink from /dev/$DEVICE_TTY to /dev/ttyMODULO1_DIAL created
          elif [ ${DEVICENAME} = '1-1.3:1.6' ] ; then
            ln -s /dev/$DEVICE_TTY /dev/ttyMODULO1_DATA
            logger -t Hotplug Symlink from /dev/$DEVICE_TTY to /dev/ttyMODULO1_DATA created
          # Module Telit HE910-* connected to minipciexpress slot SECONDARY
          elif [ ${DEVICENAME} = '1-1.2:1.0' ] ; then
            ln -s /dev/$DEVICE_TTY /dev/ttyMODULO2_DIAL
            logger -t Hotplug Symlink from /dev/$DEVICE_TTY to /dev/ttyMODULO2_DIAL created
          elif [ ${DEVICENAME} = '1-1.2:1.6' ] ; then
            ln -s /dev/$DEVICE_TTY /dev/ttyMODULO2_DATA
            logger -t Hotplug Symlink from /dev/$DEVICE_TTY to /dev/ttyMODULO2_DATA created
          fi
        ;;
      esac
    fi
    # Action to remove the symlinks
    if [ "$ACTION" = 'remove' ]  ; then
      case "${PRODUCT}" in
        1bc7*)  # Telit HE910 3g modules product id prefix
         # Module Telit HE910-* connected to minipciexpress slot MAIN
          if [ ${DEVICENAME} = '1-1.3:1.0' ] ; then
            rm /dev/ttyMODULO1_DIAL
            logger -t Hotplug Symlink /dev/ttyMODULO1_DIAL removed
          elif [ ${DEVICENAME} = '1-1.3:1.6' ] ; then
            rm /dev/ttyMODULO1_DATA
            logger -t Hotplug Symlink /dev/ttyMODULO1_DATA removed
          # Module Telit HE910-* connected to minipciexpress slot SECONDARY
          elif [ ${DEVICENAME} = '1-1.2:1.0' ] ; then
            rm /dev/ttyMODULO2_DIAL
            logger -t Hotplug Symlink /dev/ttyMODULO2_DIAL removed
          elif [ ${DEVICENAME} = '1-1.2:1.6' ] ; then
            rm /dev/ttyMODULO2_DATA
            logger -t Hotplug Symlink /dev/ttyMODULO2_DATA removed
          fi
        ;;
      esac
    fi

### Logs generated by Coldplug script below

    root@OpenWrt:~#logread | grep Hotplug
    Fri Sep 21 15:31:00 2018 user.notice Hotplug: Symlink from /dev/ttyACM0 to /dev/ttyMODULO2_DIAL created
    Fri Sep 21 15:31:06 2018 user.notice Hotplug: Symlink from /dev/ttyACM3 to /dev/ttyMODULO2_DATA created
    Fri Sep 21 15:31:39 2018 user.notice Hotplug: Symlink from /dev/ttyACM6 to /dev/ttyMODULO1_DIAL created
    Fri Sep 21 15:31:46 2018 user.notice Hotplug: Symlink from /dev/ttyACM9 to /dev/ttyMODULO1_DATA created
    Fri Sep 21 15:32:03 2018 user.notice Hotplug: Symlink /dev/ttyMODULO1_DIAL removed
    Fri Sep 21 15:32:10 2018 user.notice Hotplug: Symlink /dev/ttyMODULO1_DATA removed
    Fri Sep 21 15:33:17 2018 user.notice Hotplug: Symlink /dev/ttyMODULO2_DIAL removed
    Fri Sep 21 15:33:24 2018 user.notice Hotplug: Symlink /dev/ttyMODULO2_DATA removed
    root@OpenWrt:~#

## Troubleshoot

If you wish to troubleshoot hotplug of some type of device this can be done via simple debug script. For example to troubleshoot adding and removing of any type of usb devices, simply create this **/etc/hotplug.d/usb/10-usb_debug** script with all variables:

    #!/bin/sh
    logger -t DEBUG "hotplug usb: action='$ACTION' devicename='$DEVICENAME' devname='$DEVNAME' devpath='$DEVPATH' product='$PRODUCT' type='$TYPE' interface='$INTERFACE'"

or this one with only essential ones used:

    #!/bin/sh
    logger -t DEBUG "hotplug usb: action='$ACTION' product='$PRODUCT' type='$TYPE' interface='$INTERFACE'"

So with debuging enabled here is how it looks like when you plug two different usb bluetooth dongles:

    action='add' product='a12/1/1915' type='224/1/1' interface=''
    action='add' product='a12/1/1915' type='224/1/1' interface='224/1/1'
    action='add' product='a12/1/1915' type='224/1/1' interface='224/1/1'
    action='add' product='a12/1/1915' type='224/1/1' interface='254/1/0'
    action='remove' product='a12/1/1915' type='224/1/1' interface='224/1/1'
    action='remove' product='a12/1/1915' type='224/1/1' interface='224/1/1'
    action='remove' product='a12/1/1915' type='224/1/1' interface='254/1/0'
    action='remove' product='a12/1/1915' type='224/1/1' interface=''
    action='add' product='a12/1/134' type='224/1/1' interface=''
    action='add' product='a12/1/134' type='224/1/1' interface='224/1/1'
    action='add' product='a12/1/134' type='224/1/1' interface='224/1/1'

So my using some (maybe flawed) logic we can deduce that match bluetooth is possible if we use product='a12/1\*'

## Notes
