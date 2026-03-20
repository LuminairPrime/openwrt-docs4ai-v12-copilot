# Building image with support for 3g/4g and usb tethering

## Preparing build environment

First of all, you need a complete build environment, either physical or virtual system, as described on the [OpenWrt developer guide](/docs/guide-developer/start).

You need to clone OpenWrt git repository on your build system and synchronize all package feeds with your config file.

Be sure to understand the [build procedure](/docs/guide-user/additional-software/imagebuilder) to prevent build failure.

## Configuring packages

### Selecting target architecture and profile

Run `make menuconfig`.

Select your architecture on which you would put your compiled OpenWrt image. Then select your target profile, according your hardware type.

If you have selected correct value for target system, target profile, and target images, go to next step.

### Selecting kernel modules for usb networking support.

Go to `Kernel Modules -> USB Support`.

Select the following modules by pressing `y` to include the modules within the compiled image.

    Kernel Modules -> USB Support
    <*> kmod-usb2
    <*> kmod-usb-ohci
    <*> kmod-usb-uhci
    <*> kmod-usb-acm # For ACM based modem, such as Nokia Phones
    <*> kmod-usb-net # For tethering and rndis support

**kmod-usb-net** -\> to support usb networking interface.

Select all subsets if you want perfect support for usb network interfaces, including Android and iPhone tethering. Some newer 4g dongles use usb network interface (rndis) instead of legacy serial protocol.

    <*> kmod-usb-net............... Kernel modules for USB-to-Ethernet convertors
      <*>   kmod-usb-net-asix...... Kernel module for USB-to-Ethernet Asix convertors  
      <*>   kmod-usb-net-cdc-eem..................... Support for CDC EEM connections  
      -*-   kmod-usb-net-cdc-ether.............. Support for cdc ethernet connections  
      <*>   kmod-usb-net-cdc-mbim..................... Kernel module for MBIM Devices  
      -*-   kmod-usb-net-cdc-ncm..................... Support for CDC NCM connections  
      <*>   kmod-usb-net-cdc-subset...... Support for CDC Ethernet subset connections  
      <*>   kmod-usb-net-dm9601-ether........ Support for DM9601 ethernet connections  
      <*>   kmod-usb-net-hso.. Kernel module for Option USB High Speed Mobile Devices  
      <*>   kmod-usb-net-ipheth..................... Apple iPhone USB Ethernet driver  
      <*>   kmod-usb-net-kalmia................... Samsung Kalmia based LTE USB modem  
      <*>   kmod-usb-net-kaweth.. Kernel module for USB-to-Ethernet Kaweth convertors  
      <*>   kmod-usb-net-mcs7830                                                       
      <*>   kmod-usb-net-pegasus                                                       
      <*>   kmod-usb-net-qmi-wwan.................................... QMI WWAN driver  
      <*>   kmod-usb-net-rndis......................... Support for RNDIS connections  
      <*>   kmod-usb-net-sierrawireless.......... Support for Sierra Wireless devices  
      <*>   kmod-usb-net-smsc95xx. SMSC LAN95XX based USB 2.0 10/100 ethernet devices
      

**kmod-usb-serial** -\> to support legacy 3g dongles.

Select all subsets to ensure that your dongle works. Most 3g dongles use the option driver or generic serial driver to work. Note that option driver has better capability of distinguishing between modem serial interfaces and storage interface than generic usb serial driver.

    <*> kmod-usb-serial..................... Support for USB-to-Serial converters    
      <*>   kmod-usb-serial-ark3116........ Support for ArkMicroChips ARK3116 devices  
      <*>   kmod-usb-serial-belkin........................ Support for Belkin devices  
      <*>   kmod-usb-serial-ch341.......................... Support for CH341 devices  
      <*>   kmod-usb-serial-cp210x........... Support for Silicon Labs cp210x devices  
      <*>   kmod-usb-serial-cypress-m8.............. Support for CypressM8 USB-Serial  
      <*>   kmod-usb-serial-ftdi............................ Support for FTDI devices  
      <*> kmod-usb-serial-ipw.................... Support for IPWireless 3G devices    
      <*> kmod-usb-serial-keyspan........ Support for Keyspan USB-to-Serial devices    
      <*> kmod-usb-serial-mct.............. Support for Magic Control Tech. devices    
      <*> kmod-usb-serial-mos7720.............. Support for Moschip MOS7720 devices    
      <*> kmod-usb-serial-motorola-phone............ Support for Motorola usb phone    
      <*> kmod-usb-serial-option................... Support for Option HSDPA modems    
      <*> kmod-usb-serial-oti6858...... Support for Ours Technology OTI6858 devices    
      <*> kmod-usb-serial-pl2303............... Support for Prolific PL2303 devices    
      <*> kmod-usb-serial-qualcomm................. Support for Qualcomm USB serial    
      <*> kmod-usb-serial-sierrawireless....... Support for Sierra Wireless devices    
      <*> kmod-usb-serial-ti-usb...................... Support for TI USB 3410/5052    
      <*> kmod-usb-serial-visor............... Support for Handspring Visor devices    
      -*- kmod-usb-serial-wwan..................... Support for GSM and CDMA modems
      

### Additional packages required for 3g functionality

#### ppp, chat, and uqmi

Go to `Network` section. Select \`uqmi\` to support qmi interface and \`ppp\` to support standard point-to-point protocol. `chat` is needed to establish serial communication to prepare PPP link negotiation.

    Network
      <*>chat
      <*>ppp
      <*>uqmi

#### mbim

Some dongles are using mbim protocol. To make use of mbim protocol, install `umbim` package.

    Network
      <*>umbim

#### comgt and usb-modeswitch

Go to `Utilities` section. Select `comgt` to provide control over 3g interface and `usb-modeswitch` to provide mode switching between virtual cd-rom interface to serial interface.

    Utilities
      <*>comgt
      <*>usb-modeswitch

#### minicom, picocom, and screen

If you want to debug serial communication, you may want to install serial terminal. There are several choices of serial terminal, such as minicom, picocom, and screen. I recommend `picocom` because of its small size.

    Utilities --> Terminal
      <*>picocom

Screen can be used as persistent session manager. Minicom has a nice interface, optimized for serial communication.

    Utilities
      < >screen
    Utilities --> Terminal
      < >minicom

For devices with 4MB flash, `picocom` is the only serial terminal that can be installed.

### Web Interface Support

If you want to control your 3g dongle with Luci web interface, go to Luci.

    Luci
    1. Collections
      <*> luci
    3. Applications
      <*> luci-app-multiwan (optional to support multiple 3g dongles)
      <*> luci-app-qos (optional to provide QOS support)
    6. Protocols
      <*> luci-proto-3g
      -*- luci-proto-ppp

===== Build process ===== Continue selecting packages as needed. When you are done, run the build process

    time make V=s download &&
    time make V=s

Faster build time can be achieved by enabling multiple build jobs. In case of quad-core cpu.

    time make -j8 V=s

If build process is successful, your firmware images will be located on `bin/target-platform/`.

If your hardware-specific image name could not be found, it's possible that you added too many packages that don't fit your hardware flash memory. Try reducing packages and restart the build process if such case happens.
