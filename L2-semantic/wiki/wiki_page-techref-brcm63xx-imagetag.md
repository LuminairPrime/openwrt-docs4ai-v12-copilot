---
title: BCM63xx Firmware Image Information
module: wiki
origin_type: wiki_page
token_count: 6807
source_file: L1-raw/wiki/wiki_page-techref-brcm63xx-imagetag.md
last_pipeline_run: '2026-03-28T08:26:59.224930+00:00'
source_url: https://openwrt.org/docs/techref/brcm63xx.imagetag
language: text
ai_summary: The BCM63xx Firmware Image Information module provides tools and details for analyzing firmware image tags specific to Broadcom 63xx devices. It includes a program called `analyzetag` that can be compiled to extract information from firmware image files using various command-line options. Users can specify the input file, tag ID, flash start address, and firmware offset to retrieve detailed metadata about the firmware image. The documentation also outlines the structure of the Broadcom imagetag format, detailing the fields and their purposes for different versions of the imagetag.
ai_when_to_use: This module is useful when working with firmware images for Broadcom 63xx devices in OpenWrt, especially for developers needing to analyze or modify firmware images.
ai_related_topics:
- analyzetag
- tagVersion
- sig_1
- sig_2
- chipid
- boardid
- big_endian
- totalLength
- cfeAddress
- cfeLength
- rootAddress
- rootLength
- kernelAddress
- kernelLength
- dualImage
- inactiveFlag
- information1
- tagId
- tagIdCRC
- reserved1
- imageCRC
- reserved2
- headerCRC
- reserved3
---
# BCM63xx Firmware Image Information

## BCM63xx Firmware Image Analyzer

The following code can be compiled on Linux (and possibly BSD and Mac) with
`gcc -o analyzetag analyzetag.c` to create program called `analyzetag` that can
be used to find information about the specified imagetag file.

The full command information is:

    analyzetag -i <inputfile> -t <tagid> [-s <flashstart>] [-n <fwoffset>]

     -i <inputfile>	Name of firmware image file
     -t <tagid>		Tag id type to use (use -t list to see available
                        choices)
     -s <flashstart>    Address of the start of the firmware image
     -n <fwoffset>      Offset of the firmware from flashstart

Download the code: {{:doc:techref:analyzetag.c|analyzetag.c}}

## Information about the Broadcom 63xx imagetag format

There are different version of the imagetag, depending on the version of the
Broadcom code the imagetag was written for.  This information is for the
[OpenWrt](http://www.openwrt.org/) versions of the tags used for each version.

### Broadcom Generic CFE

|''unsigned char tagVersion[TAGVER_LEN];''           | 0-3: Version of the image tag|
|''unsigned char sig_1[20];''                        | 4-23: Company Line 1|
|''unsigned char sig_2[14];''                        | 24-37: Company Line 2|
|''unsigned char chipid[6];''                        | 38-43: Chip this image is for|
|''unsigned char boardid[16];''                      | 44-59: Board name|
|''unsigned char big_endian[2];''                    | 60-61: Map endianness -- 1 BE 0 LE|
|''unsigned char totalLength[IMAGE_LEN];''           | 62-71: Total length of image|
|''unsigned char cfeAddress[ADDRESS_LEN];''          | 72-83: Address in memory of CFE|
|''unsigned char cfeLength[IMAGE_LEN];''             | 84-93: Size of CFE|
|''unsigned char rootAddress[ADDRESS_LEN];''         | 94-105: Address in memory of rootfs|
|''unsigned char rootLength[IMAGE_LEN];''            | 106-115: Size of rootfs|
|''unsigned char kernelAddress[ADDRESS_LEN];''       | 116-127: Address in memory of kernel|
|''unsigned char kernelLength[IMAGE_LEN];''          | 128-137: Size of kernel|
|''unsigned char dualImage[2];''                     | 138-139: Unused at present|
|''unsigned char inactiveFlag[2];''                  | 140-141: Unused at present|
|''unsigned char information1[TAGINFO_LEN];''        | 142-161: Unused at present|
|''unsigned char tagId[TAGID_LEN];''                 | 162-167: Identifies which type of tag this is, currently two-letter company code, and then three digits for version of broadcom code in which this tag was first introduced|
|''unsigned char tagIdCRC[4];''                      | 168-171: CRC32 of tagId|
|''unsigned char reserved1[44];''                    | 172-215: Reserved area not in use|
|''unsigned char imageCRC[4];''                      | 216-219: CRC32 of images|
|''unsigned char reserved2[16];''                    | 220-235: Unused at present|
|''unsigned char headerCRC[4];''                     | 236-239: CRC32 of header excluding tagVersion|
|''unsigned char reserved3[16];''                    | 240-255: Unused at present|

### Broadcom Code Version 2.2x

|''unsigned char tagVersion[TAGVER_LEN];''           | 0-3: Version of the image tag|
|''unsigned char sig_1[20];''                        | 4-23: Company Line 1|
|''unsigned char sig_2[14];''                        | 24-37: Company Line 2|
|''unsigned char chipid[6];''                        | 38-43: Chip this image is for|
|''unsigned char boardid[16];''                      | 44-59: Board name|
|''unsigned char big_endian[2];''                    | 60-61: Map endianness -- 1 BE 0 LE|
|''unsigned char totalLength[IMAGE_LEN];''           | 62-71: Total length of image|
|''unsigned char cfeAddress[ADDRESS_LEN];''          | 72-83: Address in memory of CFE|
|''unsigned char cfeLength[IMAGE_LEN];''             | 84-93: Size of CFE|
|''unsigned char flashImageStart[ADDRESS_LEN];''     | 94-105: Address in memory of kernel (start of image)|
|''unsigned char flashRootLength[IMAGE_LEN];''       | 106-115: Size of rootfs + deadcode (web flash uses this + kernelLength to determine the size of the kernel+rootfs flash image)|
|''unsigned char kernelAddress[ADDRESS_LEN];''       | 116-127: Address in memory of kernel|
|''unsigned char kernelLength[IMAGE_LEN];''          | 128-137: Size of kernel|
|''unsigned char dualImage[2];''                     | 138-139: Unused at present|
|''unsigned char inactiveFlag[2];''                  | 140-141: Unused at present|
|''unsigned char rsa_signature[TAGINFO_LEN];''       | 142-161: RSA Signature (unused at present; some vendors may use this)|
|''unsigned char reserved5[2];''                     | 162-163: Unused at present|
|''unsigned char tagId[TAGID_LEN];''                 | 164-169: Identifies which type of tag this is, currently two-letter company code, and then three digits for version of broadcom code in which this tag was first introduced|
|''unsigned char rootAddress[ADDRESS_LEN];''         | 170-181: Address in memory of rootfs partition|
|''unsigned char rootLength[IMAGE_LEN];''            | 182-191: Size of rootfs partition|
|''unsigned char flashLayoutVer[4];''                | 192-195: Version flash layout|
|''unsigned char kernelCRC[4];''                     | 196-199: Guessed to be kernel CRC|
|''unsigned char reserved4[16];''                    | 200-215: Reserved area; unused at present|
|''unsigned char imageCRC[4];''                      | 216-219: CRC32 of images|
|''unsigned char reserved2[12];''                    | 220-231: Unused at present|
|''unsigned char tagIdCRC[4];''                      | 232-235: CRC32 to ensure validity of tagId|
|''unsigned char headerCRC[4];''                     | 236-239: CRC32 of header excluding tagVersion|
|''unsigned char reserved3[16];''                    | 240-255: Unused at present|

### Broadcom Code Version 3.00 - 3.08

|''unsigned char tagVersion[TAGVER_LEN];''           | 0-3: Version of the image tag|
|''unsigned char sig_1[20];''                        | 4-23: Company Line 1|
|''unsigned char sig_2[14];''                        | 24-37: Company Line 2|
|''unsigned char chipid[6];''                        | 38-43: Chip this image is for|
|''unsigned char boardid[16];''                      | 44-59: Board name|
|''unsigned char big_endian[2];''                    | 60-61: Map endianness -- 1 BE 0 LE|
|''unsigned char totalLength[IMAGE_LEN];''           | 62-71: Total length of image|
|''unsigned char cfeAddress[ADDRESS_LEN];''          | 72-83: Address in memory of CFE|
|''unsigned char cfeLength[IMAGE_LEN];''             | 84-93: Size of CFE|
|''unsigned char flashImageStart[ADDRESS_LEN];''     | 94-105: Address in memory of kernel (start of image)|
|''unsigned char flashRootLength[IMAGE_LEN];''       | 106-115: Size of rootfs + deadcode (web flash uses this + kernelLength to determine the size of the kernel+rootfs flash image)|
|''unsigned char kernelAddress[ADDRESS_LEN];''       | 116-127: Address in memory of kernel|
|''unsigned char kernelLength[IMAGE_LEN];''          | 128-137: Size of kernel|
|''unsigned char dualImage[2];''                     | 138-139: Unused at present|
|''unsigned char inactiveFlag[2];''                  | 140-141: Unused at present|
|''unsigned char information1[TAGINFO_LEN];''        | 142-161: Unused at present|
|''unsigned char tagId[TAGID_LEN];''                 | 162-167: Identifies which type of tag this is, currently two-letter company code, and then three digits for version of broadcom code in which this tag was first introduced|
|''unsigned char tagIdCRC[4];''                      | 168-173: CRC32 to ensure validity of tagId|
|''unsigned char rootAddress[ADDRESS_LEN];''         | 174-183: Address in memory of rootfs partition|
|''unsigned char rootLength[IMAGE_LEN];''            | 184-193: Size of rootfs partition|
|''unsigned char reserved1[22];''                    | 194-215: Reserved area not in use|
|''unsigned char imageCRC[4];''                      | 216-219: CRC32 of images|
|''unsigned char reserved2[16];''                    | 220-235: Unused at present|
|''unsigned char headerCRC[4];''                     | 236-239: CRC32 of header excluding tagVersion|
|''unsigned char reserved3[16];''                    | 240-255: Unused at present|

### Broadcom Code Version 3.06, Pirelli Modifed Version

|''unsigned char tagVersion[TAGVER_LEN];''           | 0-3: Version of the image tag|
|''unsigned char sig_1[20];''                        | 4-23: Company Line 1|
|''unsigned char sig_2[14];''                        | 24-37: Company Line 2|
|''unsigned char chipid[6];''                        | 38-43: Chip this image is for|
|''unsigned char boardid[16];''                      | 44-59: Board name|
|''unsigned char big_endian[2];''                    | 60-61: Map endianness -- 1 BE 0 LE|
|''unsigned char totalLength[IMAGE_LEN];''           | 62-71: Total length of image|
|''unsigned char cfeAddress[ADDRESS_LEN];''          | 72-83: Address in memory of CFE|
|''unsigned char cfeLength[IMAGE_LEN];''             | 84-93: Size of CFE|
|''unsigned char flashImageStart[ADDRESS_LEN];''     | 94-105: Address in memory of kernel (start of image)|
|''unsigned char flashRootLength[IMAGE_LEN];''       | 106-115: Size of rootfs + deadcode (web flash uses this + kernelLength to determine the size of the kernel+rootfs flash image)|
|''unsigned char kernelAddress[ADDRESS_LEN];''       | 116-127: Address in memory of kernel|
|''unsigned char kernelLength[IMAGE_LEN];''          | 128-137: Size of kernel|
|''unsigned char dualImage[2];''                     | 138-139: Unused at present|
|''unsigned char inactiveFlag[2];''                  | 140-141: Unused at present|
|''unsigned char information1[TAGINFO_LEN];''        | 142-161: Unused at present|
|''unsigned char information2[54];''                 | 162-215: Compilation and related information (not generated/used by OpenWRT)|
|''unsigned char kernelCRC[4] ;''                    | 216-219: CRC32 of images|
|''unsigned char rootAddress[ADDRESS_LEN];''         | 220-231: Address in memory of rootfs partition|
|''unsigned char tagIdCRC[4];''                      | 232-235: Checksum to ensure validity of tagId|
|''unsigned char headerCRC[4];''                     | 236-239: CRC32 of header excluding tagVersion|
|''unsigned char rootLength[IMAGE_LEN];''            | 240-249: Size of rootfs|
|''unsigned char tagId[TAGID_LEN];''                 | 250-255: Identifies which type of tag this is, currently two-letter company code, and then three digits for version of broadcom code in which this tag was first introduced|

### Broadcom Code Version 3.10+

|''unsigned char tagVersion[4];''                    | 0-3: Version of the image tag|
|''unsigned char sig_1[20];''                        | 4-23: Company Line 1|
|''unsigned char sig_2[14];''                        | 24-37: Company Line 2|
|''unsigned char chipid[6];''                        | 38-43: Chip this image is for|
|''unsigned char boardid[16];''                      | 44-59: Board name|
|''unsigned char big_endian[2];''                    | 60-61: Map endianness -- 1 BE 0 LE|
|''unsigned char totalLength[IMAGE_LEN];''           | 62-71: Total length of image|
|''unsigned char cfeAddress[ADDRESS_LEN];''          | 72-83: Address in memory of CFE|
|''unsigned char cfeLength[IMAGE_LEN];''             | 84-93: Size of CFE|
|''unsigned char flashImageStart[ADDRESS_LEN];''     | 94-105: Address in memory of kernel (start of image)|
|''unsigned char flashRootLength[IMAGE_LEN];''       | 106-115: Size of rootfs + deadcode (web flash uses this + kernelLength to determine the size of the kernel+rootfs flash image)|
|''unsigned char kernelAddress[ADDRESS_LEN];''       | 116-127: Address in memory of kernel|
|''unsigned char kernelLength[IMAGE_LEN];''          | 128-137: Size of kernel|
|''unsigned char dualImage[2];''                     | 138-139: Unused at present|
|''unsigned char inactiveFlag[2];''                  | 140-141: Unused at present|
|''unsigned char information1[TAGINFO_LEN];''        | 142-161: Unused at present; Some vendors use this for optional information|
|''unsigned char tagId[6];''                         | 162-167: Identifies which type of tag this is, currently two-letter company code, and then three digits for version of broadcom code in which this tag was first introduced|
|''unsigned char tagIdCRC[4];''                      | 168-171: CRC32 to ensure validity of tagId|
|''unsigned char rootAddress[ADDRESS_LEN];''         | 172-183: Address in memory of rootfs partition|
|''unsigned char rootLength[IMAGE_LEN];''            | 184-193: Size of rootfs partition|
|''unsigned char reserved1[22];''                    | 193-215: Reserved area not in use|
|''unsigned char imageCRC[4];''                      | 216-219: CRC32 of images|
|''unsigned char rootfsCRC[4];''                     | 220-227: CRC32 of rootfs partition|
|''unsigned char kernelCRC[4];''                     | 224-227: CRC32 of kernel partition|
|''unsigned char reserved2[8];''                     | 228-235: Unused at present|
|''unsigned char headerCRC[4];''                     | 235-239: CRC32 of header excluding tagVersion|
|''unsigned char reserved3[16];''                    | 240-255: Unused at present|

### TP-Link custom CFE

The size of the image header is 512 bytes length. Offsets are at different addresses.
^ define in kernel code                       ^ header offset ^ description ^
| ''unsigned long tagVersion;''			     | 0-3   | Tag version number |
| ''unsigned char hardwareId[16];''	             | 4-19  | HWID for cloud |
| ''unsigned char firmwareId[16];''	             | 20-35 | FWID for cloud |
| ''unsigned char oemId[16];''			     | 36-51 | OEMID for cloud |
| ''unsigned long productId;''	                     | 52-55 | product id |
| ''unsigned long productVer;''	                     | 56-59 | product version |
| ''unsigned long addHver;''                         | 60-63 | Addtional hardware version |
| ''unsigned char imageValidToken[20];''             | 64-83 | image validation token - md5 checksum (not used?) |
| ''unsigned char rcSingature[20];'' 	             | 84-103 | RC singature(only for vxWorks) - RSA |
| ''unsigned long kernelTextAddr;''                  | 104-107 | text section address of kernel |
| ''unsigned long kernelEntryPoint;''                | 108-111 | entry point address of kernel |
| ''unsigned long totalImageLen;''                   | 112-115 | the sum of kernelLen+rootfsLen+tagLen |
| ''unsigned long kernelAddress;''                   | 116-119 | starting address (offset from the beginning of FILE_TAG) of kernel image  |
| ''unsigned long kernelLen;''		             | 120-123 | length of kernel image |
| ''unsigned long rootfsAddress;''                   | 124-127 | starting address (offset) of filesystem image |
| ''unsigned long rootfsLen;''		             | 128-131 | length of filesystem image |
| ''unsigned long bootAddress;''	             | 132-135 | starting address (offset) of bootloader image |
| ''unsigned long bootLen;''		             | 136-139 | length of bootloader image |
| ''unsigned long swRevision;''		             | 140-143 | software revision |
| ''unsigned long platformVer;''	             | 144-147 | platform version |
| ''unsigned long specialVer;''                      | 148:151 | special version or CRC32 for bin(kernel+rootfs) bitfliped|
| ''unsigned long binCrc32;''		             | 152:155 | CRC32 for bin(kernel+rootfs) bitfliped or empty|
| ''unsigned long imageSequence;''                   | 156:159 | DUALIMAGE, initial value is 0, valid value is [1 .. 999], for [NAND](../wiki/wiki_page-techref-flash.md) flash: it's indicated by file extension of cferam.xxx in rootfs, for NOR flash: it's stored in kernel tag |
| ''unsigned long reserved1[12];''                   | 160-207 | reserved for future |
| ''unsigned char sig[128];''	                     | 208-335 | signature for update |
| ''unsigned char resSig[128];''                     | 336-443 | reserved for signature |
| ''unsigned long reserved2[12];''                   | 464-511 | reserved for future |

## OpenWRT Broadcom 63xx Firmware Image README

The image needed to flash onto a Broadcom 63xx-series board depends on the
board, method you are using to flash, and, for web-based flash, on the version
of the Broadcom code your router uses.

There are two major revisions of the Broadcom code as far as imagetags are
concerned, before 3.08 and after 3.08, however there are some variations
within in that, either due to vendor differences or due to changes at
Broadcom (it's not clear yet which is the case).  In addtion Pirelli modified
the Broadcom code, so Alice Gate models use a different imagetag than any
other vendor.

The imagetag format for flashing via CFE is the same for almost all the
boards, and is the same for all images generated by the imagetag utility.
Images flashable using cfe are labelled openwrt-[board]-[filesystem]-cfe.bin

The imagetags for tftp/ftp flashing is based on Broadcom 3.00-3.04 imagetags
and is known to be correct as the source code GPL and is available for reading.

Broadcom 3.00-3.02 flashing has been tested on Comtrend CT-5261, CT-536 and
Tecom GW6000, and is the version of the flashing that was present before the
imagetags were split by broadcom code version (early June 2009)

3\.04 is guessed to be the same as 3.00-3.02 based on available information

Broadom 3.06 is thought to be the same as 3.00-3.02, however the only 3.06
this author (Daniel Dickinson) has seen is the Alice Gate (Pirelli) firmware
which is known to be different due to vendor (Pirelli) modifications to the
Broadcom code.

Broadcom 3.08 introduced changes to the imagetag to deal with TR69 (a remote
router management system developed by the DSL Forum).  The version we are
using as 3.08 is based on the BT Voyager firmware image I looked at.  It may
in fact be BT Voyager-specific, and may in fact not be 3.08, but modified 3.06
and not apply to all 3.08 versions.

Broadcom 3.10 uses an imagetag that is believed to apply to all 3.10 and 3.12
versions, and has been tested on the Tecom GW6200.  It is similar to 3.08.
There is a field for vendor-specific information, that at least in some cases
is not optional.  It is based on the hexedit of a neufbox4 firmware image, the
information in https://dev.openwrt.org/ticket/4987, and the hexedit of a Tecom
GW6200 image.

Some boards share the same tag format, but require vendor-specific fields in
the board.  In that case the tagid is shared, but the filename of the generated
image reflects the router for which the image was created.

^router       ^method^ codever ^tagid ^filename
|any          |cfe   |   any   |bccfe |openwrt-[board]-[fs]-bccfe-cfe.bin
|any          |t/ftp |   any   |bc300 |openwrt-[board]-[fs]-bc300-cfe.bin
|             |web   |3.00-3.06|bc300 |openwrt-[board]-[fs]-bc300-cfe.bin
|             |web   |3.10-3.12|bc310 |openwrt-[board]-[fs]-bc310-cfe.bin
|AGVoIP2+WiFi |web   |alice3.06|ag306 |openwrt-AGPF-S0-[fs]-agv2+w-cfe.bin
|CT536        |web   |3.02     |bc300 |openwrt-96348GW-11-[fs]-bc300-cfe.bin
|CT5621       |web   |3.02     |bc300 |openwrt-96348GW-11-[fs]-bc300-cfe.bin
|DG834GT      |web   |3.02     |bc300 |openwrt-96348GW-10-[fs]-bc300-cfe.bin
|DG834PN      |web   |3.02     |bc300 |openwrt-96348GW-10-[fs]-bc300-cfe.bin
|DSL-2640B    |web   |3.10     |bc310 |openwrt-D-4P-W-[fs]-bc310-cfe.bin
|DSL-2740B    |web   |3.10     |bc310 |openwrt-96358GW-[fs]-dsl2740b-cfe.bin
|F5D7633      |web   |3.10     |bc310 |openwrt-96348GW-10-[fs]-bc310-cfe.bin
|F@ST2404     |web   |?        |bc300 |openwrt-F@ST2404-[fs]-bc300-cfe.bin
|F@ST2404     |web   |?        |bc310 |openwrt-F@ST2404-[fs]-bc310-cfe.bin
|GW6000       |web   |3.00     |bc300 |openwrt-96348GW-[fs]-bc300-cfe.bin
|GW6200       |web   |3.10     |bc310 |openwrt-96348GW-[fs]-gw6200-cfe.bin
|Neufbox4     |web   |3.12     |bc310 |openwrt-96358VW-[fs]-nb4-cfe.bin
|TD8810A      |web   |3.06     |bc300 |openwrt-8L-2M-8M-[fs]-bc306-cfe.bin
|TD8810B      |web   |3.06     |bc300 |openwrt-8L-2M-8M-[fs]-bc306-cfe.bin
|TD8811A      |web   |3.06     |bc300 |openwrt-8L-2M-8M-[fs]-bc306-cfe.bin
|TD8811B      |web   |3.06     |bc300 |openwrt-8L-2M-8M-[fs]-bc306-cfe.bin
|TD8900GB     |web   |3.06     |bc300 |openwrt-96348GW-11-[fs]-td8900gb-cfe.bin
|USR9108      |web   |?        |bc300 |openwrt-96348GW-A-[fs]-bc300-cfe.bin
|V2091_BTR    |web   |2.21     |bc221 |openwrt-V2091_BB-[fs]-btvgr-cfe.bin
|V2091_ROI    |web   |2.21     |bc221 |openwrt-V2091-[fs]-btvgr-cfe.bin
|V2091_WB     |web   |2.21     |bc221 |openwrt-V2091-[fs]-btvgr-cfe.bin
|V210_BTR     |web   |2.21     |bc221 |openwrt-V210_BB-[fs]-btvgr-cfe.bin
|V210_ROI     |web   |2.21     |bc221 |openwrt-V210-[fs]-btvgr-cfe.bin
|V210_WB      |web   |2.21     |bc221 |openwrt-V210-[fs]-btvgr-cfe.bin
|V2110        |web   |2.21     |bc221 |openwrt-V2110-[fs]-btvgr-cfe.bin
|V2110_AA     |web   |2.21     |bc221 |openwrt-V2110-[fs]-btvgr-cfe.bin
|V2110_ROI    |web   |2.21     |bc221 |openwrt-V2110-[fs]-btvgr-cfe.bin
|V2500V       |web   |2.21     |bc221 |openwrt-V2500V_BB-[fs]-btvgr-cfe.bin
|V2500V_AA    |web   |2.21     |bc221 |openwrt-V2500V_BB-[fs]-btvgr-cfe.bin
|V2500V_SIP_CLUB |web|2.21     |bc221 |openwrt-V2500V_BB-[fs]-btvgr-cfe.bin

### Old imagetag routers

Davolink DV201AMR

### Redboot routers

Inventel Livebox

## Table of Broadcom Version for Various Routers

^Vendor                     ^ Model                                  ^Code Ver
|Belkin                     |F5D7633                                 |3.10
|British Telecom (BT)       |Voyager V2091_BTR                      |2.21
|British Telecom (BT)       |Voyager V2091_ROI                      |2.21
|British Telecom (BT)       |Voyager V2091_WB                       |2.21
|British Telecom (BT)       |Voyager V210_BTR                       |2.21
|British Telecom (BT)       |Voyager V210_ROI                       |2.21
|British Telecom (BT)       |Voyager V210_WB                        |2.21
|British Telecom (BT)       |Voyager V2110                           |2.21
|British Telecom (BT)       |Voyager V2110_AA                       |2.21
|British Telecom (BT)       |Voyager V2110_ROI                      |2.21
|British Telecom (BT)       |Voyager V220V                           |2.21
|British Telecom (BT)       |Voyager V2500V                          |2.21
|British Telecom (BT)       |Voyager V2500V_AA                      |2.21
|British Telecom (BT)       |Voyager V2500V_SIP_CLUB               |2.21
|Comtrend                   |CT-5261                                 |3.02
|Comtrend                   |CT-536                                  |3.02
|D-Link                     |DSL-2640B                               |3.10
|D-Link                     |DSL-2670B                               |3.10
|NetGear 		    |DG834GT		                     |3.02
|NetGear		    |DG834PN				     |3.02
|Neuf Cegetel               |Neufbox 4                               |3.12
|Pirelli                    |Alice Gate Wi-Fi (+VoIP models?)        |ag 3.06
|Pirelli                    |DRG A125G				     |?
|Sagem			    |F@ST2404				     |?
|TP-Link                    |TD-8810A                                |3.06
|TP-Link		    |TD-8810B				     |3.06
|TP-Link		    |TD-8811A				     |3.06
|TP-Link		    |TD-8811B				     |3.06
|TP-Link		    |TD-W8900GB				     |3.06
|Tecom                      |GW6000                                  |3.00
|Tecom                      |GW6200                                  |3.10
|USR			    |9108				     |?
