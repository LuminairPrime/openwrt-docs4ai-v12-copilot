---
module: wiki
total_token_count: 95689
section_count: 40
is_monolithic: false
is_sharded_part: true
part_number: 2
part_count: 2
generated: '2026-04-01T11:39:51.401225+00:00'
---

# wiki Bundled Reference (Part 2 of 2)

> **Contains:** 40 documents
> **Tokens:** ~95689 (cl100k_base)
> **Index:** [./bundled-reference.md](./bundled-reference.md)

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
| ''unsigned long imageSequence;''                   | 156:159 | DUALIMAGE, initial value is 0, valid value is [1 .. 999], for [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash: it's indicated by file extension of cferam.xxx in rootfs, for NOR flash: it's stored in kernel tag |
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

---

# OpenWrt Buildroot – Technical Reference

See also: [Using the toolchain](/docs/guide-developer/start#using_the_toolchain)

## Kernel related options

The available Kernel version are listed in include/kernel-[version.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md):

Example:

    # Use the default kernel version if the Makefile doesn't override it

    LINUX_RELEASE?=1

    LINUX_VERSION-3.18 = .20
    LINUX_VERSION-4.0 = .9
    LINUX_VERSION-4.1 = .5

    LINUX_KERNEL_MD5SUM-3.18.20 = 952c9159acdf4efbc96e08a27109d994
    LINUX_KERNEL_MD5SUM-4.0.9 = 40fc5f6e2d718e539b45e6601c71985b
    LINUX_KERNEL_MD5SUM-4.1.5 = f23e1d4ce8f63e46db81d56e36281885

    ifdef KERNEL_PATCHVER
      LINUX_VERSION:=$(KERNEL_PATCHVER)$(strip $(LINUX_VERSION-$(KERNEL_PATCHVER)))
    endif

    split_version=$(subst ., ,$(1))
    merge_version=$(subst $(space),.,$(1))
    KERNEL_BASE=$(firstword $(subst -, ,$(LINUX_VERSION)))
    KERNEL=$(call merge_version,$(wordlist 1,2,$(call split_version,$(KERNEL_BASE))))
    KERNEL_PATCHVER ?= $(KERNEL)

    # disable the md5sum check for unknown kernel versions
    LINUX_KERNEL_MD5SUM:=$(LINUX_KERNEL_MD5SUM-$(strip $(LINUX_VERSION)))
    LINUX_KERNEL_MD5SUM?=x

Kernel code is added with contents of generic/files and selectively \<arch\>/files/ subdirs.

It is patched with generic/patches-\<Kernel version\> and \<arch\>/patches-\<Kernel version\>

### CONFIG_EXTERNAL_KERNEL_TREE

OpenWrt will create a symlink to a Kernel repository in the file system.

The target can be a local git kernel repository.

:!: You should patch your tree to contain OpenWrt changes - builds might fail to compile or fail at boot.

:!: Musl libc need patches to kernel headers that fix redifinitions errors with user space headers. uclibc and glibc don't need these changes.

Example:

    095-api-fix-compatibility-of-linux-in.h-with-netinet-in..patch
    270-uapi-kernel.h-glibc-specific-inclusion-of-sysinfo.h.patch
    271-uapi-libc-compat.h-do-not-rely-on-__GLIBC__.patch
    272-uapi-if_ether.h-prevent-redefinition-of-struct-ethhd.patch

see <http://wiki.musl-libc.org/wiki/Building_Busybox>

### OpenWrt Buildroot – Build sequence

      tools – automake, autoconf, sed, cmake
      toolchain/binutils – as, ld, …
      toolchain/gcc – gcc, g++, cpp, …
      target/linux – kernel modules
      package – core and feed packages
      target/linux – kernel image
      target/linux/image – firmware image file generation

### Make sequence

Top command `make world` calls the following sequence of the commands:
`make target/compile`
`make package/cleanup`
`make package/compile`
`make package/install`
`make package/preconfig`
`make target/install`
`make package/index`

You may run each command independently. For example, if the process of compilation of packages stops on error, you may fix the problem and next continue without cleanup:
`make package/compile`
`make package/install`
`make package/preconfig`
`make target/install`
`make package/index`

see [packages](/docs/guide-developer/packages)

### Warnings, errors and tracing

The parameter `V=x` specifies level of messages in the process of the build.

        V=99 and V=1 are now deprecated in favor of a new verbosity class system,
        though the old flags are still supported.
        You can set the V variable on the command line (or OPENWRT_VERBOSE in the
        environment) to one or more of the following characters:

        - s: stdout+stderr (equal to the old V=99)
        - c: commands (for build systems that suppress commands by default, e.g. kbuild, cmake)
        - w: warnings/errors only (equal to the old V=1)

source: <https://dev.openwrt.org/changeset/31484>

old options:

- `1` - print a messages containing the working directory before and after other processing.
- `99` - trace of the build, ordinary messages yellow, error messages red, debug - black;

Examples:

    make V=sc

    make V=sw

---

# BusyBox

[BusyBox](https://en.wikipedia.org/wiki/BusyBox) is used for several system utilities in OpenWrt like `ash` shell, `cp`, `ls`, `echo`, `ping` and many others. It provides tiny replacements with fewer options for most of the utilities from [GNU Core Utilities](https://en.wikipedia.org/wiki/GNU Core Utilities), [GNU Inetutils](https://www.gnu.org/software/inetutils/) and other essential tools like `gzip`.

All this utilities are compiled as "applets" into a single binary file `/bin/busybox`.

## Identify OpenWrt version through udhcp

When an OpenWrt system tries to obtain an IP using DHCP on its WAN interface, it adds a Vendor-Class option that contains the Busybox version:

`Vendor-Class Option 60, length 12: "udhcp 1.28.3"`

This can be used to estimate which OpenWrt version is running on a router if you don't have access to the router itself.

| OpenWrt version | Busybox version |
|:----------------|:----------------|
| 7.06            | 1.4.2           |
| 7.07            | 1.4.2           |
| 7.09            | 1.4.2           |
| 8.09            | 1.11.2          |
| 8.09.1          | 1.11.2          |
| 8.09.2          | 1.11.2          |
| 10.03           | 1.15.3          |
| 10.03.1         | 1.15.3          |
| 12.09           | 1.19.4          |
| 17.01.0         | 1.25.1          |
| 17.01.1         | 1.25.1          |
| 17.01.2         | 1.25.1          |
| 17.01.3         | 1.25.1          |
| 17.01.4         | 1.25.1          |
| 17.01.5         | 1.25.1          |
| 17.01.6         | 1.25.1          |
| 17.01.7         | 1.25.1          |
| 18.06.0         | 1.28.3          |
| 18.06.1         | 1.28.3          |
| 18.06.2         | 1.28.4          |
| 18.06.3         | 1.28.4          |
| 18.06.4         | 1.28.4          |
| 18.06.5         | 1.28.4          |
| 19.07.0         | 1.30.1          |
| 22.03.0         | 1.35.0          |
| 23.05.0         | 1.36.1          |
| 24.10.0         | 1.36.1          |

---

# DFS

[Dynamic_frequency_selection](https://en.wikipedia.org/wiki/Dynamic_frequency_selection) plays a role in 5GHz frequencies that are shared with [Terminal_Doppler_Weather_Radar](https://en.wikipedia.org/wiki/Terminal_Doppler_Weather_Radar). It is related to [802.11h](https://en.wikipedia.org/wiki/IEEE_802.11h).

DFS support is used during ACS/"survey" in [hostapd](/docs/guide-user/network/wifi/wireless-tool/wireless.utilities#hostapd) to find and select free WLAN channels.

Many countries regulate operation of the 5GHz spectrum - see [List_of_WLAN_channels](https://en.wikipedia.org/wiki/List_of_WLAN_channels) & [DFS/TPC channel information](https://en.wikipedia.org/wiki/List_of_WLAN_channels#DFS_and_TPC).

:!: Due to fast development, changing hardware, regulatory changes and compliance issues there can be interoperability issues.

:!: OpenWrt uses open source drivers with varying quality and upstream support. Sometimes they may be abandoned by the manufacturer, or no longer support some 5GHz operation due to regulatory changes.

:!: OEM proprietary drivers can sometimes offer DFS channel where OpenWrt opensource drivers cannot.

:!: There are different DFS schemes: DFS-FCC (USA), DFS-ETSI (Europe), DFS-JP (Japan).

:!: Try to use the non DFS channels if you have older wifi hardware/wifi clients.

## DFS support

- ath9k: DFS-ETSI, DFS-FCC (source: [linux-wireless](http://marc.info/?l=linux-wireless&m=144524581929146)), probably DFS-JP (git commits)
- ath10k: DFS-FCC (source: [linux-wireless](http://marc.info/?l=linux-wireless&m=144524581929146)), probably DFS-ETSI
- ath11k: DFS-FCC (source: [linux-wireless](https://marc.info/?l=linux-wireless&m=170227574420539)), probably DFS-ETSI
- mt76: DFS-ETSI, DFS-FCC, DFS-JP. As of 2021-02-22, DFS is unsupported [on MT7613 radio](/unsupported/dfs) however, despite the hardware supporting it.
- mwlwifi (source:[linux-wireless](http://marc.info/?l=linux-wireless&m=146707822404863&w=2)), but support is problematic on some hardware and won't be fixed ([GitHub issue \#75](https://github.com/kaloz/mwlwifi/issues/75))
- mwifiex (source: git log: "DFS support in AP mode",[kernel.org](http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cf075eac9ca94ec54b5ae0c0ec798839f962be55))

## DFS status unknown

- ath9k_htc
- wlcore, wl18xx (allow using dfs channels,add radar_debug_mode debugfs file for DFS testing)
- brcmfmac
- brcmsmac
- b43

## No DFS support

- mwl8k

---

# External Documentation

OpenWrt is a Linux distribution and comes with own documentation, but much documentation is provided upstream, by the creators of the components.

## Bootloader

### Das U-Boot (GPLv2)

<http://www.denx.de/wiki/U-Boot/>

### RedBoot (modified GPL)

RedBoot (Red Hat Embedded Debug and Bootstrap firmware) <http://ecos.sourceware.org/redboot/>

### CFE (BSD like)

CFE (Common Firmware Environment) is a firmware developed by Broadcom. <http://www.broadcom.com/support/communications_processors/downloads.php#cfe>

## Linux Kernel (GPLv2)

This is the Homepage of the Linux Kernel: <http://www.kernel.org/>.

## GNU/Linux Drivers (diverse)

While all drivers belong into the kernel, official Wikis additionally exist for wireless and sound:

- <http://wireless.kernel.org/>
- <http://alsa-project.org/main/index.php/Main_Page>

## C standard library

### µClibc (LGPL)

At the moment OpenWrt uses µClibc as C standard library. <http://www.uclibc.org/>

### EGLIBC (LGPL)

### newlib (LGPL)

### diet libc (GPLv2)

The project homepage <http://www.fefe.de/dietlibc/> and some [FAQ](http://www.fefe.de/dietlibc/FAQ.txt).

## Opkg (GPLv2)

OpenWrt can be seen as a Linux Distribution for embeded devices. It does bring a Package Manager: <http://code.google.com/p/opkg/>

## BusyBox (GPLv2)

OpenWRT uses [BusyBox](http://www.busybox.net/) to implement the shell environment and most of the usual Unix commands. Instead of having a collection of separate binaries, BusyBox condenses them into one. Executables like vi, ls and grep are merely symbolic links to the BusyBox binary. [BusyBox Command Help](http://busybox.net/downloads/BusyBox.html)

## Netfilter (GPLv2+)

iptables, ip6tables, ebtables: <http://www.netfilter.org/>

## Dropbear (MIT-style license)

OpenWrt prefers <http://matt.ucc.asn.au/dropbear/dropbear.html> over openssl-daemon because of its smaller footprint.

## Dnsmasq (GPL)

In order to handle various OpenWrt configurations, the dnsmasq init script is quite complex. Documentation on all the options passed to dnsmasq is available. [Dnsmasq manual](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)

## Samba (GPLv3)

Official documentation: <http://www.samba.org/samba/docs/>

## Web servers

### µHTTPd (New BSD License)

Since 10.03 'Backfire' OpenWrt utilizes µHTTPd instead of httpd included in Busybox. <https://dev.openwrt.org/browser/trunk/package/uhttpd/> (install `uhttpd`)

### httpd (Busybox) (GPLv2)

[httpd](http://www.busybox.net/downloads/BusyBox.html) (recompile busybox with this included)

### lighttpd (revised BSD)

Currently used by the X-Wrt project. [lighttpd](http://www.lighttpd.net/) (install `lighttpd` and mods)

### mini-httpd (GPLv3+)

[mini-httpd](http://www.nongnu.org/mini-httpd/) (install `mini-httpd` and mods)

### Audio Servers

- <http://pulseaudio.org/>

---

# OpenWrt File System Hierarchy / Memory Usage

| OpenWrt File System Hierarchy |                                                                     |                                       |                                                                       |                                                   |                                |                                |                                                   |                                                   |                    |
|:-----------------------------:|---------------------------------------------------------------------|---------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------|--------------------------------|--------------------------------|---------------------------------------------------|---------------------------------------------------|--------------------|
|                               | Flash Storage Partitioning (TP-Link WR1043ND)                       |                                       |                                                                       |                                                   |                                | Main Memory Usage              |                                                   |                                                   |                    |
|           Hardware            | m25p80 [spi](https://en.wikipedia.org/wiki/spi)0.0: m25p64 8192 KiB |                                       |                                                                       |                                                   |                                | main memory 32 768 KiB         |                                                   |                                                   |                    |
|            Layer1             | @#de401d:mtd0 ***u-boot*** 128 KiB                                  | @#25540b:mtd5 ***firmware*** 8000 KiB |                                                                       |                                                   | @#1dbade:mtd4 ***art*** 64 KiB | @#ff00ff:Kernel space 3828 KiB | @#00ffff:User space 28 940 KiB                    |                                                   |                    |
|            Layer2             | @#de401d:                                                           | @#a11dde:mtd1 ***kernel*** 1280 KiB   | @#378712:mtd2 ***rootfs*** 6720 KiB                                   |                                                   | @#1dbade:                      | @#ff00ff:                      | @#00ffff:up to 50%                                | @#00ffff:512 KiB                                  | @#00ffff:remaining |
|          mountpoint           | @#de401d:                                                           | @#a11dde:                             | @#378712:/                                                            |                                                   | @#1dbade:                      | @#ff00ff:                      | @#00ffff:                                         | @#00ffff:                                         | @#00ffff:          |
|          filesystem           | @#de401d:                                                           | @#a11dde:                             | @#378712:[filesystems#overlayfs](/docs/techref/filesystems#overlayfs) |                                                   | @#1dbade:                      | @#ff00ff:                      | @#00ffff:                                         | @#00ffff:                                         | @#00ffff:          |
|            Layer3             | @#de401d:                                                           | @#a11dde:                             | @#dea11d:1536 KiB                                                     | @#5ade1d:mtd3 ***rootfs_data*** 5184 KiB          | @#1dbade:                      | @#ff00ff:                      | @#00ffff:                                         | @#00ffff:                                         | @#00ffff:          |
|          mountpoint           | @#de401d:none                                                       | @#a11dde:none                         | @#dea11d:/rom                                                         | @#5ade1d:/overlay                                 | @#1dbade:none                  | @#ff00ff:                      | @#00ffff:/tmp                                     | @#00ffff:/dev                                     | @#00ffff:          |
|          filesystem           | @#de401d:none                                                       | @#a11dde:none                         | @#dea11d:[SquashFS](/docs/techref/filesystems#squashfs)               | @#5ade1d:[JFFS2](/docs/techref/filesystems#JFFS2) | @#1dbade:none                  | @#ff00ff:                      | @#00ffff:[tmpfs](/docs/techref/filesystems#tmpfs) | @#00ffff:[tmpfs](/docs/techref/filesystems#tmpfs) | @#00ffff:          |

### Mount Points

- `/` this is your entire root filesystem, it comprises `/rom` and `/overlay`. Please ignore `/rom` and `/overlay` and use exclusively `/` for your daily routines!
- `/rom` contains all the basic files, like `busybox`, `dropbear` or `iptables`. It also includes default configuration files used when booting into [OpenWrt Failsafe mode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset). It does not contain the Linux kernel. All files in this directory are located on the SqashFS partition, and thus cannot be altered or deleted. But, because we use overlay_fs filesystem, so called *overlay-whiteout*-symlinks can be created on the JFFS2 partition.
- `/overlay` is the writable part of the file system that gets merged with `/rom` to create a uniform `/`-tree. It contains anything that was written to the router after [installation](/docs/guide-user/installation/generic.flashing), e.g. changed configuration files, additional packages installed with `opkg`, etc. It is formated with JFFS2.
  Rather than deleting the files, insert a whiteout, a special high-priority entry that marks the file as deleted. File system code that sees a whiteout entry for file F behaves as if F does not exist.
  `#!/bin/sh
  # shows all overlay-whiteout symlinks in the directory /overlay

  find /overlay -type l | while read FILE
    do
      [ -z "$FILE" ] && break
      if ls -la "$FILE" 2>&- | grep -q '(overlay-whiteout)'; then
      echo "$FILE"
      fi
    done
  `
- `/tmp` is a tmpfs-partition `#!/bin/sh
  # shows current size of the tmpfs-partition mounted to /tmp
  calc_tmpfs_size() {pi_size=$(awk '/MemTotal:/ {l=10485760;mt=($2*1024);print((s=mt/2)<l)&&(mt>l)?mt-l:s}' /proc/meminfo)}}
  echo $pi_size
  `
- `/dev` [Driver Core: devtmpfs - kernel-maintained tmpfs-based /dev](http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2b2af54a5bb6f7e80ccf78f20084b93c398c3a8b)

## History

- early OpenWrt-versions: the rootfs was readonly and only NVRAM-variables could be edited
- symlink approach
- [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md) [r3667 add mini_fo patches to mount_root and firstboot](https://dev.openwrt.org/changeset/3667) and [r3669 mini_fo works](https://dev.openwrt.org/changeset/3669) and [r3928 enabled mini_fo by default](https://dev.openwrt.org/changeset/3928)
- overlayfs [r26209 kernel: replace mini_fo with overlayfs for 2.6.37](https://dev.openwrt.org/changeset/26209) and [r26213 kernel: replace mini_fo with overlayfs for 2.6.38](https://dev.openwrt.org/changeset/26213)

---

# Network Filesystems

OpenWrt can mount several filesystem that are attached to an IP Network. OpenWrt acts as a client.

OpenWrt can provide filesystems over network links; it acts as a server.

Files can be provided by other means: see [filesharing](/doc/howto/filesharing)

## Supported Network Filesystems

- ftp (via curlftpfs) [ftp.overview](/docs/guide-user/services/nas/ftp.overview)
- sshfs [sshfs.client](/docs/guide-user/services/ssh/sshfs.client) ,
- sftp [sshfs.server](/docs/guide-user/services/ssh/sshfs.server) , [sftp.server](/docs/guide-user/services/nas/sftp.server)
- nfs [nfs.client](/docs/guide-user/services/nas/nfs.client) , [nfs.server](/docs/guide-user/services/nas/nfs.server)
- cifs [cifs.server](/docs/guide-user/services/nas/cifs.server) , [samba](/docs/guide-user/services/nas/samba)
- iscsi : tgt package
- remotefs
- tftp [tftp.overview](/doc/howto/tftp.overview)
- webdav via davfs2

## Embedded FS

:FIXME:

- owfs ?
- gadgetfs ?

## Security

:FIXME:

The Filesystems mentioned, support varying security. Accessible via TCP often means support for tcp-wrappers (libwrap). Blacklists/Whitelists are sometimes possible. Authentication via ldap ....

---

# Filesystems

This article is about file systems used by OpenWrt for device built-in flash.

For installing additional file systems, including partitioning and mounting, see this page for [general storage](/docs/guide-user/storage/start) as well as this page to other common [filesystems](/docs/guide-user/storage/filesystems-and-partitions).

Please read about the [flash.layout](flash.layout) as well. Also, note that there are two types of flash memory: [NOR flash](https://en.wikipedia.org/wiki/Flash_memory#NOR_flash) and [NAND flash](https://en.wikipedia.org/wiki/Flash_memory#NAND_flash). See also [mtd](/docs/techref/mtd).

## Common File System

### OverlayFS

Used to merge two filesystems, one read-only and the other writable. [flash.layout](flash.layout) explains how this is used in OpenWrt.

- [OverlayFS](https://en.wikipedia.org/wiki/OverlayFS)
- [Overlayfs documentation](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)
- <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.38/209-overlayfs.patch?rev=26213>
- [Debating overlayfs](http://lwn.net/Articles/447650/) on LWN.net
- Was mainlined in Linux kernel 3.18
- Overlayfs's support for inotify mechanisms is not complete yet. Events like IN_CLOSE_WRITE cannot be notified to listening process.

### tmpfs

[tmpfs](https://en.wikipedia.org/wiki/tmpfs) is implemented on many Unix-like operating systems (including OpenWrt). It operates similar to a RAM-Disk, without writing files to disk. In OpenWrt, `/tmp` resides on a tmpfs-partition and `/var` is a symlink to it; `/dev` resides on a little tmpfs partition of its own.

- [Kernel documentation on tmpfs](https://www.kernel.org/doc/html/latest/filesystems/tmpfs.html)

- (+) doesn't directly use space on non-volatile storage
- (-) no wear leveling
- (-) volatile (doesn't survive a reboot)

### SquashFS

[SquashFS](https://en.wikipedia.org/wiki/SquashFS) is a *read only* compressed filesystem. While [gzip](https://en.wikipedia.org/wiki/gzip) is available, at OpenWrt it uses [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) for the compression. Since SquashFS is a read only filesystem, it doesn't need to align the data, allowing it to pack the files tighter thus taking up significantly less space than JFFS2 (20-30% savings over a JFFS2 filesystem)!

- (+) taking up as little space as possible
- (+) allowing the implementation of an idiot proof [FailSafe](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) for recovery, since it is not possible to write to it
- (-) read only
- (-) waste space, since each time a file contained on it is modified, actually a copy of it is being copied to the second (JFFS2) partition
- [Kernel documentation on SquashFS](https://www.kernel.org/doc/html/latest/filesystems/squashfs.html)
- [SquashFs Performance Comparisons](https://elinux.org/Squash_Fs_Comparisons)

There is a generic problem when running SquashFS on [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md): The issue is that SquashFS has no bad block management at all and requires all blocks on order; but for proper [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) bad block management you also need to be able to skip bad blocks and occasionally relocate blocks (see [squashfs and NAND flash](https://www.infradead.org/pipermail/linux-mtd/2006-April/015386.html)). That's why raw SquashFS is a bad idea on [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) (it works if you use a FTL like UBIFS).

### JFFS2

[JFFS2](https://en.wikipedia.org/wiki/JFFS2) is a *writable* compressed filesystem with *[journaling](https://en.wikipedia.org/wiki/Journaling file system)* and *[wear leveling](https://en.wikipedia.org/wiki/wear leveling)* using [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) for the compression.

- (+) is writable, has journaling and wear leveling
- (+) is cool
- (-) is compressed, so a program (`opkg` in particular) cannot know in advance how much space a package will occupy
- (+) is compressed, so a program (which is preinstalled) takes much less space, so effectively you have more space

For [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md)-flash targets, it was replaced with UBIFS.

### UBIFS

- [UBIFS](https://en.wikipedia.org/wiki/UBIFS) is a file system for [raw flash](/docs/techref/flash.layout). It is used in OpenWrt [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) targets since :FIXME: around r40364
- [Kernel documentation on UBIFS](https://www.kernel.org/doc/html/latest/filesystems/ubifs.html)
- [UBIFS File Encryption](https://lwn.net/Articles/704261/) how does UBIFS understand what a "file" is? Isn't a file
- [UBIFS File Encryption v1](https://lwn.net/Articles/706338/) on LWN.net
- [UBIFS File Encryption v2](https://lwn.net/Articles/707900/) on LWN.net
- [UBIFS Supports OverlayFS In Linux 4.9, Readying UBI For MLC Support](https://www.phoronix.com/scan.php?page=news_item&px=UBI-UBIFS-Linux-4.9)

### ext2

- [ext2](https://en.wikipedia.org/wiki/ext2)
- Ext2/3/4 is used on x86, x86-64 and for some arch with SD-card rootfs
- [Kernel documentation on ext2](https://www.kernel.org/doc/html/latest/filesystems/ext2.html)
- (+) a program (`opkg` in particularly) knows how much space is left!
- (+) good ol' veteran FOSS file system
- (-) no journaling (ext3, ext4 support journaling)
- (-) no wear leveling
- (-) no transparent compression

## Other filesystems

OpenWrt does not use other filesystems as rootfs. It supports several filesystems attached to via various mechanisms like USB, SATA or network. For a list see [start](/docs/guide-user/storage/start).

### mini_fo

- was used by older OpenWrt version and thus there are still references to this in the Wiki
- replaced by [\#OverlayFS](#OverlayFS) now.
- [The mini_fo filesystem](https://lwn.net/Articles/135283) on LWN.net
- [mini_fo: The mini fanout overlay file system](https://www.denx.de/wiki/bin/view/Know/MiniFOHome) official site

## Implementation in OpenWrt

The [flash.layout](/docs/techref/flash.layout) article documents how OpenWrt uses both SquashFS and JFFS2 filesystems combined into one filesystem by overlayfs. The kernel is also stored separately from these partitions in raw flash. When the kernel is built, it is also compressed with [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) and [gzip](https://en.wikipedia.org/wiki/gzip), as documented in [imagebuilder](/docs/guide-user/additional-software/imagebuilder).

### Boot process

System bootup is as follows: -\>[process.boot](process.boot)

1.  kernel boots from a known raw partition (without a FS), scans mtd partition *rootfs* for a valid superblock and mounts the SquashFS partition (containing `/etc`) then runs `/etc/preinit`. (More info at [filesystems#technical.details](/docs/techref/filesystems#technical.details))
2.  `/etc/preinit` runs `/sbin/mount_root`
3.  `mount_root` mounts the JFFS2 partition (`/overlay`) and **combines** it with the SquashFS partition (`/rom`) to create a new *virtual root filesystem* (`/`)
4.  bootup continues with `/sbin/init`

`/overlay` was previously named `/jffs2`

### Explanations

|                                                                   |
|-------------------------------------------------------------------|
| FIXME: Please feel free to merge Explanation 1 with Explanation 2 |

#### Explanations 1

Both SquashFS and JFFS2 are compressed filesystems using [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm) for the compression. SquashFS is a *read only* filesystem while JFFS2 is a writable filesystem with *journaling* and *wear leveling*.
Our job when writing the firmware is to put as much common functionality on SquashFS while not wasting space with unwanted features. Additional features can always be installed onto JFFS2 by the user. The use of `mini_fo`/`overlayfs` means that the filesystem is presented as one large writable filesystem to the user with no visible boundary between SquashFS and JFFS2 -- files are simply copied to JFFS2 when they're written.
It's not all without side effects however.
The fact that we pack things so tightly in flash means that if the firmware ever changes, the size and location of the JFFS2 partition also changes, potentially wiping out a large chunk of JFFS2 data and corrupting the filesystem. To deal with this, we've implemented a policy that after each reflash the JFFS2 data is reformatted. The trick to doing that is a special value, `0xdeadc0de`; when this value appears in a JFFS2 partition, everything from that point to the end of the partition is wiped. So, hidden at the end of the firmware images, is the value 0xdeadcode, positioned such that it becomes the start of the JFFS2 partition.
The fact that we use a combination of compressed and partially read only filesystems also has an interesting effect on package management:
In particular, you need to be careful what packages you update. While `opkg` is more than happy to install an updated package on JFFS2, it's unable to remove the original package from SquashFS; the end result is that you slowly start using more and more space until the JFFS2 partition is filled. The opkg util really has no idea how much space is available on the JFFS2 partition since it's compressed, and so it will blindly keep going until the opkg system crashes -- at that point you have so little space you probably can't even use opkg to remove anything.

#### Explanation 2

On many embedded targets that use [NOR flash](https://en.wikipedia.org/wiki/Flash_memory#NOR_flash) for the root filesystem, OpenWrt implements a clever trick to get the most out of the limited flash memory capacity while retaining flexibility for the end-user:
Basically, during the image creation, all of the rootfs contents is packed up in a SquashFS filesystem -- a highly efficient filesystem with compression support. There's one important detail about it though: it is a read-only filesystem. To overcome this limitation OpenWrt uses the remaining portion of the NOR rootfs partition to store an additional read/write jffs2 filesystem which is "overlayed" on top of the rootfs (that is, allowing to read unchanged files from the SquashFS but storing all the modifications made to the jffs2 part).
This design has another important advantage for the end-user: even when the read/write partition is in total mess, he can always boot to the failsafe mode (which mounts only the squashfs part) and proceed from there.

### Technical Details

The kernel boot process involves discovering of partitions within the NOR flash and it can be done by various target-dependent means:

- some bootloaders store a partition table at a known location
- some pass the partition layout via kernel command line
- some targets require specifying the kernel command line at the compile time (thus overriding the one provided by the bootloader).

Either way, if there is a partition named `rootfs` and `MTD_ROOTFS_ROOT_DEV` kernel config option is set to `yes`, this partition is automatically used for the root filesystem.

After that, if `MTD_ROOTFS_SPLIT` is enabled, the kernel adjusts the `rootfs` partition size to the minimum required by the particular SquashFS image and automatically adds `rootfs_data` to the list of the available mtd partitions setting its beginning to the first appropriate address after the SquashFS end and size to the remainder of the original `rootfs` partition. The resulting list is stored in RAM only, so no partition table of any kind gets actually modified.

For more details please refer to the actual patch at: <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.37/065-rootfs_split.patch>

For overlaying a special `mini_fo` filesystem is used, the `README` is available from the sources at <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.37/209-mini_fo.patch>

#### Can we switch the filesystem to be entirely JFFS2?

***`Note:`***: It is possible to contain the entire root filesystem on a JFFS2-Partition only, instead of a combination of both. The advantage is that changes to included files no longer leaves behind an old copy on the read only filesystem. So you could end up saving space. The disadvantage of this would be, that you have no failsafe any longer and also, JFFS2 takes significantly more space then SquashFS.

Yes, it's technically possible, but a bit of a mess to actually pull off. The firmware has to be loaded as a trx file, which means that you have to put the JFFS2 data inside of the trx. But, as I said above, the trx has a checksum, meaning that if you ever change that data, you invalidate the checksum. The solution is that you install with the JFFS2 data contained within the trx, and then change the trx-boundaries at runtime. The end result is a single JFFS2 partition for the root filesystem. Why someone would want to do it is beyond me; it takes more space, and while it would allow you to upgrade the contents of the filesystem you would still be unable to replace the kernel (outside of the filesystem), meaning that a seamless upgrade between releases is still not possible! Having SquashFS gives you a failsafe mechanism where you can always ignore the JFFS2 partition and boot directly off SquashFS, or restore files to their original SquashFS versions.

I used to have a trick where I could convert a SquashFS install to a JFFS2 install at runtime by copying all the data onto the SquashFS partition and changing the partition boundaries. I never really had much use for the util -- not to mention it required a rather large flash to store both SquashFS and JFFS2 copies of the root during transition -- so support for it was dropped.

## Notes

Example pictures: on formatted partition / how data is stored (and addressed on ext3)

- how data is stored and addressed by ext2:
- how data is stored and addressed by ext3:
- how data is stored and addressed by SquashFS:
- how data is stored and addressed by JFFS2:

---

# The OpenWrt Flash Layout

The embedded devices (routers and such) OpenWrt/LEDE (Linux Embedded Development Environment) has mainly targeted since its inception, use flash memory as the form of non-volatile memory for the persistent storage of the firmware and its configuration.

## Types of flash memory

### Non-mechanical wear

Moving parts are prone to [wear](https://en.wikipedia.org/wiki/wear) (german: [Verschleiß](https://de.wikipedia.org/wiki/Verschleiß)) and experience all sorts of "mechanical breakage/mechanical failure". But how can a non-moving part possibly break? Possibly by [electromigration](https://en.wikipedia.org/wiki/electromigration), by [whisker growth](https://en.wikipedia.org/wiki/Whisker (metallurgy)), etc.

Non-mechanical wear does not only occur when flash memory is erased!

> [![NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md)]
> 1. Flash memory is more likely to experience failure than a [Hard_disk_drive](https://en.wikipedia.org/wiki/Hard_disk_drive) (the ones with the platters rotating at 5400–15000 [RPM](https://en.wikipedia.org/wiki/Revolutions per minute))
>
> 2. Some types of flash memory seem to experience more non-mechanical wear then other types
>
> 3. How do we deal with failure?

### Host-managed vs. self-managed

Based on how the flash memory chip is connected with the [SoC](/docs/techref/hardware/soc) (i.e. the "host") we at OpenWrt distinguish between ***"raw flash"*** or ***"host-managed"*** and ***"FTL (Flash Translation Layer) flash"*** or ***"self-managed"***: in case the flash memory chip is connected directly with the SoC we call it "raw flash" / "host-managed" and in case there is an additional controller chip between the flash memory chip and the SoC, we call it "FTL flash" / "self-managed". Primarily the controller chip does [wear-leveling](https://en.wikipedia.org/wiki/wear-leveling) and manages known bad blocks, but it may do other stuff as well. The flash memory cannot be accessed directly, but only through this controller. The controller has to be considered a [black box](https://en.wikipedia.org/wiki/black box).

> [![NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md)]
> Embedded systems almost exclusively use "raw flash", while [solid-state drives (SSDs)](https://en.wikipedia.org/wiki/Solid-state drive) and USB memory sticks, almost exclusively use "FTL flash"!

### NOR flash vs NAND flash

Additionally we at OpenWrt distinguish between the two basic types of flash memory: [NOR flash](https://en.wikipedia.org/wiki/Flash_memory#NOR_flash) and [NAND flash](https://en.wikipedia.org/wiki/Flash_memory#NAND_flash).
"Raw NOR flash" in typical routers is generally small (4 MiB – 16 MiB) and **error-free**: all data blocks are guaranteed to work correctly. Because raw NOR flash is error-free, the installed file system(s) do not need to take bad blocks into account, and neither SquashFS nor JFFS2 do. The combination of OverlayFS with SquashFS and JFFS2 has been the default OpenWrt setup since the beginning, and it works flawlessly on "raw NOR flash". Older routers typically use NOR flash.

"Raw [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash" in typical routers is generally much larger (32 MiB – 1 GiB) and **not error-free**: in general the flash contains bad blocks when new and may develop more at any time. Newer routers use [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash because it is much cheaper for a given capacity and is also faster for bulk access (disk emulation), but at the cost of the increased complexity required to handle flash defects.

Bad blocks in [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash and handled in various ways:

- The [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash manufacturer guarantees that certain very small areas of the flash are defect-free. The use of such areas is up to the system designer. Some SoCs may store the first stage bootloader there (but since newer SoCs tend to support chain-of-trust booting, they typically store the first stage bootloader on-chip).
- Some partitions are used as large files that can only be read or written completely and in one go. This is the case of raw bootloaders and kernels in MTD partitions. For these partitions, bad blocks are simply skipped during both reads and writes. Because new defects almost exclusively develop during erase and writes, once written these partitions are mostly trusted to be readable forever. (But newer devices tend to duplicate these partitions to minimize failures.)
- Some partitions are used as large files that can only be written completely and in one go, but can be read in a random access fashion. This is the case of raw read-only file systems (such as squashfs) in MTD partitions. For these partitions, bad blocks are simply skipped during writes, and a kernel driver is used to read them. The driver reads the complete partition during setup skipping bad blocks, and builds a logical-block-to-flash-block table in RAM to be able to later access the partition random-access.
- Some large partitions are used as containers for other compartmentalized data. Note that the amount of bad blocks in a certain partition is a-priory unknown, and thus a raw partition size cannot be taken as the its usable size. For smaller partitions this effect is amplified: although there is a manufacturer-defined limit on the number of bad blocks in a flash, nothing precludes all bad blocks from residing in the same partition. Thus, for guaranteed operation, a system designer should allow *in each and every partition* the maximum number of bad blocks specified for the complete flash. (In practice though, this is almost never done.) Also note that the previous kinds of defect handling do not spread wear produced by erase/write cycles across the whole flash, and thus in general reduce the lifespan of the device. These problems are both solved by UBI. Ideally a single very large UBI partition is created that entirely manages flash defects and wear-leveling for contained volumes, and inside it different UBI volumes are created:
  - Some UBI volumes are used as large files that can only be read or written completely and in one go. This is the case of kernels in UBI partitions.
  - Some UBI volumes are used as large files that can only be written completely and in one go, but can be read in a random access fashion. This is the case of read-only file systems (such as squashfs) in UBI partitions. For these volumes, an ubiblock kernel device is used to read them: the device emulates a read-only block device and maintains a logical-block-to-flash-block table in RAM to be able to access the volume random-access.
  - Some UBI volumes are used as read-write filesystems. Only the [UBIFS](../wiki/chunked-reference/wiki_page-techref-filesystems.md) filesystem is used for this. (It would be possible to emulate read-write block devices on top of UBI and use regular filesystems on top of that, but such setups would underperfom compared to [UBIFS](../wiki/chunked-reference/wiki_page-techref-filesystems.md), and it seems that the necessary UBI block emulation driver has not yet been implemented, if ever.)

Note that because of these factors, the OpenWrt [Image Generator](/docs/guide-user/additional-software/imagebuilder) has been constrained to build images that are smaller than the size of the partitions to which they are supposed to be flashed by an arbitrary margin, to maximize the probability that such images can be flashed on all devices.

### MLC vs. SLC flash

The main difference between SLC and MLC is durability. [single-level cell (SLC)](https://en.wikipedia.org/wiki/Single-level cell) flash memory may have a lifetime of about 50,000 to 100,000 program/erase cycles, while [multi-level cell (MLC)](https://en.wikipedia.org/wiki/Multi-level cell) flash may have a lifetime of about 1,000 to 10,000 program/erase cycles.

To be noted that it is **NOT RIGHT** to estimate the life of a [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash in embedded devices using the same method for SSD!

## Partitioning of NOR flash-based devices

On these systems, the storage is presented by the kernel as an MTD device, and it is divided into MTD partitions. The device is not partitioned in the traditional way, where you store information about partitions in a [GPT](https://en.wikipedia.org/wiki/GUID Partition Table) or [MBR](https://en.wikipedia.org/wiki/Master boot record). Instead, the partitioning information is directly known by the bootloader and the kernel, either through configuration, or more typically through baking it in at build time. For example, in the kernel it may simply be defined that *"MTD partition **`kernel`** starts at flash block `X` and consists of `Y` blocks"*. MTD partitions can be accessed by name or number.

The generic flash layout is:

```tsv
Layer0	raw flash
Layer1	bootloader; partition(s)	optional; SoC; specific; partition(s)	firmware partition	 	 	optional; SoC; specific; partition(s)
Layer2	:::	:::	OpenWrt firmware image	 	*(space available for storage)*	:::
Layer3	:::	:::	Linux kernel; (raw image)	**`rootfs`**; mounted: "`/rom`", [SquashFS](/docs/techref/filesystems#SquashFS); size depends on selected packages	**`rootfs_data`**; mounted: "`/overlay`", [JFFS2](/docs/techref/filesystems#JFFS2); all remaining free space	:::
Layer4	:::	:::	:::	mounted: "`/`", [OverlayFS](/docs/techref/filesystems#overlayfs); stacking `/overlay` on top of `/rom`	 	:::
```

Many NOR devices share this scheme, but the flash layout can differ between the devices. Please see the wiki pages for each SoC and devices for information about a particular layout. In case the flash layout differs for your device please update the wiki pages.

### Sysupgrade and `rootfs_data`

To better use the minimal storage on devices available when OpenWrt was originally being developed, the **`rootfs_data`** partition was placed immediately after the OpenWrt firmware image (which contains the kernel and rootfs), without any padding in-between. This means that during upgrades, the beginning of **`rootfs_data`** might need to be overwritten (either because the OpenWrt image grew, or because the [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash developed new defects in the firmware area that need to be skipped during firmware flashing).

To handle this situation, sysupgrade works in an atypical fashion. During an upgrade OpenWrt reads selected content from **`rootfs_data`** that it wants surviving the upgrade into RAM, flashes the new firmware, formats the remaining flash space as the new **`rootfs_data`** partition, and writes back the selected content to it from RAM.

Because of this, a failed sysupgrade might not only brick the device, it might also cause the contents of **`rootfs_data`** to be irrevocably lost.

Note: Arbitrary files you may choose to store in **`rootfs_data`** are by default **not kept** across sysupgrades (but there is a way to request future sysupgrades to conserve selected files).

### Example NOR flash partitioning

[Qualcomm Atheros](/docs/techref/hardware/soc/soc.qualcomm)-based [TL-WR1043ND](/toh/tp-link/TL-WR1043ND). Somebody also provided a [LibreOffice Calc ODS](https://web.archive.org/web/20131021013058/http://ubuntuone.com/2aPBH9pwkxtYzy93S0cS1z).

SquashFS-Images are suitable for devices with *"raw NOR flash memory"*-chips and it is not recommended to install them onto devices with *"raw [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash memory"*-chips. SquashFS-Images comprise both, a SquashFS partition and an JFFS2 partition. JFFS2-Images omit the SquashFS partition.

|     TP-Link WR1043ND Flash Layout     |                                                                                                                             |                              |                                                            |                                                      |                       |
|:-------------------------------------:|-----------------------------------------------------------------------------------------------------------------------------|------------------------------|------------------------------------------------------------|------------------------------------------------------|-----------------------|
|                Layer0                 | raw NOR flash memory chip (m25p80 [spi](https://en.wikipedia.org/wiki/Serial Peripheral Interface Bus)0.0: m25p64) 8192 KiB |                              |                                                            |                                                      |                       |
|                Layer1                 | mtd0 ***u-boot*** 128 KiB                                                                                                   | mtd5 ***firmware*** 8000 KiB |                                                            |                                                      | mtd4 ***art*** 64 KiB |
|                Layer2                 |                                                                                                                             | mtd1 ***kernel*** 1280 KiB   | mtd2 ***rootfs*** 6720 KiB                                 |                                                      |                       |
| mountpoint |                                                                                                                             |                              | `/`                             |                                                      |                       |
|              filesystem               |                                                                                                                             |                              | [OverlayFS](/docs/techref/filesystems#overlayfs)           |                                                      |                       |
|                Layer3                 |                                                                                                                             |                              |                                                            | mtd3 ***rootfs_data*** 5184 KiB                      |                       |
|              Size in KiB              | 128 KiB                                                                                                                     | 1280 KiB                     | 1536 KiB                                                   | 5184 KiB                                             | 64 KiB                |
|                 Name                  | ***u-boot***                                                                                                                | ***kernel***                 |                                                            | ***rootfs_data***                                    | ***art***             |
| mountpoint | *none*                                                                                                                      | *none*                       | `/rom`                          | `/overlay`                | *none*                |
|              filesystem               | *none*                                                                                                                      | *none*                       | [filesystems#SquashFS](/docs/techref/filesystems#SquashFS) | [filesystems#JFFS2](/docs/techref/filesystems#JFFS2) | *none*                |

#### Another Flash layout example

[TP-Link Archer C6 V2 (EU/RU/JP)](/toh/tp-link/archer_c6_v2#flash_layout)

### Explanations

The Linux kernel treats "raw flash memory" (no matter whether NOR or [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md)) chips as an [MTD (Memory Technology Device)](/docs/techref/mtd) and employs [filesystems](/docs/techref/filesystems) developed for this purpose on top of the MTD layer.

Since the partitions are nested we look at this whole thing in layers:

1.  Layer0: So we have the Flashchip, 8 MiB in size, which is soldered to the PCB and connected to the [soc](/docs/techref/hardware/soc) over [SPI (Serial Peripheral Interface Bus)](https://en.wikipedia.org/wiki/Serial Peripheral Interface Bus).
2.  Layer1: We "partition" the space into mtd0 for the bootloader, mtd5 for OpenWrt and, in this case, mtd4 for the ART (Atheros Radio Test) - it contains calibration data for the wifi (EEPROM). If it is missing or corrupt, `ath9k` (wireless driver) won't come up anymore. The bootloader (128 KiB) contains of the u-boot 64KiB block AND a data section which contains the MAC, WPS-PIN and type description. If no MAC is configured ath9k will not work correctly due to a faulty MAC.
3.  Layer2: we subdivide mtd5 (firmware) into mtd1 (kernel) and mtd2 (rootfs); In the generation process of the firmware (see [imagebuilder](/docs/guide-user/additional-software/imagebuilder)) the Kernel binary file is first packed with [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm), then the obtained file is packed with [gzip](https://en.wikipedia.org/wiki/gzip) and then this file will be written onto the raw flash (mtd1) without being part of any filesystem! During boot, u-boot copies this entire section into RAM and executes it. From there on, the Linux kernel bootstraps itself…
4.  Layer3: we subdivide rootfs even further into mtd3 for rootfs_data and the rest for an unnamed partition which will accommodate the SquashFS-partition.

#### Mount Points

- `/` this is your entire root filesystem, it comprises `/rom` and `/overlay`. Please ignore `/rom` and `/overlay` and use exclusively `/` for your daily routines!
- `/rom` contains all the basic files, like `busybox`, `dropbear` or `iptables`. It also includes default configuration files used when booting into [OpenWrt Failsafe mode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset). It does not contain the Linux kernel. All files in this directory are located on the SquashFS partition, and thus cannot be altered or deleted. But, because we use overlay_fs filesystem, *overlay-whiteout*-symlinks can be created on the JFFS2 partition.
- `/overlay` is the writable part of the file system that gets merged with `/rom` to create a uniform `/`-tree. It contains anything that was written to the router after [installation](/docs/guide-user/installation/generic.flashing), e.g. changed configuration files, additional packages installed with `opkg`, etc. It is formatted with JFFS2.

Whenever the system is asked to look for an existing file in `/`, it first looks in `/overlay`, and if not there, then in `/rom`. In this way `/overlay` overrides `/rom` and creates the effect of a writable `/` while much of the content is safely and efficiently stored in the read-only `/rom`.

When the system is asked to delete a file that is in `/rom`, it instead creates a corresponding entry in `/overlay`, a whiteout. A whiteout is a symlink to `(overlay-whiteout)` that mostly behaves like a file that doesn't exist. In newer versions, the whiteout is created as a character device with 0/0 device number instead.

``` bash
#!/bin/sh
# shows all overlay-whiteout symlinks
# 2018: overlay-whiteouts are a character device on CC 'find /overlay -type c' seems to work
#  https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt  put me on the right track

find /overlay -type c; find /overlay -type l -exec sh -c \
    'for x; do [ "$(readlink -n -- "$x")" = "(overlay-whiteout)" ] && printf %s\\n "$x"; done' -- {} +
```

#### Example 2: Hoo Too HT-TM02

[Ralink RT5350F](/docs/techref/hardware/soc/soc.ralink)-based [Hoo Too HT-TM02](/toh/hwdata/hootoo/hootoo_tripmatenano_v15).

```tsv
Layer0	raw flash, 8192 KiB
Layer1	**mtd0**; `u-boot`; 192 KiB	**mtd1**; `u-boot-env`; 64 KiB	**mtd2**; `factory`; 64 KiB	**mtd3**; `firmware`; 7872 KiB (= FlashSize-(192+64+64))
Layer2	:::	:::	:::	**mtd4**; `kernel`; about 1 MiB	**mtd5**; `rootfs`
Layer3	:::	:::	:::	:::	**`/dev/root`**; around 2 MiB	**mtd6**; `rootfs_data`; around 4.5 MiB
```

#### Example 3: D-Link DIR-300

For some devices, the OpenWrt partition `firmware` may not exist at all. The [DIR-300 flash layout](/toh/d-link/DIR-300#flash_layout) is such an example.

## Partitioning of NAND flash-based devices

On these systems, the storage is presented by the kernel as an MTD device, and it is divided into MTD partitions. The device is not partitioned in the traditional way, where you store information about partitions in a [GPT](https://en.wikipedia.org/wiki/GUID Partition Table) or [MBR](https://en.wikipedia.org/wiki/Master boot record). Instead, the partitioning information is directly known by the bootloader and the kernel, either through configuration, or more typically through baking it in at build time. For example, in the kernel it may simply be defined that *"MTD partition **`kernel`** starts at flash block `X` and consists of `Y` blocks"*. MTD partitions can be accessed by name or number.

Some [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) devices contain bootloaders that do not understand UBI partitions and thus cannot boot kernels contained in UBI volumes. The generic flash layout for these devices is:

```tsv
Layer0	raw flash
Layer1	bootloader; partition(s)	optional; SoC; specific; partition(s)	Linux kernel; (raw image)	optional; SoC; specific; partition(s)	UBI partition	 	optional; SoC; specific; partition(s)
Layer2	:::	:::	:::	:::	**`rootfs`**; mounted: "`/rom`", [SquashFS](/docs/techref/filesystems#SquashFS); size depends on selected packages	**`rootfs_data`**; mounted: "`/overlay`", [UBIFS](/docs/techref/filesystems#UBIFS); all remaining free space	:::
Layer3	:::	:::	:::	:::	mounted: "`/`", [OverlayFS](/docs/techref/filesystems#overlayfs); stacking `/overlay` on top of `/rom`	 	:::
```

The generic flash layout for [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) devices that can boot kernels contained in UBI volumes is:

```tsv
Layer0	raw flash
Layer1	bootloader; partition(s)	optional; SoC; specific; partition(s)	UBI partition	 	 	optional; SoC; specific; partition(s)
Layer2	:::	:::	**`kernel`**; Linux kernel; (raw image)	**`rootfs`**; mounted: "`/rom`", [SquashFS](/docs/techref/filesystems#SquashFS); size depends on selected packages	**`rootfs_data`**; mounted: "`/overlay`", [UBIFS](/docs/techref/filesystems#UBIFS); all remaining free space	:::
Layer3	:::	:::	:::	mounted: "`/`", [OverlayFS](/docs/techref/filesystems#overlayfs); stacking `/overlay` on top of `/rom`	 	:::
```

Many [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) devices share this scheme, but the flash layout can differ between the devices. Please see the wiki pages for each SoC and devices for information about a particular layout. In case the flash layout differs for your device please update the wiki pages.

### Reserving UBI partition space for user-defined UBI volumes

For [historical reasons](/docs/techref/flash.layout#sysupgrade_and_rootfs_data) concerning NOR flash-based devices, sysupgrade works in an atypical fashion. During upgrades OpenWrt reads selected content from **`rootfs_data`** that it wants surviving the upgrade into RAM, creates an all-new **`rootfs_data`**, and writes back the selected content to it from RAM.

On [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) devices using UBI, sysupgrade partially reads the **`rootfs_data`** volume to RAM, deletes **`kernel`** (for kernel-in-UBI devices), **`rootfs`** and **`rootfs_data`** volumes, recreates **`kernel`** (if kernel-in-UBI) and **`rootfs`** volumes sizing them to fit the new images, recreates the **`rootfs_data`** volume utilizing all remaining free space in the UBI partition, flashes the firmware, and writes back data from RAM to **`rootfs_data`**.

While this setup worked well for old space-limited NOR devices, it may not be optimal for today's large NANDs. Nowadays, devices with flash sizes of 1 GiB or more are not uncommon, and for these devices moving all flash data to RAM and back is inefficient, unduly dangerous, and may not even be possible.

Fortunately the default behavior of sysupgrade on [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) devices using UBI can be modified: instead of recreating the **`rootfs_data`** volume utilizing all the free space in the UBI partition, sysupgrade can restrict the volume to a specific user-defined size. The requested **`rootfs_data`** size must be specified in bytes in the **`rootfs_data_max`** bootloader environment variable. (The variable is evaluated when read, so "128\*1024\*1024", "0x8000000", "134217728" are all valid and equivalent.)

The relevant bootloader variable can be read with this command:

    fw_printenv -n rootfs_data_max

Set with:

    fw_setenv rootfs_data_max <VALUE>

And cleared with:

    fw_setenv rootfs_data_max

Note that sysupgrade will fail if there is not enough space in the UBI partition to create **`rootfs_data`** of the specified size, and the contents of **`rootfs_data`** will then be lost. (The **`rootfs_data_max`** variable should have better been named **`rootfs_data_size`**.) The user must make sure that enough free space exists in UBI to accommodate growth of future OpenWrt images and/or custom OpenWrt images with more packages.

### Example: Creating a UBI volume for persistent storage across sysupgrades

In an Askey RT4230W REV6 router with 512 MiB flash, the **`rootfs_data`** volume is normally sized at around 370 MiB (the remaining flash space being used for bootloaders, SoC-specific partitions, kernel, rootfs, and recovery). You can check this using:

    root@router:~# ubinfo -d 0 -N rootfs_data
    Volume ID:   2 (on ubi0)
    Type:        dynamic
    Alignment:   1
    Size:        3086 LEBs (391847936 bytes, 373.6 MiB)
    State:       OK
    Name:        rootfs_data
    Character device major/minor: 246:3

Given that this volume is routinely wiped by sysupgrade, storing any remotely valuable files here would be ill-advised. For this router you might choose to limit **`rootfs_data`** to a generous 128 MiB, and create a new 192 MiB [UBIFS](../wiki/chunked-reference/wiki_page-techref-filesystems.md) volume for persistent storage, while still reserving 50+ MiB as free space to accommodate future growth of OpenWrt images. Let's do just that and name the new volume **`extra`**.

First you need to limit **`rootfs_data`** to 128 MiB for all following sysupgrades:

    root@router:~# fw_setenv rootfs_data_max 0x8000000

Next do a sysupgarde (even if no upgrade is needed) to resize **`rootfs_data`**. After that, verify its new size:

    root@router:~# ubinfo -d 0 -N rootfs_data
    Volume ID:   2 (on ubi0)
    Type:        dynamic
    Alignment:   1
    Size:        1058 LEBs (134340608 bytes, 128.1 MiB)
    State:       OK
    Name:        rootfs_data
    Character device major/minor: 246:3

You just freed 240+ MiB in the UBI partition. Next, you could manually create, format, and mount a new [UBIFS](../wiki/chunked-reference/wiki_page-techref-filesystems.md) volume. But OpenWrt has a tool to automate this, so let's use it.

Connect the router to the internet if necessary, and use Luci to install package `uvol` (**System \> Software**). You might also want to install your favorite text editor now (`nano-full` is a good option).

Now check the installation (sizes are in bytes):

    root@router:~# uvol list
    root@router:~# uvol total
    422576128
    root@router:~# uvol free
    253317120

Create and enable the `extra` volume using `uvol`:

    root@router:~# uvol create extra $(( 192*1024*1024 )) rw
    Volume ID 4, size 1586 LEBs (201383936 bytes, 192.0 MiB), LEB size 126976 bytes (124.0 KiB), dynamic, name "uvol-wp-extra", alignment 1
    root@router:~# uvol up extra
    root@router:~# uvol list
    extra rw 201383936
    root@router:~# mount | grep extra
    /dev/ubi0_4 on /tmp/run/uvol/extra type ubifs (rw,relatime,assert=read-only,ubi=0,vol=4)

You do not like the default mount path (`/tmp/run/uvol/extra`), so you change it to `/extra` using you text editor:

    root@router:~# nano /etc/config/fstab

Finally reboot and check that your new volume is mounted where you want it:

    root@router:~# mount | grep extra
    /dev/ubi0_4 on /extra type ubifs (rw,relatime,assert=read-only,ubi=0,vol=4)

## MTD (Memory Technology Device) and MTDSPLIT

The Linux kernel treats "raw/host-managed" flash memory (NOR and [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) alike) as an MTD (Memory Technology Device). An MTD is different to a [block device](https://en.wikipedia.org/wiki/block device) or a [character device](https://en.wikipedia.org/wiki/character device).

On a common block device such as a hard drive, the storage space is split up into "blocks", which are also named "sectors", of a size of 512 Bytes or 4096 Bytes. Blocks do not get corrupted during common operation, but only exceptionally. In the very rare case this happens, the LBA hard disk controller takes care, that accesses to such a bad block are redirected to a replacement block. Block devices support 2 main operations - read a whole block and write a whole block. When a block device is partitioned, the information is stored in the [MBR](https://en.wikipedia.org/wiki/Master boot record) or the [GPT](https://en.wikipedia.org/wiki/GUID Partition Table).

Flash memory using MTD is different from this.

The storage space of a MTD is split up into "erase-blocks", of a size of e.g 64 KiB, 128 KiB or much more, which themselves are split up into "blocks", which are more correctly named "pages", of smaller sizes.

A single "page" can be written to, but it cannot be overwritten, but instead the entire "erase block" that page is part of, has to be erased before it becomes possible to re-write its "pages". Erase-blocks do become worn out after some number of erase cycles – typically 100K-1G for SLC [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) and NOR flashes, and 1K-10K for MLC [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flashes. Erase-blocks may become bad (only [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md)). In case of "FTL flash", the controller should notice and avoid further access to bad erase-blocks. In case of "raw flash", the operating system should deal with such cases.

MTD devices support 3 main operations - read from some offset within an erase block, write to some offset within an erase-block, and erase a whole erase-block.

The utility program [mtd](/docs/techref/mtd) can be used to manage MTD devices.

### MTD partitions

The MTD device is often subdivided into logical chunks of memory called partitions. Each partition start at the beginning of an erase-block and end at the end of an erase-block.

The partitioning of MTD devices is not stored in some MBR/GPT, but it is done in the Linux Kernel using MTD-specific partition parsers determining the location and size of these partitions. (sometimes the partitioning is implemented independently in the [bootloader](/docs/techref/bootloader) as well!).

The kernel boot process involves discovering of partitions within the NOR flash and it can be done by various target-dependent means:

- some bootloaders store a partition table at a known location
- some pass the partition layout via kernel command line
- some pass the partition layout using Device Tree
- some targets require specifying the kernel command line at the compile time (thus overriding the one provided by the bootloader).

Some of these schemes but not all are implemented in the mainline Linux kernel. The standard kernel can usually detect the top level coarse partitioning scheme, but not the more fine-grained sub-partitions.

### MTDSPLIT

In order to deal with some of the custom flash partitioning schemes directly in the kernel, OpenWrt has developed `mtdsplit` which is a set of patches currently maintained separately from the mainline kernel, but used in OpenWrt to parse different flash layouts and split them into further "logical" partitions.

This is done recursively so that further split of a new "child" partition may be attempted. Whether an attempt is made to split a partition depends on the partition name.

- `rootfs` is hardcoded to be split.
- `CONFIG_MTD_SPLIT_FIRMWARE` can be used to control whether attempt is made on `firmware` partition. The most common splitting here is kernel, followed by padding, followed by SquashFS root filesystem, followed by padding, followed by free space.

During splitting, the kernel walks the erase blocks and detects magic bytes via parsers. Each partition type (usually determined from name) has its own list of parsers.

New partitions are usually some offset into the start of the original partition. The size and number of the "children" depends on what is detected. For example if SquashFS image is found then the `rootfs` partition is added. For SquashFS image the splitter also automatically adds `rootfs_data` to the list of the available mtd partitions, setting this partition's beginning to the first appropriate address after the SquashFS end and size to the remainder of the `rootfs` partition.

The resulting list of split off partitions is stored in RAM only, so no partition table of any kind gets actually modified. This also includes detection and creation of `ubi` partition and others, as well as for vendor-specific layouts.

For more details please refer to the code for the mtdsplit: <https://github.com/openwrt/openwrt/tree/master/target/linux/generic/files/drivers/mtd/mtdsplit>

For overlaying a special `mini_fo` filesystem is used, the `README` is available from the sources at <https://dev.openwrt.org/browser/trunk/target/linux/generic/patches-2.6.37/209-mini_fo.patch>

## UBI (Unsorted Block Images)

Unsorted Block Images (UBI) is an `erase block` management layer in the Linux kernel for raw [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash memory chips. It is layer on top of the MTD layer. UBI is used by [UBIFS](/docs/techref/filesystems#UBIFS).

UBI serves two purposes, tracking "bad erase blocks" of a raw [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flash memory chip and also providing wear-leveling. To accomplish this, UBI maps *logical erase blocks* to *physical erase blocks* and presents the first ones to higher layers.

- \[<http://www.linux-mtd.infradead.org/doc/ubi.html> UBI Documentation\]

## Discovery (How to find out)

    cat /proc/mtd
    dev:    size   erasesize  name
    mtd0: 00020000 00010000 "u-boot"
    mtd1: 00140000 00010000 "kernel"
    mtd2: 00690000 00010000 "rootfs"
    mtd3: 00530000 00010000 "rootfs_data"
    mtd4: 00010000 00010000 "art"
    mtd5: 007d0000 00010000 "firmware"

The *erasesize* is the [block size](https://en.wikipedia.org/wiki/Block (data storage)) of the flash, in this case 64KiB. The *size* is little or big [endian](https://en.wikipedia.org/wiki/Endianess) hex value in Bytes. In case of little endian, you switch to hex-mode and enter 02 0000 into the calculator for example and convert to decimal (by switching back to decimal mode again). Then guess how they are nested into each other. Or execute `dmesg` after a fresh boot and look for something like:

    Creating 5 MTD partitions on "spi0.0":
    0x000000000000-0x000000020000 : "u-boot"
    0x000000020000-0x000000160000 : "kernel"
    0x000000160000-0x0000007f0000 : "rootfs"
    mtd: partition "rootfs" set to be root filesystem
    mtd: partition "rootfs_data" created automatically, ofs=2C0000, len=530000
    0x0000002c0000-0x0000007f0000 : "rootfs_data"
    0x0000007f0000-0x000000800000 : "art"
    0x000000020000-0x0000007f0000 : "firmware"

These are the start and end offsets of the partitions as hex values in Bytes. Now you don't have to guess which is nested in which. E.g. 02 0000 = 131.072 Bytes = 128KiB.

## Details

### generic

The flash chip can be represented as a large block of continuous space:

|                                               |
|:----------------------------------------------|
| start of flash ................. end of flash |

There is no ROM to boot from; at power up the CPU begins executing the code at the very start of the flash. Luckily this isn't the firmware or we'd be in real danger every time we reflashed. Boot is actually handled by a section of code we tend to refer to as the [bootloader](bootloader) (the BIOS of your PC *is* a bootloader).

|          |                                          |                    |                              |                  |               |
|----------|------------------------------------------|--------------------|------------------------------|------------------|---------------|
|          | Boot Loader Partition                    | Firmware Partition | `Special Configuration Data` |                  |               |
| Atheros  | [U-Boot](/docs/techref/bootloader/uboot) | firmware           | `ART`                        |                  |               |
| Broadcom | CFE                                      | firmware           | `NVRAM`                      |                  |               |
| Atheros  | RedBoot                                  | firmware           | `FIS recovery`               | `RedBoot config` | `boardconfig` |

The partition or partitions containing so called *Special Configuration Data* differ very much from each other. Example: The `ART`-partition you will meet in conjunction with Atheros-Wireless and U-Boot, contains only data regarding the wireless driver, while the `NVRAM`-partition of broadcom devices is used for much more than only that. There are special utilities to access and modify special configuration partitions. For Broadcom devices this is the `nvram` utility. To find out what is written in `NVRAM` you can run `nvram show`.

Note that clearing these special configuration data partitions like `ART, NVRAM` and `FIS` does not clear much of OpenWrt's configuration, unlike other router software which keep configuration data solely in e.g. `NVRAM`. Instead, as a consequence of using the overlay_fs filesystem configuration with JFFS2 flash partition, the whole file system is writable and allows the flexibility of extending your OpenWrt installation in any way you want. OpenWrt's main configuration is therefore just kept in the root file system, using [UCI](/docs/guide-user/base-system/uci) configuration files. For convenience, many other packages are made UCI compatible. If you want to reset your complete installation you should use OpenWrt's built-in functionality such as [sysupgrade](/docs/guide-user/installation/generic.sysupgrade) to restore settings, by clearing the JFFS2 partition. Or, if you cannot boot normally, you can wipe or change the JFFS2 partition using OpenWrt's [failsafe mode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) (look in your device's dedicated page for information how to boot into failsafe).

### broadcom with CFE

If you dig into the "firmware" section you'll find a trx. A trx is just an encapsulation, which looks something like this:

| trx-header |        |       |       |          |      |     |
|------------|--------|-------|-------|----------|------|-----|
| HDR0       | length | crc32 | flags | pointers | data |     |

"HDR0" is a magic value to indicate a trx header, rest is 4 byte unsigned values followed by the actual contents. In short, it's a block of data with a length and a checksum. So, our flash usage actually looks something like this:

|     |                         |       |
|:---:|:-----------------------:|:-----:|
| CFE | trx containing firmware | NVRAM |

Except that the firmware is generally pretty small and doesn't use the entire space between CFE and NVRAM:

|     |              |        |       |
|:---:|:------------:|:------:|:-----:|
| CFE | trx firmware | unused | NVRAM |

(***`NOTE`*:** The \<model\>.bin files are nothing more than the generic \*.trx file with an additional header appended to the start to identify the model. The model information gets verified by the vendor's upgrade utilities and only the remaining data -- the trx -- gets written to the flash. When upgrading from within OpenWrt remember to use the \*.trx file.)

So what exactly is the firmware?

The boot loader really has no concept of filesystems, it pretty much assumes that the start of the trx data section is executable code. So, at the very start of our firmware is the kernel. But just putting a kernel directly onto flash is quite boring and consumes a lot of space, so we compress the kernel with a heavy compression known as [LZMA](https://en.wikipedia.org/wiki/Lempel–Ziv–Markov chain algorithm). Now the start of firmware is code for an LZMA decompress:

|                 |                        |
|:---------------:|:----------------------:|
| lzma decompress | lzma compressed kernel |

Now, the boot loader boots into an LZMA program which decompresses the kernel into RAM and executes it. It adds one second to the bootup time, but it saves a large chunk of flash space. (And if that wasn't amusing enough, it turns out the boot loader does know gzip compression, so we gzip compressed the LZMA decompression program)

Immediately following the kernel is the filesystem. We use SquashFS for this because it's a highly compressed readonly filesystem -- remember that altering the contents of the trx in any way would invalidate the crc, so we put our writable data in a JFFS2 partition, which is outside the trx. This means that our firmware looks like this:

|     |                        |               |                       |
|:---:|:-----------------------|:-------------:|:---------------------:|
| trx | gzip'd lzma decompress | lzma'd kernel | (SquashFS filesystem) |

And the entire flash usage looks like this -

|     |     |           |               |          |                  |       |
|:---:|:---:|:---------:|:-------------:|:--------:|:----------------:|:-----:|
| CFE | trx | gz'd lzma | lzma'd kernel | SquashFS | JFFS2 filesystem | NVRAM |

That's about as tight as we can possibly pack things into flash.

------------------------------------------------------------------------

## Explanations

### What is an Image File?

An image file is byte by byte copy of data contained in a file system. If you installed a Debian or a Windows in the usual way onto one or two hard disk partitions and would afterwards copy the whole content byte by byte from the hard disk into one file:

``` bash
dd if=/dev/sda of=/media/sdb3/backup.dd
```

the obtained backup file `/media/sdb3/backup.dd`, could be used in the exact same manner like an OpenWrt-Image-File.

The difference is, that OpenWrt-Image-File are not created that way ;-) They are being generated with the [Image Generator](/docs/guide-user/additional-software/imagebuilder) (former called Image Builder). Other resources:

- [headers](/docs/techref/headers)
- back to [downloads](/downloads)
- About [Broadcom Firmware Format](http://skaya.enix.org/wiki/FirmwareFormat)

---

# Flash memory

Flash in embedded devices is a really hot topic – there are quite some questions which should be asked before choosing the “right” flash memory type. Often the wrong decision turns out to backfire – I experienced this in several projects and companies.

Questions which should get asked for evaluating possible flash chips and types are:

- How many read/write cycles and for which amount of size the flash needs to last without failure?
- NOR or NAND flash?
- SLC (single cell) or MLC (multi cell) flash?
- What about bad blocks and how to deal with them?
- How much flash space in spare do I need for my project?
- If a filesystem is needed: what kind of filesystem?

Those questions should be dealt with quite carefully when evaluating the right type of flash for a project.

Since to most of the above questions there aren’t really simple answers but implications to each other and of course each solution its very own advantages and disadvantages, I’ll try to illustrate some scenarios instead.

## Erase blocks and erase cycles

Flash storage consists of so-called “erase blocks” (just called blocks from now on). Its size highly depend on the kind of flash (NOR/NAND) and the flash total size.

Usually NOR flash has much greater blocks than NAND flash – typical block sizes are e.g. 64KB for a 4MB NOR flash, 64KB for a 256MB NAND flash, 128KB for a 512MB NAND flash. When flash (especially NAND flash) got bigger and bigger in storage size, pages and later sub-pages got introduced.

NAND flash consists of erase blocks which might consist of pages which might consist of sub-pages.

Though technically erase blocks, pages and sub-pages are not the same, they represent – if existing – the smallest flash I/O unit. Whenever I write about (erase-)blocks on flash and your NAND flash has support for pages (most modern NAND flashes do), just consider mentioned blocks here as pages.

NAND flash also may contain an ‘out of band (OOB) area’ which usually is a fraction of the block size. This is dedicated for meta information (like information about bad blocks, ECC data, erase counters, etc.) and not supposed to be used for your actual data payload. Flash storage needs to be addressed ‘by block’ for writing. Blocks can only be ‘erased’ for certain times, till they get corrupted and unusable (10.000 – 100.000 times are typical values).

Usual conclusion of above is, flash storage can be read but not written byte wise – to write to flash, you need to erase the whole block before. This is not totally wrong, but misleading since simplified. Flash storage cells by default have the state “erased” (which matches the logical bit ’1′). Once a bit got flipped to ’0′ you can only get it back to ’1′ by erasing the entire block.

Even though you can indeed only address the flash “per erase block” for writing – and you have to erase (and therewith write the whole erase block) when intended to flip a bit from ’0′ to ’1′ – that doesn’t mean every write operation needs a prior block erase. Bits can be flipped from ’1′ to ’0′ but only an entire block can be switched (erased) in order to get bits within back to ’1′.

Considering an (in this example unrealistic small) erase block contains ’1111 1110′ and you want to change it to, let’s say, ’1110 1111′, you have to:

1.  erase the whole block, so it will be ’1111 1111′
2.  flip the 4th byte down to ’0′

But if we e.g. want to turn ’1111 1110′ into ’1010 0110′ we just flip the 2nd, 4th and and 5th bit of the block. That way we don’t need to erase the whole block before, because no bit within the block needs to be changed from ’0′ to ’1′. That way, due to clever write handling of the flash, not every write operation within erase blocks imply erasing the block before.

Taking this into account might significantly enhance the lifetime of your flash (especially SLC NAND, MLC requires some even more sophisticated methods), as blocks can only be erased a certain number of times. It might also allow you to take cheaper flash (with less guaranteed erase cycles).

Also you should make sure, that you don’t keep a majority of erase blocks untouched, while others get erased thousands of times. To avoid this, you usually some kind of ‘wear leveling’. That means, you keep track of how many times blocks got erased, and – if possible – relocate data on blocks, which gets changed often, to blocks which didn’t get erased that often. To get wear leveling done properly, you need to have certain amount of blocks in spare to be able to rotate the blocks and relocate the actual data properly.

### Hardware vs. Software

Both techniques can significantly improve the lifetime of your flash, however require quite some sophisticated algorithms to get a reasonable advantage over not using them. Bare flash doesn’t deal with those issues. There is controller hardware taking care of that (e.g. in higher-class memory cards / USB sticks), but it usually sucks. If possible, do it in software. Using e.g. Linux to drive your flash, offers quite some possibilities here (looking at file-systems).

### NAND vs. NOR

NOR blocks compared to those of NAND, in relation to the total storage size of the flash, are quite big – which means:

- bad write performance (several times slower than on NAND flash)
- the very same erase block gets erased far more often and therewith exceed the ‘max. erase cycles’ far easier (in addition: erase cycles are usually about 1000 times less on NOR than on NAND flash)

## Bad blocks

Bad blocks and how they’re dealt with decides whether you can use your flash in the end as normal storage or end up in debugging nightmares, caused by weird device failures which might result of improper bad block handling of your flash.

A bad block is considered an erase block, which shouldn’t be used anymore because it doesn’t always store data as intended due to bit flips. This means, parts of the block can’t be erased (flipped back to ’1′ anymore, parts “float” and can’t be get into a well-defined state anymore, etc.). Blocks only can be erased certain amount of times, until they get corrupted and therewith ‘bad’. Once you encounter a probably bad block, it should be marked as bad immediately and never ever be used again.

Marking a bad block means: Adding this bad block to a table of bad blocks (which is mostly settled at the end of the flash). Since this table sit within blocks on the flash, which might get bad as well, this table is usually redundant.

Bad blocks happen, especially on NAND flash. Even never used NAND flash, right from the factory, might contain bad blocks. Because of that, NAND flash manufacturers ship their flash with “pre-installed” information about which blocks are bad from the beginning. Unfortunately, how this information is stored on the flash, is vendor / product specific. Another common area to store this kind of information is the OOB area (if existing) of the flash.

This also means, flash of the very same vendor and product, will have a different amount of usable blocks. This is a fact you have to deal with – don’t be too tight in your calculation, **you’re going to need space in spare as replacement for bad blocks!**

### Hardware vs. Software

There are actually NAND chips available doing bad block management by their own. Although I never used them myself, what I read it sounds quite nice. Most bare flash however doesn’t deal with bad blocks. There might be pre-installed information about bad blocks from the beginning, there might be not. And if there is, the format is what the vendor chose to be the format. That means, if using a flash controller dealing with bad blocks for you, it needs to be able to read and write the type of format those information are stored in. It needs to be aware about whether the flash has an OOB-areas or not and how they’re organized.

There is quite some sophisticated and flexible flash controller hardware out there, but again: if possible, do it in software. There is quite good and proven code for that available.

### NAND vs. NOR

NOR flash is way more predictable than NAND flash. NAND flash blocks might get bad whenever they want (humidity, temperature, whatever..). Reading NAND flash stresses it as well – **yes, reading NAND flash causes bad blocks!** Although this doesn’t happen as often as due to write operations (and far less on SLC than on MLC flash), it happens and you better deal with it!

The number of expected erase cycles is mentioned in the data-sheets of NAND flashes. The number of read cycles isn’t. However it’s usually something around 10 to 100 times the erase cycles. Imagine you want to boot from your NAND flash, and the boot-loader – which doesn’t deal yet with bad blocks – sits within blocks which react unpredictable / become bad.. a nightmare! That’s why it’s common now, that the first few blocks of NAND flash are guaranteed to be safe for the first N erase cycles. **Make sure your boot-loader fits into those safe blocks!**

## Flash memory lifetime

Conclusion of the above: The flash memory lifetime expectancy depends on many variables, with your usecase probably being the most relevant. The less you use your flash memory, the longer it will last, or even boiled down to: The less you write to your flash, the longer it will last.

See also:

- [Flash memory lifetime](https://forum.openwrt.org/viewtopic.php?id=55982) in the OpenWrt forum

## Innocent mtdblock I/O errors

One may encounter syslog messages that can safely be ignored. These messages are like

    print_req_error: I/O error, dev mtdblock1, sector 0

Explanation: (quoted from [FS#1871, closing comment by Jonas Gorski](https://bugs.openwrt.org/index.php?do=details&task_id=1871))

> The first few blocks of a NAND flash are guaranteed good to ensure that a bootloader stored there can never get corrupted, so it will get written without valid ECC data (the SoC won't check the ECC anyway).

\>

> When block-mount scans all block devices, it will try to read from those blocks, which are exposed as partitions, and the NAND driver will report failed ECC checks (the I/O errors in the log).

\>

> There is nothing wrong here in either way, and nothing we can really do to prevent it.

## NAND memory and bitflips

While reading or writing raw files on NAND flash you might encounter a similar output:

    root@OpenWrt:/# nanddump --file /tmp/mounts/USB-A/home/hh5a.nanddump /dev/mtd4
    ECC failed: 0
    ECC corrected: 0
    Number of bad blocks: 0
    Number of bbt blocks: 4
    Block size 131072, page size 2048, OOB size 64
    Dumping data starting at 0x00000000 and ending at 0x08000000...
    ECC: 1 corrected bitflip(s) at offset 0x01a7e000
    ECC: 1 corrected bitflip(s) at offset 0x01dbf000
    ECC: 1 corrected bitflip(s) at offset 0x01ddc800
    ....

These lines with "ECC: 1 corrected bitflip blablabla" may sound like errors or issues but they are not.

Note how it says “correctED bitflips”, and not “correctABLE bitflips”.

The messages you are seeing there are normal for NAND flash. They mean that the ECC (error detection and correction) logic has detected issues and corrected the data on read using the parity bits.

A “bitflip” error is a situation where a bit changes its state on its own, a 1 becomes a 0 or the reverse. It’s not a bad block (permanent damage), it’s just something that randomly happens in NAND because they are less reliable by design (to keep costs down), and work around this drawback by having ECC logic implemented to correct any bitflip (and this is still cheaper than making them more reliable at the hardware level).

So in a NAND flash device you have some space that is actually storing data, and some space that stores parity information, so the system can use ECC logic and correct bitflips. This is automatic.

The same thing happens inside SSDs, usb flash drives, SD cards and Smartphones (all use NAND flash), you just don’t see this happening it because it’s all handled by the storage controller, while in an embedded device where read/write speed isn’t important (like a router) the flash memory is accessed raw, there is no such controller, so the system itself uses ECC when reading/writing it.

:!: **Note that with the ECC logic implemented (by either a storage controller or the system), the NAND flash is as reliable as you would expect a storage device to be.**

## NAND-specific tools for reading and writing to raw NAND

The ECC logic required by NAND (discussed above) is the main reason you MUST use NAND-aware tools like **nanddump** and **nandwrite** instead of the more common **dd** tool to create or restore a backup of the flash partitions on NAND.

Nanddump reads the NAND with ECC logic, and stores only the actual data (correcting bitflips) in the backup you are creating. Likewise nandwrite writes the image also writing the appropriate parity data for the ECC logic to work when reading it.

The **dd** tool (or more advanced ones like **pv**) is not aware of NAND ECC logic, so it will read all the NAND partition, both data AND parity and will generate a backup that is exactly the same as actually on flash, but is completely useless and unreadable as it will contain both data and hardware-specific parity information which cannot be restored on a different device. Likewise on writing, it will not write parity information for ECC logic to work, so whatever you write will be read as garbage.

Tools like **dd** and **pv** can only be used on block devices. SSDs, SDcards, Hard drives (yes also mechanical hard drives have ECC logic integrated), and so on where any ECC is done by the storage controller, not by the system, so whatever it reads is pure data, no metadata or parity for ECC logic.

---

# TRX vs. TRX2 vs. BIN

[Broadcom Firmware Format](http://skaya.enix.org/wiki/FirmwareFormat)

# The various headers

Some devices have firmware files with different file name endings. While the overall content of the files are identical, there are some slight differences at their beginnings:

## TRX v1

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +---------------------------------------------------------------+
     |                     magic number ('HDR0')                     |
     +---------------------------------------------------------------+
     |                  length (header size + data)                  |
     +---------------+---------------+-------------------------------+
     |                       32-bit CRC value                        |
     +---------------+---------------+-------------------------------+
     |           TRX flags           |          TRX version          |
     +-------------------------------+-------------------------------+
     |                      Partition offset[0]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[1]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[2]                      |
     +---------------------------------------------------------------+

- offset\[0\] = lzma-loader
- offset\[1\] = Linux-Kernel
- offset\[2\] = rootfs

## TRX v2

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +---------------------------------------------------------------+
     |                     magic number ('HDR0')                     |
     +---------------------------------------------------------------+
     |                  length (header size + data)                  |
     +---------------+---------------+-------------------------------+
     |                       32-bit CRC value                        |
     +---------------+---------------+-------------------------------+
     |           TRX flags           |          TRX version          |
     +-------------------------------+-------------------------------+
     |                      Partition offset[0]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[1]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[2]                      |
     +---------------------------------------------------------------+
     |                      Partition offset[3]                      |
     +---------------------------------------------------------------+

- offset\[0\] = lzma-loader
- offset\[1\] = Linux-Kernel
- offset\[2\] = rootfs
- offset\[3\] = bin-Header

Source: [openwrt/tools/firmware-utils/src/trx.c](http://git.openwrt.org/?p=14.07/openwrt.git;a=blob;f=tools/firmware-utils/src/trx.c;h=aa1f5be4b65b66ac9a1a48d7304d9bef131080e1;hb=HEAD#l69)

## BIN-Header

FIXME (which bin header?)

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +---------------------------------------------------------------+
     |                            magic                              |
     +---------------------------------------------------------------+
     |                            res1                               |
     +---------------------------------------------------------------+
     |                fwdate                         |   fwvern...   |
     +---------------------------------------------------------------+
     |    ...fwvern                  |              ID...            |
     +---------------------------------------------------------------+
     |         ...ID                 |  hw_ver       |    s/n        |
     +---------------------------------------------------------------+
     |           flags               |           stable              |
     +---------------------------------------------------------------+
     |           try1                |           try2                |
     +---------------------------------------------------------------+
     |           try3                |           res3                |
     +---------------------------------------------------------------+

- magic: firmware magic depends on board etc. s.th. like '3G2V' or 'W54U'
- res1: reserved for extra magic??
- char fwdate\[3\]: fwdate\[0\]: Year, fwdate\[1\]: Month, fwdate\[2\]: Day
- fwvern: version informations a.b.c.
- ID: fix "U2ND"
- hw_ver: depends on board
- s/n: depends on board
- flags:
- stable: Marks the firmware stable, this is 0xFF in the image and will be written to 0x73 by the running system once it completed booting.
- try1-3: 0xFF in firmware image. CFE will set try1 to 0x74 on first boot and continue with try2 and try3 unless "stable" was written by the running image. After writing try3 and the stable flag was not written yet, the CFE assumes that the image is broken and starts a [TFTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) server
- res3: unused?

## TP-LINK BIN Header

      0   1   2   3   4   5   6   7   8   9   a   b   c   d   e   f
    +---------------------------------------------------------------+
    |    version    |          vendor_name...                       |
    +---------------------------------------------------------------+
    |                       ...vendor_name          | fw_version... |
    +---------------------------------------------------------------+
    |                       ...fw_version...                        |
    +---------------------------------------------------------------+
    |                       ...fw_version                           |
    +---------------------------------------------------------------+
    |     hw_id     |    hw_rev     |     unk1      |    md5sum1... |
    +---------------------------------------------------------------+
    |                         ...md5sum1            |     unk2      |
    +---------------------------------------------------------------+
    |                            md5sum2                            |
    +---------------------------------------------------------------+
    |     unk3      |   kernel_la   |   kernel_ep   |   fw_length   |
    +---------------------------------------------------------------+
    |  kernel_ofs   |   kernel_len  |   rootfs_ofs  |  rootfs_len   |
    +---------------------------------------------------------------+
    |   boot_ofs    |   boot_len    |ver_hi |ver_mid| ver_lo| pad...|
    +---------------------------------------------------------------+
    |                           ...pad...                           |
    +---------------------------------------------------------------+

source: [openwrt/tools/firmware-utils/src/mktplinkfw.c](http://git.openwrt.org/?p=openwrt.git;a=blob;f=tools/firmware-utils/src/mktplinkfw.c;h=a6aab598a1ffa677e64307ee4234479d45de9140;hb=HEAD#l78)

---

# Image formats

 You can help to improve this page by adding explanations for the different firmware types below.

If you are confused by the many different firmware types and extensions in the [OpenWrt firmware downloads](/toh/views/toh_fwdownload) table, this pages tries to explain a bit about this topic.

## Standard formats

### factory (.img/.bin)

Use when flashing from OEM ( non-openwrt ) [^1]

If only a sysupgrade image is available for your router, either the router is already running some kind of OpenWrt fork (which understands the sysupgrade format natively) or web flash via the OEM UI is not possible... Please consult the Table of Hardware for your device for installation instructions from OEM firmware.

### sysupgrade ( or trx )

Previously known as *trx image*, *sysupgrade* is designed to be flashed from OpenWrt/LEDE itself [^2]. Commonly used when upgrading.

## Specific formats

### ext4

This firmware contains a regular ext4 Linux partition. Mostly used in x86 and x86_x64 systems.

### squashfs

This firmware contains a type of partition that is compressed and mounts read-only. All modifications (file edit, new files, deleted files) are committed to an overlay. .bin/.chk/.trx

- See also [TRX vs. TRX2 vs. BIN](/docs/techref/headers)

### initramfs

Can be loaded from an arbitrary location ( most often tftp ) and is self-contained in memory. This is like a Linux LiveCD. Often used to test firmware, as the first part of a multi-stage installation or as a recovery tool. [^3]

An initramfs and initrd are basically the same. It’s a filesystem in memory, which contains userland software. In an embedded environment it might contain the whole distro, on bigger systems it can contain tools&scripts to assemble&mount raid arrays and stuff like that before passing userland boot to them. Both can have a uHeader, to let uBoot know what it is.

The initramfs-kernel image is used for development or special situations as a one-time boot as a stepping stone toward installing the regular sysupgrade version. Since the initramfs version runs entirely from RAM, it does not store any settings in flash, so it is not suitable for operational use.

initramfs-uImage.bin: initramfs-kernel.bin:

### sdcard.img.gz

Used by few devices ( mvebu/RPi etc. ), most often a multi partition image which is uncompressed and written to external storage via PC.

### rootfs

Only the root filesystem.

### kernel

Linux core, generally without compression or appended headers.

### ubifs

??

### ubi

??

### tftp

Designed to be loaded from tftp server. Device in recovery mode?

### u-boot

This is an image format designed for U-Boot loader. Same as initramfs-or-uImage?

### ubinized.bin

### uImage

This is an image format designed for U-Boot loader, generally consisting of a kernel with a header for information. Often a zImage with a 64 byte uImage header, which contains the load address & entry point of the zImage, so that uBoot knows what to do with it. Further is contains a description of the actual contents (linux kernel, version, …)

### zImage

zImage is a compressed plain kernel with a ‘pyggyback’. Some extra code which can decompress the kernel before booting it.

## Subformats

### bin, img, elf, dtb, chk, dlf

These are raw binary data of the firmware file

### xz, gz, tar, lzma

These are compressed images

## Developer files

### sdk

SDK Toolchain for compiling single userspace packages [^4]

### Imagebuilder

To build custom images without compiling [^5]

### vmlinux

Linux kernel for build [^6]

# Example Firmware image names

## Firmware types

| Target | Install | Upgrade |
| --- | --- | --- |
| adm5120 | squashfs.bin | squashfs.bin |
| apm821xx | squashfs-factory.img; initramfs-kernel.bin | squashfs-sysupgrade.tar; ext4-rootfs.img.gz |
| ar7 | squashfs.bin; squashfs-code.bin | squashfs.bin |
| ar71xx | factory.img; factory.bin | sysupgrade.bin |
| at91 |   |   |
| atheros | squashfs-factory.bin | squashfs-sysupgrade.tar |
| brcm2708 | ext4-sdcard.img.gz | - |
| brcm47xx | squashfs.bin; squashfs.chk; squashfs.trx | squashfs.bin; squashfs.chk; squashfs.trx |
| bcm53xx | squashfs.bin; squashfs.chk; squashfs.trx | squashfs.chk; squashfs.trx |
| brcm63xx | squashfs-cfe.bin; squashfs-factory.chk | squashfs-sysupgrade.bin |
| cns3xxx | - | sysupgrade.bin |
| imx6 | ? | ? |
| ipq806x | factory.img | sysupgrade.tar |
| ixp4xx | squashfs.bin; squashfs.img; zImage | squashfs-sysupgrade.bin |
| kirkwood | squashfs-factory.bin | squashfs-sysupgrade.bin |
| lantiq | initramfs-kernel.bin; squashfs-factory.bin | squashfs-sysupgrade.bin |
| layerscape | squashfs-firmware.bin | - |
| mpc85xx | squashfs-factory.bin | squashfs-sysupgrade.bin |
| mvebu | sdcard.img.gz; squashfs-factory.img | squashfs-sysupgrade.bin |
| mxs | ? | ? |
| orion | not supported | not supported |
| oxnas | squashfs-ubinized.bin; ubifs-ubinized.bin | squashfs-sysupgrade.tar; ubifs-sysupgrade.tar |
| ramips | initramfs-kernel.bin; squashfs-factory.bin; squashfs-factory.dlf; initramfs-uImage.bin | squashfs-sysupgrade.bin; squashfs-sysupgrade.tar |
| sunxi | ext4-sdcard.img.gz; squashfs-sdcard.img.gz |   |
| x86 | combined-ext4.img | combined-ext4.img.gz |

# Image Formats General

This article describes and links to the various factory firmware image formats found.

For OpenWrt Flash Layout see: [flash.layout](/docs/techref/flash.layout).

[Binwalk](https://github.com/ReFirmLabs/binwalk) can help to analyze unknown formats.

## Known Formats

by extension:

- BIN
- CHK
- DLF
- IMG
- TRX

## Other Formats

- see [brcm63xx.imagetag](/docs/techref/brcm63xx.imagetag)
- see [headers](/docs/techref/headers)

[^1]: [before.installation](/docs/guide-user/installation/before.installation)

[^2]: [before.installation](/docs/guide-user/installation/before.installation)

[^3]: <https://forum.lede-project.org/t/toward-a-good-flashing-lede-instructions-page/52/5>

[^4]: <https://we.riseup.net/lackof/openwrt-on-x86-64>

[^5]: <https://we.riseup.net/lackof/openwrt-on-x86-64>

[^6]: <https://we.riseup.net/lackof/openwrt-on-x86-64>

---

# image/Makefile Details

![wip&noheader&nofooter&noeditbtn](/page>meta/infobox/wip&noheader&nofooter&noeditbtn)

- I think its(this page) needed to clarify the intent, preferred style and function of the image/Makefile.
- I believe one of the following should be placed here:
  - Adding a new platform (new buildroot howto section?)
  - OpenWrt Buildroot - new platform (new page/how-to on adding platform support to the buildroot system)

## image/Makefile from scratch or modify

Inside your platform directory you will need to create a file to tell the buildroot system how to process the results of a compiled kernel. Most of the work is done automatically by [image.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md) but different platforms and individual devices will need specific work for images to be useful.

## Basic Function

See example.

### Image/Prepare

Can be used to append data to image but often used simply to move to another directory such as \$(KDIR)

Example:

    cat $(LINUX_DIR)/arch/arm/boot/[zImage](../wiki/chunked-reference/wiki_page-techref-image-format.md) >> $(KDIR)/$(call zimage_name,$(1))

### Image/Build/Initramfs

This section allows automated modification of the elf file before loading onto the device. The file can be found with this line

    $(BIN_DIR)/$(IMG_PREFIX)-vmlinux.elf

### Image/Build/jffs2-64k

### Image/Build/jffs2-128k

### Image/Build/squashfs

### Image/Build

Appears to be used to call the other build defines (squashfs, jffs2-64k, jffs2-128k, etc) after they were processed and their resulting files were placed into \$(TARGET_DIR)

to call a define for each use:

    $(call Image/Build/$(1),$(1))

## Example

Example of: **trunk/target/linux*/platform*/image/Makefile**

``` make
#
# Copyright (C) 2010 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#
include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/image.mk

define Image/Prepare

endef

define Image/Build/Initramfs
    $(BIN_DIR)/$(IMG_PREFIX)-vmlinux.elf
endef

define Image/BuildKernel

endef

define Image/Build/jffs2-64k
    dd if=$(KDIR)/root.$(1) of=$(BIN_DIR)/openwrt-$(BOARD)-$(1).img bs=65536 conv=sync
endef

define Image/Build/jffs2-128k
    dd if=$(KDIR)/root.$(1) of=$(BIN_DIR)/openwrt-$(BOARD)-$(1).img bs=131072 conv=sync
endef

define Image/Build/squashfs
    $(call prepare_generic_squashfs,$(KDIR)/root.squashfs)
endef

define Image/Build
    $(call Image/Build/$(1),$(1))
endef
```

## See also

have a look at your copy of **trunk/include/[image.mk](../openwrt-core/chunked-reference/makefile_meta-include-mk.md)**

# Platform/Device configuration files

## config-4.x

Kernel options required by the platform + kernel version.

``` make
CONFIG_QCOM_PM=y
CONFIG_QCOM_QFPROM=y
CONFIG_QCOM_RPMCC=y
```

## files-4.x

Kernel specific device source. Primarily the location of device DTS files. You will need to add a new device dts here and reference in image/Makefile under DEVICE_DTS.

## patches-4.x

Kernel source additions. No changes for basic device additions.

## Makefile

Platform wide device definition and common package set. Generally does not require modification when adding additional platform devices.

``` make
include $(TOPDIR)/rules.mk

ARCH:=arm
BOARD:=ipq806x
BOARDNAME:=Qualcomm Atheros IPQ806X
FEATURES:=squashfs nand fpu ramdisk
CPU_TYPE:=cortex-a15
CPU_SUBTYPE:=neon-vfpv4
MAINTAINER:=John Crispin <john@phrozen.org>

KERNEL_PATCHVER:=4.14

KERNELNAME:=zImage Image dtbs

include $(INCLUDE_DIR)/target.mk
DEFAULT_PACKAGES += \
    kmod-leds-gpio kmod-gpio-button-hotplug swconfig \
    kmod-ata-core kmod-ata-ahci kmod-ata-ahci-platform \
    kmod-usb-core kmod-usb-ohci kmod-usb2 kmod-usb-ledtrig-usbport \
    kmod-usb3 kmod-usb-dwc3-of-simple kmod-usb-phy-qcom-dwc3 \
    kmod-ath10k-ct wpad-basic \
    uboot-envtools

$(eval $(call BuildTarget))
```

## image/Makefile

Device specific image creation parameters and image generation functions.

``` make
define Device/zyxel_nbg6817
    DEVICE_DTS := qcom-ipq8065-nbg6817
    KERNEL_SIZE := 4096k
    BLOCKSIZE := 64k
    BOARD_NAME := nbg6817
    RAS_BOARD := NBG6817
    RAS_ROOTFS_SIZE := 20934k
    RAS_VERSION := "V1.99(OWRT.9999)C0"
    SUPPORTED_DEVICES += nbg6817
    DEVICE_VENDOR := ZyXEL
    DEVICE_MODEL := NBG6817
    DEVICE_PACKAGES := ath10k-firmware-qca9984-ct e2fsprogs kmod-fs-ext4 losetup
    $(call Device/ZyXELImage)
endef
TARGET_DEVICES += zyxel_nbg6817
```

## base-files

Initialization scripts. Instantiation of LED, wifi and upgrade/install routines. etc. Many changes needed to add new device.

## profiles/00-default.mk

Board core firmware.

---

# Init (User space boot) reference for Chaos Calmer: procd

Analysis of how the user space part of the boot sequence is implemented in OpenWrt, Chaos Calmer release.

## Procd replaces init

On a fully booted Chaos Calmer system, pid 1 is `/sbin/procd`:

    root@openwrt:~# ps
      PID USER       VSZ STAT COMMAND
        1 root      1440 S    /sbin/procd
        ...

At boot, Linux kernel starts `/sbin/init` as the first user process. In Chaos Calmer, `/sbin/init` does the preinit/failsafe steps, those that depend only on the read-only partition in flashed image, then execs (that is: is replaced by) `/sbin/procd` to continue boot as specified by the configuration in writable flash partition. Procd started as pid 1 assumes several roles: service manager, hotplug events handler; this as of February 2016, when this research was done. [Procd techref wiki page](/docs/techref/procd) at this point in time is a design document and work in progress, if you are reading here and know/understand procd's semantics and API, please update that page.

Procd sources:
<http://git.openwrt.org/?p=project/procd.git;a=tree;hb=0da5bf2ff222d1a499172a6e09507388676b5a08>
at the commit used to build the procd package in Chaos Calmer release:
`PKG_SOURCE_VERSION:=0da5bf2ff222d1a499172a6e09507388676b5a08`

`/sbin/init` source:
<http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/init.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l71>

## Life and death of a Chaos Calmer system

This is the source code path followed in logical order of execution by the processor in user space while booting Chaos Calmer.

:!: All links to source repositories should show the code at the commit used in Chaos Calmer release.
:!: Pathnames evaluated at preinit time when / is read only have "(/rom)" prepended, to signify the path where the file is found on a fully booted system.

1.  `main(int argc, char **argv)` in /sbin/init, line 71
    User space life begins here. OpenWrt calls this phase "preinit".
    1.  `early()` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/early.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l92)
        Mount filesystems: `/proc`, `/sys`, `/sys/fs/cgroup`, `/dev` (a tmpfs), `/dev/pts`
        Populate `/dev` with entries from `/sys/dev/{char;block}`
        Open `/dev/console` as STDIN/STDOUT/STDERR
        Make directories `/tmp` (optionally on zram), `/tmp/run`, `tmp/lock`, `/tmp/state`

        This accounts for most of the filesystem layout, observed that `/etc/fstab` is a [broken symlink, line 161](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/Makefile;hb=483dac821788b457d349233e770329186a0aa860#l161), with the following additions:
        - `procd_coldplug()` [invoked at hotplug setup time](http://git.openwrt.org/?p=project/procd.git;a=blob;f=state.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l105) will recreate `/dev` from scratch.
        - `/etc/rc.d/S10boot` will invoke `mount_root` to setup a writable filesystem based on extroot or jffs2 overlay or a tmpfs backed [snapshot capable](/docs/guide-user/installation/snapshot) overlay, add some directories and files, and mount debugfs.
    2.  `cmdline()` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/init.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l56)
        Check kernel cmdline for boot parameter "`init_debug={1,2,3,4}`".
    3.  Fork `/sbin/kmodloader (/rom)/etc/modules-boot.d/` [kmodloader source](http://git.openwrt.org/?p=project/ubox.git;a=blob;f=kmodloader.c;hb=907d046c8929fb74e5a3502a9498198695e62ad8#l830)
        Wait up to 120 seconds for `/sbin/kmodloader` to probe the kernel modules declared in `(/rom)/etc/modules-boot.d/`
        At this point in the boot sequence, '/etc/modules-boot.d' is the one from the rom image (`/rom/etc/...` when boot is done). The overlay filesystem is mounted later.

        kmodloader is a multicall binary, invoked as
        '' kmodloader` does ` [main_loader()](http://git.openwrt.org/?p=project/ubox.git;a=blob;f=kmodloader.c;hb=907d046c8929fb74e5a3502a9498198695e62ad8#l732)''
        which reads files in `(/rom)/etc/modules-boot.d/`, looking for lines starting with the name of a module to load, optionally followed by a space and module parameters. There appear to be [special treatment for files with names beginning with a number](http://git.openwrt.org/?p=project/ubox.git;a=blob;f=kmodloader.c;hb=907d046c8929fb74e5a3502a9498198695e62ad8#l788): the modules they list are immediately loaded, then modules from files with name beginning with an ascii char greater than "9" are loaded all together in a final load_modprobe call.
    4.  `uloop_init()` line 116 [(definition)](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l211)
        [Documentation of libubox/uloop.h](/docs/techref/libubox#libuboxulooph) says:
        *Uloop is a loop runner for i/o. Gets in charge of polling the different file descriptors you have added to it, gets in charge of running timers, and helps you manage child processes. Supports epoll and kqueue as event running backends.*
        [uloop.c source in libubox](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l666) says uloop's process management duty is assigned by a call to
        '' [int uloop_process_add(struct uloop_process \*p)](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l492)` `p-\>pid'' is the process id of a child process to monitor and `p->cb` a pointer to a callback function.
        When the managed child process will exit, uloop_run, running in parent context to receive SIGCHLD signal, will trigger execution of the callback.
    5.  `preinit()` line 117 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l86)
        1.  [Forks a "plugd instance"](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l94), line 94
            '' /sbin/procd -h [(/rom)/etc/hotplug-preinit.json](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/system/procd/files/hotplug-preinit.json;hb=483dac821788b457d349233e770329186a0aa860)''
            to listen to kernel uevents for any required firmware or for notification of button pressed, handled by '' [(/rom)/etc/rc.button/failsafe](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/files/etc/rc.button/failsafe;hb=483dac821788b457d349233e770329186a0aa860)''
            as the request to enter failsafe mode. A flag file `/tmp/failsafe_button` containing the value of `${BUTTON}` is created if failsafe has been requested.
        2.  Forks, [at lines 106-111](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l106),
            '' PREINIT=1 /bin/sh [(/rom)/etc/preinit](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/files/etc/preinit;hb=483dac821788b457d349233e770329186a0aa860)''
            a shell to execute `(/rom)/etc/preinit` with `PREINIT=1` in its environment. Submits the child process to uloop management with the callback
            '' [spawn_procd()](http://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l51)''
            that will exec procd to replace init as pid 1 at completion of `(/rom)/etc/preinit`.
            1.  `/etc/preinit`
                A shell script, fully documented here [preinit_mount#preinit_operation](/docs/techref/preinit_mount#preinit_operation). In short, parse files in `(/rom)/lib/preinit` to build 5 lists of hooks and an environment, then run the hooks from some of the lists depending on the state of the environment.
                One of the steps in a successful boot sequence is to mount the overlay file system with a hook setup by
                '' [(/rom)/lib/preinit/80_mount_root](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/base-files/files/lib/preinit/80_mount_root;hb=483dac821788b457d349233e770329186a0aa860)` to call ` [mount_root](http://git.openwrt.org/?p=project/fstools.git;a=blob;f=mount_root.c;hb=09027fc86babc3986027a0e677aca1b6999a9e14)''
                which if extroot is not configured, mounts the writable data partition "rootfs_data" as overlay over the / partition "rootfs". If the data partition is being prepared, overlays a tmpfs in ram.
                Filesystem snapshots are supported; this is a feature listed in Barrier Breaker announce, shell wrapper is `/sbin/snapshot` script. The "`SNAPSHOT=magic`" environment variable is set in `mount_snapshot()` line 330.
    6.  `uloop_run()`, line 118
        At exit of the `(/rom)/etc/preinit` shell script, invokes the callback spawn_procd()
    7.  `spawn_procd()`
        As a callback by uloop_run in pid 1, this is pid 1; execs `/sbin/procd`

2.  `/sbin/procd`
    Execed by pid 1 `/sbin/init`, `/sbin/procd` replaces it as pid 1.
    1.  `setsid()`, line 67
        *The process group ID and session ID of the calling process are set to the PID of the calling process: [man 2 setsid](http://man7.org/linux/man-pages/man2/setsid.2.html)* See also [man 7 credentials](http://man7.org/linux/man-pages/man7/credentials.7.html).
    2.  `uloop_init()`, line 68
        The uloop instance set up before by `/sbin/init` is gone. Creates a new one.
    3.  `procd_signal()`, line 69 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=signal.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l82), line 82.
        Setup signal handlers. Reboot on SIGTERM or SIGINT, poweroff on SIGUSR2 or SIGUSR2.
    4.  `trigger_init()`, line 70 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=service/trigger.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l319)
        Procd triggers on config file/network interface changes, see [procd-init-scripts#procd_triggers_on_config_filenetwork_interface_changes](/docs/guide-developer/procd-init-scripts#procd_triggers_on_config_filenetwork_interface_changes)
        Initialise a run queue. An [example](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=examples/runqueue-example.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8) is the sole documentation. A queued task has an uloop callback invoked when done, here sets the empty queue callback to do nothing.
    5.  `procd_state_next()`, line 74 [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=state.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l179)
        Transitions from NONE to EARLY the state of a state machine implemented in `state_enter(void)` used to sequence the remaining boot steps.
    6.  `STATE_EARLY` in `state_enter()`
        1.  Emits "- early -" to syslog,
        2.  Initialise the watchdog,
        3.  `hotplug("/etc/hotplug.json")` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/hotplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l568)
            User space device hotplugging handler setup.
            Static variables in file scope are important. The filename of the script to execute is kept in hotplug.c global scope: `static char * rule_file;`.
            Opens a netlink socket ([man 7 netlink](http://man7.org/linux/man-pages/man7/netlink.7.html)) and handles the file descriptor to uloop, to listen to uevents: kernel messages informing **u**serspace of kernel **events**. See <https://www.kernel.org/doc/pending/hotplug.txt>
            The uloop instance in pid 1 [uses epoll_wait](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=uloop.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8#l259) to monitor file descriptors, the kernel netlink socket FD is one of them, and is instructed to invoke the callback `hotplug_handler()` on uevent arrival.
            This `hotplug_handler` callback stays active after coldplug, and will handle all uevents the kernel will emit.
        4.  `procd_coldplug()` [(definition)](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/coldplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l40)
            Umounts `/dev/pts` and `/dev`, mounts a tmpfs on `/dev`, creates directories `/dev/shm` and `/dev/pts`, forks `udevtrigger` to reconstruct kernel uevents went unheard before netlink socket opening ("coldplug").
            1.  `udevtrigger`
                Scans `/sys/bus/*/devices`, `/sys/class`; and `/sys/block` if it isn't a subdir of `/sys/class`, writing "add" to the uevent file of all devices. Then the kernel synthesizes an "add" uevent message on netlink. See Injecting events into hotplug via "uevent" in <https://www.kernel.org/doc/pending/hotplug.txt>

                A callback chain, `udevtrigger_complete()` followed by `coldplug_complete()` is attached to completion of the child udevtrigger process, such that the still to be reached `uloop_run()` in procd `main()` function, after all uevents will have been processed, will advance procd state to STATE_UBUS, [line 31](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/coldplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l31).
    7.  `uloop_run`, line 75
        Solicited by udevtrigger in another process, the kernel emits uevents and uloop invokes the user space hotplug handler: the callback
        1.  `hotplug_handler`
            to run `/etc/hotplug.json`.
            1.  The `/etc/hotplug.json` script
                - creates and removes devices files, assigns them permissions,
                - loads firmware,
                - handles buttons by calling scripts in `/etc/rc.button/%BUTTON%` if the uevent has the "`BUTTON`" value,
                - and invokes `/sbin/hotplug-call "%SUBSYSTEM%"` to handle all other subsystem related actions.
                Subystems are: "platform" "net", "input", "usb", "usbmisc", "ieee1394", "block", "atm", "zaptel", "tty", "button" (without BUTTON value, possible?), "usb-serial". "usb-serial" is aliased to "tty" in hotplug.json.
                Documentation of json script syntax? Offline. [Use the source](http://git.openwrt.org/?p=project/libubox.git;a=blob;f=json_script.c;hb=d1c66ef1131d14f0ed197b368d03f71b964e45f8). It is the json representation of the abstract syntax tree of a script in a fairly intuitive scripting language.
                There are 2 levels at which decisions are taken: hotplug.json acts as fast path executor or lightweight dispatcher, the subsystem scripts in /etc/hotplug.d/%SUBSYSTEM%/ do the heavy lifting.
                Uevent messages from the kernel contain key-value pairs passed as environment variables to the scripts. The kernel function
                '' [int add_uevent_var(struct kobj_uevent_env \*env, const char \*format, ...)](http://lxr.free-electrons.com/source/lib/kobject_uevent.c?v=3.18#L387)''
                creates them. This link <http://lxr.free-electrons.com/ident?v=3.18;i=add_uevent_var> provides a list of all places in the Linux kernel where it is used. It is an authoritative reference of the upstream defined uevent variables. Button events are generated by the out of tree kernel modules `button-hotplug` `gpio-button-hotplug` specific to OpenWrt.
                1.  `/sbin/hotplug-call "%SUBSYSTEM%"`
                    is a shell script that scans `/etc/hotlug.d/%SUBSYSTEM%/*` and sources all scripts assigned to a subsystem. "button" subsystem is handled here if the uevent lacks the "BUTTON" value, unlikely or impossible?.
        2.  `STATE_UBUS`
            At end of coldplug uevents processing, the callback [coldplug_complete calls](http://git.openwrt.org/?p=project/procd.git;a=blob;f=plug/coldplug.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l34) `procd_state_next` which results in advancing procd to STATE_UBUS.
            "- ubus -" is logged to console, the services infrastructure is initialised, then procd schedules connect to after 1" ([line 67](http://git.openwrt.org/?p=project/procd.git;a=blob;f=ubus.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l64)) and starts `/sbin/ubus` as the system [ubus](/docs/techref/ubus) service.
            Transition to next state is triggered by the callback `ubus_connect_cb` that at the end, line 118, calls `procd_state_ubus_connect()`, line 186, that calls `procd_state_next` to transition to
        3.  `STATE_INIT`
            "- init -" is logged, `/etc/inittab` is parsed and entries
            '' ::askconsole:/bin/ash --login` ` ::sysinit:/etc/init.d/rcS S boot` executed. inittab format is the same as the one from busybox (Busybox example inittab). The "`sysinit'' action" handler
            1.  `runrc`
                instantiates a queue, whose empty handler `rcdone` will advance procd state.
                `runrc` [ignores](http://git.openwrt.org/?p=project/procd.git;a=blob;f=inittab.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l151) the process specification "`/etc/init.d/rcS`" (there is no such a script!), and runs
                1.  `rcS(pattern="S" , param="boot", rcdone)` (line 159)
                    that invokes the equivalent of
                    `_rc(&q, *path="/etc/rc.d", *file="S", *pattern="*", *param="boot")`
                    to enqueue in glob sort order the scripts
                    '' /etc/rc.d/S\* boot` with "`boot''" as the action. `/etc/rc.d/S*` are [symlinks made by rc.common enable](http://git.openwrt.org/?p=15.05/openwrt.git;a=blob;f=package/Makefile;hb=483dac821788b457d349233e770329186a0aa860#l117) to files in `/etc/init.d`, that are shell scripts with the shebang `#!/bin/sh /etc/rc.common`.
                    Invoking a `/etc/rc.d/S*` script runs `rc.common` that sources the /etc/rc.d/S\* script to set up a context, then invokes the function named as the action parameter ("`boot()`"), in that context.
        4.  `STATE_RUNNING`
            Execution arrives here after rcS scripts are done.
            "- init complete -" is logged.
            This is a stable state, keeping uloop_run in procd.c main() running, mostly waiting on epoll_wait. [Upon receipt of a signal](http://git.openwrt.org/?p=project/procd.git;a=blob;f=signal.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l33) in SIGTERM, SIGINT (reboot), or SIGUSR2, SIGUSR2 (poweroff), procd transitions to
        5.  `STATE_SHUTDOWN`
            "- shutdown -" is logged, /etc/inittab shutdown entry is executed, and procd sleeps [at line 169](http://git.openwrt.org/?p=project/procd.git;a=blob;f=state.c;hb=0da5bf2ff222d1a499172a6e09507388676b5a08#l169) while the kernel does poweroff or reboot.
    8.  `uloop_done`
        `return 0`
        lines 75 & 76 are never reached by pid 1, kernel would panic if init exited.

---

# Init Scripts

|FIXME This **mostly** applies to traditional SysV-style initscripts, See [[docs:guide-developer:procd-init-scripts]] as well for procd-style initscripts|

[[wp>Init]] scripts configure the [[wp>Daemon_(computing)|daemons]] of the Linux system. Init scripts are run to start required processes as part of the [[docs:techref:process.boot|boot process]]. In OpenWrt init is implemented with init.d. The init process that calls the scripts at boot time is provided by [[docs:techref:process.boot#busybox_init|Busybox]]. This article explains how init.d scripts work and how to create them. Note that this is mostly equivalent to other init.d implementations and in-depth documentation can be found elsewhere. You could also take a look at the set of [[commit>?p=openwrt/openwrt.git;a=blob;f=package/base-files/files/etc/rc.common;hb=HEAD|shell functions in /etc/rc.common]] to see how the building blocks of the init scripts are implemented.
## Example Init Script
Init scripts are explained best by example. Suppose we have a daemon we want to handle by init.d. We create a file ''/etc/init.d/example'', which as a bare minimum looks as follows:
^ Code ^
|```#!/bin/sh /etc/rc.common
# Example script
# Copyright (C) 2007 OpenWrt.org

START=10
STOP=15

start() {
        echo start
        # commands to launch application
}

stop() {
        echo stop
        # commands to kill application
}```|
This init script is just a shell script. The first line is a [[wp>Shebang_(Unix)|shebang line]] that uses ''[[docs:guide-user:base-system:notuci.config#etcrc.common|/etc/rc.common]]'' as a wrapper to provide its main and default functionality and to check the script prior to execution.

:!: Look inside ''[[commit>?p=openwrt/openwrt.git;a=blob;f=package/base-files/files/etc/rc.common;hb=HEAD|rc.common]]'' to understand its functionality.

By this ''rc.common'' template, the available commands for an init scripts are as follows:

        start   Start the service
        stop    Stop the service
        restart Restart the service
        reload  Reload configuration files (or restart if that fails)
        enable  Enable service autostart
        disable Disable service autostart

All these arguments can be passed to the script when run. For example, to restart the service call it with ''restart'':
^ Shell Output ^
|```root@OpenWrt:/# /etc/init.d/example restart```|

The script's necessary ''start()'' and ''stop()'' functions determine the core steps necessary to start and stop this service.
  * **start()** - these commands will be run when it is called with 'start' as its parameter.
  * **stop()** - these commands will be run when it is called with 'stop' as its parameter.

The ''START='' and ''STOP='' lines determine at which point in the [[docs:techref:process.boot#init|init sequence]] this script gets executed. At boot time ''init.d'' just starts executing scripts it finds in ''/etc/rc.d'' according to their file names. The init scripts can be placed here as symbolic links to the ''init.d'' scripts in ''/etc/init.d/''. Using [[#enable_and_disable|the enable and disable commands]] this is done automatically. In this case:
  * ''**START=10**'' - this means the file will be symlinked as /etc/rc.d/S10example - in other words, it will start after the init scripts with START=9 and below, but before START=11 and above.
  * ''**STOP=15**'' - this means the file will be symlinked as /etc/rc.d/K15example - this means it will be stopped after the init scripts with STOP=14 and below, but before STOP=16 and above. This is optional.

:!: If multiple init scripts have the same start value, the call order is determined by the alphabetical order of the init script's names.

:!: Don't forget to make sure the script has execution permission, by running ''chmod +x /etc/init.d/example''.

:!: START and STOP values should fall in the range 1-99 as they are run alphabetically meaning 100 would execute after 10.

:!: OpenWrt will run the initscript **in the host system during build** (currently using actions "enable" or "disable"), and it must correctly deal with that special case without undue side-effects. Refer to the "enable and disable" section below for more on this pitfall.

### Other functions

The ''rc.common'' script defines other functions that you can override if you need to, eg:

  * ''boot()'' - called once each time the system starts up. By default this function calls ''start $@'', so if your service has a "one-off" component (eg. turn on some hardware) and an ongoing component (eg. use the hardware), you will almost certainly want to call ''start "$@"'' at the end of your own ''boot()'' function too. If there is no ongoing component, you can leave it out.
  * ''shutdown()'' - called once each time the system is shut down (whether for reboot or poweroff). Like the ''boot()'' function, this function calls ''stop'' by default (note no arguments), so if your service has an ongoing component like above, and a one-off shutdown command (eg. turn off some hardware), you will want to call ''stop'' first, and then your one-off command.

These functions can be called by procd init scripts too.

For example:

^ Code ^
|```
boot() {
  echo "Turning on extra comms device"
  # This is a made up command to illustrate the point
  comms2_power --on
  start "$@"
}

start() {
  # Service that uses the device we turned on in boot()
  my_service
}

shutdown() {
  # The service is finished, so turn off the hardware
  stop
  echo "Turning off extra comms device"
  comms2_power --off
}
```|

### Custom commands

You can add your own custom commands by using the EXTRA_COMMANDS variable, and provide help for those commands with the EXTRA_HELP variable, then adding sections for each of your custom commands:

^ Code ^
|```EXTRA_COMMANDS="custom"
EXTRA_HELP="        custom  Help for the custom command"

custom() {
        echo "custom command"
        # do your custom stuff
}```|

If you run the script with this code added, with no parameters, this is what you'll see:

^ Shell Output ^
|```root@OpenWrt:/# /etc/init.d/example
Syntax: /etc/init.d/example [command]

Available commands:
        start   Start the service
        stop    Stop the service
        restart Restart the service
        reload  Reload configuration files (or restart if that fails)
        enable  Enable service autostart
        disable Disable service autostart
        custom  Help for the custom command```|

If you have multiple custom commands to add, you can add help text for each of them:

^ Code ^
|```EXTRA_COMMANDS="custom1 custom2 custom3"
EXTRA_HELP=<<EOF
        custom1 Help for the custom1 command
        custom2 Help for the custom2 command
        custom3 Help for the custom3 command
EOF

custom1 () {
        echo "custom1"
        # do the stuff for custom1
}
custom2 () {
        echo "custom2"
        # do the stuff for custom2
}
custom3 () {
        echo "custom3"
        # do the stuff for custom3
}```|\\

## Enable and disable

In order to automatically start the init script on boot, it must be installed into /etc/rc.d/ (see above).  On recent versions of OpenWrt, the build system will attempt to "enable" and/or "disable" initscripts during package install and removal by itself (refer to default_postinst() and default_prerm() in /lib/functions.sh from package base-files -- this thing is utterly undocumented, including how to AVOID the automatic behavior where unwanted), and it will "enable" the initscripts on packages *included* in the ROM images during build, see below.

:!: WARNING :!: OpenWrt initscripts **will be run** while building OpenWrt images (when installing packages in what will become a ROM image) in the **host system** (right now, for actions "//enable//" and "//disable//").  **They must not fail, or have undesired side-effects in that situation.**  When being run by the build system, environment variable **${IPKG_INSTROOT}** will be set to the working directory being used.  On the "target system", that environment variable will be empty/unset.  Refer to "/lib/functions.sh" and also to "/etc/rc.common" in package "base-files" for the nasty details.

Invoke the "enable" command to run the initscript on boot:

^ Shell Output ^
|```root@OpenWrt:/# /etc/init.d/example enable```|

This will create one or more symlinks in ''/etc/rc.d/'' which automatically execute at boot time (see [[docs:techref:process.boot|Boot process]])) and shutdown. This makes the application behave as a system service, by starting when the device boots and stopping at shutdown, as configured in the init.d script.

To disable the script, use the "disable" command:

^ Shell Output ^
|```root@OpenWrt:/# /etc/init.d/example disable```|

which is configured to remove the symlinks again.

The current state can be queried with the "enabled" command:

^ Shell Output ^
|```root@OpenWrt:/# /etc/init.d/example enabled && echo on
on```|

FIXME Many useful daemons are included in the official binaries, but they are not enabled by default. For example, the ''cron'' daemon is not activated by default, thus only editing the ''crontab'' won't do anything. You have to either start the daemon with ''/etc/init.d/cron start'' or enable it with ''/etc/init.d/cron enable''. You can ''disable'', ''stop'' and ''restart'' most of those daemons, too. -- This might not be true anymore!

To query the state of all init scripts, you can use the command below:
^ Shell Output ^
|```for F in /etc/init.d/* ; do $F enabled && echo $F on || echo $F **disabled**; done```|
|```root@OW2:~# for F in /etc/init.d/* ; do $F enabled && echo $F on || echo $F **disabled**; done
/etc/init.d/boot on
/etc/init.d/collectd on
...
/etc/init.d/led on
/etc/init.d/log on
/etc/init.d/luci_statistics on
/etc/init.d/miniupnpd **disabled**
/etc/init.d/network on
/etc/init.d/odhcpd on
...```|

---

# Internal Layout D-Link DIR-825

This article describes the internal layout and configuration of the [D-Link DIR-825](/toh/d-link/dir-825). This particular hardware has two physical network interfaces, `eth0` and `eth1`, whereas most emebedded devices have only one: `eth0`. It also has two two wireless network interfaces using the IEEE 802.11 protocol, represented by `wlan0` and `wlan1`.

![dir-825_hardware_diagram2.gif](/media/dlink/dir-825/dir-825_hardware_diagram2.gif)

| iface | Port                                                     |
|-------|----------------------------------------------------------|
| eth0  | internal interface connected to Gigabit Switch (default) |
| eth1  | internal interface connected to WAN port (default)       |
| wlan0 | radio0                                                   |
| wlan1 | radio1                                                   |
| usb   | Bluetooth/3G/etc.                                        |

Additional information on the rtl8366s switch. Switch 1: rtl8366s(RTL8366S), ports: 6 (cpu @ 5), vlans: 16 (4096 starting with 10.03.1-rc4)

| switch port id | Label on the back |
|:---------------|:------------------|
| port:0         | LAN4              |
| port:1         | LAN3              |
| port:2         | LAN2              |
| port:3         | LAN1              |
| port:4         | WAN               |
| port:5         | internal          |

The default config provided looks something like below:

    config interface loopback
            option ifname   lo
            option proto    static
            option ipaddr   127.0.0.1
            option netmask  255.0.0.0

    config interface lan
            option ifname   eth0
            option type     bridge
            option proto    static
            option ipaddr   192.168.1.1
            option netmask  255.255.255.0

    config interface wan
            option ifname   eth1
            option proto    dhcp

    config switch rtl8366s
            option enable   1
            option reset    1
            option enable_vlan 1

    config switch_vlan
            option device   rtl8366s
            option vlan     0
            option ports    "0 1 2 3 5"

Going through the configuration, step by step, provides the following information.

- First there's the loopback interface `lo`.
- Second, in this configuration, `eth0` is part of the bridged interface `lan`.
- Third, `eth1` is configured as the `wan` interface.
- Fourth, is the switch configuration.
- The 'config switch rtl8366s' options enable the switch, reset it and enable VLAN capability.
- The 'config switch_vlan' options enable VLAN0 and assigns it to the 4 external LAN ports and internal `eth0` interface.

**Note:** The `eth1` network interface is assigned to VLAN1 by default, which in turn is assigned to switch port 4 by default. Further, `eth1` is also configured to be part of the virtual interface `wan`. Configuring `wan` with a static ip address will provide another avenue to access the router using SSH. Finally, either of the wireless interfaces can be configured to enable wifi access as well.

---

# libnl and libnl-tiny – Technical Reference

`libnl` is a library for applications dealing with netlink sockets, for instance to retrieve or change routing information, interface settings, and is used more generally when communicating with the kernel.

## libnl

The upstream version of `libnl` is maintained at <http://www.infradead.org/~tgr/libnl/>

Since `libnl` is somewhat heavyweight, it is not included by default on OpenWRT. If you need only basic netlink functionalities, you may want to use `libnl-tiny` instead. However, some applications require the full features of `libnl`.

Since [r47037](https://dev.openwrt.org/changeset/47037), the `libnl` package has been split into multiple components. The sizes below are approximate sizes after compression, based on the `ar71xx` target with musl:

| Name          | Size | Description                           |
|---------------|------|---------------------------------------|
| `libnl-core`  | 37K  | Common code for all netlink libraries |
| `libnl-genl`  | 8K   | Generic Netlink Library Functions     |
| `libnl-nf`    | 25K  | Netfilter Netlink Library Functions   |
| `libnl-route` | 91K  | Routing Netlink Library Functions     |

For compatibility, a meta-package name `libnl` depends on all the above packages.

## libnl-tiny

The `libnl-tiny` package is a stripped down version of libnl, included by default on OpenWRT.

The code is maintained directly in the OpenWRT code tree, see <http://git.openwrt.org/?p=openwrt.git;a=tree;f=package/libs/libnl-tiny>

| Name         | Size | Description                                                   |
|--------------|------|---------------------------------------------------------------|
| `libnl-tiny` | 14K  | Drop-in replacement for most of `libnl-core` and `libnl-genl` |

`libnl-tiny` replaces the most commonly used parts of `libnl-core` and `libnl-genl`. The API is a bit more limited, but compatible for most applications. The ABI is different, but that doesn't matter much.

Any package that can easily work with `libnl-tiny` instead of `libnl` should be changed to make use of it, since `libnl-tiny` is usually part of the default package set.

However, mixing `libnl`-based libraries with `libnl-tiny` does not work.

---

# libubox

It's one of the core libraries used within openwrt because it's a set of utilities, mostly wrappers, that are present usually in programs and that have been coded in a flexible and reusable way to avoid wasting time.

The library consists mostly on independent functionalities, ones higher level than others.

## libubox/utils.h

Simple utility functions. Endian conversion, bitfield operations, compiler attribute wrapping, sequential memory allocation function (calloc_a), static array size macro, assertion/bug utility function, clock get time wrapper for apple compatibility, base64 encoding decoding.

## libubox/usock.h

This is a really simple library encouraged to be a wrapper to avoid all those socket api library calls. You can create TCP, UDP and UNIX sockets, clients and servers, ipv4/v6 and non/blocking.

The idea is to call usock() and have your fd returned.

## libubox/uloop.h

The most used part. Uloop is a loop runner for i/o. Gets in charge of polling the different file descriptors you have added to it, gets in charge of running timers, and helps you manage child processes. Supports epoll and kqueue as event running backends.

The fd management part is set up with the uloop_fd struct, just adding the fd and the callback function you want called when an event arises. The rest of the structure is for internal use.

The timeout management part is mostly prepared to do simple things. If you want to do something complex, you might want to have a look at libubox/runqueue.h which implements interesting functionality on top of uloop.

Timeout structure should be initialized with just the callback and pending=false (timeout={.cb=cb_func} does the work), and added to uloop using uloop_timeout_set(), do not use the other \_add() function because then you will need to set up the time yourself calling time.h functions. \_set() uses \_add() internally.

TBDN: Process management part

## libubox/blob.h

This part is a helper to pass data in binary. There are several supported datatypes, and it creates blobs that could be sent over any socket, as endianess is taken care in the library itself.

The method is to create a type-value chained data, supporting nested data. This part basically covers putting and getting datatypes. Further functionality is implemented in blobmsg.h

## libubox/blobmsg.h

Blobmsg sits on top of blob.h, providing tables and arrays, providing it's own but parallel datatypes.

## libubox/list.h

Utility to create lists. A way to create lists of structures just by adding struct list_head to your structures. It comes with a lot of iterator macros, with some of them allowing deletion on iteration (the ones ending in \_safe). It also has some list operations like slicing, moving, and inserting in different points. It is a double linked list implementation (just in case). Uses the same API as the one present in the linux kernel.

## libubox/safe-list.h

Uses list.h to provide protection against recursive iteration with deletes.

## libubox/kvlist.h

Key value lists, allowing duplicate elements. Keys are meant to be strings, values can be any datatype, the user has to provide a data measuring function though. If you are using strings or blobs (from blob.h), there are two measuring functions already, kvlist_strlen and kvlist_blob_len respectively.

kvlist.h implementation uses avl.h.

- [Project's git](http://git.openwrt.org/?p=project/libubox.git;a=summary)

---

# lldpd

See also: [lldpd upstream documentation](https://github.com/lldpd/lldpd/blob/master/README.md)

The goal of LLDP is to provide an inter-vendor compatible mechanism to deliver Link-Layer notifications to adjacent network devices.

## Abstract

An implementation of IEEE 802.1ab

lldpd (Link Layer Discovery Protocol daemon) daemon providing an industry standard protocol designed to supplant proprietary Link-Layer protocols such as Extreme's EDP (Extreme Discovery Protocol) and CDP (Cisco Discovery Protocol).

# Installation & Configuration

## Installation

OpenWRT uses the standard, lightweight lldpd package. Drop into your ER-X via SSH:

``` bash
opkg update
opkg install lldpd
```

## Configuration

LLDP frames are link-local frames, do not use any network interfaces other than the ones that achieve a link with its link partner, and the link partner being another networking device. Do not use bridge,VLAN, or DSA conduit interfaces.

Example `/etc/config/lldpd`, start lldpd on all interfaces:

``` bash
config lldpd config
       # lldp defaults to listening on all interfaces
       # Set class of device
       option lldp_class 4
       # if empty, the distribution description is sent
       option lldp_description "OpenWrt System"
```

## Usage

*daemon must be running for lldpcli to work*

View neighbors across each enabled interface.

``` bash
lldpcli show neighbors
```

Get statistics about which interfaces are sending/receiving LLDP frames:

``` bash
lldpcli show statistics
```

## Known Issues

\- lldpd unable to receive frames on mediatek due to bug: <https://github.com/openwrt/openwrt/issues/13788>

---

# LuCI – Technical Reference

- See also the [LuCI Essentials](/docs/guide-user/luci/luci.essentials) page
- [LuCI Wiki](https://github.com/openwrt/luci/wiki)
- [LuCI Documentation](https://github.com/openwrt/luci/wiki/Documentation)
- [LuCI Github](https://github.com/openwrt/luci)

## What is LuCI

[Lua](https://en.wikipedia.org/wiki/Lua_(programming_language)) Control Interface (LuCI) was founded in 2008 as "FFLuCI" as part of the efforts to port the Freifunk-Firmware from [White Russian](/about/history) code branch to its successor [Kamikaze](/about/history).

The initial reason for this project was the absence of a free, clean, extensible and easily maintainable [web user interface](/docs/guide-user/luci/webinterface.overview) for embedded devices. While most similar configuration interfaces make heavy use of the Shell-scripting language, LuCI:

- uses the Lua programming language and
- splits the interface up into logical parts like models and views, uses object-oriented libraries and templating.

That ensures better performance, smaller installation size, faster runtimes, and simple maintainability.

Meanwhile LuCI evolved from a MVC-Webframework to a collection of libraries, applications and user interfaces with general purpose for Lua programmers while the focus still remains on the [web user interface](/docs/guide-user/luci/webinterface.overview) which became an official part of OpenWrt since 'Kamikaze' 8.09.

## Dependencies

- [uci](/docs/techref/uci) (including libuci-lua)

## Encompassed Packages

`luci` and `luci-ssl` are meta-packages. Here you see what they comprise, the sizes are in Bytes compiled for the ar71xx platform. They shouldn't differ much from binaries compiled for other architectures. Also note, that with JFFS2 it is not possible to precisely predict the occupied space.

In case you want to use a different web server than [uhttpd](/docs/guide-user/services/webserver/http.uhttpd) and not install uhttpd at all, do not install the meta-package because it includes it. Install the individual components instead and a web server of your choice. The article [start](/docs/guide-user/services/webserver/start) shows you some choices from the repos.

|                      Name                      | Size  | Description                                                                                                                                                                                                                                                                                   |
|:----------------------------------------------:|:-----:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                      luci                      |  779  | Meta package. Standard OpenWrt set including full and mini admin and the standard theme                                                                                                                                                                                                       |
|                     uhttpd                     | 23778 | uHTTPd is a tiny single threaded [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) server with TLS, CGI and Lua support. It is intended as a drop-in replacement for the Busybox [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) daemon.                                                                                                                                              |
|              luci-mod-admin-full               | 60827 | LuCI Administration - full-featured for full control                                                                                                                                                                                                                                          |
|              luci-mod-admin-core               | 5257  | Web UI Core module                                                                                                                                                                                                                                                                            |
|              luci-theme-bootstrap              | 13801 | Bootstrap theme (default)                                                                                                                                                                                                                                                                     |
|               luci-theme-openwrt               | 7756  | OpenWrt.org theme                                                                                                                                                                                                                                                                             |
|               luci-i18n-english                | 1252  | English                                                                                                                                                                                                                                                                                       |
|               luci-app-firewall                | 16630 | Firmware and Portforwarding application                                                                                                                                                                                                                                                       |
|                    firewall                    | 11603 | UCI based firewall for OpenWrt /etc/config/firewall /etc/firewall.user. Dependencies: iptables, iptables-mod-conntrack, iptables-mod-nat                                                                                                                                                      |
|                luci-app-initmgr                | 5713  | LuCI Initscript Management                                                                                                                                                                                                                                                                    |
|                   libiwinfo                    | 25362 | Wireless information library with consistent interface for proprietary Broadcom, madwifi, nl80211 and wext driver interfaces.                                                                                                                                                                 |
|                 luci-lib-ipkg                  | 2846  | LuCI IPKG/OPKG call abstraction library                                                                                                                                                                                                                                                       |
|                luci-theme-base                 | 25065 | Common base for all themes                                                                                                                                                                                                                                                                    |
|                   libnl-tiny                   | 14390 | This package contains a stripped down version of libnl                                                                                                                                                                                                                                        |
|                     liblua                     | 81477 | Lua is a powerful light-weight programming language designed for extending applications. Lua is also frequently used as a general-purpose, stand-alone language. Lua is free software. This package contains the Lua shared libraries, needed by other programs.                              |
|                      lua                       | 9069  | Lua is a powerful light-weight programming language designed for extending applications. Lua is also frequently used as a general-purpose, stand-alone language. Lua is free software. This package contains the Lua language interpreter. (5.1.4-7)                                          |
|                  luci-lib-web                  | 59695 | MVC Webframework                                                                                                                                                                                                                                                                              |
|                  luci-lib-sys                  | 15795 | LuCI Linux/POSIX system library                                                                                                                                                                                                                                                               |
|                 luci-lib-nixio                 | 31683 | NIXIO POSIX library                                                                                                                                                                                                                                                                           |
|                 luci-lib-core                  | 28096 | LuCI core libraries                                                                                                                                                                                                                                                                           |
|                  luci-sgi-cgi                  | 2420  | CGI Gateway behind existing Webserver                                                                                                                                                                                                                                                         |
|                  luci-lib-lmo                  | 4714  | LuCI LMO I18N library                                                                                                                                                                                                                                                                         |
|        Additionally Required for HTTPS         |       |                                                                                                                                                                                                                                                                                               |
|                    luci-ssl                    |  782  | Meta package. Standard OpenWrt set including full admin, the standard theme + HTTPS support. Installs px5g and libustream-mbedtls by default (since Dec2016)                                                                                                                                  |
|                (uhttpd-mod-tls)                | 5825  | The TLS plugin adds HTTPS support to uHTTPd. Note: Not needed since r35295 in Jan2013 as uhttpd is always built ready to utilize SSL library via a libustream- library                                                                                                                        |
|                 uhttpd-mod-lua                 | 9178  | The Lua plugin adds a CGI-like Lua runtime interface to uHTTPd.                                                                                                                                                                                                                               |
|                      px5g                      | 28480 | Px5g is a tiny standalone X.509 certificate generator. It's suitable to create key files and certificates in [DER](https://en.wikipedia.org/wiki/Distinguished Encoding Rules) and [PEM](https://en.wikipedia.org/wiki/Privacy Enhanced Mail) format for use with stunnel, uhttpd and others. |
| Internationalization and localization packages |       |                                                                                                                                                                                                                                                                                               |
|                 luci-i18n-xxx                  | ????? | Please refer to <https://github.com/openwrt/luci/wiki/i18n> for an overview of the translation progress.                                                                                                                                                                                      |

---

# LuCI2 (OpenWrt web user interface)

![outdated&noheader&nofooter&noeditbtn](/page>meta/infobox/outdated&noheader&nofooter&noeditbtn)

### NOTE: This page currently mixes the five+ years old abandoned original "luci2" and the new JavaScript based standard LuCI implementation. Information on this page can be partially misleading

For years OpenWrt was using [LuCI](LuCI), a web user interface written in [Lua](http://en.wikipedia.org/wiki/Lua_(programming_language)). It required several Lua extensions (like `ubus`, `luci.model.uci`, `nixio.fs`, etc.) to access system info and settings. Unfortunately this solution appeared to be quite resource consuming and didn't work well on devices with slow CPU and little amount of RAM.

This led to developing LuCI2, a new web interface with a different architecture. It doesn't use Lua anymore, but static HTML page and [JavaScript XHR](http://en.wikipedia.org/wiki/XMLHttpRequest) method. It means building HTML pages is done on client (browser) side offloading OpenWrt device. To access any kind of system data [ubus](ubus) is used (with the help of [uhttpd-mod-ubus](ubus#access_to_ubus_over_http) to provide [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) based API).

LuCI2 is still experimental. Its predecessor is still used by default in all builds, including the trunk.

## Implementation details

As explained above, LuCI2 uses `ubus` to communicate with OpenWrt subsystems (that includes for example `network` and `service` but also many others). Unfortunately not every major OpenWrt tool registers itself with `ubus`. For example it's not possible to use `opkg` (packages management) that way. LuCI2 resolves this problem providing it's own `rpcd` plugin which adds extra `ubus` namespaces. For the previous example of `opkg` it registers new `luci2.opkg` path in the `ubus`.

To sum up, LuCI2 consists of two things: a pack of HTML/CSS/JS files (`htdocs`) and few extra small tools working in the OpenWrt environment.

In next sections you will find details about various LuCI2 parts that should help in the development.

### Menu

The first thing to know about LuCI2 menu is that it is not hardcoded in any file received by a browser. Instead of that, it's provided by `ubus` using `luci2.ui` path and `menu` method. For debugging purposes menu layout can be verified using:

    ubus call luci2.ui menu '{ "ubus_rpc_session": "invalid" }'

Internally `rpcd` plugin parses all files located in `/usr/share/rpcd/menu.d`, joins them and removes entries that are not available for a current user (based on a passed `ubus_rpc_session`). This results in a two-level menu limited to entries that current has rights to.

Top level entries are defined using following JSON:

    "foo": {
        "title": "Foo",
        "index": 12
    }

(and ordered using `index` values).

Second level entries are defined in a similar way:

    "foo/bar": {
        "title": "Bar",
        "acls": [ "baz", "qux" ],
        "view": "foo/bar",
        "index": 5
    }

Please note that second level entries may be located in separated files. This allows easy addition of new entries without modifying existing files.

### Templates

Every LuCI2 subpage has to have it's template located in `/www/luci2/template/`. These are very simple HTML files providing place for a content. Please note they don't contain references to any variables, it's JavaScript role to access them and fill with a content. The only special syntax in these files is for internationalization (i18n) system that uses following special tags:

    <p><%:Hello world%></p>

### Views

Apart from a template, every LuCI2 subpage requires also it's view to be defined and placed in `/www/luci2/view/`. Views are JavaScript files extending `L.ui.view` using subpage specific object. They are obligated to provide `execute` method that will be called after loading a template. Optionally they may also provide subpage `title` and `description`.

A bit of attention requires `execute` method. Building a view may fail because of various reasons, especially when it requires loading extra data using `ubus`. So it makes sense for `execute` method to provide info if it succeed or failed. Unfortunately it can't simply return `true` of `false`, as loading extra data is done asynchronously. To resolve this problem a `Promise` object should be returned which allows to postpone taking a decision about a success or failure.

The simplest view could look like this:

    L.ui.view.extend({
        title: L.tr('Foo'),         /* Optional title */
        description: 'Bar',         /* Optional description */

        execute: function() {
            var deferred = $.Deferred();    /* Create a new Deferred object */
            deferred.resolve();     /* Resolve it immediately, there is nothing that could fail */
            return deferred.promise();  /* Return Promise object (a subset of Deferred) */
        }
    });

### Communication with ubus

Before starting, please know that LuCI2 provides many helpers for accessing [UCI](UCI) system. To write a simple view managing config files in `/etc/config/`, the full understanding of `ubus` calls is not required and this section can be skipped.

For more complicated LuCI2 views it's good to first figure out all needed `ubus` calls. A complete list of objects and methods can be listed using `ubus -v list` command.

Below is an example of simple call to `log` object and `write` method. It requires `event` parameter to be passed as an argument. When using `ubus` command-line tool, this call could be done with:

    ubus call log write '{ "event": "Foo" }'

LuCI2 provides a helper for `ubus` communication called `L.rpc.declare`. This is JavaScript helper magically creating a function that will call specified `ubus` method. Please note that at declaring time no call is executed and no arguments are passed. This is only preparing a function that will be used later. Below is an example function calling `log` object and it's `write` method:

    var writeToLog = L.rpc.declare({
        object: 'log',
        method: 'write',
        params: [ 'event' ]
    })

Once declared such a function, it can be called at anytime simply using:

    writeToLog('Foo');

In the above example result of the call was silently ignored. It's not an option if view has to access data returned by an `ubus` call. The next example will access `info` method of the `system` object. In the command-line this would be following call:

    # ubus call system info
    {
        "uptime": 123,
        "localtime": 1234567890,
        "load": [
            1,
            2,
            3
        ],
        "memory": {
            "total": 67108864,
            "free": 33554432,
            "shared": 0,
            "buffered": 16777216
        },
        "swap": {
            "total": 0,
            "free": 0
        }
    }

When using LuCI2 (and JavaScript) declaration for the above call should look like this:

    var readSystemInfo = L.rpc.declare({
        object: 'system',
        method: 'info',
        expect: { memory: { } }         /* Optional, extracts only part of the result */
    })

Accessing result of the call requires using a simple `.then` function:

    readSystemInfo().then(function(memory) {
        console.log(memory);
    });

### Dependencies of LuCI2

- `libubox` (~ 12KiB) is a general purpose library which provides things like an event loop, binary blob message formatting and handling, the Linux linked list implementation, and some JSON helpers. The functions in `libubox` are used to write the other software in LuCI2
- `ubox`
- `ubus` (~ 13KiB) is an [IPC](https://en.wikipedia.org/wiki/Inter-process_communication) daemon similar to D-Bus but with a much friendlier C API
- `mountd`
- `rpcd`

---

# mountd – Technical Reference

OpenWrt automount daemon, is configured in `/etc/config/mountd`

- mountd is available in OpenWrt since [r17853 (trunk)](https://dev.openwrt.org/changeset/17853) and published under the GPLv2.
- [mountd has been replaced](https://git.openwrt.org/?p=openwrt/openwrt.git;a=commit;h=6a772cb953c4c36dfdf49365937b71017652562a) by [blockd](https://git.openwrt.org/?p=openwrt/openwrt.git;a=commit;h=7e4b869c451383f7fca654abd1cd726c862d6dd7)
- [git commits regarding mountd](git>mountd)

## What is mountd?

- `mountd` is another [daemon](https://en.wikipedia.org/wiki/Daemon (computing)) written in [C](https://en.wikipedia.org/wiki/C (programming language)) with the ability to ...:?:
- `mountd` replaces ...:?:... on full blown desktop distributions.

## Help with the development of mountd

1.  review of the code
2.  augment new functions

## Why do we want mountd?

There was no daemon for the above mentioned purposes suited for embedded devices available. Now there is one.

## Dependencies of mountd

- +uci +kmod-usb-storage +kmod-fs-autofs4

---

# MTD

|                                                                                                                                                                     |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FIXME This page is a Work In Progress. The goal is to make it similar to [opkg](/docs/guide-user/additional-software/opkg) and then link to it as often as possible |

# MTD

`mtd` is a utility we use to write to an MTD (Memory Technology Device). Please read the [\#Notes](#Notes) to learn more.

## Invocation

    Usage: mtd [<options> ...] <command> [<arguments> ...] <device>[:<device>...]

### Writing to MTD

|                       |                                                      |
|:----------------------|:-----------------------------------------------------|
| `unlock <dev>`        | unlock the device                                    |
| `refresh <dev>`       | refresh mtd partition                                |
| `erase <dev>`         | erase all data on device                             |
| `write <imagefile>|-` | write \<imagefile\> (use - for stdin) to device      |
| `jffs2write <file>`   | append \<file\> to the jffs2 partition on the device |
| `fixtrx <dev>`        | fix the checksum in a trx header on first boot       |

### Options

|                                                 |                                                                                                                                                                        |
|:------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-q`                                            | quiet mode (once: no \[w\] on writing, twice: no status messages)                                                                                                      |
| `-n`                                            | write without first erasing the blocks                                                                                                                                 |
| `-r`                                            | reboot after successful command                                                                                                                                        |
| `-f`                                            | force write without trx checks                                                                                                                                         |
| `-e <device>`                                   | erase \<device\> before executing the command                                                                                                                          |
| `-d <name>`                                     | directory for jffs2write, defaults to "tmp"                                                                                                                            |
| `-j <name>`                                     | integrate \<file\> into jffs2 data when writing an image                                                                                                               |
| `-o offset`                                     | offset of the image header in the partition(for fixtrx)                                                                                                                |
| `-F <part>[:<size>[:<entrypoint>]][,<part>...]` | alter the fis partition table to create new partitions replacing the partitions provided as argument to the write command (only valid together with the write command) |

## Examples

Download `linux.bin` from Internet (it's not safe to do so, here is for demonstration purpose only), then write `linux.bin` to a MTD partition labeled as `linux` (could be `mtd4`) and reboot afterwards:

    cd /tmp
    wget http://www.example.org/linux.bin
    mtd -r write /tmp/linux.bin linux

## Example (flash u-boot from OpenWrt)

Tested on Marvell EspressoBinBoard based on MVEBU, (see [forum topic](https://forum.openwrt.org/t/is-it-possible-to-flash-u-boot-from-openwrt/90284)) Download `flash-image.bin` for your specific hardware from [SnapShots](https://downloads.openwrt.org/snapshots/targets/mvebu/cortexa53/)

You can checks your mtd partitions from proc :

    root@EBIN:~# cat /proc/mtd
    dev:    size   erasesize  name
    mtd0: 003f0000 00010000 "firmware"
    mtd1: 00010000 00010000 "u-boot-env"

(it's not safe to do so, here is for demonstration purpose only),

then write `flash-image.bin` to a MTD partition labeled as `spi0.0` (could be `mtd0` or `firmware`) and reboot afterwards :

    cd /tmp
    wget https://downloads.openwrt.org/snapshots/targets/mvebu/cortexa53/trusted-firmware-a-espressobin-v7-1gb/flash-image.bin
    mtd -r write /tmp/flash-image.bin /dev/mtd0

## mtd vs dd

The differences between `dd` (disc dump) and `mtd` are ... [TODO](/docs/techref/flash#nand-specific_tools_for_reading_and_writing_to_raw_nand)

## mtd on vendor-firmware

`mtd` can even be used with vendor-firmware, as long as the kernel had mtd-support and not using something "home-brewed". When the vendor is not shipping the binary it can probably transferred via `scp`, `netcat`, `tftp`, `ftp`, `http`onto the board. The original binary from the OpenWrt-package might not run on the vendor-os, but linking it static should do the trick. With OpenWrt-21.02 I was using a small hack to to let the buildroot create a static binary:

    sed -i -e "s/^LDFLAGS += /LDFLAGS += -static /" package/system/mtd/src/Makefile
    make package/mtd/compile

This patches the mtd source to include the "-static" option when building the binary. This way the binary gets all dependent library-code embedded to make it run itself, as long as the correct CPU-target is used. The new binary can be extracted from the resulting package or just copied from `build_dir/target-<ARCH>/linux-<TARGET>-<SUBTARGET>/mtd`.

## Notes

- [Flash memory - things to consider](/docs/techref/flash)
- [MTD (Memory Technology Device)](https://en.wikipedia.org/wiki/Memory Technology Device)
- [documentation on MTDs](http://www.linux-mtd.infradead.org/doc/general.html).
- [The differences between flash devices and block drives in a table](http://www.linux-mtd.infradead.org/faq/general.html#L_mtd_vs_hdd)
- To make it more clear, here is a small [comparison of MTD devices and block devices](http://lxr.free-electrons.com/source/Documentation/filesystems/ubifs.txt):
  - MTD devices represent flash devices and they consist of eraseblocks of rather large size, typically about 128KiB. Block devices consist of small blocks, typically 512 bytes. MTD devices support 3 main operations - read from some offset within an eraseblock, write to some offset within an eraseblock, and erase a whole eraseblock. Block devices support 2 main operations - read a whole block and write a whole block.
  - The whole eraseblock has to be erased before it becomes possible to re-write its contents. Blocks may be just re-written.
  - Eraseblocks become worn out after some number of erase cycles - typically 100K-1G for SLC [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) and NOR flashes, and 1K-10K for MLC [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flashes. Blocks do not have the wear-out property.
  - Eraseblocks may become bad (only on [NAND](../wiki/chunked-reference/wiki_page-techref-flash.md) flashes) and software should deal with this. Blocks on hard drives typically do not become bad, because hardware has mechanisms to substitute bad blocks, at least in modern LBA disks.
- Sometimes flash memory uses FTL: [Raw Flash vs. FTL (Flash Translation Layer)](http://www.linux-mtd.infradead.org/doc/ubifs.html#L_raw_vs_ftl)
- Although most flashes on the commodity hardware have FTL, there are systems which have **bare flashes and do not use FTL**! Those are mostly various handheld devices and **embedded systems**.

---

# netifd (Network Interface Daemon) – Technical Reference

- [Project's git](http://git.openwrt.org/?p=project/netifd.git;a=summary)
- netifd is available in OpenWrt since [R28499 (trunk)](https://dev.openwrt.org/changeset/28499) and published under the GPLv2.
- [commits to OpenWrt trunk regarding netifd](https://dev.openwrt.org/search?changeset=on&milestone=on&wiki=on&q=netifd&page=1&noquickjump=1)
- [Design of netifd](http://git.openwrt.org/?p=project/netifd.git;a=blob;f=DESIGN)

### What is netifd?

`netifd` is an [RPC](https://en.wikipedia.org/wiki/Remote procedure call)-capable [daemon](https://en.wikipedia.org/wiki/Daemon (computing)) written in [C](https://en.wikipedia.org/wiki/C (programming language)) for better access to kernel APIs with the ability to listen on [netlink events](https://en.wikipedia.org/wiki/Netlink). `Netifd` has replaced the old *OpenWrt-network configuration scripts*, the actual scripts that configured the network, e.g.

- `/lib/network/*.sh`,
- `/sbin/ifup`
- some scripts in `/etc/hotplug.d`.)

`netifd` is intended to stay compatible with the existing format of `/etc/config/network`, the only exceptions being rare special cases like aliases or the overlay variables in `/var/state` (though even most of those can be easily emulated).

### Debugging

- Add the switch `-l <level>` to */etc/init.d/network*
  - Level is specified as an integer:
    - 0 = L_CRIT
    - 1 = L_WARNING
    - 2 = L_NOTICE (default)
    - 3 = L_INFO
    - 4 = L_DEBUG
- For the L_DEBUG level, there is another option `-d <mask>` to set a mask:
  - Options are:
    - 1 = DEBUG_SYSTEM
    - 2 = DEBUG_DEVICE
    - 4 = DEBUG_INTERFACE
    - 8 = DEBUG_WIRELESS
  - Add your favorite options together to obtain the `<mask>`.

      * In order for the output to be seen you'll need to modify /etc/init.d/network to add:
        * [procd_set_param](../cookbook/chunked-reference/procd-service-lifecycle.md) stdout 1
        * [procd_set_param](../cookbook/chunked-reference/procd-service-lifecycle.md) stderr 1
      * to start_service so that procd doesn't send netifd hotplug script output to /dev/null.

### Help with the development of netifd

1.  test what has been ported
2.  review of the code
3.  help porting more of our protocol handler scripts (so far, static, ppp, pppoe, pppoa and dhcp are supported)

### Why do we want netifd?

One thing that `netifd` does much better then old *OpenWrt-network configuration scripts* is handling configuration changes. With `netifd`, when the file `/etc/config/network` changes, you no longer have to restart all interfaces. Simply run **`/etc/init.d/network reload`**. This will issue an `ubus`-call to `netifd`, telling it to figure out the difference between runtime state and the new config and apply only that. This works on a per-interface level, even with protocol handlers written as shell scripts.

It boils down to the fact that the current network and interface setup mechanisms (via network configuration scripts) are rather constrained and inflexible:

- lack of statefulness
- tendency for raceconditions
- inability to properly nest protocols
- limited featureset of the ash shell which will not allow for complex interface operations like e.g. calculating [ULAs](https://en.wikipedia.org/wiki/Unique local address)
- you name it

`Netifd` will be able to manage even complex interface configurations with a mix of bonding, vlans, bridges, etc. and handle the dependencies between interfaces properly - and of course all that without adding unnecessary bloat.
AFAIK there are no alternatives to netifd, e.g. [connman](https://connman.net/) seems to be centered around one specifific use case only: having a mobile device access the internet through multiple connections. Connman is based on dbus.

The following is a brief conversation from IRC regarding hints on how netifd is involved with wifi interface startup and variables used. It 'documents' my frustration with trying to add a new uci variable (utf8_ssid), and I don't think the answers contained should be lost:

    [20:20:06]  <jow> ldir: its complicated
    [20:20:29]  <jow>   ldir: upon start, netifd scans all wireless handlers in /lib/netifd/wireless/
    [20:21:08]  <jow>   ldir: so for mac80211 that'd be /lib/netifd/wireless/mac80211.sh
    [20:22:33]  <jow>   ldir: the handler tells netifd about which options it recognized, for mac80211.sh this can be seen in drv_mac80211_init_device_config() (for config wifi-device) and drv_mac80211_init_iface_config() (for config wifi-iface)
    [20:27:26]  <jow>   ldir: netifd reads /etc/config/wireless, converts it into json and eventually passes it via various indirections back to the script
    [20:28:07]  <jow>   ldir: it will execute something like  /lib/netifd/wireless/mac80211.sh mac80211 setup radio0 '{ lots of json encoded uci options }'
    [20:29:20]  <jow>   ldir: this invocation is catched by `init_wireless_driver "$@"` in /lib/netifd/wireless/mac80211.sh (declared in the shared /lib/netifd/netifd-wireless.sh)
    [20:31:03]  <ldir>  jow: thank you - I shall try to digest this.
    [20:31:38]  <jow>   ldir: init_wireless_driver() will parse the passed json into shell variables and dispatch back to one of the drv_*() functions in /lib/netifd/wireless/mac80211.sh
    [20:32:02]  <jow>   e.g. /lib/netifd/wireless/mac80211.sh mac80211 setup radio0 '{ lots of json encoded uci options }'  will eventually call  drv_mac80211_setup()
    [20:32:48]  <jow>   drv_mac80211_setup() will have access to all the uci config variables via the loaded jshn environment so you can accesss them using json_get_vars, json_select etc.
    [20:33:15]  <jow>   the radio we're operating on is passed as "$1" and will contain the uci wifi-device section name, e.g. "radio0"
    [20:35:11]  <jow>   from then on its "just" shell magic translating things back and forth, writing temporary hostapd config etc. and eventually instructing netifd to launch a hostapd process using wireless_add_process()
    [20:35:50]  <jow>   executive summary
    [20:36:03]  <ldir>  that's hell on a stick :-)
    [20:36:26]  <ldir>  btw the executive summary was 'it's complicated' ;-)
    [20:36:33]  <jow>   - register new config options in /lib/netifd/wireless/mac80211.sh using either drv_mac80211_init_device_config or drv_mac80211_init_iface_config - for utf8ssid you likely want drv_mac80211_init_iface_config
    [20:38:32]  <jow>   correction; register it in hostapd_common_add_bss_config() of /lib/netifd/hostapd.sh
    [20:39:07]  <jow>   - and process it in hostapd_set_bss_options()
    [20:39:12]  <jow>   thats it
    [20:39:19]  <ldir>  jow: in theory I've done that - I noticed mac80211.sh has a 'common' set options
    [20:39:36]  <jow>   you most likely need to restart netifd for it to become aware of the new option
    [20:39:50]  <jow>   du to the uci->blob->json->string->jshn call chain

---

# odhcpd

See also: [odhcpd upstream documentation](https://github.com/openwrt/odhcpd/blob/master/README.md)

odhcpd is an embedded DHCP/DHCPv6/RA server & NDP relay.

## Abstract

odhcpd is a daemon for serving and relaying IP management protocols to configure clients and downstream routers. It tries to follow the [RFC 6204](https://datatracker.ietf.org/doc/html/rfc6204) requirements for IPv6 home routers.

odhcpd provides server services for DHCP, RA, stateless SLAAC and stateful DHCPv6, prefix delegation and can be used to relay RA, DHCPv6 and NDP between routed (non-bridged) interfaces in case no delegated prefixes are available.

## Features

### Router Discovery (RD)

Router Discovery (RD) support (solicitations and advertisements) with 2 modes of operation:

1.  RD Server mode: Router Discovery (RD) server for slave interfaces:
    1.  Automatic detection of prefixes, delegated prefix, default routes and MTU.
    2.  Automatic re-announcement of any changes in either prefixes or routes.
2.  RD Relay mode: Router Discovery (RD) relay between master and slave interfaces.
    1.  Supports rewriting of the announced DNS server addresses.

### DHCPv6

DHCPv6 support with 2 modes of operation:

1.  DHCPv6 Server mode: stateless, stateful and Prefix Delegation (PD) server mode:
    1.  Stateless and stateful address assignment.
    2.  Prefix delegation support.
    3.  Dynamic reconfiguration of any changes in Prefix Delegation.
    4.  Hostname detection and hosts-file creation.
2.  DHCPv6 Relay mode: A mostly standards-compliant DHCPv6-relay:
    1.  Supports rewriting of the announced DNS server addresses.

### DHCPv4

1.  Stateless and stateful DHCPv4 server mode.

### Neighbor Discovery Proxy (NDP)

Proxy for Neighbor Discovery solicitation and advertisement messages (NDP):

1.  Supports auto-learning of routes to the local routing table.
2.  Supports marking interfaces as "external".

Interfaces marked as "external" will not receive any proxyied NDP content and are only served with NDP for Duplicate Address Detection (DAD) and traffic to the router itself.

:!: Interfaces marked as external need additional firewall rules for security!

## Configuration

odhcpd uses a UCI configuration file in `/etc/config/dhcp` for configuration and may also receive information from ubus.

### odhcpd section

Configuration for the odhcp daemon.

| Name           | Type    | Default                   | Description                                                                                    |
|:---------------|:--------|:--------------------------|:-----------------------------------------------------------------------------------------------|
| `legacy`       | boolean | `0`                       | Enable DHCPv4 if the 'dhcp' section contains a `start` option, but no `dhcpv4` option set.     |
| `maindhcp`     | boolean | `0`                       | Use odhcpd as the main DHCPv4 service.                                                         |
| `leasefile`    | string  | `/tmp/odhcpd.leases`      | Location of the lease/hostfile for DHCPv4 and DHCPv6.                                          |
| `leasetrigger` | string  | `/usr/sbin/odhcpd-update` | Location of the lease trigger script.                                                          |
| `hostsdir`     | string  | `/tmp/hosts`              | Directory to store hosts files (IP address to hostname mapping) in. Used by e.g. dnsmasq.      |
| `piodir`       | string  | `/tmp/odhcpd-piodir`      | Directory to store IPv6 prefix information (to detect stale prefixes, see RFC9096, §3.5).      |
| `loglevel`     | integer | `4`                       | Syslog level priority (0-7). 0=emer, 1=alert, 2=crit, 3=err, 4=warn, 5=notice, 6=info, 7=debug |
| `enable_tz`    | boolean | `1`                       | Set to `0` to disable sending option 41 and 42 timezone info to clients that request them      |

 **RFC9096 § 3.5 SLAAC compliance relies on the `piodir` option, which may wear out the flash under certain conditions.
For example: ISPs with dynamic IPv6 prefixes which disconnect the clients every X hours.
Therefore, setting `dhcp.odhcpd.piodir` to persistent storage in the router flash is not advisable and should be set to other kinds of persistent storage such as USBs, SDs, NVMEs...
In order to prevent wearing out the router flash it's set to ephemeral storage by default:
`uci set dhcp.odhcpd.piodir=/tmp/odhcpd-piodir`
`uci commit dhcp`**

If dhcp.odhcpd.piodir is set to persistent storage, you should also add that directory to sysupgrade.conf in order to preserve the PIOs when OpenWrt is upgraded.
`$(uci -q get dhcp.odhcpd.piodir) >> /etc/sysupgrade.conf`

### dhcp section

Configuration for DHCPv4, DHCPv6, RA and NDP services.

```tsv
Name	Type	Required	Default	Description
`interface`	string	 	`<name of UCI section>`	Logical OpenWrt interface.
`ifname`	string	 	`<resolved from logical>`	Physical network interface.
`networkid`	string	 	`<same as ifname>`	Alias of `ifname` for compatibility.
`ignore`	boolean	 	`0`	Do not serve this interface unless overridden by `ra`, `ndp`, `dhcpv4` or `dhcpv6` options.
`master`	boolean	 	`0`	Is a master interface for relaying.
`ra`	string	 	`disabled`	Router Advert service. Set to `disabled`, `server`, `relay` or `hybrid`.
`dhcpv6`	string	 	`disabled`	DHCPv6 service. Set to `disabled`, `server`, `relay` or `hybrid`.
`dhcpv4`	string	 	`disabled`	DHCPv4 service. Set to `disabled` or `server`.
`ndp`	string	 	`disabled`	Neighbor Discovery Proxy. Set to `disabled`, `relay` or `hybrid`.
`dynamicdhcp`	boolean	 	`1`	Leases for DHCPv4 and DHCPv6 are created dynamically.
`dhcpv4_forcereconf`	boolean	 	`0`	Force reconfiguration by sending force renew message even if the client did not include the force renew nonce capability option ([RFC 6704](https://datatracker.ietf.org/doc/html/rfc6704)).
`dhcpv6_assignall`	boolean	 	`1`	Assign all viable DHCPv6 addresses in statefull mode. If disabled only the DHCPv6 address having the longest preferred lifetime is assigned.
`dhcpv6_hostidlength`	integer	 	`12`	Host ID length of dynamically created leases, allowed values: 12 - 64 (bits).
`dhcpv6_na`	boolean	 	`1`	DHCPv6 stateful addressing hands out IA_NA - Internet Address - Network Address.
`dhcpv6_pd`	boolean	 	`1`	DHCPv6 stateful addressing hands out IA_PD - Internet Address - Prefix Delegation.
`router`	list	 	`<local address>`	Routers to announce accepts IPv4 only.
`dns`	list	 	`<local address>`	DNS servers to announce on the network. IPv4 and IPv6 addresses are accepted.
`dns_service`	boolean	 	`1`	Announce the address of interface as DNS service if the list of DNS is empty.
`domain`	list	 	`<local search domain>`	Search domains to announce on the network.
`leasetime`	string	 	`12h`	DHCPv4 address leasetime
`start`	integer	 	`100`	Starting address of the DHCPv4 pool.
`limit`	integer	 	`150`	Number of addresses in the DHCPv4 pool.
`preferred_lifetime`	string	 	`12h`	Value for the preferred lifetime for a prefix.
`ra_default`	integer	 	`0`	Override default route. Set to `0` (default), `1` (ignore, no public address) or `2` (ignore all).
`ra_flags`	list	 	`other-config`	List of RA flags to be advertised in RA messages:; `managed-config` - get address information from DHCPv6 server. If this flag is set, `other-config` flag is redundant.; `other-config` - get other configuration from DHCPv6 server (such as DNS servers). See [here](https://datatracker.ietf.org/doc/html/rfc4861#section-4.2) for details.; `home-agent` - see [here](https://datatracker.ietf.org/doc/html/rfc3775#section-7.1) for details.; `none`.; OpenWrt since version 21.02 configures `managed-config` and `other-config` [by default](https://github.com/openwrt/openwrt/blob/openwrt-21.02/package/network/services/odhcpd/files/odhcpd.defaults#L49-L50).
`ra_slaac`	boolean	 	`1`	Announce SLAAC for a prefix (that is, set the A flag in RA messages).
`ra_management`	integer	no	`1`	:!: This option is [deprecated](commit>?p=project/odhcpd.git;a=commit;h=e73bf11dee1073aaaddc0dc67ca8c7d75ae3c6ad). Use `ra_flags` and `ra_slaac` options instead.; RA management mode: no M-Flag but A-Flag and ra_slaac is ture (`0`) , both M and A flags and ra_slaac is ture(`1`), both M and A flags and ra_slaac is false (`2`)
`ra_offlink`	boolean	 	`0`	Announce prefixes off-link.
`ra_preference`	string	 	`medium`	Route preference `medium`, `high` or `low`.
`ra_maxinterval`	integer	 	`600`	Maximum time allowed between sending unsolicited Router Advertisements (RA).
`ra_mininterval`	integer	 	`200`	Minimum time allowed between sending unsolicited Router Advertisements (RA).
`ra_lifetime`	integer	 	`1800`	Router Lifetime published in Router Advertisement (RA) messages.
`ra_useleasetime`	boolean	 	`0`	If set, the configured DHCPv4 `leasetime` is used both as limit for the preferred and valid lifetime of an IPv6 prefix.
`ra_reachabletime`	integer	 	`0`	Reachable Time in milliseconds to be published in Router Advertisement (RA) messages'.
`ra_retranstime`	integer	 	`0`	Retransmit Time in milliseconds to be published in Router Advertisment (RA) messages.
`ra_hoplimit`	integer	 	`0`	The maximum hops to be published in Router Advertisement (RA) messages.
`ra_mtu`	integer	 	`0`	The MTU to be published in Router Advertisement (RA) messages.
`ra_dns`	boolean	 	`1`	Announce DNS configuration in RA messages ([RFC 8106](https://datatracker.ietf.org/doc/html/rfc8106)).
`ndproxy_routing`	boolean	 	`1`	Learn routes from NDP.
`ndproxy_slave`	boolean	 	`0`	NDProxy external slave.
`ndproxy_static`	list	 	 	Static NDProxy prefixes.
`prefix_filter`	string	 	`::/0`	Only advertise on-link prefixes within the provided IPv6 prefix. Others are filtered out.
`ntp`	list	 	 	DHCPv6 stateful option 56 to Announce NTP servers
```

### host section

The `host` section is where static leases are defined.

| Name        | Type   | Required | Default  | Description          |
|-------------|--------|----------|----------|----------------------|
| `ip`        | string | yes      | *(none)* | IP address to lease  |
| `mac`       | string | no       | *(none)* | MAC address          |
| `duid`      | string | no       | *(none)* | DUID in base16       |
| `hostid`    | string | no       | *(none)* | IPv6 host identifier |
| `name`      | string | no       | *(none)* | Hostname             |
| `leasetime` | string | no       | *(none)* | DHCPv4/v6 leasetime  |

Example `hostid='105ee0badc0de`' =\> IPv6 '::1:5ee:bad:c0de'

## ubus API

Replace dnsmasq with odhcpd to access IPv4 leases.

``` bash
ubus -v list dhcp
ubus call dhcp ipv4leases
ubus call dhcp ipv6leases
ubus call dhcp ipv6ra
```

## Compiling

odhcpd uses cmake.

``` bash
# Prepare
cmake .

# Build/install
make
make install

# Build DEB/RPM packages
make package
```

---

# Abstract

======= Preinit and Root Mount and Firstboot Scripts =======

FIXME Information may be outdated and obsolete information as of April, 2018; Overview, Preinit and Overview, Failsafe updated from April 2018 based on reading `master` code.

See [Rootfs on External Storage](/docs/guide-user/additional-software/extroot_configuration) for information on external rootfs mounting.

# Abstract

This document presents the preinit / firstboot boot sequence. The boot system is extensible via (new) packages such as rootfs on usb, or enhanced failsafe.

We describe the portion of the OpenWrt boot sequence that occurs before the 'init' program is executed (when booting in multiuser mode), as well as the script that is responsible for creating and initializing the root filesystem on the first boot after flashing the device with OpenWrt.

# Context: Boot Sequence

The basic OpenWrt boot sequence is:

1.  boot loader loads kernel
2.  kernel loads whilst scanning the mtd partition *rootfs* for a valid superblock for mounting the SquashFS partition (which contains /etc). More info at [filesystems#technical.details](/docs/techref/filesystems#technical.details)
3.  ~~kernel calls `/etc/preinit` (the kernel considers this to be the `init` (or root) process~~ `/sbin/init` now the init process, which in turn launches `/sbin/procd -h /etc/hotplug-preinit.json` (a.k.a., "plugd") followed by `/bin/sh /etc/preinit`. Each is launched via `fork` and `execvp` and managed by the uloop library in libubox.
4.  `/etc/preinit` prepares system for multiuser mode
5.  `/etc/preinit` `exec`s `/sbin/init` which becomes the `init` (or root) process and launches multiuser
6.  `/sbin/init` launches processes according to /etc/inittab.
7.  Typically the first process launched is `/etc/init.d/rcS` which causes the scripts in `/etc/rc.d` which begin with 'S' to be launched (in glob sort order). The `/etc/rc.d` directory is populated with symlinks to the scripts in `/etc/init.d`. Each script in `/etc/init.d` accepts `enable` and `disable` arguments for creating and removing the symlinks.
8.  These script initialize the system and also initialize daemons that wait for input, so that when all the scripts have executed the normal system is active. On first boot this initializing includes the process of preparing the root filesystem for use.

------------------------------------------------------------------------

# Overview

The following preinit scripts are available in the OpenWrt master branches for base and packages feed (Status September 2024)

|          |                  |             |             |                                                                                    |                                            |                    |                       |
|:---------|:-----------------|:------------|:------------|:-----------------------------------------------------------------------------------|:-------------------------------------------|:-------------------|:----------------------|
| repo     | packages         | target      | subtarget   | file-repo                                                                          | file-target                                | hook               | info                  |
| packages | openssh          | all         | all         | net/openssh/files/sshd.failsafe                                                    | /lib/preinit/99_10_failsafe_sshd           | failsafe           |                       |
| packages | btrfs-progs      | all         | all         | utils/btrfs-progs/files/btrfs-scan.init                                            | /lib/preinit/85_btrfs_scan                 | preinit_main       | INITRAMFS check 'NO'  |
| packages | lvm2             | all         | all         | utils/lvm2/files/lvm2.preinit                                                      | /lib/preinit/80_lvm2                       | preinit_main       | INITRAMFS check 'NO'  |
| base     | dropbear         | all         | all         | package/network/services/dropbear/files/dropbear.failsafe                          | /lib/preinit/99_10_failsafe_dropbear       | failsafe           |                       |
| base     | zyxel-bootconfig | all         | all         | package/utils/zyxel-bootconfig/files/95_apply_bootconfig                           | /lib/preinit/95_apply_bootconfig           | preinit_main       | INITRAMFS check 'YES' |
| base     | linux            | imx         | cortexa53   | target/linux/imx/cortexa53/base-files/lib/preinit/79_move_config                   | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | imx         | cortexa7    | target/linux/imx/cortexa7/base-files/lib/preinit/79_move_config                    | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | imx         | cortexa9    | target/linux/imx/cortexa9/base-files/lib/preinit/79_move_config                    | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | rockchip    | armv8       | target/linux/rockchip/armv8/base-files/lib/preinit/79_move_config                  | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | omap        |             | target/linux/omap/base-files/lib/preinit/79_move_config                            | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | qoriq       |             | target/linux/qoriq/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | sifiveu     |             | target/linux/sifiveu/base-files/lib/preinit/79_move_config                         | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | tegra       |             | target/linux/tegra/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | sunxi       |             | target/linux/sunxi/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/02_default_set_state                          | /lib/preinit/02_default_set_state          | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/02_sysinfo                                    | /lib/preinit/02_sysinfo                    | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/10_indicate_failsafe                          | /lib/preinit/10_indicate_failsafe          | failsafe           |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/10_indicate_preinit                           | /lib/preinit/10_indicate_preinit           | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/30_failsafe_wait                              | /lib/preinit/30_failsafe_wait              | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/40_run_failsafe_hook                          | /lib/preinit/40_run_failsafe_hook          | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/50_indicate_regular_preinit                   | /lib/preinit/50_indicate_regular_preinit   | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/70_initramfs_test                             | /lib/preinit/70_initramfs_test             | preinit_main       |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/80_mount_root                                 | /lib/preinit/80_mount_root                 | preinit_main       | INITRAMFS check 'YES' |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/99_10_failsafe_login                          | /lib/preinit/99_10_failsafe_login          | failsafe           |                       |
| base     | base-files       | all         | all         | package/base-files/files/lib/preinit/99_10_run_init                                | /lib/preinit/99_10_run_init                | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | bcm47xx     |             | target/linux/bcm47xx/base-files/lib/preinit/01_sysinfo                             | /lib/preinit/01_sysinfo                    | preinit_main       |                       |
| base     | linux            | lantiq      | xway_legacy | target/linux/lantiq/xway_legacy/base-files/lib/preinit/05_set_preinit_iface_lantiq | /lib/preinit/05_set_preinit_iface_lantiq   | preinit_main       |                       |
| base     | linux            | lantiq      | xway        | target/linux/lantiq/xway/base-files/lib/preinit/05_set_preinit_iface_lantiq        | /lib/preinit/05_set_preinit_iface_lantiq   | preinit_main       |                       |
| base     | linux            | lanitq      | ase         | target/linux/lantiq/ase/base-files/lib/preinit/05_set_preinit_iface_lantiq         | /lib/preinit/05_set_preinit_iface_lantiq   | preinit_main       |                       |
| base     | linux            | armsr       |             | target/linux/armsr/base-files/lib/preinit/01_sysinfo_acpi                          | /lib/preinit/01_sysinfo_acpi               | preinit_main       |                       |
| base     | linux            | armsr       |             | target/linux/armsr/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/02_load_x86_ucode                          | /lib/preinit/02_load_x86_ucode             | preinit_main       |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/15_essential_fs_x86                        | /lib/preinit/15_essential_fs_x86           | ?                  |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/20_check_iso                               | /lib/preinit/20_check_iso                  | preinit_mount_root |                       |
| base     | linux            | x86         |             | target/linux/x86/base-files/lib/preinit/79_move_config                             | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | x86         |             | target/linux/x86/generic/base-files/lib/preinit/45_mount_xenfs                     | /lib/preinit/45_mount_xenfs                | preinit_mount_root |                       |
| base     | linux            | x86         | 64          | target/linux/x86/64/base-files/lib/preinit/45_mount_xenfs                          | /lib/preinit/45_mount_xenfs                | preinit_mount_root |                       |
| base     | linux            | bcm27xx     |             | target/linux/bcm27xx/base-files/lib/preinit/05_set_preinit_iface_brcm2708          | /lib/preinit/05_set_preinit_iface_brcm2708 | preinit_main       |                       |
| base     | linux            | bcm27xx     |             | target/linux/bcm27xx/base-files/lib/preinit/79_move_config                         | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | bcm27xx     |             | target/linux/bcm27xx/base-files/lib/preinit/81_set_root_part                       | /lib/preinit/81_set_root_part              | preinit_main       | INITRAMFS check 'YES' |
| base     | linux            | mediatek    |             | target/linux/mediatek/base-files/lib/preinit/05_set_preinit_iface                  | /lib/preinit/05_set_preinit_iface          | preinit_main       |                       |
| base     | linux            | mediatek    |             | target/linux/mediatek/base-files/lib/preinit/06_set_rps_sock_flow                  | /lib/preinit/06_set_rps_sock_flow          | preinit_main       |                       |
| base     | linux            | mediatek    |             | target/linux/mediatek/base-files/lib/preinit/07_trigger_fip_scrubbing              | /lib/preinit/07_trigger_fip_scrubbing      | preinit_main       |                       |
| base     | linux            | mediatek    | mt7623      | target/linux/mediatek/mt7623/base-files/lib/preinit/07_set_iface_mac               | /lib/preinit/07_set_iface_mac              | preinit_main       |                       |
| base     | linux            | mediatek    | mt7623      | target/linux/mediatek/mt7623/base-files/lib/preinit/79_move_config                 | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/04_set_netdev_label           | /lib/preinit/04_set_netdev_label           | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/05_extract_factory_data.sh    | /lib/preinit/05_extract_factory_data.sh    | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/09_mount_cfg_part             | /lib/preinit/09_mount_cfg_part             | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/10_fix_eth_mac.sh             | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | mediatek    | filogic     | target/linux/mediatek/filogic/base-files/lib/preinit/75_rootfs_prepare             | /lib/preinit/75_rootfs_prepare             | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | apm821xx    |             | target/linux/apm821xx/base-files/lib/preinit/05_set_preinit_iface_apm821xx         | /lib/preinit/05_set_preinit_iface_apm821xx | preinit_main       |                       |
| base     | linux            | apm821xx    |             | target/linux/apm821xx/base-files/lib/preinit/05_set_iface_mac_apm821xx             | /lib/preinit/05_set_iface_mac_apm821xx     | preinit_main       |                       |
| base     | linux            | apm821xx    |             | target/linux/apm821xx/base-files/lib/preinit/79_move_config                        | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | ixp4xx      |             | target/linux/ixp4xx/base-files/lib/preinit/05_set_ether_mac_ixp4xx                 | /lib/preinit/05_set_ether_mac_ixp4xx       | preinit_main       |                       |
| base     | linux            | kirkwood    |             | target/linux/kirkwood/base-files/lib/preinit/07_set_iface_mac                      | /lib/preinit/07_set_iface_mac              | preinit_main       |                       |
| base     | linux            | mvebu       |             | target/linux/mvebu/base-files/lib/preinit/79_move_config                           | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | mvebu       | cortexa53   | target/linux/mvebu/cortexa53/base-files/lib/preinit/82_uDPU                        | /lib/preinit/82_uDPU                       | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | mvebu       | cortexa9    | target/linux/mvebu/cortexa9/base-files/lib/preinit/81_linksys_syscfg               | /lib/preinit/81_linksys_syscfg             | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | ipq806x     |             | target/linux/ipq806x/base-files/lib/preinit/04_reorder_eth                         | /lib/preinit/04_reorder_eth                | preinit_main       |                       |
| base     | linux            | ath79       | generic     | target/linux/ath79/generic/base-files/lib/preinit/02_sysinfo_fixup                 | /lib/preinit/02_sysinfo_fixup              | preinit_main       |                       |
| base     | linux            | ath79       | generic     | target/linux/ath79/generic/base-files/lib/preinit/10_fix_eth_mac.sh                | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | ath79       | nand        | target/linux/ath79/nand/base-files/lib/preinit/10_fix_eth_mac.sh                   | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | bcm4908     |             | target/linux/bcm4908/base-files/lib/preinit/75_rootfs_prepare                      | /lib/preinit/75_rootfs_prepare             | preinit_main       | INITRAMFS check 'NO'  |
| base     | linux            | gemini      |             | target/linux/gemini/base-files/lib/preinit/05_set_ether_mac_gemini                 | /lib/preinit/05_set_ether_mac_gemini       | preinit_main       |                       |
| base     | linux            | loongarch64 |             | target/linux/loongarch64/base-files/lib/preinit/01_sysinfo_acpi                    | /lib/preinit/01_sysinfo_acpi               | preinit_main       |                       |
| base     | linux            | loongarch64 |             | target/linux/loongarch64/base-files/lib/preinit/79_move_config                     | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | mpc85xx     |             | target/linux/mpc85xx/base-files/lib/preinit/05_set_preinit_iface_mpc85xx           | /lib/preinit/05_set_preinit_iface_mpc85xx  | preinit_main       |                       |
| base     | linux            | mpc85xx     |             | target/linux/mpc85xx/base-files/lib/preinit/10_fix_eth_mac.sh                      | /lib/preinit/10_fix_eth_mac.sh             | preinit_main       |                       |
| base     | linux            | layerscape  |             | target/linux/layerscape/base-files/lib/preinit/02_sysinfo_fixup                    | /lib/preinit/02_sysinfo_fixup              | preinit_main       |                       |
| base     | linux            | layerscape  |             | target/linux/layerscape/base-files/lib/preinit/79_move_config                      | /lib/preinit/79_move_config                | preinit_mount_root |                       |
| base     | linux            | ramips      | mt7621      | target/linux/ramips/mt7621/base-files/lib/preinit/04_set_netdev_label              | /lib/preinit/04_set_netdev_label           | preinit_main       |                       |
| base     | linux            | ramips      | rt305x      | target/linux/ramips/rt305x/base-files/lib/preinit/04_handle_checksumming           | /lib/preinit/04_handle_checksumming        | preinit_main       |                       |
| base     | linux            | ramips      | rt3883      | target/linux/ramips/rt3883/base-files/lib/preinit/04_handle_checksumming           | /lib/preinit/04_handle_checksumming        | preinit_main       |                       |
| base     | linux            | ipq40xx     |             | target/linux/ipq40xx/base-files/lib/preinit/05_set_iface_mac_ipq40xx.sh            | /lib/preinit/05_set_iface_mac_ipq40xx.sh   | preinit_main       |                       |
| base     | linux            | octeon      |             | target/linux/octeon/base-files/lib/preinit/01_sysinfo                              | /lib/preinit/01_sysinfo                    | preinit_main       |                       |
| base     | linux            | octeon      |             | target/linux/octeon/base-files/lib/preinit/79_move_config                          | /lib/preinit/79_move_config                | preinit_mount_root |                       |

## Preinit

Preinit brings the system from raw kernel to ready for multiuser. To do so, as of April, 2018, `/etc/preinit` (ar71xx, Archer C7) performs the following tasks:

1.  Checks to see if `$PREINIT` is empty; if so `exec /sbin/init` and skip the rest
2.  Sources a set of files for common functions for boot/mount:
    - `/lib/functions.sh`
    - `/lib/functions/preinit.sh`
    -  `/lib/functions/system.sh`
3.  Prepares the "hooks" for the various stages of the preinit process
    - preinit_essential
    - preinit_main
    - failsafe
    - initramfs
    - preinit_mount_root
4.  Source the contents of `/lib/preinit/*` which generally add `sh` functions to the appropriate hooks
5.  Runs the `preinit_essential` hooks
6.  Runs the `preinit_main` hooks

On an ar71xx device (Archer C7) the default functions added to the various hooks include (with functions from device-specific files in *italics):*

- **preinit_main**
  1.  *do_ar71xx*
  2.  define_default_set_state
  3.  do_sysinfo_generic
  4.  *preinit_set_mac_address*
  5.  *set_preinit_iface*
  6.  preinit_ip
  7.  pi_indicate_preinit
  8.  failsafe_wait
  9.  run_failsafe_hook
      - **failsafe** (if "\$pi_preinit_no_failsafe" != "y" and "\$FAILSAFE" = "true")
        1.  indicate_failsafe
        2.  failsafe_netlogin
        3.  failsafe_shell
  10. indicate_regular_preinit
  11. do_mount_root (if "\$INITRAMFS" != "1")
  12. do_urandom_seed
  13. *check_patch_ath10k_firmware*
  14. run_init

Presently unused hooks, at least for the ar71xx Archer C7, appear to include

- preinit_essential
- initramfs
- preinit_mount_root

## Failsafe

The *root file system* is actually an overlay which can be consisted of a read-only SquashFS file system (mounted at `/rom`) and a writable JFFS2 partition (mounted under `/overlay`). In Failsafe mode only the squashfs FS will be mounted (changes made to jffs2 partitons will be ignored), plus the following steps:

1.  Notifies that failsafe mode is being entered (indicate_failsafe)
2.  Launches daemon to allow network logins (failsafe_netlogin)
3.  Allows login via serial console, if there is one (failsafe_shell)
    - If the serial console login process exits, failsafe doesn't exit, but restarts the process for additional logins.

## Mount Root Filesystem

all_jffs2 refers to a 'jffs2' target in menuconfig; e.g. firmware has no squashfs, but is purely a rw filesystem (jffs2), while, jffs2 in the following text refers to the jffs2 portion of a [squashfs/jffs2](/docs/techref/filesystems#overlayfs) system.

1.  Kernel has previously mounted squashfs partition by scanning the mtd partition `rootfs` for a valid superblock (see step 2 of [preinit_mount#contextboot.sequencel](/docs/techref/preinit_mount#contextboot.sequencel)) FIXME **Make sure it's correct**
2.  If there is no mtd device with label `rootfs_data`, then mounts `/dev/root` (e.g. squashfs or all_jffs2 with no squashfs) as root filesystem, and indicates that further steps should be skipped
3.  If mtd device `rootfs_data` has not already been formatted, mounts a tmpfs (ramdisk) as root filesystem, and indicates that further steps should be skipped.
4.  Mounts previously formatted jffs2 partition on `/overlay` and indicates successful mount.
5.  Makes successfully mounted `/overlay` (if it exists) the new root filesystem and moves previous root filesystem to `/rom`, and indicates to skip further steps.
6.  This is only reached on an error condition; attempts to mount a tmpfs (ramdisk) as root filesystem
7.  This is only reached if no other step succeeds; attempt to mount `/dev/root` (e.g. squashfs/all_jffs2) as root filesystem.

\*\* \* \*\* `/overlay` was previously named `/jffs2`.
\*\* \* \*\* [NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md): If volatile files (e.g. a config) were preserved across firmware update via `sysupgrade`, step 3 is skipped. Instead, preinit_main hangs while the rootfs_data partition is formatted and the jffs2 overlay is mounted. Hypothetically, this is fatal on systems with weak cpu and exceptionally large rootfs_data partitions. For more information [consult this forum post](https://forum.openwrt.org/t/error-in-preinit-documentation-regarding-overlays/60188/4).

## First Boot

Updated to version 23.05. And, likely applies to a number of previous versions.

`/sbin/firstboot` is a script that simply calls `/sbin/jffs2reset $@` which clears the overlay if it's mounted:

- -y Answer yes to "Are you sure?"
- -r Reboot instead of returning control to the caller.
- -k Keep the file `/sysupgrade.tgz` while clearing the overlay.

`/lib/preinit/80_mount_root` will extract the contents of `/sysupgrade.tgz` into the overlay after the reboot. This mechanism may be used to write into `/etc/uci-defaults` as a way to create a custom configuration immediately after the reboot.

### Common

1.  Source `/lib/functions/boot.sh` for common functions (e.g. also used by preinit)
2.  Source files used by hooks
3.  Determine how called, and branch to appropriate commands.

### Sourced rather than executed

1.  Determine (and set variable for) MTD rootfs_data partition
2.  Determine (and set variable for) rom partition
3.  Determine (and set variable for) jffs2 partition

### Executed with no parameters

- Resets jffs2 to original settings, if possible.
- If jffs2 is not mounted, erases mtd and attempts format, mount, and pivot jffs2 as root.

If jffs2 is mounted, `firstboot` runs hook `jffs2reset`

1.  Determine (and set variable for) MTD rootfs_data partition
2.  Determine (and set variable for) rom partition
3.  Determine (and set variable for) jffs2 partition
4.  Determine (and set variable to indicate) whether the mini overlay filesystem type is supported.
5.  If overlay is supported, remove all files on jffs2 and remount it.
6.  If overlay not supported, create directories and symlinks, copying only certain critical files

- Note: since r35712 the firstboot script requires an inputted 'y' as confirmation. If using firstboot in a reset button script, you need to get that y inputted, e.g. by using the yes command: yes \| firstboot

### Executed with parameter 'switch2jffs'

1.  Determine (and set variable for) MTD rootfs_data partition
2.  Determine (and set variable for) rom partition
3.  Determine (and set variable for) jffs2 partition
4.  Determine if mini overlay is supported. If not run hook no_fo
5.  Otherwise, if mounted, skip the rest, otherwise mount under squashfs (`/rom/jffs`)
6.  Copy ramdisk to jffs2
7.  Move `/jffs` to `/` (root) and move `/` (root) to `/rom`
8.  Cleanup

### hook no_fo

1.  Switch to kernel fs, get rid of union overlay and bind from /tmp/root
2.  Mount jffs (and make it safe for union)
3.  If not mounted, mount; copy from squashfs, and pivot so that /jffs is now / (root)
4.  Copy files from ramdisk
5.  Get rid of unnecessary mounts (cleanup)

# Preinit Operation

Preinit consists of a number of scripts. The main script is `/etc/preinit` which reads in the scripts. The scripts define functions which they attach to hooks. These hooks are, when processed, launching the functions in the order they were added to the hooks.

Currently there are five hooks used by the preinit system:

- `preinit_essential`
- `preinit_main`
- `failsafe`
- `initramfs`
- `preinit_mount_root`

Each hook have a corresponding string variable containing the name of each function to be executed, separated by spaces. The hook variables have `_hook` appended to the hook name. Thus the name of the variable for the `preinit_essential` hook is `preinit_essential_hook`.

## Main Preinit Script

The main preinit script is actually quite empty. It:

1.  Initializes some variables (including the hook variables)
2.  Defines the function `pi_hook_add`, which is used to add functions to a hook
3.  Defines the function `pi_run_hook`, which executes the functions that were added to a hook
4.  Sources (reads) the shell scripts under folder `/lib/preinit/`, in glob sort order
5.  Processes the hook `preinit_essential`
6.  Initializes variables used by `preinit_main`
7.  Processes the hook `preinit_main`

That's it.

## Variables

There are a number of variables that control options of preinit. Defaults are defined in the main script `/etc/preinit` defined by the `base-files` package. However the variables are customizable via `make menuconfig`, in section "Preinit configuration options". The OpenWrt build process will then create the file `/lib/preinit/00_preinit.conf` which will be sourced by the main script.

The variables defined at present are:

| Variable                        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|:--------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `pi_ifname`                     | The device name of the network interface used to emit network messages during preinit (except failsafe)                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `pi_ip`                         | The IP address of the preinit network (see above)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `pi_broadcast`                  | The broadcast address of the preinit network (see above)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `pi_netmask`                    | The netmask for the preinit network (see above)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `fs_failsafe_wait_timeout`      | How long to pause while allowing the user to choose to enter failsafe mode. Default is two (2) seconds.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `pi_suppress_stderr`            | If this is "y", then output on standard error (stderr, file descriptor 2), is ignored during preinit. This is the default in previous versions of OpenWrt (which did not have this option)                                                                                                                                                                                                                                                                                                                                                      |
| `pi_init_suppress_stderr`       | If `pi_suppress_stderr` is not "y" (i.e. stderr is not suppressed for preinit), then this option controls whether init, and process run by init, except those associated with a terminal device (e.g. `tts/0`, `ttyS0`, `tty1`, `pts/0`, or other similar devices) will have stderr suppressed (not that network terminals such as those from SSH are associated with a pseudo-terminal device such as `pty0/pty1` and are thus unaffected). As with `pi_suppress_stderr`, the default, and behaviour from previous versions of OpenWrt is "y". |
| `pi_init_path`                  | The default search PATH for binaries for commands run by init. Default is `/bin:/sbin:/usr/bin:/usr/sbin`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `pi_init_cmd`                   | The command to run as `init`. Default is `/sbin/init`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `pi_preinit_no_failsafe_netmsg` | suppress netmsg to say that one can enter failsafe mode                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `pi_preinit_net_messages`       | If enabled, show more network messages than just the message that one can enter failsafe mode                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

There are also variables used in the operation of preinit. They are:

| Variable                  | Description                                                                                                        |
|:--------------------------|:-------------------------------------------------------------------------------------------------------------------|
| `preinit_essential_hook`  | Variable containing hook names to execute, in order, for hook `preinit_essential`                                  |
| `preinit_main_hook`       | Ditto, for `preinit_main`                                                                                          |
| `failsafe_hook`           | Ditto, for `failsafe`                                                                                              |
| `initramfs_hook`          | Ditto, for `initramfs`                                                                                             |
| `preinit_mount_root_hook` | Ditto, for `preinit_mount_root`                                                                                    |
| `pi_mount_skip_next`      | During hook `preinit_mount_root`, skips most steps; usually set by a preceeding step                               |
| `pi_jffs2_mount_success`  | During hook `preinit_mount_root`, used by steps following mount attempt to determine which action they should take |

## Hooks

The following sections describe the files and functions used by the various hooks.

**NB**: The files, even though divided by hook here are all in the single `/lib/preinit` directory, and are thus combined in the directory lists, and are processed in glob sort order, not by hook (when sourcing them, the hooks specify the order of the execution of functions, which is as listed below)

### Development

For the purposes of development, you will locate the files under `$ROOTDIR/package/base-files/files/lib/preinit`, for the existing files, and you can add new files anywhere that ultimately ends up in `/lib/preinit` on the router (while in preinit, e.g. not by user edits after read-write is mounted).

### preinit_essentials

:!: With the introduction of [procd](/docs/techref/procd), effective in Chaos Calmer release, the tasks of this hook are done in c code and at least on some images (verified on a BRCM63xx one) this hook is unused.

The preinit_essentials hook takes care of mounting essential kernel filesystems such as proc, and initializing the console.

Files containing the functions executed by this hook

| File               | Functions                                                         |
|:-------------------|:------------------------------------------------------------------|
| 10_essential_fs    | do_mount_procfs, do_mount_sysfs, do_mount_tmpfs                   |
| 20_device_fs_mount | do_mount_devfs, do_mount_hotplug, do_mount_udev, choose_device_fs |
| 30_device_daemons  | init_hotplug, init_udev, init_device_fs                           |
| 40_init_shm        | init_shm                                                          |
| 40_pts_mount       | do_mount_pts                                                      |
| 50_choose_console  | choose_console                                                    |
| 60_init_console    | init_console                                                      |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function         | Description                                                                                                                                                |
|:-----------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| do_mount_procfs  | mounts /proc                                                                                                                                               |
| do_mount_sysfs   | mounts /sys                                                                                                                                                |
| do_mount_tmpfs   | mounts /tmp                                                                                                                                                |
| choose_device_fs | determines type of device daemon and the appropriate filesystem to mount on /dev for that device daemon                                                    |
| init_device_fs   | launches daemons (if any) responsible for population /dev, and/or creating hotplug events when devices are added/removed (and for initial coldplug events) |
| init_shm         | makes sure /dev/shm exists                                                                                                                                 |
| init_pts         | makes sure /dev/pts exists                                                                                                                                 |
| do_mount_pts     | mounts devpts on /dev/pts (pseudo-terminals)                                                                                                               |
| choose_console   | determines devices for stdin, stdout, and stderr                                                                                                           |
| init_console     | activates stdin, stdout, and stderr of preinit (and subsequent init) (prior to this they are not present in the environment)                               |

Functions which are called by other functions, rather than directly as part of a hook

| Function         | Description                                                 |
|:-----------------|:------------------------------------------------------------|
| do_mount_devfs   | mount devfs on /dev                                         |
| do_mount_hotplug | mount tmpfs on /dev (for hotplug)                           |
| do_mount_udev    | mount tmpfs on /dev (for udev)                              |
| init_hotplug     | set hotplug handler (actually initiated after console init) |
| init_udev        | start udev                                                  |

### preinit_main

The *preinit_main* hook performs all the functions required of preinit, except those functions, like console, that are essential even for preinit tasks.

| File                        | Description                                                                                           |
|:----------------------------|:------------------------------------------------------------------------------------------------------|
| 10_indicate_preinit         | preinit_ip, preinit_ip_deconfig, preinit_net_echo, preinit_echo, pi_indicate_led, pi_indicate_preinit |
| 30_failsafe_wait            | fs_wait_for_key, failsafe_wait                                                                        |
| 40_run_failsafe_hook        | run_failsafe_hook                                                                                     |
| 50_indicate_regular_preinit | indicate_regular_preinit_boot                                                                         |
| 60_init_hotplug             | init_hotplug                                                                                          |
| 70_initramfs_test           | initramfs_test                                                                                        |
| 80_mount_root               | do_mount_root                                                                                         |
| 90_restore_config           | restore_config                                                                                        |
| 99_10_run_init              | run_init                                                                                              |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function                      | Description                                                                                                                                                                                                |
|:------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| init_hotplug                  | Initialize hotplug, if needed (that is for devfs). Hotplug or a device daemon is needed so that devices are available for use for preinit                                                                  |
| preinit_ip                    | Initialize network interface (if one has been defined for as available for preinit)                                                                                                                        |
| pi_indicate_preinit           | Send messages to console, network, and/or led, depending on which, if any, of these is present which say that we are in preinit mode                                                                       |
| failsafe_wait                 | Emits messages (to network and console) that indicate the user has the option to enter failsafe mode and wait for the configured period of time (default two seconds) for the user to select failsafe mode |
| run_failsafe_hook             | If user chooses to enter failsafe mode, run the \*failsafe\* hook (which at present doesn't return, which means no more functions from preinit_main get run on this boot)                                  |
| indicate_regular_preinit_boot | Emits messages to network, console, and/or LED depending on which (if any) is present, indicating that it's a regular boot not a failsafe boot                                                             |
| initramfs_test                | If initramfs is present run the \*initramfs\* hook and exit                                                                                                                                                |
| do_mount_root                 | Executes hook \*preinit_mount_root\*                                                                                                                                                                       |
| restore_config                | If a previous configuration was stored by sysupgrade, restore it to the rootfs                                                                                                                             |
| run_init                      | Exec the command defined by \`pi_init_cmd\` with the environment variables defined by \`pi_init_env\`, plus PATH \`pi_init_path\`                                                                          |

Functions which are called by other functions, rather than directly as part of a hook.

| Function            | Description                                                                 |
|:--------------------|:----------------------------------------------------------------------------|
| preinit_ip_deconfig | deconfigure interface used for preinit network messages etc                 |
| preinit_net_echo    | emit a message on the preinit network interface                             |
| preinit_echo        | emit a message on the (serial) console                                      |
| pi_indicate_led     | set LED status to indicate preinit mode                                     |
| fs_wait_for_key     | wait for reset button press, CTRL-C, or \<some_key\>\<ENTER\>, with timeout |

### failsafe

Do what needs to done to prepare failsafe mode and enter it.

| File                 | Description                              |
|:---------------------|:-----------------------------------------|
| 10_indicate_failsafe | indicate_failsafe_led, indicate_failsafe |
| 99_10_failsafe_login | failsafe_netlogin, failsafe_shell        |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function          | Description                                                                                                                                      |
|:------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
| indicate_failsafe | Emit message/status to network, console, and/or LED (depending on which, if any, are present) indicating that the device is now in failsafe mode |
| failsafe_netlogin | Launch telnet daemon to allow telnet login on the defined network interface (if any)                                                             |
| failsafe_shell    | Launch a shell for access via serial console (if present)                                                                                        |

Functions which are called by other functions, rather than directly as part of a hook

| Function              | Description                             |
|:----------------------|:----------------------------------------|
| indicate_failsafe_led | set LED status to indicate preinit mode |

### preinit_mount_root

Mount the root filesystem

| File             | Description                 |
|:-----------------|:----------------------------|
| 05_mount_skip    | check_skip                  |
| 10_check_for_mtd | mount_no_mtd, check_for_mtd |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function          | Description                                                                                                                          |
|:------------------|:-------------------------------------------------------------------------------------------------------------------------------------|
| check_for_mtd     | Check for a mtd partition named rootfs_data. If not present mount kernel fs as root (e.g. all_jjfs2 or squashfs only) and skip rest. |
| check_for_jffs2   | Check if jffs2 formatted yet. If not, mount ramoverlay and skip rest                                                                 |
| do_mount_jffs2    | find jffs2 partition and mount it, indicating result                                                                                 |
| rootfs_pivot      | if jffs2 mounted, make it root (/) and old root (squashfs) /rom , skipping rest on success                                           |
| do_mount_no_jffs2 | If nothing was mounted so far, mount ramdisk (ram overlay), skipping rest on success                                                 |
| do_mount_no_mtd   | If there was nothing mounted , mount /dev/root as root (/)                                                                           |

Functions which are called by other functions, rather than directly as part of a hook

| Function          | Description                                                                                                                                                                   |
|:------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mount_no_mtd      | if there is not mtd partition named rootfs_data, mount /dev/root as / (root). E.g. this can occur if the firmware filesystem is entirely a jffs2 partition, with no squashfs) |
| mount_no_jffs2    | mount ramdisk (ram overlay) if there is rootfs_data, but it has not been formatted yet)                                                                                       |
| find_mount_jffs2  | find and mount rootfs_data jffs2 partition on /jffs                                                                                                                           |
| jffs2_not_mounted | returns true (0) if jffs2 is not mounted                                                                                                                                      |

### initramfs

No files or functions at this time.

# Firstboot Operation

## Main Firstboot Script

1.  Source common functions
2.  Source functions for hooks
3.  if block:

      if invoked as executable
           if called with `switch2jffs` parameter (i.e. from rcS)
               run hook `switch2jffs`
           if called standalone (e.g. from commandline)
               if there is a jffs2 partition mounted
                    run hook `jffs2reset`
               else
                    erase rootfs_data mtd partition
                    format
                    and remount it
               end
           end
     if sourced (that is not executed)
          set some variables
     end

## Hooks

### switch2jffs

Make the filesystem that we want to be the rootfs, to be the rootfs

| File                  | Description                                                                                               |
|:----------------------|:----------------------------------------------------------------------------------------------------------|
| 10_determine_parts    | deterimine_mtd_part, determine_rom_part, determine_jffs2_part, set_mtd_part, set_rom_part, set_jffs2_part |
| 20_has_mini_fo        | check_for_mini_fo                                                                                         |
| 30_is_rootfs_mounted  | skip_if_rootfs_mounted                                                                                    |
| 40_copy_ramoverlay    | copy_ramoverlay                                                                                           |
| 50_pivot              | with_fo_pivot                                                                                             |
| 99_10_with_fo_cleanup | with_fo_cleanup                                                                                           |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function               | Description                                                                                                   |
|:-----------------------|:--------------------------------------------------------------------------------------------------------------|
| determine_mtd_part     | exit if no mtd partition at all                                                                               |
| determine_rom_part     | exit if not squashfs partition (firstboot not for all_jffs2)                                                  |
| determine_jffs2_part   | figure out the jffs2 partition (assuming we have an mtd part                                                  |
| check_for_mini_fo      | determine if we have [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md) overlay in kernel. If not run \*no_fo\* hook                                     |
| skip_if_rootfs_mounted | attempt mount jffs2 on /rom/jffs2. If partition already mounted exit                                          |
| copy_ramoverlay        | copy the data from the temporary rootfs (on the ramdisk overlay over the squashfs) to the new jffs2 partition |
| with_fo_pivot          | make current jffs2 partition the root partition and the current root /rom                                     |
| with_fo_cleanup        | clean up unneeded mount of ramdisk, if possible                                                               |

Functions which are called by other functions, rather than directly as part of a hook

| Function      | Description                               |
|:--------------|:------------------------------------------|
| set_mtd_part  | set variables for mtd partition           |
| set_rom_part  | set variable for squashfs (rom) partition |
| set_jffs_part | set variable for jffs2 partition          |

### no_fo

Make the filesystem that we want to be the rootfs, to be the rootfs, given that we have no mini\\fo overlay filesystem

| File                      | Description            |
|:--------------------------|:-----------------------|
| 10_no_fo_clear_overlay    | no_fo_clear_overlay    |
| 20_no_fo_mount_jffs       | no_fo_mount_jffs       |
| 30_no_fo_pivot            | no_fo_pivot            |
| 40_no_fo_copy_ram_overlay | no_fo_copy_ram_overlay |
| 99_10_no_fo_cleanup       | no_fo_cleanup          |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function               | Description                                                                     |
|:-----------------------|:--------------------------------------------------------------------------------|
| no_fo_clear_overlay    | stop ramdisk overlaying the squashfs                                            |
| no_fo_mount_jffs       | attempt to mount jffs (work around problem with union). If already mounted exit |
| no_fo_pivot            | make jffs root and old root /rom                                                |
| no_fo_copy_ram_overlay | copy data from ram overlay to jffs2 overlay of squashfs                         |
| no_fo_cleanup          | get rid of extra binds and mounts                                               |

### jffs2reset

Reset jffs2 to defaults

| File                | Description             |
|:--------------------|:------------------------|
| 10_rest_has_mini_fo | reset_check_for_mini_fo |
| 20_reset_clear_jffs | reset_clear_jffs        |
| 30_reset_copy_rom   | reset_copy_rom          |

Functions, in order, executed by this hook (doesn't list the functions only called by other functions)

| Function                | Description                                                                                             |
|:------------------------|:--------------------------------------------------------------------------------------------------------|
| reset_check_for_mini_fo | Determine if the kernel supports [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md) overlay                                                        |
| reset_clear_jffs        | if [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md) is supported, erase all data in overlay and remount (resets back to 'pure' squashfs versions |
| reset_copy_rom          | if [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md) is not supported, make symlinks and copy critical files from squashfs to jffs                |

# Customizing the system

**NB**: These files must be added to the \*squashfs\* (or if using a all_jffs2 system, to the jffs2). That means, for instance adding it to the image's rootfs. This can be done, for instace, by creating \`\${ROOTDIR}/files/filename\` (with appropriate substitutions of course).

## Overriding Example

![dangerous&noheader&nofooter&noeditbtn](/page>meta/infobox/dangerous&noheader&nofooter&noeditbtn)

Customizing the system is quite simple. We give an example of changing the message for preinit from '- preinit -' to '- setting the table for dinner -'

Create a file that replaces the function \`indicate_regular_preinit_boot\`. \`pi_indicate_preinit\` is defined in \`20_indicate_preinit\`, so we define our replace functions in \`25_dinner_not_router\`.

\`/lib/preinit/25_dinner_not_router\`

       pi_indicate_preinit() {
             echo "- setting the table for dinner -"
             preinit_net_echo "Dinner is just about ready!"
             pi_indicate_led
       }

This results in the following boot log:

      NET: Registered protocol family 17
      802.1Q VLAN Support v1.8 Ben Greear <greearb@candelatech.com>
      All bugs added by David S. Miller <davem@redhat.com>
      VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
      Freeing unused kernel memory: 132k freed
      Please be patient, while OpenWrt loads ...
      eth1: link forced UP - 100/full - flow control off/off
      - setting the table for dinner -
      Press CTRL-C or Press f<ENTER> to enter failsafe mode
      switching to jffs2
      [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md): using base directory: /
      [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md): using storage directory: /jffs
      - init -

The default boot log is

      NET: Registered protocol family 17
      802.1Q VLAN Support v1.8 Ben Greear <greearb@candelatech.com>
      All bugs added by David S. Miller <davem@redhat.com>
      VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
      Freeing unused kernel memory: 132k freed
      Please be patient, while OpenWrt loads ...
      eth1: link forced UP - 100/full - flow control off/off
      - preinit -
      Press CTRL-C or Press f<ENTER> to enter failsafe mode
      switching to jffs2
      [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md): using base directory: /
      [mini_fo](../wiki/chunked-reference/wiki_page-techref-filesystems.md): using storage directory: /jffs
      - init -

## Adding Example

As another example we will add a message to failsafe, between the notice that we're in failsafe mode in the shell. You could use this, for example, to create a text menu system, or to launch a simple web server (with cgi scripts) to permit the user to do failsafe things.

We want to add the message, 'Remember, at this point there are no writable filesystems'

We create the file \`50_failsafe_remember_no_rw\`, in \`/lib/preinit\`

      remember_no_rw() {
          echo "Remember, at this point there are no writable filesystems"
      }

      boot_hook_add failsafe remember_no_rw

This creates the function \`remember_no_rw\` and adds it to the failsafe hook, in between \`10_indicate_failsafe\` and \`99_10_failsafe_login\` which define the other functions in the \`failsafe\` hook. This wasn't necessary for the previous example because the function was already in a hook.

The boot log for this, when entering failsafe, is:

      VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
      Freeing unused kernel memory: 132k freed
      Please be patient, while OpenWrt loads ...
      eth1: link forced UP - 100/full - flow control off/off
      - preinit -
      Press CTRL-C or Press f<ENTER> to enter failsafe mode
      f
      - failsafe -
      Remember, at this point there are no writable filesystems

      BusyBox v1.15.3 (2010-01-20 19:26:26 EST) built-in shell (ash)
      Enter 'help' for a list of built-in commands.

      ash: can't access tty; job control turned off

        _______                     ________        __
       |       |.-----.-----.-----.|  |  |  |.----.|  |_
       |   -   ||  _  |  -__|     ||  |  |  ||   _||   _|
       |_______||   __|_____|__|__||________||__|  |____|
                    |__| W I R E L E S S   F R E E D O M

       KAMIKAZE (bleeding edge, r19235) ------------------
        * 10 oz Vodka       Shake well with ice and strain
        * 10 oz Triple sec  mixture into 10 shot glasses.
        * 10 oz lime juice  Salute!
       ---------------------------------------------------

# Architecture-specific notes

Some architectures have additional files and functions (or overrides of the above functions) in order to accommodate specific needs of that hardware. In that case the files are located in the source tree under `$ROOTDIR/target/linux/<architecture[/subarch]/base-files/lib/preinit`. During build they are merged and appear under `/lib/preinit` along with the rest.

---

# Procd system init and daemon management

**See also: [procd-init-scripts#procd_init_scripts](/docs/guide-developer/procd-init-scripts#procd_init_scripts)**

`procd` is the OpenWrt [process](https://en.wikipedia.org/wiki/Process (computing)) management daemon written in [C](https://en.wikipedia.org/wiki/C (programming language)). It keeps track of processes started from init scripts (via ubus calls), and can suppress redundant service start/restart requests when the config/environment has not changed.

`procd` has replaced ... , e.g.

- `hotplug2`, a dynamic device management subsystem for embedded systems. Hotplug2 is a trivial replacement of some of the UDev functionality in a tiny pack, intended for Linux early userspace: Init RAM FS and InitRD.
- `busybox-klogd` and `busybox-syslogd`
- `busybox-watchdog`

`procd` is intended to stay compatible with the existing format of `/etc/config/`; exceptions ...

## Help with the development of procd

1.  test what has been ported
2.  review of the code

## Buttons with procd

:!: see commit in <https://dev.openwrt.org/log/trunk/package/base-files/files/etc/rc.button>

:!: see use case [hardware.button](/docs/guide-user/hardware/hardware.button)

## Init scripts with procd

see [procd-init-scripts](/docs/guide-developer/procd-init-scripts)

## early state and preinit

Before the real procd runs, a small init process is started. This process has the job of early system init. It will do the following things in the listed order

- bring up basic mounts such as /proc /sys/{,fs/cgroup} /dev/{,shm,pts}
- create some required folder, /tmp/{run,lock,state}
- bring up /dev/console and map the processes stdin/out/err to the console (this is the "Console is alive" message)
- setup the PATH environment variable
- check if "init_debug=" is set in the kernel command line and apply the debug level if set
- initialise the watchdog
- start kmodloader and load the modules listed in /etc/modules-boot.d/
- start hotplug with the preinit rules (/etc/hotplug-preinit.json)
- start preinit scripts found inside /lib/preinit/

Once preinit is complete the init process is done and will do an exec on the real procd. This will replace init as pid1 with an instance of procd running as the new pid 1. The watchdog file descriptor is not closed. Instead it is handed over to the new procd process. The debug_level will also be handed over to the new procd instance if it was set via command line or during preinit.

## procd start up

Procd will first do some basic process init such as setting itself to be owner of its own process group and setting up signals. We are now ready to bring up the userland in the following order

- find out if a watchdog file descriptor was passed by the init process and start up the watchdog
- setup /dev/console to be our stdin/out/err
- start the coldplug process using the full rule set (/etc/hotplug.json). This is done by manually triggering all events that have already happened using udevtrigger
- start ubus, register it as a service and connect to it.

The basic system bringup is now complete, procd is up and running and can start handling daemons and services

## /etc/inittab

Procd supports four commands inside inittab

- respawn - this works just like you expect it. It starts a process and will respawn it once it has completed.
- respawnlate - this works like the respawn but will start the process only when the procd init is completed.
- askfirst - this works just like respawn but will print the line "Please press Enter to activate this console." before starting the process
- askconsole - this works like askfirst but, instead of running on the tty passed as a parameter, it will look for the tty defined in the kernel command line using "console="
- askconsolelate - this works like the askconsole but will start the process only when the procd init is completed.
- sysinit - this will trigger procd to run the command, given as a parameter, only once. This is usually used to trigger execution of /etc/rc.d/

Once all items inside /etc/inittab are processed, procd enter its normal run mode and will handle messages coming in via ubus. It will stay in this state until a reboot/shutdown is triggered.

## ubus command interface

## hotplug

Hotplug scripts are located inside /etc/hotplug.d and are based on json_script. This is a json based if then else syntax. Procd hotplug service offers the following actions:

- makedev
- rm
- exec
- button
- load-firmware

![construction&noheader&nofooter&noeditbtn](/page>meta/infobox/construction&noheader&nofooter&noeditbtn)

## procd (process management daemon) – Technical Reference

- [Project's git](http://git.openwrt.org/?p=project/procd.git;a=summary)
- procd is available in OpenWrt since [r34865 (trunk)](https://dev.openwrt.org/changeset/34865). It consists of files under GPLv2, LGPLv2.1 and ISC licenses.
- [commits to OpenWrt trunk regarding procd](https://dev.openwrt.org/search?q=procd&noquickjump=1&changeset=on)

## OpenWrt – operating system architecture

![architecture&noheader&nofooter](/page>docs/techref/architecture&noheader&nofooter)

### History

Package history is available at:

- current history: <https://dev.openwrt.org/log/trunk/package/system/procd>
- old history pre r37007 <https://dev.openwrt.org/log/trunk/package/procd/Makefile?rev=36995>

- [r34865: procd: add initial implementation](https://dev.openwrt.org/changeset/34865)
- [r34866: base-files: add basic procd integration, let procd start (and restart) ubus instead of having an ubus init script](https://dev.openwrt.org/changeset/34866)
- [r34867: dropbear: convert init script to procd](https://dev.openwrt.org/changeset/34867)
- [r36003: base-files: make basefiles aware of procd](https://dev.openwrt.org/changeset/36003)
- [r36005: busybox: make init and logread depend on !PROCD_INIT](https://dev.openwrt.org/changeset/36005)
- [r36446: hotplug2: make it depend on !PROCD_INIT](https://dev.openwrt.org/changeset/36446)
- [r36896: procd: make the preinit rules wildcard all buttons for failsafe](https://dev.openwrt.org/changeset/36896)
- [r36987: hotplug2: procd does the hotplugging now](https://dev.openwrt.org/changeset/36987)
- [r36998: base-files: procd is now the init process](https://dev.openwrt.org/changeset/36998)
- [r36999: base-files: diag does not need to insmod any drivers, procd already did it for us](https://dev.openwrt.org/changeset/36999)
- [r37000: base-files: input/button drivers get loaded before preinit by procd](https://dev.openwrt.org/changeset/37000)
- [r37002: base-files: /etc/init.d/rcS is no longer needed, procd handles this for us now](https://dev.openwrt.org/changeset/37002)
- [r37039: busybox: disable syslogd/klogd by default, procd replaces them](https://dev.openwrt.org/changeset/37039)
- [r37106: busybox: disable the watchdog utility by default (procd handles watchdog devices)](https://dev.openwrt.org/changeset/37106)
- [r37242, 37243, 37244: busybox: convert telnet, crond and sysntpd init scripts to procd](https://dev.openwrt.org/changeset/37242)
- [r37245: dropbear: register a config.change trigger: procd_add_config_trigger "dropbear" "/etc/init.d/dropbear" "restart"](https://dev.openwrt.org/changeset/37245)
- [r37429: procd: add proto and trigger support to the /etc/init.d/log](https://dev.openwrt.org/changeset/37249)
- [r37336: procd: make old button hotplug rules work until all packages are migrated](https://dev.openwrt.org/changeset/37336)

---

# The Boot Process

 As noted below, this page is woefully out of date

> [![NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md)]
> Please also see [requirements.boot.process](/docs/techref/requirements.boot.process)
>
> This guide it not up-to-date! It does not mention [procd](/docs/techref/procd)

This guide shall help you understand, e.g.

- When is it time for [kexec](/docs/guide-user/advanced/kexec) and when for [extroot_configuration](/docs/guide-user/additional-software/extroot_configuration) (see particularly [extroot.theory](/docs/guide-user/additional-software/extroot_configuration/extroot.theory))?
- How does the [OpenWrt FailSafe](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) work?
- the [flash.layout](/docs/techref/flash.layout) and the combination of [Utilization of file systems in OpenWrt](/docs/techref/filesystems#implementation_in_openwrt)
- When does the tmpfs get mounted and `/tmp` symlinked to it and `/var` symlinked to `/tmp`?

- [Preinit mount](/docs/techref/preinit_mount) Preinit, Mount Root, and First Boot Scripts
- [Init Scripts](/docs/techref/initscripts) Init script implementation reference
- [Block Mount](/docs/techref/block_mount) Block Device Mounting

## Process Trinity

The Machine gets powered on and some very very basic very low level hardware stuff gets done. You could connect to it over the [JTAG Port](/docs/techref/hardware/port.jtag) and issue commands.

### Bootloader

1.  the [bootloader](bootloader) on the flash gets executed
2.  the bootloader performs the [POST](https://en.wikipedia.org/wiki/Power-on self-test), which is a low-level hardware initialization
3.  the bootloader decompresses the Kernel image from its (known!) location on the flash storage into main memory (=RAM)
4.  the bootloader executes the Kernel with `init=...` option (default is ~~`/etc/preinit`~~ `/sbin/init`)

### Kernel

1.  the Kernel further bootstraps itself (sic!)
2.  issues the command/op-code `start_kernel`
3.  kernel scans the mtd partition *rootfs* for a valid superblock and mounts the SquashFS partition (which contains `/etc`) once found. (More info at [filesystems#technical_details](/docs/techref/filesystems#technical_details))
4.  `/etc/preinit` does pre-initialization setups (create directories, mount fs, /proc, /sys, ... )
5.  the Kernel `mounts` any other partition (e.g. jffs2 partition) under *rootfs (root file system)*. see [flash.layout](/docs/techref/flash.layout), [preinit and root mount](/docs/techref/preinit_mount#mount.root.filesystem), and also [udev](https://en.wikipedia.org/wiki/udev) FIXME **make sure**
6.  if "INITRAMFS" is not defined, calls `/sbin/init` (the mother of all processes)
7.  finally some *kernel thread* becomes the userspace `init` process

### Init

The user space starts when kernel mounts *rootfs* and the very first program to run is (by default) `/sbin/init`. Please remember, that the interface between application and kernel is the `clib` and the syscalls it offers.

1.  init reads `/etc/inittab` for the "sysinit" entry (default is "::sysinit:/etc/init.d/rcS S boot")
2.  init calls `/etc/init.d/rcS S boot`
3.  `rcS` executes the symlinks to the actual startup scripts located in `/etc/rc.d/S##xxxxxx` with option `"start"`:
4.  after rcS finishes, system should be up and running

#### Vanilla Startup Scripts

***[NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md):*** [](/Packages/) you install with `opkg` will likely add additional scripts!

|              |                                                                                                                                                                                                                 |
|:-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| S05defconfig | create config files with default values for platform (if config file is not exist), really does this on first start after OpenWrt installed (copy unexisted files from /etc/defconfig/\$board/ to /etc/config/) |
| S10boot      | starts hotplug-script, mounts filesystesm, starts .., starts syslogd, ...                                                                                                                                       |
| S39usb       | `mount -t usbfs none /proc/bus/usb`                                                                                                                                                                             |
| S40network   | start a network subsystem (run /sbin/netifd, up interfaces and wifi                                                                                                                                             |
| S45firewall  | create and implement firewall rules from /etc/config/firewall                                                                                                                                                   |
| S50cron      | starts `crond`, see -\> `/etc/crontabs/root` for configuration                                                                                                                                                  |
| S50dropbear  | starts `dropbear`, see -\> `/etc/config/dropbear` for configuration                                                                                                                                             |
| S50telnet    | checks for root password, if non is set, `/usr/sbin/telnetd` gets started                                                                                                                                       |
| S60dnsmasq   | starts `dnsmasq`, see -\> `/etc/config/dhcp` for configuration                                                                                                                                                  |
| S95done      | executes `/etc/rc.local`                                                                                                                                                                                        |
| S96led       | load a LED configuration from /etc/config/system and set up LEDs (write values to /sys/class/leds/\*/\*)                                                                                                        |
| S97watchdog  | start the watchdog daemon (/sbin/watchdog)                                                                                                                                                                      |
| S99sysctl    | interprets `/etc/sysctl.conf`                                                                                                                                                                                   |

The `init` daemon will run all the time. On a shutdown command, `init`

1.  reads `/etc/inittab` for shutdown (default is "::shutdodwn:/etc/init.d/rcS K stop")
2.  `init` calls `/etc/init.d/rcS K stop`
3.  rcS executes the shutdown scripts located in /etc/rc.d/K##xxxxxx with option "stop"
4.  system halts/reboots

|             |                                                    |
|-------------|----------------------------------------------------|
| K50dropbear | kill all instances of dropbear                     |
| K90network  | down all interfaces and stop netifd                |
| K98boot     | stop logger daemons: /sbin/syslogd and /sbin/klogd |
| K99umount   | writes caches to disk, unmounts all filesystems    |

## Detailed boot sequence

- [boot process example for blackfin devices](http://docs.blackfin.uclinux.org/doku.php?id=bootloaders)

### Boot loader

After the bootloader (grub, in this example) initializes and parses any options that are presented at the boot menu, the bootloader loads the kernel.

Example from the openwrt-x86-ext2-image.kernel file entry for normal boot:

- "kernel /boot/vmlinuz root=/dev/hda2 init=/etc/preinit \[rest of options\]"

This entry in the boot/grub/menu.lst file tells grub that the kernel is located under the /boot directory and the filename is vmlinuz. The rest of the lines are the options that are passed to the kernel. To see how the kernel was started, you can view the options by reading the /proc/cmdline file. You can see what options were passed from grub by logging into the device and typing "cat /proc/cmdline".

For my test system, the options that were passed to the kernel at load time was:

- "root=/dev/hda2 rootfstype=ext2 init=/etc/preinit noinitrd console=ttyS0,38400,n,8,1 reboot=bios"

The options are:

1.  **root**: root device/partition where the rest of the OpenWrt system is located
2.  **rootfstype**: Format for the root partition - ext2 in this example
3.  **init**: The first program to call after the kernel is loaded and initialized
4.  **noinitrd**: All drivers for access to the rest of the system are built into the kernel, so no need to load an initial ramdisk with extra drivers
5.  **console**: Which device to accept console login commands from - talk to ttyS0 (first serial port) at 38400 speed using no flow control, eight data bits and one stop bit. See the kernel documentation for other options
6.  **reboot**: Not sure, but I believe that this option tells the kernel how to perform a reboot

The first program called after the kernel loads is located at the kernel options entry of the boot loader. For grub, the entry is located in the openwrt--.image.kernel.image file in the /boot/grub/menu.lst file.

\[ [NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md): See the man page on grub for all of the grub parameters \] In this example, the entry "init=/etc/preinit" tells the kernel that the first program to run after initializing is "preinit" found in the "/etc" directory located on the disk "/dev/hda" and partition "hda2".

### /etc/preinit script

The preinit script's primary purpose is initial checks and setups for the rest of the startup scripts. One primary job is to mount the /proc and /sys pseudo filesystems so access to status information and some control functions are made available. Another primary function is to prepare the /dev directory for access to things like console, tty, and media access devices. The final job of preinit is to start the init daemon process itself.

### Busybox init

Init is considered the "Mother Of All Processes" since it controls things like starting daemons, changing runlevels, setting up the console/pseudo-consoles/tty access daemons, as well as some other housekeeping chores.

Once init is started, it reads the /etc/inittab configuration file to tell it what process to start, monitor for certain activities, and when an activity is triggered to call the relevant program.

The init program used by busybox is a minimalistic daemon. It does not have the knowledge of runlevels and such, so the config file is somewhat abbreviated from the normal init config file. If you are running a full linux desktop, you can "man inittab" and read about the normal init process and entries. Fields are separated by a colon and are defined as:

- \[ID\] : \[Runlevel(s)\] : \[Action\] : \[Process to execute \]

For busybox init, the only fields needed are the "ID" (1st), "Action" (3rd) and "Process" (4th) entries. Busybox init has several caveats from a normal init: the ID field is used for controlling TTY/Console, and there are no defined runlevels. A minimalistic /etc/inittab would look like:

1.  ::sysinit:/etc/init.d/rcS S boot
2.  ::shutdown:/etc/init.d/rcS K stop
3.  tts/0::askfirst:/bin/ash --login
4.  ttyS0::askfirst:/bin/ash --login
5.  tty1::askfirst:/bin/ash --login

Lines 1 and 2 with a blank ID field indicate they are not specific to any terminal or console. The other lines are directed to specific terminals/consoles.

Notice that both the "sysinit" and "shutdown" actions are calling the same program (the "/etc/init.d/rcS" script). The only difference is the options that are passed to the rcS script. This will become clearer later on.

At this point, init has parsed the configuration file and is looking for what to do next. So, now we get to the "sysinit" entry: call /etc/init.d/rcS with the options "S" and "boot"

## /etc/init.d/rcS Script At Startup

At this point, all basic setup has been done, all programs and system/configuration files are accessible, and we are now ready to start the rest of the processes.

The rcS script is pretty simplistic in it's function - it's sole purpose is to execute all of the scripts in the /etc/rc.d directory with the appropriate options. if you paid attention to the sysinit entry, the rcS script was called with the "S" and "boot" options. Since we called rcS with 2 options ("S" and "boot"), the rcS script will substitute \$1 with "S" and \$2 with "boot". The relevant lines in rcS are:

       -  for i in /etc/rc.d/$1* ; do
      2.      [ -x $i ] && $i $2
      3.  done

The basic breakdown is:

1.  Execute the following line once for every entry (file/link) in the /etc/rc.d directory that begins with "S"
2.  If the file is executable, execute the file with the option "boot"
3.  Repeat at step 1, replacing \$i with the next filename until there are no more files to check

Unlike Microsoft programs, Linux uses file permissions rather than filename extensions to tell it if this entry is executable or not. For an explanation of file permissions, see "man chmod" on a Linux/Unix machine on explanations for permissions and executable files.

If you look at the /etc/rc.d directory, you may notice that some scripts have relevant links for startup, but no shutdown (i.e., /etc/init.d/httpd), while some others have no startup script, but do have a shutdown script (i.e., /etc/init.d/umount).

In the case of httpd (the webserver), it doesn't matter if it dies or not, there's nothing to clean up before quitting.

On the other hand, the umount script MUST be executed before shutdown to ensure that all data is flushed to the media before unmounting of any relevant storage media, otherwise data corruption could occur. There's no need to call unmount at startup, since storage media mounting is handled somewhere else (like /etc/preinit), so there's no startup script for this one.

After the last startup script is executed, you should have a fully operational OpenWrt system.

## Notes

- See also [Booting](https://en.wikipedia.org/wiki/Booting) on the boot process in general.
- [log.essentials](/docs/guide-user/base-system/log.essentials) busybox-klogd and busybox-syslogd
- watchdog: <http://www.google.com/search?sclient=psy&hl=en&source=hp&q=openwrt+watchdog&btnG=Search>
- `pppd` is configured only in [network](/doc/uci/network), need this for you [internet.connection](/docs/guide-user/network/wan/internet.connection)
- see [init](https://en.wikipedia.org/wiki/init), [init manpage](http://linux.die.net/man/8/init), <http://linux.die.net/sag/init-intro.html>

---

# Boot/Init Requirements

|                                                                   |                                                                                                                           |
|-------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| ![48px-dialog-warning.svg.png](/meta/48px-dialog-warning.svg.png) | This is not a reference document, it's an old design document that, at least in part, led to [procd](/docs/techref/procd) |

# Boot/Init Requirements

This article attempts to state what the initscripts must and should do for the new init system being developed for OpenWrt. The goal is to deal with the race conditions that currently can occur, without losing current functionality.

## Boot/Preinit

The Boot process currently consists of the kernel bootstrap (not discussed here), preinit, and init. Preinit takes care of things that init can't function without, while init is responsible for starting up the rest of the system.

On a Debian desktop system there is an analogue to preinit, which uses initramfs to bring up the system enough to the point init can operate. Unfortunately initramfs is not an option on openwrt because it wastes too much space. The binaries and scripts in an initramfs cannot be retained for use in the booted system, unless they are copied to RAM (tmpfs) (if anyone know otherwise and can point out how, please contact the devs), which is why preinit exists.

Preinit looks to linux like the final boot stage to init on the rootfs. Preinit then mounts the root file system, does `pivot_root` to the rootfs, and then use the real init to replace itself. Basically it transforms intself into the 'real' init and rootfs.

### Goals

- Reduce preinit as much as possible so that init does most of the work
- Maintain failsafe ability, so that if mounting, etc, rootfs fails, or init makes system inaccessible, that there is a way to get into the device and fix it.
- Not start hotplug at all in preinit ... for that matter no processes except the real init should cross the preinit/init boundary.
- Be configurable...it should be possible to configure rootfs mount, init start and anything else that can happen after the jffs2 is mounted (and therefore a writable config is available)
- LED and network message functionality should be available to switchinit (which runs a script to shutdown process and make some other process than the current init PID 1, e.g. for doing a safer sysupgrade, and firstboot ('factory reset'))
- Support /opt type deployments as well as extroot (that is, extra packages on /opt rather than by replacing the jffs2 rootfs)
- No open file descriptors/references on the old rootfs when init is executed on the target rootfs (this is why we don't just mount/pivot in init).

#### Notes

- JFFS2 Formatting must be done on a fully booted system, because on some routers (like the Fon with NOR flash), formatting takes a significant amount of time during which the router would be unavailable for use). That means preinit can't be where the formatting happens.
- Ideally the firstboot script will take the router back to state exactly like after flashing without configuration saved), including the needs for formatting jffs2
- Restoring the configuration needs to be done after the rootfs is mounted, but before most configuration is used (most configuration is used in init or init-launched hotplug).
- Saving the configuration should save the jffs2 (for squashfs)/or boot rootfs config not the config on external root. This is because the external root will still be available on the external storage after flashing, but the internal (jff2 or other boot rootfs) won't.

### Must-do's

1.  Allow failsafe
2.  If initramfs, do initramfs, skip rest of this list
3.  For Squashfs: Mount jffs2 (if already formatted)
4.  For External Block: Mount swap (so fsck has enough memory)[^1] if present
5.  For External Block: Mount rootfs (checking first if fsck available) or tmpfs (if no rootfs yet)
6.  For External Block: Mount marked fses before init (e.g. for deployments where /opt contains packages/script that need to run early in init)
7.  Start init or kexec

### 0) Before failsafe

- Enable script output to serial before failsafe
- emit UDP messages with progress of boot, or at the very least failsafe prompt
- Network or Serial access
  - network kernel modules
- LEDs indicator for hit button
  - kernel modules for gpio and gpio-leds
- Button (on any button during failsafe window, enter failsafe)
  - kernel module for gpio, gpio-buttons or keys-polled, and button-hotplug
- Setting LEDs requires sysfs (/sys)
- OpenWrt LEDs depend on specific hardware as defined by /proc/cpuinfo, so /proc is needed
- Obviously /dev is needed

### 1) Allow Failsafe

- LED indicator for failsafe mode

#### Configuration at Compile-time not Run-time

- failsafe-related items \*must not\* rely on changing config, only on what is available in the flashed image.

### 2) Mount swap and 3) Mount rootfs

- check if jffs2 formatted
- if formatted, mount it in a temporary location
- combine boot rootfs and jffs2 (if present) kernel modules and swap/rootfs config
- mount should have /proc
- requires /dev

#### 2) Mount swap

- load modules needed for swap (if swap configured) (from rootfs or jffs2)
- run any swap-related scripts from either boot rootfs or jffs2
- using swap-utils from either boot rootfs or jffs2 (if present) do swapon for configured swap
- needs swap-utils and blkid (for UUID based config) on bootfs or jffs2

#### 3) Mount rootfs

- load modules needed for rootfs (from rootfs or jffs2)
- run any rootfs-related scripts (e.g. for mmc) (e.g. mount usbfs)
- check filesystem for errors if fsck present on boot rootfs or jffs2 (depends on blkid)
- mount target rootfs (depends on blkid on boot rootfs or jffs2)
- pivot_root
- move any fs mounted on old root to new root

### 4) Mount marked fses other rootfs

- load modules needed by fses (if not previously loaded)
- run any associated scripts (.e.g for mmc/usbfs) (if not previously run)
- check filesystem for errors if fsck present on rootfs (depends on blkid)
- mount fs (depends on blkid)

### 5) Start Init or Kexec

- For Init: Configurable PATH and environment variables
- Either do init or kexec a kernel on the rootfs or other previously mounted storage

## Init

### Goals

- Split /etc/init.d into independent chunks

### Wants

- Support betwork rootfs, perhaps by using switchinit with network kept up

[^1]: Roughly 1 MB of RAM for every 1 GB of disk to successfully fsck the disk. [Source](http://www.openbsd.org/faq/faq14.html#LargeDrive).

---

# rpcd: OpenWrt ubus RPC daemon for backend server

In OpenWrt we commonly use [ubus](/docs/techref/ubus) for all kinds of communication. It can provide info from various software as well as request various actions. Nevertheless, not every part of OpenWrt has a daemon that can register itself using `ubus`. For an example `uci` and `opkg` are command-line tools without any background process running all the time.

It would be not efficient to write a daemon for every software like this and run them independently. This is why `rpcd` was developed. It’s a tiny daemon with support for plugins using trivial API. It loads library `.so` files and calls init function of each of them.

The code is published under [ISC license](https://en.wikipedia.org/wiki/ISC_license) and can be found via git at <https://git.openwrt.org/project/rpcd.git>.

### Default plugins

There are few small plugins distributed with the `rpcd` sources. Two of them (`session` and `uci`) are built-in, others are optional and have to be build as separated `.so` libraries. Apart from that there are other projects providing their own plugins.

## plugin executables

It is possible to expose shell script functionality over ubus by using `rpcd` plugin executables functionality. Executables stored in `/usr/libexec/rpcd/` directory will be run by `rpcd`. Lets look at the following example:

``` bash
mkdir -p /usr/libexec/rpcd
cat << "EOF" > /usr/libexec/rpcd/foo
#!/bin/sh

case "$1" in
    list)
        echo '{ "bar": { "arg1": true, "arg2": 32, "arg3": "str" }, "toto": { }, "failme": {} }'
    ;;
    call)
        case "$2" in
            bar)
                # read the arguments
                read input;

                # optionally log the call
                logger -t "foo" "call" "$2" "$input"

                # return json object or an array
                echo '{ "hello": "world" }'
            ;;
            toto)
                # return json object
                echo '{ "something": "somevalue" }'
            ;;
                        failme)
                                # return invalid
                                echo '{asdf/3454'
                        ;;
        esac
    ;;
esac
EOF
chmod +x /usr/libexec/rpcd/foo
service rpcd restart
```

This will create new ubus functions which then can be used (after restarting rpcd):

``` bash
$ ubus -v list foo
'foo' @a9482c5b
    "bar":{"arg1":"Boolean","arg2":"Integer","arg3":"String"}
    "toto":{}
    "failme":{}

$ ubus -S call foo bar '{"arg1": true }'
{{"hello":"world"}}

$ ubus -S call foo toto
{"something":"somevalue"}

$ ubus -S call foo failme

$ echo $?
2
```

On startup rpcd will call all executables in `/usr/libexec/rpcd/` with `argv[1]` set to "list". For a plugin, which responds with a valid list of methods and signatures, ubus method with appropriate arguments will be created. When a method provided by the plugin is about to be invoked, `rpcd` calls the binary with `argv[1]` set to `call` and `argv[2]` set to the invoked method name.

**The actual data is then sent by the `ubus` client via `stdin`.** I.e. if you're testing the script itself, you need to use

``` bash
echo '{"arg1": 42}' | yourscript call yourmethod
```

You *cannot* simply use `yourscript call yourmethod '{"arg1": 42}`' as you might have expected.

The method signature is a simple object containing `key:value` pairs. The argument type is inferred from the value. If the value is a string (regardless of the contents) it is registered as string, if the value is a bool true or false, its registered as bool, if the value is an integer, it is registered as either int8, int16, int32 or int64 depending on the value i.e. `"foo": 16` will be `INT16`, `"foo": 64` will be `INT64`, `"foo": 8` will be `INT8` and everything else will be `INT32`.

It is enough to issue `service rpcd reload` to make it pick up new plugin executables, that way one does not lose active sessions.

**[NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md):** At least on CC builds, reload is *not* enough, and you must `restart` to pickup new plugins and changes to existing plugins.

---

# swconfig

The program `swconfig` allows you to configure *configurable* [Ethernet network switches](/docs/techref/hardware/switch).

It is considered legacy and new switch drivers should use the DSA (distributed switch architecture) kernel framework which makes it possible to use standard userspace tools such as `ip` to configure the switches.

Make sure you can [safemode](/docs/guide-user/troubleshooting/failsafe_and_factory_reset) or TTL before changing network/switch settings

## Supported hardware

`swconfig` supports the following hardware switches using the mentioned `swconfig` driver;

| Driver                                                                                                    | Ethernet switches models                                                             | Hardware wiring   |
|-----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|-------------------|
| [adm6996](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/adm6996.c)     | Infineon/ADMTek 6996M/L/FC                                                           | MDIO / [GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md)       |
| [ar8216](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/ar8216.c)       | Qualcomm/Atheros AR8216/8236/8316/8327/8337                                          | MDIO              |
| [b53](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/b53)               | Broadcom BCM5325/5365/5395/5398/53115/53125/53128/53010/53011/53012/53018/53019/63xx | MDIO / SPI / MMIO |
| [ip17xx](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/ip17xx.c)       | IC+ IP178C IP175A/C/D                                                                | MDIO              |
| [psb6970](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/psb6970.c)     | Lantiq PSB6970                                                                       | MDIO              |
| [rtl8306](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8306.c)     | Realtek RTL8306S/SD/SDM                                                              | MDIO              |
| [rtl8366s](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8366s.c)   | Realtek RTL8366S                                                                     | MDIO [GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md)/SMI     |
| [rtl8366rb](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8366rb.c) | Realtek RTL8366RB                                                                    | MDIO [GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md)/SMI     |
| [rtl8367](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8367.c)     | Realtek RTL8367                                                                      | MDIO              |
| [rtl8367b](https://dev.openwrt.org/browser/trunk/target/linux/generic/files/drivers/net/phy/rtl8367b.c)   | Realtek RTL8367B                                                                     | MDIO              |

## Usage examples

## Show

- `swconfig list`
- `swconfig dev switch0 show`
- Show current configuration`swconfig dev rtl8366rb show
  `and you will obtain:`VLAN 1:
          info: VLAN 1: Ports: '12345t', members=003e, untag=001e, fid=0
          fid: 0
          ports: 1 2 3 4 5t
  VLAN 2:
          info: VLAN 2: Ports: '05t', members=0021, untag=0001, fid=0
          fid: 0
          ports: 0 5t
  `
- Show available features`swconfig dev rt305x help
  switch0: rt305x(rt305x-esw), ports: 7 (cpu @ 6), vlans: 4096
       --switch
          Attribute 1 (int): enable_vlan (VLAN mode (1:enabled))
          Attribute 2 (int): alternate_vlan_disable (Use en_vlan instead of doubletag to disable VLAN mode)
          Attribute 3 (none): apply (Activate changes in the hardware)
          Attribute 4 (none): reset (Reset the switch)
       --vlan
          Attribute 1 (ports): ports (VLAN port mapping)
       --port
          Attribute 1 (int): disable (Port state (1:disabled))
          Attribute 2 (int): doubletag (Double tagging for incoming vlan packets (1:enabled))
          Attribute 3 (int): untag (Untag (1:strip outgoing vlan tag))
          Attribute 4 (int): led (LED mode (0:link, 1:100m, 2:duplex, 3:activity, 4:collision, 5:linkact, 6:duplcoll, 7:10mact, 8:1)
          Attribute 5 (int): lan (HW port group (0:wan, 1:lan))
          Attribute 6 (int): recv_bad (Receive bad packet counter)
          Attribute 7 (int): recv_good (Receive good packet counter)
          Attribute 8 (int): pvid (Primary VLAN ID)
          Attribute 9 (string): link (Get port link information)
  `or`swconfig dev rtl8366rb help
  switch1: rtl8366rb(RTL8366RB), ports: 6 (cpu @ 5), vlans: 4096
       --switch
          Attribute 1 (int): enable_learning (Enable learning, enable aging)
          Attribute 2 (int): enable_vlan (Enable VLAN mode)
          Attribute 3 (int): enable_vlan4k (Enable VLAN 4K mode)
          Attribute 4 (none): reset_mibs (Reset all MIB counters)
          Attribute 5 (int): blinkrate (Get/Set LED blinking rate (0 = 43ms, 1 = 84ms, 2 = 120ms, 3 = 170ms, 4 = 340ms, 5 = 670ms))
          Attribute 6 (int): enable_qos (Enable QOS)
          Attribute 7 (none): apply (Activate changes in the hardware)
          Attribute 8 (none): reset (Reset the switch)
       --vlan
          Attribute 1 (string): info (Get vlan information)
          Attribute 2 (int): fid (Get/Set vlan FID)
          Attribute 3 (ports): ports (VLAN port mapping)
       --port
          Attribute 1 (none): reset_mib (Reset single port MIB counters)
          Attribute 2 (string): mib (Get MIB counters for port)
          Attribute 3 (int): led (Get/Set port group (0 - 3) led mode (0 - 15))
          Attribute 4 (int): disable (Get/Set port state (enabled or disabled))
          Attribute 5 (int): rate_in (Get/Set port ingress (incoming) bandwidth limit in kbps)
          Attribute 6 (int): rate_out (Get/Set port egress (outgoing) bandwidth limit in kbps)
          Attribute 7 (int): pvid (Primary VLAN ID)
          Attribute 8 (string): link (Get port link information)
  `

### Example switch port on/off per port (ex: on/off port 4)

    disable: ssh > swconfig dev switch0 port 4 set disable 1
    enable:  ssh > swconfig dev switch0 port 4 set disable 0

## Change

Note: Make sure to apply any changes made previously with the "**set**" command.

- LEDs:`swconfig dev rtl8366s port 0 set led 2
  swconfig dev rtl8366rb set apply`
- Disable VLANs:`swconfig dev switch0 set enable_vlan 0
  swconfig dev switch0 set apply`

### Design and rationale

Generic Netlink Switch configuration API

## Introduction

The following documentation covers the Linux Ethernet switch configuration API which is based on the Generic Netlink infrastructure.

## Scope and rationale

Most Ethernet switches found in small routers are managed switches which allow the following operations:

- configure a port to belong to a particular set of VLANs either as tagged or untagged
- configure a particular port to advertise specific link/speed/duplex settings
- collect statistics about the number of packets/bytes transferred/received
- any other vendor specific feature: rate limiting, single/double tagging...

Such switches can be connected to the controlling CPU using different hardware busses, but most commonly:

- SPI/I2C/[GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) bitbanging
- MDIO
- Memory mapped into the CPU register address space

As of today the usual way to configure such a switch was either to write a specific driver or to write an user-space application which would have to know about the hardware differences and figure out a way to access the switch registers (spidev, SIOCIGGMIIREG, mmap...) from user-space.

This has multiple issues:

- proliferation of ad-hoc solutions to configure a switch both open source and proprietary
- absence of common software reference for switches commonly found on the market (Broadcom, Lantiq/Infineon/ADMTek, Marvell, Qualcomm/Atheros...) which implies a duplication effort for each implementer
- inability to leverage existing hardware representation mechanisms such as Device Tree (spidev, i2c-dev.. do not belong in Device Tree and rely on Linux-specific "forwarder" drivers) to describe a switch device

The goal of the switch configuration API is to provide a common basis to build re-usable and extensible switch drivers with the following ideas in mind:

- having a central point of configuration on top of which a reference user-space implementation can be provided but also allow for other user-space implementations to exist
- ensure the Linux kernel is in control of the actual hardware access
- be extensible enough to support per-switch features without making the generic implementation too heavy weighted and without making user-space changes each and every time a new feature is added

Based on these design goals the Generic Netlink kernel/user-space communication mechanism was chosen because it allows for all design goals to be met.

## Distributed Switch Architecture vs. swconfig

The Marvell Distributed Switch Architecture (DSA) drivers is an existing solution which is a heavy switch driver infrastructure, is [Marvell](/docs/techref/hardware/soc/soc.marvell)-centric, only supports MDIO connected switches, mangles an Ethernet driver transmit/receive paths and does not offer a central control path for the user.

swconfig is vendor agnostic, does not mangle the transmit/receive path of an Ethernet driver and is focused on the control path of the switch rather that the data path. It is based on Generic Netlink to allow for each switch driver to easily extend the swconfig API without causing major core parts rework each and every time someone has a specific feature to implement and offers a central configuration point with a well-defined API.

\* More info e.g. at [LWN.net 2017-04-19: The rise of Linux-based networking hardware](https://lwn.net/Articles/720313/):

"The Linux kernel manipulates switches with three different operation structures: `switchdev_ops`, `ethtool_ops` and `netdev_ops`. Certain switches, however, also need distributed switch architecture (DSA).

DSA's development was parallel to swconfig, written by the OpenWrt project. The main difference between swconfig and DSA is that DSA-supported switches show one network interface per port, whereas swconfig-configured switches show up as a single port, which limits the amount of information that can be extracted from the switch. For example, you cannot have per-port traffic statistics with swconfig. That limitation is what led to the creation of the switchdev framework, when swconfig was proposed (then refused) for inclusion in mainline. Another goal of switchdev was to support bridge hardware offloading and network interface card (NIC) virtualization…"

## Switch configuration API

The main data structure of the switch configuration API is a "struct switch_dev" which contains the following members:

- a set of common operations to all switches (struct switch_dev_ops)
- a network device pointer it is physically attached to
- a number of physical switch ports (including CPU port)
- a set of configured vlans
- a CPU specific port index

A particular switch device is registered/unregistered using the following pair of functions:

register_switch(struct switch_dev \*sw_dev, struct net_device \*dev); unregister_switch(struct switch_dev);

A given switch driver can be backed by any kind of underlying bus driver (i2c client, [GPIO](../wiki/chunked-reference/wiki_page-guide-developer-add-new-device.md) driver, MMIO driver, directly into the Ethernet MAC driver...).

The set of common operations to all switches is represented by the "struct switch_dev_ops" function pointers, these common operations are defined as such:

- get the port list of a VLAN identifier
- set the port list of a VLAN identifier
- get the primary VLAN identifier of a port
- set the primary VLAN identifier of a port
- apply the changed configuration to the switch
- reset the switch
- get a port link status
- get a port statistics counters

The switch_dev_ops structure also contains an extensible way of representing and querying switch specific features, 3 different types of attributes are available:

- global attributes: attributes global to a switch (name, identifier, number of ports)
- port attributes: per-port specific attributes (MIB counters, enabling port mirroring...)
- vlan attributes: per-VLAN specific attributes (VLAN id, specific VLAN information)

Each of these 3 categories must be represented using an array of "struct switch_attr" attributes. This structure must be filed with:

- an unique name for the operation
- a description for the operation
- a setter operation
- a getter operation
- a data type (string, integer, port)
- eventual min/max limits to validate user input data

The "struct switch_attr" directly maps to a Generic Netlink type of command and will be automatically discovered by the "swconfig" user-space utility without requiring user-space changes.

## References

- <https://web.archive.org/web/20081205103732/http://inst.eecs.berkeley.edu/~pathorn/ip175c/> (links to archive.org; content of original site is gone)
- <https://web.archive.org/web/20110831151445/http://inst.eecs.berkeley.edu/~pathorn/ip175c/phylib-swconfig/> (links to archive.org; content of original site is gone)
- <http://www.debwrt.net/2010/11/07/switch-configuration-command-line-tool-swconfig-ported-2/>
- <http://www.icplus.com.tw/pp-IP175C.html>
- [OpenWrt Forum](https://forum.openwrt.org/viewtopic.php?pid=152508)
- [switch_port](https://forum.openwrt.org/viewtopic.php?id=28716)
- [Is VLAN trunking on WR1034ND with VLAN id higher than 15 possible](https://forum.openwrt.org/viewtopic.php?id=27485)

---

# Sysupgrade – Technical Reference

This information is based upon v21.02, last updated for [commit 6d266ef158 on 2022-02-10](https://github.com/openwrt/openwrt/tree/6d266ef158).

# Sysupgrade – Technical Reference

In contrast to `apk`, `mtd` and others, `sysupgrade` is merely a shell script: `/sbin/sysupgrade` intended to facilitate easy updates.

## Usage

This page lists all `sysupgrade` command-line options. For the overall upgrade procedure and typical usage, please read [OpenWrt OS upgrade procedure (sysupgrade or LuCI)](/docs/guide-user/installation/generic.sysupgrade) instead.

## Options

sysupgrade supports the following options

    Usage: /sbin/sysupgrade [<upgrade-option>...] <image file or URL>
           /sbin/sysupgrade [-q] [-i] [-c] [-u] [-o] [-k] <backup-command> <file>

    upgrade-option:
            -f <config>  restore configuration from .tar.gz (file or url)
            -i           interactive mode
            -c           attempt to preserve all changed files in /etc/
            -o           attempt to preserve all changed files in /, except those
                         from packages but including changed confs.
            -u           skip from backup files that are equal to those in /rom
            -n           do not save configuration over reflash
            -p           do not attempt to restore the partition table after flash.
            -k           include in backup a list of current installed packages at
                         /etc/backup/installed_packages.txt
            -T | --test
                         Verify image and config .tar.gz but do not actually flash.
            -F | --force
                         Flash image even if image checks fail, this is dangerous!
            -q           less verbose
            -v           more verbose
            -h | --help  display this help

    backup-command:
            -b | --create-backup <file>
                         create .tar.gz of files specified in sysupgrade.conf
                         then exit. Does not flash an image. If file is '-',
                         i.e. stdout, verbosity is set to 0 (i.e. quiet).
            -r | --restore-backup <file>
                         restore a .tar.gz created with sysupgrade -b
                         then exit. Does not flash an image. If file is '-',
                         the archive is read from stdin.
            -l | --list-backup
                         list the files that would be backed up when calling
                         sysupgrade -b. Does not create a backup file.

WARNING: Trying to copy all files from `/etc` with the `-c` option in a sysupgrade may cause unwanted version-specific files like `/etc/apk/world` to be included. That may cause incompatibilities in the new version.

WARNING: Preserving files across sysupgrades [can be fatal](this>docs/techref/preinit_mount#mount_root_filesystem) (see '[NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md): ...') on systems with weak cpu and exceptionally large rootfs_data partitions.

Files to be preserved depend on the following:

- `/etc/sysupgrade.conf` - customizable backup configuration.
- `/lib/upgrade/keep.d/*` - system configurations provided by specific packages preserved by default.
- `apk audit` - list of files derived by package manager.
- `-o` will cause the entire `/overlay` directory to be saved (with the `-u` caveat below).
- `-n` will cause *NO* files will be saved and all configuration settings will be initialized from default values.
- `-u` will prevent preservation of any file that has not been changed since the last sysupgrade. This prevents the need for programs to migrate an old configuration and reduces time needed for sysupgrade.
- `-f` will *COMPLETELY OVERRIDE* all behaviour described above. Instead, the exact files provided in the .tar.gz file will be extracted into `/overlay/upper` after the sysupgrade.

**Q:** Does this mean, I make an archive.tar.gz of /etc and /root for example and sysupgrade -f archive.tar.gz will flash the router and afterwards restores the configs from this archive?

**A:** That's what is says: 'restore configuration from .tar.gz (file or url)'. Anything archived in the tgz will be written to /overlay after the flash. This way you can hand-pick the files that will be the system after new firmware boot.

## How It Works

The `sysupgrade` process starts with the execution of `/sbin/sysupgrade`. The below list describes its behavior.

1.  Parse command line and validate no mutually exclusive options passed.
2.  At this point, sysupgrade calls `include /lib/upgrade` -- a function in `/lib/functions.sh` that will source all `*.sh` files in the given directory.
    1.  [NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md): An optional, platform-specific `/lib/upgrade/platform.sh` can override behavior, so for a full understanding, you should examine this file. (See `target/linux/<arch>//base-files/lib/upgrade/platform.sh` in your source tree.)
    2.  The optional functions `platform_copy_config` and `platform_do_upgrade` are at the end of this list.
3.  Create list of files to preserve and store them in `/tmp/sysupgrade.tgz` (unless `-f` was supplied).
4.  If the image supplied is an http or https URL, `wget` is run to retrieve it.
5.  The firmware image is saved (if a URL) or copied to `/tmp/sysupgrade.img`.
6.  Validates the firmware image, and that the root `compatible` node in the device tree file matches the value in `/sys/firmware/devicetree/base/compatible` from the existing firmware's device tree. (May be overridden with `-F`).
7.  Copies `/sbin/upgraded` into `/tmp`
8.  Builds a [json message](https://git.openwrt.org/?p=project/procd.git;a=blob;f=system.c;h=83aea423ec6aaceedca54e42aea18ce90d7ddfa1;hb=37eed131e9967a35f47bacb3437a9d3c8a57b3f4#l627) and sends a message, via `ubus`, to `procd`, to initiate the upgrade. Among other things, the message specifies:
    1.  path: `/tmp/sysupgrade.img`,
    2.  backup: `/tmp/sysupgrade.tgz` if any files are being preserved, unset otherwise,
    3.  force: if `-F` was supplied,
    4.  and command: `/lib/upgrade/do_stage2`.
9.  The `sysupgrade` function in `procd` will unpack and validate the message, then validate the firmware image and such.
10. Notably, `procd` does not terminate any services here.
11. **This is where things get funky!** If all is well, we call [sysupgrade_exec_upgraded](https://git.openwrt.org/?p=project/procd.git;a=blob;f=sysupgrade.c;h=fc588b0248353137d4b81fce130d2d35d8dfa710;hb=37eed131e9967a35f47bacb3437a9d3c8a57b3f4#l28), which further parses the original json and then passes control to `/sbin/upgraded` via `execvp`.
    1.  Note that at boot time, the kernel passes control to `/sbin/init` as PID=1, which in turn `exec`s `/sbin/procd`. Thus, this results in `/tmp/upgraded` becoming the new PID=1 ("init") process.
    2.  At this point, service management is no longer possible.
12. `/sbin/upgraded` executes the command passed (`/lib/upgrade/stage2`) with parameters. The remaining sequence runs from this shell script.
    1.  `/bin/sh /lib/upgrade/stage2` is run via fork/exec, so is not PID1.
13. Terminate (`SIGKILL`) all `telnet`, `ash`, and `dropbear` processes.
14. Loop over all remaining processes, sending them the TERM signal.
15. Loop over all remaining processes, sending them the KILL signal.
16. Create a new RAM filesystem, mount it, and copy over a very small set of binaries into it.
17. Change root into the new RAM filesystem.
18. Remount `/overlay` read-only, and lazy-unmount it.
19. Write the upgraded firmware to disk. If `platform_do_upgrade` is defined then it is run. Otherwise, this is done via [default_do_upgrade](https://github.com/openwrt/openwrt/blob/6d266ef158/package/base-files/files/lib/upgrade/common.sh#L301), using `mtd` to flash the firmware.
20. If any files are being preserved, the tarball is passed via `mtd`'s `-j` option. This causes mtd to [write a raw jffs2 inode (with id = 1) and file data](https://github.com/openwrt/openwrt/blob/6d266ef158/package/system/mtd/src/jffs2.c#L163), resulting in the tarball to appearing as `/sysupgrade.tgz` once the jffs2 file system is mounted.
    1.  A consequence is that the mtd sources are intimately tied to the jffs2 implementation and can break if changes are made to jffs2 in the kernel (it should probably be using the uapi header from the kernel `make headers_install` instead of copying it into its source tree).
    2.  After reboot, this file will be extracted by `/lib/preinit/80_mount_root` (`/sbin/init` during [preinit](https://git.openwrt.org/?p=project/procd.git;a=blob;f=initd/preinit.c;h=46411aa413a2a65614cfc765d3d6a42dee200532;hb=37eed131e9967a35f47bacb3437a9d3c8a57b3f4#l157) --\> `/bin/sh /etc/preinit` --\> `/lib/preinit/80_mount_root`)
    3.  and finally deleted by `/etc/rc.d/S95done` (`/sbin/procd` --\> at `STATE_INIT` --\> `procd_inittab_run("sysinit");` --\> `/etc/inittab`)
21. If a `platform_copy_config` is implemented, it is run at this point.
22. Unmount any remaining filesystems.
23. Reboot.

There are plenty of potential deficiencies in this process, among them:

- Hardcodes a list of "potentially-interfering" / interactive processes (`ash`, `telnet`, `dropbear`) to kill first; this is not exhaustive or up-to-date (e.g., `telnet` is no longer in the base install; `openssh` is not handled).
- Does not give processes much time in between TERM and KILL signals.
- Does not utilise `procd` to tear down services.
- Susceptible to fork bombs.
- Easily broken by open files on storage devices (e.g., for swap, or explicitly opened), as these can prevent unmounting `/overlay`.
- Does not handle errors (e.g., I/O) in writing the disk image, potentially leaving a partially-upgraded system upon reboot.
- Various error conditions are ignored in `mtd`, which can also result in preserved files not being written to the new jffs2 file system or and leaving the file system corrupted, but without reporting an error.

Many of these deficiencies are historical artifacts, remaining simply because no one has fixed them.

Thanks to Michael Jones for writing most of this down on the mailing list [\[OpenWrt-Devel\] Sysupgrade and Failed to kill all processes](http://lists.openwrt.org/pipermail/openwrt-devel/2020-May/029074.html).

TODO: Explain how this process works during failsafe mode.

---

# ubox

- [Project's git](http://git.openwrt.org/?p=project/ubox.git;a=summary)

Package `ubox` was added in [r36427](https://dev.openwrt.org/changeset/36427) and package `block-mount` was dropped in [r36988](https://dev.openwrt.org/changeset/36988). [r37199](https://dev.openwrt.org/changeset/37199) finally adds a UCI-default script for fstab generation.

Cf.

- <https://forum.openwrt.org/viewtopic.php?pid=205552#p205552>
- <https://lists.openwrt.org/pipermail/openwrt-devel/2013-June/020538.html>

for some insight.

call

    block detect

to get a sample UCI configuration file. If target is / then it will be used as extroot. block info is also valid to get the uuid.

## OpenWrt – operating system architecture

![architecture&noheader&nofooter](/page>docs/techref/architecture&noheader&nofooter)

---

# ubus (OpenWrt micro bus architecture)

See also: [What is UBUS?](https://hackmd.io/@rYMqzC-9Rxy0Isn3zClURg/H1BY98bRw)

To provide [Inter-process communication](https://en.wikipedia.org/wiki/Inter-process_communication) between various daemons and applications in OpenWrt a project called `ubus` has been developed. It consists of several parts including daemon, library and some extra helpers.

The heart of this project is the `ubusd` daemon. It provides an interface for other daemons to register themselves as well as sending messages. For those curious, this interface is implemented using Unix sockets and it uses [TLV (type-length-value)](https://en.wikipedia.org/wiki/Type-length-value) messages.

To simplify development of software using `ubus` (connecting to it) a library called `libubus` has been created.

Every daemon registers a set of paths under a specific namespace. Every path can provide multiple procedures with any number of arguments. Procedures can reply with a message.

The code is published under [LGPL 2.1 license](https://en.wikipedia.org/wiki/GNU_Lesser_General_Public_License) and can be found via git at <https://git.openwrt.org/project/ubus.git>.

## Command-line ubus tool

The `ubus` command line tool allows to interact with the `ubusd` server (with all currently registered services). It's useful for investigating/debugging registered namespaces as well as writing shell scripts. For calling procedures with parameters and returning responses it uses the user-friendly JSON format. Below is an explanation of its commands.

### Help output

    # ubus
    Usage: ubus [<options>] <command> [arguments...]
    Options:
     -s <socket>:       Set the unix domain socket to connect to
     -t <timeout>:      Set the timeout (in seconds) for a command to complete
     -S:            Use simplified output (for scripts)
     -v:            More verbose output
     -m <type>:     (for monitor): include a specific message type
                (can be used more than once)
     -M <r|t>       (for monitor): only capture received or transmitted traffic

    Commands:
     - list [<path>]            List objects
     - call <path> <method> [<message>] Call an object method
     - listen [<path>...]           Listen for events
     - send <type> [<message>]      Send an event
     - wait_for <object> [<object>...]  Wait for multiple objects to appear on ubus
     - monitor              Monitor ubus traffic

### list

To find out which services are currently running on the bus simply use the `ubus list` command. This will show a complete list of all namespaces registered with the RPC server:

    # ubus list
    dhcp
    dnsmasq
    file
    iwinfo
    log
    luci
    luci-rpc
    network
    network.device
    network.interface
    network.interface.lan
    network.interface.loopback
    network.interface.wan
    network.interface.wan6
    network.rrdns
    network.wireless
    service
    session
    system
    uci

You can filter the list by specifying a service path:

    # ubus list network.interface.*
    network.interface.lan
    network.interface.loopback
    network.interface.wan
    network.interface.wan6

To find out which procedures/methods and their argument signatures a specific service provides add `-v` in addition to the namespace path:

    # ubus -v list network.interface.lan
    'network.interface.lan' @099f0c8b
        "up": {  }
        "down": {  }
        "status": {  }
        "prepare": {  }
        "add_device": { "name": "String" }
        "remove_device": { "name": "String" }
        "notify_proto": {  }
        "remove": {  }
        "set_data": {  }

### call

Calls a given procedure within a given namespace and optionally pass arguments to it:

``` bash
# ubus call network.interface.wan status
{
    "up": true,
    "pending": false,
    "available": true,
    "autostart": true,
    "uptime": 86017,
    "l3_device": "eth1",
    "device": "eth1",
    "address": [
        {
            "address": "178.25.65.236",
            "mask": 21
        }
    ],
    "route": [
        {
            "target": "0.0.0.0",
            "mask": 0,
            "nexthop": "178.25.71.254"
        }
    ],
    "data": {

    }
}
```

The arguments must be a valid JSON string, with keys and values set according to the function signature:

``` bash
# ubus call network.device status '{ "name": "eth0" }'
{
    "type": "Network device",
    "up": true,
    "link": true,
    "mtu": 1500,
    "macaddr": "c6:3d:c7:90:aa:da",
    "txqueuelen": 1000,
    "statistics": {
        "collisions": 0,
        "rx_frame_errors": 0,
        "tx_compressed": 0,
        "multicast": 0,
        "rx_length_errors": 0,
        "tx_dropped": 0,
        "rx_bytes": 0,
        "rx_missed_errors": 0,
        "tx_errors": 0,
        "rx_compressed": 0,
        "rx_over_errors": 0,
        "tx_fifo_errors": 0,
        "rx_crc_errors": 0,
        "rx_packets": 0,
        "tx_heartbeat_errors": 0,
        "rx_dropped": 0,
        "tx_aborted_errors": 0,
        "tx_packets": 184546,
        "rx_errors": 0,
        "tx_bytes": 17409452,
        "tx_window_errors": 0,
        "rx_fifo_errors": 0,
        "tx_carrier_errors": 0
    }
}
```

### listen

Set up a listening socket and observe incoming events:

``` bash
# ubus listen &
# ubus call network.interface.wan down
{ "network.interface": { "action": "ifdown", "interface": "wan" } }
# ubus call network.interface.wan up
{ "network.interface": { "action": "ifup", "interface": "wan" } }
{ "network.interface": { "action": "ifdown", "interface": "he" } }
{ "network.interface": { "action": "ifdown", "interface": "v6" } }
{ "network.interface": { "action": "ifup", "interface": "he" } }
{ "network.interface": { "action": "ifup", "interface": "v6" } }
```

### send

Send an event notification:

``` bash
# ubus listen &
# ubus send foo '{ "bar": "baz" }'
{ "foo": { "bar": "baz" } }
```

## Access to ubus over HTTP

There is an `uhttpd` plugin called `uhttpd-mod-ubus` that allows `ubus` calls using [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) protocol. For example this is used in [LuCI2](/docs/techref/luci2). Requests have to be sent to the `/ubus` URL (unless changed by `ubus_prefix` option) using the `POST` method. This interface uses [jsonrpc v2.0](https://www.jsonrpc.org/specification) There are a few steps that you will need to understand.

If uhttpd-mod-ubus is installed, uhttpd automatically configures it and enables it, by default at /ubus, but you can [configure this](/docs/guide-user/services/webserver/uhttpd) Also if you want to use the `/ubus` directly from a web client you need to specify `ubus_cors=1` option.

If you are using Nginx then you may try [nginx-ubus-module](https://github.com/Ansuel/nginx-ubus-module). For other web servers like Lighttpd you may use the [ubus as CGI](https://github.com/yurt-page/cgi-ubus).

See the [Postman collection](https://documenter.getpostman.com/view/5972215/TVzNHeej#154b5d84-4065-4887-a5a8-c1f3b51fe9a6) with some examples of calling UBUS over [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md)

### ACLs

While logged in via ssh, you have direct, full access to ubus. When you're accessing the `/ubus` url in uhttpd however, uhttpd first queries whether your call is allowed, and whoever is providing the ubus `session.*` namespace is in charge of implementing the access control:

``` bash
ubus call session access '{ "ubus_rpc_session": "xxxxx", "object": "requested-object", "function": "requested-method" }'
```

This happens to be `rpcd` at the moment, with the `http-json` interface, for friendly operation with browser code, but this is just one possible implementation. Because we're using rpcd to implement the ACLs at this time, this allows/requires (depending on your point of view) ACLs to be configured in `/usr/share/rpcd/acl.d/*.json`. The **names** of the files in `/usr/share/rpcd/acl.d/*.json` don't matter, but the top level keys define roles. The default ACL, listed below, **only** defines the login methods, so you can log in, but you still wouldn't be able to do anything.

``` yaml
{
        "unauthenticated": {
                "description": "Access controls for unauthenticated requests",
                "read": {
                        "ubus": {
                                "session": [ "access", "login" ]
                        }
                }
        }
}
```

An example of a complicated ACL, allowing quite fine grained access to different ubus modules and methods is [available in the Luci2 project](https://git.openwrt.org/?p=project/luci2/ui.git;a=blob;f=luci2/share/acl.d/luci2.json)

An example of a "security is for suckers" config, where a `superuser` ACL group is defined, allowing unrestricted access to everything, is shown below. This illustrates the usage of `*` definitions in the ACLs, but keep reading for better examples.

Placing this file in `/usr/share/rpcd/acl.d/superuser.json` will help you move forward to the next steps.

``` yaml
{
        "superuser": {
                "description": "Super user access role",
                "read": {
                        "ubus": {
                                "*": [ "*" ]
                        },
                        "uci": [ "*" ],
                        "file": {
                                "*": ["*"]
                        }
                },
                "write": {
                        "ubus": {
                                "*": [ "*" ]
                        },
                        "uci": [ "*" ],
                        "file": {
                                "*": ["*"]
                        },
                        "cgi-io": ["*"]
                }
        }
}
```

Below is an example of an ACL definition that only allows access to some specific ubus modules, rather than unrestricted access to everything.

``` yaml
{
        "lesssuperuser": {
                "description": "not quite as super user",
                "read": {
                        "ubus": {
                                "file": [ "*" ],
                                "log": [ "*" ],
                                "service": [ "*" ],
                        },
                },
                "write": {
                        "ubus": {
                                "file": [ "*" ],
                                "log": [ "*" ],
                                "service": [ "*" ],
                        },
                }
        }
}
```

**Note:** Before we leave this section, you may have noticed that there's both a `ubus` and a `uci` section, even though ubus has a uci method. The `uci` scope is used for the [uci api](/docs/techref/uci) provided by rpcd to allow defining per-file permissions because using the ubus scope you can only say `uci set` is allowed or not, but not specify that it is allowed to e.g. modify `/etc/config/system` but not `/etc/config/network`. If your application/ACL doesn't need UCI access, you can just leave out the UCI section altogether.

### Authentication

Now that we have an ACL that allows operations beyond just logging in, we can actually try this out. As mentioned, `rpcd` is handling this, so you need an entry in `/etc/config/rpcd`

``` bash
config login
    option username 'root'
    option password '$p$root'
    list read '*'
    list write '*'

config login
        option username 'blaer'
        option password '$p$blaer'
        list read lesssuperuser
        list write lesssuperuser
```

The `$p` magic means to look in `/etc/shadow` and the `$root` part means to use the password for the root user in that file. The list of read and write sections, those map ACL roles to user accounts. So `list read *` means the read credential of any group listed in the merged ACLs. Write implies read.

You can also use `$1$<hash>` which is a [crypt](https://en.wikipedia.org/wiki/Crypt_(Unix)) hash, using SHA1, exactly as used in `/etc/shadow`. You can generate these with `uhttpd -m secret`.

### Session management

To login and receive a session id:

``` bash
$ curl -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "00000000000000000000000000000000", "session", "login", { "username": "root", "password": "secret"  } ] }'  http://your.server.ip/ubus

{"jsonrpc":"2.0","id":1,"result":[0,{"ubus_rpc_session":"c1ed6c7b025d0caca723a816fa61b668","timeout":300,"expires":299,"acls":{"access-group":{"superuser":["read","write"],"unauthenticated":["read"]},"ubus":{"*":["*"],"session":["access","login"]},"uci":{"*":["read","write"]}},"data":{"username":"root"}}]}
```

The session id `00000000000000000000000000000000` (32 zeros) is a special null-session which only has the rights from the `unauthenticated` access group, only enabling the `session.login` ubus call. A session has a timeout that can be specified when you login, otherwise it defaults to 5 minutes.

If you ever receive a response like `{"jsonrpc":"2.0","id":1,"result":[6]}`, that is a valid jsonrpc response, 6 is the ubus code for `UBUS_STATUS_PERMISSION_DENIED` (you'll get this if you try and login before setting up the `superuser` file, or any file that gives you more rights than just being allowed to attempt logins).

To list all active sessions, try `ubus call session list`

The session timeout is automatically reset on every use. There are plans to use these sessions even for luci1, but at present, if you use this interface in a luci1 environment, you'll need to manage sessions yourself.

### Actually making calls

Now that you have a `ubus_rpc_session` you can make calls, based on your ACLs and the available ubus services. `ubus -v list` is your primary documentation on what can be done, but see the rest of this page for more information. For example, `ubus -v list file` returns

``` javascript
'file' @ff0a2c92
    "read":{"path":"String","base64":"Boolean"}
    "write":{"path":"String","data":"String","append":"Boolean","mode":"Integer","base64":"Boolean"}
    "list":{"path":"String"}
    "stat":{"path":"String"}
    "md5":{"path":"String"}
    "exec":{"command":"String","params":"Array","env":"Table"}
```

The RPC-JSON container format is:

``` javascript
{ "jsonrpc": "2.0",
  "id": <unique-id-to-identify-request>,
  "method": "call",
  "params": [
             <ubus_rpc_session>, <ubus_object>, <ubus_method>,
             { <ubus_arguments> }
            ]
}
```

The "id" key is merely echo'ed by the server, so it needs not be strictly unique, it's mainly intended for client software to easily correlate responses to previously made requests. Its type is either a string or a number, so it can be an UUID, sha1 hash, md5 sum, sequence counter, unix timestamp, etc.

An example request to read a file `/etc/board.json` which contains device info would be:

``` bash
$ curl -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "c1ed6c7b025d0caca723a816fa61b668", "file", "read", { "path": "/etc/board.json" } ] }'  http://your.server.ip/ubus
{"jsonrpc":"2.0","id":1,"result":[0,{"data":"{\n\t\"model\": {\n\t\t\"id\": \"innotek-gmbh-virtualbox\",\n\t\t\"name\": \"innotek GmbH VirtualBox\"\n\t},\n\t\"network\": {\n\t\t\"lan\": {\n\t\t\t\"ifname\": \"eth0\",\n\t\t\t\"protocol\": \"static\"\n\t\t}\n\t}\n}\n"}]}
```

Here the first param `c1ed6c7b025d0caca723a816fa61b668` is the `ubus_rpc_session` received during the login call. If you received a response like `{"jsonrpc":"2.0","id":1,"error":{"code":-32002,"message":"Access denied"}}` then probably your session token was expired and you need to request a new one.

To beautify output you can use [jq](https://stedolan.github.io/jq/) utility:

``` bash
curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "c1ed6c7b025d0caca723a816fa61b668", "file", "read", { "path": "/etc/board.json" } ] }'  http://your.server.ip/ubus | jq
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    0,
    {
      "data": "{\n\t\"model\": {\n\t\t\"id\": \"innotek-gmbh-virtualbox\",\n\t\t\"name\": \"innotek GmbH VirtualBox\"\n\t},\n\t\"network\": {\n\t\t\"lan\": {\n\t\t\t\"ifname\": \"eth0\",\n\t\t\t\"protocol\": \"static\"\n\t\t}\n\t}\n}\n"
    }
  ]
}
```

In the response JSON document in the `result[1].data` field contains escaped JSON with the `model` and `network` objects. To fetch the concrete model name you can parse the response with the [jq](https://stedolan.github.io/jq/) program:

    curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "id": 1, "method": "call", "params": [ "c1ed6c7b025d0caca723a816fa61b668", "file", "read", { "path": "/etc/board.json" } ] }'  http://your.server.ip/ubus | jq -r '.result[1].data' | jq .model.name
    "innotek GmbH VirtualBox"

As you can see in the example the router model is in fact just a OpenWrt runned on [virtual machine in VirtualBox](/docs/guide-user/virtualization/virtualbox-vm).

## Lua module for ubus

This is even possible to use `ubus` in `lua` scripts. Of course it's not possible to use native libraries directly in `lua`, so an extra module has been created. It's simply called `ubus` and is a simple interface between `lua` scripts and the `ubus` (it uses `libubus` internally).

``` lua
-- Load module
require "ubus"
-- Establish connection
local conn = ubus.connect()
if not conn then
    error("Failed to connect to ubusd")
end

-- Iterate all namespaces and procedures
local namespaces = conn:objects()
for i, n in ipairs(namespaces) do
    print("namespace=" .. n)
    local signatures = conn:signatures(n)
    for p, s in pairs(signatures) do
        print("\tprocedure=" .. p)
        for k, v in pairs(s) do
            print("\t\tattribute=" .. k .. " type=" .. v)
        end
    end
end

-- Call a procedure
local status = conn:call("network.device", "status", { name = "eth0" })
for k, v in pairs(status) do
    print("key=" .. k .. " value=" .. tostring(v))
end

-- Close connection
conn:close()
```

Optional arguments to `connect()` are a path to use for sockets (pass nil to use the default) and a per call timeout value (in milliseconds)

``` lua
local conn = ubus.connect(nil, 500) -- default socket path, 500ms per call timeout
```

## Namespaces & Procedures

As explained earlier, there can be many different daemons (services) registered in `ubus`. Below you will find a list of the most common projects with namespaces, paths and procedures they provide.

**Path only contains the first context, e.g. network for network.interface.wan**

| path                                          | Description                     | Package      |
|-----------------------------------------------|---------------------------------|--------------|
| [dhcp](/docs/guide-developer/ubus/dhcp)       | dhcp server                     | odhcpd       |
| [file](/docs/guide-developer/ubus/file)       | file                            | rpcd         |
| [hostapd](/docs/guide-developer/ubus/hostapd) | acesspoints                     | wpad/hostapd |
| [iwinfo](/docs/guide-developer/ubus/iwinfo)   | wireless informations           | rpcd iwinfo  |
| [log](/docs/guide-developer/ubus/log)         | logging                         | procd        |
| [mdns](/docs/guide-developer/ubus/mdns)       | mdns avahi replacement          | mdnsd        |
| [network](/docs/guide-developer/ubus/network) | network                         | netifd       |
| [service](/docs/guide-developer/ubus/service) | init/service                    | procd        |
| [session](/docs/guide-developer/ubus/session) | Session management              | rpcd         |
| [system](/docs/guide-developer/ubus/system)   | system misc                     | procd        |
| [uci](/docs/guide-developer/ubus/uci)         | Unified Configuration Interface | rpcd         |

### procd

Project [procd: Procd system init and daemon management](/docs/techref/procd)

![system&nofooter](/page>docs/guide-developer/ubus/system&nofooter) ![service&nofooter](/page>docs/guide-developer/ubus/service&nofooter) ![log&nofooter](/page>docs/guide-developer/ubus/log&nofooter)

### netifd

Project [netifd: Network Interface Daemon](/docs/techref/netifd)

![network&nofooter](/page>docs/guide-developer/ubus/network&nofooter)

### rpcd

Project [rpcd: OpenWrt ubus RPC daemon for backend server](/docs/techref/rpcd) is a set of small plugins providing sets of `ubus` procedures in separated namespaces. These plugins are not strictly related to any particular software (like `netifd` or `dhcp`) so it wasn't worth it to implement them as separated projects. rpcd and the desired plugins must be available or installed via opkg. After installing remember to enable and start the service via `service rpcd enable` and `service rpcd start` .

![file&nofooter](/page>docs/guide-developer/ubus/file&nofooter) ![iwinfo&nofooter](/page>docs/guide-developer/ubus/iwinfo&nofooter)

Always included in `rpcd`:

![session&nofooter](/page>docs/guide-developer/ubus/session&nofooter) ![uci&nofooter](/page>docs/guide-developer/ubus/uci&nofooter)

## What's the difference between ubus vs dbus?

[D-Bus](https://en.wikipedia.org/wiki/D-Bus) is bloated, its C API is very annoying to use and requires writing large amounts of boilerplate code. In fact, the pure C API is so annoying that its own API documentation states: "If you use this low-level API directly, you're signing up for some pain."

`ubus` is tiny and has the advantage of being easy to use from regular C code, as well as automatically making all exported API functionality also available to shell scripts with no extra effort.

## Examples

### FHEM

#### User mapping

In this example we map username `root` to `fhem_acl` for [FHEM](/docs/guide-user/services/automation/fhem) server. Edit `/etc/config/rpcd`:

``` bash
# /etc/config/rpcd
config login
    option username 'root'
    option password '$p$root'
    list read '*'
    list write '*'

config login
    option username 'fhem'
        #
        # '$p$<username> => reference to user passowrd on /etc/shadow
        # '$1$<hash>' => crypt() hash, using SHA1. generate via 'uhttpd -m fhem'
        #
        # password: fhem
        #
    option password '$1$$xEODf2fNSQ0ArfkJu4L2i1'
    #
        # map username to rpcd acl name "fhem_acl"
        #
        list read 'fhem_acl'
    list write ''
```

Then reload rpcd config:

``` bash
uci commit rpcd
```

#### User ACL

All files under `/usr/share/rpcd/acl.d/` will be merge by `rpcd` to one config file!!

``` bash
ubus call hostapd.wlan0 get_clients
ubus call hostapd.wlan1 get_clients
```

Example permissions to run ubus calls remote by fhem over http/json.

``` yaml
{
        "fhem_acl": {
                "description": "FHEM PRESENCE Module User.. https://github.com/janLo/OpenWRT-Wifi-Clients-POC",
                "read": {
                        "ubus": {
                                "hostapd.wlan0": [ "get_clients" ],
                                "hostapd.wlan1": [ "get_clients" ]
                        }
                }
        }
}
```

FHEM Server - show all connected wireless clients:

``` bash
$ python wifi_clients.py
Usage: wifi_clients.py.orig <OpenWrt_Host> <User> <Pass> <WiFi_1> [<WiFi2> ...]
$ python wifi_clients.py 192.168.1.71 fhem fhem wlan0 wlan1
c8:f6:50:e1:a9:10, 2c:f0:a2:e2:c0:15, 8c:a9:82:f1:9c:2a, 7c:c3:a1:b8:d2:1e, 64:9a:be:6a:6c:13, 00:1d:63:a3:8f:4a
```

### Getting firmware version

Get firmware version with [JSON RPC](https://github.com/openwrt/luci/wiki/JsonRpcHowTo).

``` bash
luci_rpc() {
local LIB="${1}"
local DATA="${2}"
local URL="https://${HOST}/\
cgi-bin/luci/rpc/${LIB}?auth=${TOKEN}"
curl -s -k -d "${DATA}" "${URL}" \
| jsonfilter -e "$['result']"
}
HOST="localhost"
USER="root"
PASS=""
DATA="{ \"id\": 1, \"method\": \"login\",
\"params\": [ \"${USER}\", \"${PASS}\" ] }"
TOKEN="$(luci_rpc auth "${DATA}")"
DATA="{ \"id\": 2, \"method\": \"exec\",
\"params\": [ \"ubus call system board\" ] }"
VERSION="$(luci_rpc sys "${DATA}" \
| jsonfilter -e "$['release']['version']")"
echo "${VERSION}"
```

Get firmware version with ubus RPC.

``` bash
ubus_rpc() {
local DATA="${1}"
local URL="https://${HOST}/ubus"
curl -s -k -d "${DATA}" "${URL}" \
| jsonfilter -e "$['result']"
}
HOST="localhost"
USER="root"
PASS=""
DATA="{ 'jsonrpc': '2.0', 'id': 1, 'method': 'call',
'params': [ '00000000000000000000000000000000', 'session',
'login', { 'username': '${USER}', 'password': '${PASS}' } ] }"
SESSION="$(ubus_rpc "${DATA}" \
| jsonfilter -e "$[*]['ubus_rpc_session']")"
DATA="{ 'jsonrpc': '2.0', 'id': 2, 'method': 'call',
'params': [ '${SESSION}', 'system', 'board', {} ] }"
VERSION="$(ubus_rpc "${DATA}" \
| jsonfilter -e "$[*]['release']['version']")"
echo "${VERSION}"
```

---

# UCI (Unified Configuration Interface) – Technical Reference

This is the Technical Reference. Please see **[UCI (Unified Configuration Interface) – Usage](/docs/guide-user/base-system/uci)**

Source code is available here <http://git.openwrt.org/project/uci.git>

### What is UCI?

`UCI` is a small utility written in [C](https://en.wikipedia.org/wiki/C (programming language)) (a [shell script](https://en.wikipedia.org/wiki/shell script)-wrapper is available as well) and is intended to *centralize* the whole configuration of a device running OpenWrt. UCI is the successor of the NVRAM based configuration found in the historical OpenWrt branch [White Russian](/about/history) and a wrapper for the standard configuration files programs bring with them, like e.g. `/etc/network/interfaces`, `/etc/exports`, `/etc/dnsmasq.conf`, `/etc/samba/samba.conf` etc.

> [![NOTE](../wiki/chunked-reference/wiki_page-techref-luci2.md)]
> UCI configuration files are located in the directory **`/etc/config/`**
>
> Their documentation can be accessed online in the OpenWrt-Wiki under [UCI configuration files](/docs/guide-user/base-system/uci).

They can be altered with any text editor or with the command line utility program `uci` or through various programming APIs (like Shell, Lua and C). The WUI [luci](/docs/techref/luci) e.g. uses Lua to manipulate them.

### Dependencies of UCI

- `libuci` a small library for UCI written in [C](https://en.wikipedia.org/wiki/C (programming language))
  - `libuci-lua` is a libuci-plugin for [Lua](https://en.wikipedia.org/wiki/Lua (programming language)) which is utilized by e.g. [luci](/docs/techref/luci)

Both are maintained in the same git as UCI.

## Packages

The functionality is provided by the two packages `uci` and `libuci`. The package `libuci-lua` is also available.

| Name       | Size in Bytes | Description                                                                                                                        |
|:-----------|---------------|------------------------------------------------------------------------------------------------------------------------------------|
| uci        | 7196          | Utility for the Unified Configuration Interface (UCI)                                                                              |
| libuci     | 18765         | C library for the Unified Configuration Interface (UCI)                                                                            |
| libuci-lua | ~6000         | libuci-plugin for [Lua](https://en.wikipedia.org/wiki/Lua (programming language)), e.g. [luci](/docs/techref/luci) makes use of it |

### Installed Files

#### uci

| path/file          | file type    | Description                                         |
|:-------------------|--------------|:----------------------------------------------------|
| /sbin/uci          | binary       | uci executable                                      |
| /lib/config/uci.sh | shell script | Shell script compatibility wrappers for `/sbin/uci` |

#### libuci

| path/file                 | file type | Description              |
|:--------------------------|-----------|:-------------------------|
| /lib/libuci.so            | symlink   | symlink to libuci.so.xxx |
| /lib/libuci.so.2011-01-19 | binary    | Library                  |

#### libuci-lua

| path/file           | file type | Description |
|:--------------------|-----------|:------------|
| /usr/lib/lua/uci.so | binary    | Library     |

## CLI behaviour

All `uci set`, `uci add`, `uci rename` and `uci delete` commands are staged in `/tmp/.uci` and written to flash at once with `uci commit`. Note that subsequent calls to uci get before uci commit will return the staged value.

The reload_config script will reload the necessary configurations based on the last `uci commit`.

This obviously does not apply to people using text editors, but to scripts, GUIs and other programs working with uci files.

## CLI Usage

Let's create a new section in `/etc/config/firewall` that looks like that:

    config zone 'guest_zone'
        option enabled '1'
        option name 'guest'
        option input 'REJECT'
        option forward 'REJECT'
        option output 'ACCEPT'
        list network 'guest_network'

Execute commands:

``` bash
# delete a section 'guest_zone' if any to start from scratch
uci -q delete network.guest_dev
# creates a section called 'guest_zone'
uci add firewall guest_zone
# specify the section type
uci set firewall.guest_zone=zone
# set enabled option
uci set firewall.guest_zone.enabled=1
uci set firewall.guest_zone.name='guest'
uci set firewall.guest_zone.input='REJECT'
uci set firewall.guest_zone.forward='REJECT'
uci set firewall.guest_zone.output='ACCEPT'
# add a list option
uci add_list firewall.guest_zone.network='guest_network'
# get the enabled option of the guest_zone section
uci get firewall.guest_zone.enabled
# show the new added section
uci show firewall.guest_zone
# show the full firewall config before commit
uci show firewall
# save the changes to /etc/config/firewall
uci commit firewall
```

## ubus interface (rpcd)

If you want to access or modify uci configuration via ubus, [rpcd implements this](commit>?p=project/rpcd.git;a=blob;f=uci.c;h=3cd2b829efd055e3096da1499fbf2e70f5f1850b;hb=HEAD). It has its own set of commands which are not exactly the same as those in the CLI.

**Significantly**, it has its own apply/confirm/reload_config mechanism designed to support the LuCI frontend, and it does not do exactly the same thing as the reload_config script. Also, if provided with a ubus_rpc_session as the LuCI does, rather than storing staged changes in `/tmp/.uci` it stores them in `/tmp/run/rpcd/uci-<ubus_rpc_session>` (you can get the CLI to use or view these changes with `-t/-p/-P`).

## LuCI

The LuCI frontend most commonly interacts with UCI via [uci.js](https://openwrt.github.io/luci/jsapi/LuCI.uci.html). This pretends that it has ordinary get/set methods, but these get/set methods do not make calls of the backend, as it maintains its own staged changes (i.e. separate from the staged changes on the backend). The basic flow is:

- `uci.load('someconfig')` \# loads all of someconfig into memory via ubus
- `uci.set('someconfig', 'somesection', 'someoption', 'somevalue')` \# adds to the list of changes to someconfig (similar to how staged changes work in the backend)
- `uci.save()` \# stage the changes in the backend via ubus
- `uci.apply()` \# apply the changes in the backend, but with a 10 sec automatic rollback if not confirmed, implemented via ubus

However, the standard frontend handleSave/handleSaveApply methods do \_not\_ call uci.apply(), but instead call [ui.changes.apply](https://openwrt.github.io/luci/jsapi/LuCI.ui.changes.html). This in turn calls a separate [HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md) endpoint (not via uhttp-mod-ubus) implemented in lua (\<=OpenWrt 22) or ucode (\>=OpenWrt 23), which itself calls ubus.

**Warning**: as well as the backend uci maintaining staged changes, and the frontend uci.js maintaining staged changes, the form elements (AbstractValues) have their own view of the config (cfgvalue) which is used to determine if they should save changes (i.e. saves only occur if the cfgvalue is different from the formvalue).

------------------------------------------------------------------------

## ucode Bindings for UCI

Use in `ucode` scripts is provided by the `ucode-mod-uci` package. This package should already be installed on your device as it's a dependency of `firewall4`.

The [API documentation](https://ucode.mein.io/module-uci.html) is quite throrough, but here's a small example to get you started.

``` javascript
#!/usr/bin/ucode -S

import { cursor } from 'uci';
let uci = cursor();

printf("configs:\n");
let configs = uci.configs();
for (let item in configs) {
    printf("  %s\n", item);
}

function show_section(config, section)
{
    printf("%s.%s:\n", config, section);
    for (let item, value in uci.get_all(config, section)) {
        printf("  %s = %s\n", item, value);
    }
}

show_section("dhcp", "@host[0]");
show_section("system", "ntp");
```

## Lua Bindings for UCI

For those who like lua, UCI can be accessed in your code via the package `libuci-lua`. Just install the package then, in your lua code do `require("uci")`

## API

The api is quite simple

### top level entry point

[uci.cursor()](../ucode/chunked-reference/c_source-api-module-uci.md) instantiates a uci context instance, e.g:

``` lua
x = uci.cursor()
```

if you want to involve state vars:

``` lua
x = uci.cursor(nil, "/var/state")
```

if you need to work on UCI config files that are located in a non standard directory:

``` lua
x = uci.cursor("/etc/mypackage/config", "/tmp/mypackage/.uci")
```

### on that you can call the usual operations

Get value (returns `string` or `nil` if not found):

``` lua
x:get("config", "sectionname", "option")

-- real world example:
x:get("network", "lan", "proto")
```

Set simple string value:

``` lua
x:set("config", "sectionname", "option", "value")

-- real world example:
x:set("network", "lan", "proto", "dhcp")
```

Set list value:

``` lua
x:set("config", "sectionname", "option", { "foo", "bar" })

-- real world example:
x:set("system", "ntp", "server", {
  "0.openwrt.pool.ntp.org",
  "1.openwrt.pool.ntp.org",
  "2.openwrt.pool.ntp.org",
  "3.openwrt.pool.ntp.org"
})
```

Delete option:

``` lua
x:delete("config", "section", "option")

-- real world example:
x:delete("network", "lan", "force_link")
```

Delete section:

``` lua
x:delete("config", "section")

-- real world example:
x:delete("network", "wan6")
```

Add new anonymous section "type" and return its name:

``` lua
x:add("config", "type")
```

``` lua
> -- real world example from interpreter:
> name = x:add("network", "switch")
> print(name)
cfg0e3777
```

Add new section "name" with type "type":

``` lua
x:set("config", "name", "type")

-- real world example:
x:set("network", "wan6", "interface")
```

Iterate over all section of type "type" and invoke a callback function:

``` lua
x:foreach("config", "type", function(s) ... end)
```

In the preceding example, s is a table containing all options and two special properties:

     * ''s['.type']'' -> section type
     * ''s['.name']''  -> section name

If the callback function returns `false` \[NB: **not** `nil`!\], `foreach()` will terminate at that point without iterating over any remaining sections. `foreach()` returns `true` if at least one section exists and the callback function didn't raise an error for it; `false` otherwise.

Here's another example:

``` lua
> -- real world example from interpreter:
> x:foreach("system", "led", function(s)
>>     print('------------------')
>>     for key, value in pairs(s) do
>>         print(key .. ': ' .. tostring(value))
>>     end
>> end)
------------------
dev: 1-1.1
.anonymous: false
trigger: usbdev
.index: 2
name: USB1
interval: 50
.name: led_usb1
.type: led
sysfs: tp-link:green:usb1
------------------
dev: 1-1.2
.anonymous: false
trigger: usbdev
.index: 3
name: USB2
interval: 50
.name: led_usb2
.type: led
sysfs: tp-link:green:usb2
------------------
.name: led_wlan2g
.type: led
name: WLAN2G
trigger: phy0tpt
sysfs: tp-link:blue:wlan2g
.anonymous: false
.index: 4
```

Move a section to another position. Position starts at 0. This is for example handy to change the wireless config order (changing priority).

``` lua
x:reorder("config", "sectionname", position)
```

Discard any changes made to the configuration, that have not yet been committed:

``` lua
x:revert("config")
```

commits (saves) the changed configuration to the corresponding file in `/etc/config`

``` lua
x:commit("config")
```

That's basically all you need.

#### About uci structure

It took me some time to understand the difference between "section" and "type". Let's start with an example:

    #uci show system
    system.@system[0]=system
    system.@system[0].hostname=OpenWrt
    system.@system[0].timezone=UTC
    system.@rdate[0]=rdate
    system.@rdate[0].server=ac-ntp0.net.cmu.edu ptbtime1.ptb.de ac-ntp1.net.cmu.edu ntp.xs4all.nl ptbtime2.ptb.de cudns.cit.cornell.edu ptbtime3.ptb.de

Here, `x:get("system","@rdate[0]","server")` won't work. rdate is a type, not a section.

Here is the return of `x:get_all("system")`:

``` lua
{
  cfg02f02f = {
    [".name"] = "cfg02f02f",
    [".type"] = "system",
    hostname = "OpenWrt",
    [".index"] = 0,
    [".anonymous"] = true,
    timezone = "UTC"
  },
  cfg04e10c = {
    [".name"] = "cfg04e10c",
    [".type"] = "rdate",
    [".index"] = 1,
    [".anonymous"] = true,
    server = {
      "ac-ntp0.net.cmu.edu",
      "ptbtime1.ptb.de",
      "ac-tp1.net.cmu.edu",
      "ntp.xs4all.nl",
      "ptbtime2.ptb.de",
      "cudns.cit.cornell.edu",
      "ptbtime3.ptb.de"
    }
  }
}
```

`[".type"]` gives the type of the section;

`[".name"]` gives the real name of the section (note that these names are auto-generated);

`[".index"]` is the index of the list (starting from 1);

From what I know, there seem to be no way to access `"@rdate[0]"` directly. You have to iterate with `x:foreach` to list all the elements of a given type.

I use the following function:

``` lua
uci=require("uci")
function getConfType(conf,type)
   local curs=uci.cursor()
   local ifce={}
   curs:foreach(conf,type,function(s) ifce[s[".index"]]=s end)
   return ifce
end
```

`getConfType("system","rdate")` returns:

``` lua
{
  {
    [".name"] = "cfg04e10c",
    [".type"] = "rdate",
    [".index"] = 1,
    [".anonymous"] = true,
    server = {
      "ac-ntp0.net.cmu.edu",
      "ptbtime1.ptb.de",
      "ac-ntp1.net.cmu.edu",
      "ntp.xs4all.nl",
      "ptbtime2.ptb.de",
      "cudns.cit.cornell.edu",
      "ptbtime3.ptb.de"
    }
  }
}
```

So if you want to modify `system.@rdate[0].server` you need to iterate the type, retrieve the section name `[".name"]` and then call:

``` lua
x:set("system","cfg04e10c","server","zzz.com")
```

Hope this helps.

Sophana

(Luci has however a [Cursor:get_first](https://openwrt.github.io/luci/api/modules/luci.model.uci.html#Cursor.get_first) function that is similar to get except it takes a type instead as section as second argument.)

------------------------------------------------------------------------

## Usage outside of OpenWrt

If you want to use the libuci apart from OpenWrt (for e.g. you are developing an application in C on your host computer) then prepare as follows: Note that libuci depends on \[libubox\]

Grab the source.

    git clone https://git.openwrt.org/project/uci.git

Go to the source directory (where the [CMakeLists.txt](../wiki/chunked-reference/wiki_page-guide-developer-creating-a-cmake-package-in-openwrt.md) lives) and optionally configure the build without Lua bindings:

    cd uci/; cmake [-D BUILD_LUA:BOOL=OFF] .

Build and install uci as root (this will install uci into /usr/local/, see this thread on how to install and use uci without root permissions in your home directory: <https://forum.openwrt.org/viewtopic.php?id=40547>):

    make install

**Setup library search paths using `ld.so.conf`**

Setting your system library search path can be done in many ways, and is largely out of scope of the OpenWrt wiki.

Open /etc/ld.so.conf and add the place where you installed the uci library:

    vi /etc/ld.so.conf

Add this line somewhere to /etc/ld.so.conf

    /usr/local/lib

Execute ldconfig as root to apply the changes to /etc/ld.so.conf

    ldconfig

**Setup library search paths using `Using LD_LIBRARY_PATH`**

Alternatively, just `export LD_LIBRARY_PATH=<where/you/installed/the/.so>`

**Building your own application**

To compile your application you have to link it against the uci library. Append -luci in your Makefile:

    $(CC) test.o -o test -luci

And examples on how to use UCI in C can be found in this thread: <https://forum.openwrt.org/viewtopic.php?pid=183335#p183335> To get more examples look into the source directory of uci which you got by git clone and open cli.c or ucimap-example.c

### Building and running tests with scripts/devel-build.sh

Assuming you already have the following packages installed: [install-buildsystem](/docs/guide-developer/toolchain/install-buildsystem).

Additional packages required (package names for ubuntu):

    cmake pkgconf python3.13-venv valgrind

Clone the repo. Run:

    cd uci
    scripts/devel-build.sh

## See also

1.  [UCI command usage](https://wiki.teltonika-networks.com/view/UCI_command_usage)

---

# EasyCwmp (CPE WAN Management Protocol daemon)

EasyCwmp project is a client implementation of [TR-069](http://en.wikipedia.org/wiki/TR-069) for OpenWrt. Code is licensed under GPL 2 and can be accessed at www.easycwmp.org

EasyCwmp is developed by PIVA Software.The aim of this project is to be fully compliant with the TR069 CWMP standard.

## EasyCwmp Presentation in Broadban Worl Forum

![](youtube>2dzLzk8I_So)

## Compliant Standards

-  TR-069: CPE WAN Management Protocol v1.1
-  TR-098: Internet Gateway Device version 1 (Data Model for TR-069)
-  TR-181: Device version 2.
-  TR-104: Provisioning Parameters for VoIP CPE version 2
-  TR-106: Data Model Template for TR-069-Enabled Devices
-  TR-111: Applying TR-069 to Remote Management of Home Networking Devices

## EasyCwmp design

The EasyCwmp design includes 2 parts:

-  EasyCwmp core: it includes the TR069 CWMP engine and it is in charge of communication with ACS server. It is developed with C.
-  EasyCwmp DataModel: it includes the DATAModel of TR-06 and it is compliant to some DataModel standards such as TR-098, TR-181, TR-104, ...

The key design goal is to separate the CWMP method execution from the CWMP engine. That makes easy to add and test new features.

DataModel is developped with shell as free solution and with C as commercial solution.

## Benefits

-  Easy to update the DataModel parameters thanks to the DataModel solution design.
-  Easy to install on Linux systems and to port on POSIX systems thanks to the design flexibility.
-  Easy to use thanks to the availability of a good documentation.
-  Supports all required TR-069 methods.
-  Supports integrated file transfer ([HTTP](../wiki/chunked-reference/wiki_page-guide-developer-adding-new-device.md), HTTPS, FTP).
-  Supports SSL.
-  Supports IPv6.

## Interoperability

-  ACSLite (Commercial ACS from Netmania)
-  tGem (Commercial ACS from Tilgin)
-  Open ACS/LibreACS (open source ACS)
-  GenieACS (open source ACS)
-  FreeACS (open source ACS)

## Install

#### EasyCwmp

EasyCwmp is mainly developed and tested with OpenWRT Linux platform.

Download:

Download the easycwmp-openwrt-{x}.{y}.{z}.tar.gz and then copy it to your /path/to/openwrt/package/

      cd /path/to/openwrt/package/
      tar -xzvf easycwmp-openwrt.tar.gz
      cd ..

Build as built-in

      make menuconfig   #(And then select the package as <*>)
      make

Build as package:

      make menuconfig   #(And then select the package as <M>)
      make package/easycwmp/compile

Install:

Build as built-in: install your OpenWRT system in your device according to the OpenWRT manuals and then start your system and you will get easycwmp running automatically

Build as package: copy the package to the OpenWRT system and then install it with:

      opkg install

And then run it with:

      /etc/init.d/easycwmpd start

or run it with:

      /etc/init.d/easycwmpd boot

Note: If you run easycwmpd with start command then it will send inform to the ACS containing "2 PERIODIC" event and send GetRPCMethods to the ACS. And if you run easycwmpd with boot command then it will send inform to the ACS containing "1 BOOT" event.

Note: A third party application could trigger EasyCwmp daemon to send notify (inform with value change event) by calling the command:

      ubus call tr069 notify

If the EasyCwmp daemon receive the ubus call notify then it will check if there is a value changed of parameters with notification not equal to 0

#### microxml

If you got any problem related to libmicroxml when building EasyCwmp in OpenWRT, then you can use the following libmicroxml package:

      cd /path/to/openwrt/package/
      wget http://easycwmp.org/download/libmicroxml.tar.gz

---

# unetd

unetd is a WireGuard based VPN daemon that simplifies creating and managing fully-meshed VPN connections between OpenWrt routers.

Source: [project/unetd.git](commit>project/unetd.git)

## Features

      * Splits network setup into network config (shared across all participating nodes) and local config (limited mostly to local private key, public signing device key, optionally tunnel device names)
      * Supports automatic replication of peer IP addresses
      * Supports automatic replication of network config updates
        * network config data is secure and protected by a Ed25519 signature
        * network config data replication is encrypted and only available to members of the network, even during bootstrap
      * Fully meshed (all nodes connect to each other directly unless configured otherwise)
      * Supports automatic VXLAN setup with multiple peers
        * automatically installs eBPF program to deal with MTU limitations and avoid fragmentation
      * Automatic setup of routes / IP addresses based on network config data
      * Supports direct connection through double-NAT, as long as the network has one node with a public IP address
      * Simple CLI for creating and updating networks between OpenWrt hosts with very few commands
      * Builds and runs on regular Linux distributions as well, and also macOS (with some limitations)
      * Automatically assigns an IPv6 address for each host, which is generated from the host public key
      * writes a host file containing entries for all configured hosts
        * can be used with dnsmasq for local lookup
        * configurable domain suffix
      * allows creating freeform service definitions, which allows services to query member IP addresses using ubus
      * Supports peer discovery via BitTorrent 'Mainline' DHT, which works even through double-NAT

## Building

### OpenWrt

TBC

### Linux

The following build dependencies are required:

      * cmake, pkg-config
      * libelf-dev, zlib1g-dev, libjson-c-dev

To build:

    git clone https://git.openwrt.org/project/unetd.git
    cd unetd
    ./build.sh

## Example setup

#### Preparation

This set of example commands assumes two OpenWRT routers with the IP addresses `192.168.1.13` and `192.168.1.15` which have **not** been configured for unetd yet, each has `unetd`, `unet-cli` and `unet-tool` installed. `vxlan` (and its implied `kmod-vxlan`) are also installed. The assumption here is that the local host, here say `192.168.1.2` has these installed, and also forms a unet node.

Note: `unetd` is not yet capable of installing these prerequisites above via `opkg`.

#### Example

This creates a new JSON file `test.json` locally and also generates a signing key in `test.json.key` locally (if it doesn't exist already):

    # unet-cli test.json create

Result:

    test.json:
    {
        "config": {
            "port": 51830,
            "keepalive": 10,
            "peer-exchange-port": 51831
        },
        "hosts": {
        },
        "services": {
        }
    }

This creates a VXLAN tunnel definition in `test.json` and predicates hosts that are to be members of it via the `ap` group:

    # unet-cli test.json add-service l2-tunnel type=vxlan members=@ap

Result:

    test.json:
    {
        ...
        "services": {
            "l2-tunnel": {
                "config": {
                },
                "members": [
                    "@ap"
                ],
                "type": "vxlan"
            }
        }
    }

This connects to 192.168.1.13 over SSH, and on 192.168.1.13, generates an unetd interface named `unet`, along with new host keys, puts in the signing key and also tells it to create the `vx0` VXLAN device connected to the `l2-tunnel` service description we created in the last command, storing its public key in the local `test.json`, along with its endpoint address `192.168.1.13`:

    # unet-cli test.json add-ssh-host ap1 root@192.168.1.13 endpoint=192.168.1.13 tunnels=vx0:l2-tunnel groups=ap

Note: you will authenticate via SSH, either user:pass or key based, if that was set up in advance.

Result:

    test.json:
    {
        ...
        "hosts": {
            "ap1": {
                "key": "....=",
                "endpoint": "192.168.1.13",
                "groups": [
                    "ap"
                ]
            }
        },
        ...
    }

This does the same for the other host:

    # unet-cli test.json add-ssh-host ap2 root@192.168.1.15 endpoint=192.168.1.15 tunnels=vx0:l2-tunnel groups=ap

Result:

    test.json:
    {
        ...
        "hosts": {
            ...
            "ap2": {
                "key": "...=",
                "endpoint": "192.168.178.1",
                "groups": [
                    "ap"
                ]
            }
        },
        ...
    }

This signs the network data and uploads it to unetd running on 192.168.1.13:

    # unet-cli test.json sign upload=192.168.1.13

By now, uploading the data to one of the two hosts is enough, because once it (192.168.1.13) has processed the update, it (192.168.1.13) will find the endpoint address of the other host (192.168.1.15) and sync the network data with it automatically. After that last command, the unetd network should be up on both sides, and the VXLAN tunnel created as well.

## Configuration

### UCI network interface

Configuration of a `interface` section in /etc/config/network for unetd.

| Name       | Type    | Required | Description                                                                                                          |
|------------|---------|----------|----------------------------------------------------------------------------------------------------------------------|
| `proto`    | string  | required | Needs to be `unet`                                                                                                   |
| `device`   | string  | required | Name of the tunnel device                                                                                            |
| `key`      | string  | required | Local wireguard key                                                                                                  |
| `auth_key` | string  | required | Key used to sign network config                                                                                      |
| `tunnels`  | list    |          | List of tunnel devices mapped to VXLAN service definitions in the network config (format: `<device>=<servicename>`). |
| `connect`  | list    |          | List of external unetd host IP addresses to download network config updates from                                     |
| `domain`   | string  |          | Domain suffix for hosts in the generated hosts file                                                                  |
| `dht`      | boolean |          | Enable DHT peer discovery for this network                                                                           |

The `connect` option only needs to be used for bootstrapping the setup in case you're not uploading the network data to the node directly. Once unetd has a working peer connection, it will always replicate updates over the tunnel.

### Network config data

Network config is written as a JSON file.

##### Example:

    {
            "config": {
                    "port": 51830,
                    "keepalive": 10,
                    "peer-exchange-port": 51831,
                    "stun-servers": [
                            "stun.l.google.com:19302",
                            "stun1.l.google.com:19302"
                    ]
            },
            "hosts": {
                    "ap1": {
                            "key": "yB3V0Wz37qheZoZiG0KNFAqfuI2TetO4sfXgqO/Gd0c=",
                            "endpoint": "192.168.1.13",
                            "groups": [
                                    "ap"
                            ]
                    },
                    "ap2": {
                            "key": "aGNcyMLrN+C4WW0nJBUGwqw8ifIleUVefv/9vh+d1Fw=",
                            "endpoint": "192.168.1.15",
                            "groups": [
                                    "ap"
                            ]
                    }
            },
            "services": {
                    "l2-tunnel": {
                            "config": {
                            },
                            "members": [
                                    "@ap"
                            ],
                            "type": "vxlan"
                    }
            }
    }

##### Config properties:

| Name                 | Type             | Description                                                                |
|:---------------------|:-----------------|:---------------------------------------------------------------------------|
| `port`               | int              | Wireguard tunnel port (can be overriden for individual hosts)              |
| `keepalive`          | int              | Interval (in seconds) for keepalive and forcing peer reconnection attempts |
| `peer-exchange-port` | int              | Port for exchanging peer messages on the WireGuard tunnel (0: disabled)    |
| `stun-servers`       | array of strings | List of STUN servers written as hostname:port strings                      |

##### Host properties:

| Name                 | Type             | Description                                                                                                              |
|:---------------------|:-----------------|:-------------------------------------------------------------------------------------------------------------------------|
| `key`                | string           | Wireguard public key                                                                                                     |
| `groups`             | array of strings | Names of groups that the host is a member of                                                                             |
| `ipaddr`             | array of strings | Local IP addresses of the host (IPv4 or IPv6)                                                                            |
| `subnet`             | array of strings | Subnets routed by the host (IPv4 or IPv6) (format: `<addr>/<mask>`)                                                      |
| `port`               | int              | Wireguard tunnel port (overrides `config` property)                                                                      |
| `peer-exchange-port` | int              | Host specific port for exchanging peer messages on the WireGuard tunnel (0: disabled)                                    |
| `endpoint`           | string           | Public endpoint address (format: `<addr>` for IPv4, `[<addr>]` for IPv6 with optional `:<port>` suffix)                  |
| `gateway`            | string           | Name of another host to use as gateway (can be used for avoiding direct connections with all other peers from this host) |

##### Service properties

| Name      | Type             | Description                                                 |
|:----------|:-----------------|:------------------------------------------------------------|
| `type`    | string           | Service type                                                |
| `config`  | object           | Service type specific config options                        |
| `members` | array of strings | Members assigned to this service (use `@<name>` for groups) |

### CLI usage

    Usage: unet-cli [<flags>] <file> <command> [<args>] [<option>=<value> ...]

         Commands:
          - create:                                 Create a new network file
          - set-config:                             Change network config parameters
          - add-host <name>:                        Add a host
          - add-ssh-host <name> <host>:             Add a remote OpenWrt host via SSH
                                                    (<host> can contain SSH options as well)
          - set-host <name>:                        Change host settings
          - set-ssh-host <name> <host>:             Update local and remote host settings
          - add-service <name>:                     Add a service
          - set-service <name>:                     Change service settings
          - sign                                    Sign network data

         Flags:
          -p:                                       Print modified JSON instead of updating file

         Options:
          - config options (create, set-config):
            port=<val>                              set tunnel port (default: 51830)
            pex_port=<val>                          set peer-exchange port (default: 51831, 0: disabled)
            keepalive=<val>                         set keepalive interval (seconds, 0: off, default: 10)
            stun=[+|-]<host:port>[,<host:port>...]  set/add/remove STUN servers
          - host options (add-host, add-ssh-host, set-host):
            key=<val>                               set host public key (required for add-host)
            port=<val>                              set host tunnel port number
            pex_port=<val>                          set host peer-exchange port (default: network pex_port, 0: disabled)
            groups=[+|-]<val>[,<val>...]            set/add/remove groups that the host is a member of
            ipaddr=[+|-]<val>[,<val>...]            set/add/remove host ip addresses
            subnet=[+|-]<val>[,<val>...]            set/add/remove host announced subnets
            endpoint=<val>                          set host endpoint address
            gateway=<name>                          set host gateway (using name of other host)
         - ssh host options (add-ssh-host, set-ssh-host)
            auth_key=<key>                          use <key> as public auth key on the remote host
            priv_key=<key>                          use <key> as private host key on the remote host (default: generate a new key)
            interface=<name>                        use <name> as interface in /etc/config/network on the remote host
            domain=<name>                           use <name> as hosts file domain on the remote host (default: unet)
            connect=<val>[,<val>...]                set IP addresses that the host will contact for network updates
            tunnels=<ifname>:<service>[,...]        set active tunnel devices
         - service options (add-service, set-service):
            type=<val>                              set service type (required for add-service)
            members=[+|-]<val>[,<val>...]           set/add/remove service member hosts/groups
         - vxlan service options (add-service, set-service):
            id=<val>                                set VXLAN ID
            port=<val>                              set VXLAN port
            mtu=<val>                               set VXLAN device MTU
            forward_ports=[+|-]<val>[,<val>...]     set members allowed to receive broadcast/multicast/unknown-unicast
         - sign options:
            upload=<ip>[,<ip>...]                   upload signed file to hosts

### DHT support

For DHT peer discovery, the unet-dht package needs to be installed, and dht enabled in the interface on the nodes. For NAT support, you also need to configure at least one working STUN server in the network data. While peers can find each other through DHT directly, STUN is needed for figuring out the external wireguard port and establishing a network connection over it. Please note that DHT based discovery needs some time for peers to actually discover each other, sometimes 1-3 minutes.

---

# Wireless Modes

FIXME This needs to indicate the UCI values for `option mode` to have any value

# Wireless Modes

For setting up the wireless modes see [Documentation](/docs/start)

    iw list

has a section with `Supported interface modes`

## AP

AP ... Access Point Also called "master" mode.

## AP/vlan

Dynamic VLAN tagging support in hostapd. see Kernel: [hostapd](https://wireless.wiki.kernel.org/en/users/documentation/hostapd#dynamic_vlan_tagging) see [ML](http://comments.gmane.org/gmane.linux.kernel.wireless.general/58064)

## IBSS (Ad-Hoc)

## MESH POINT (802.11s)

see [80211s](/docs/guide-user/network/wifi/mesh/80211s)

## MONITOR

radiotap headers package survey and injection

## OCB

Outside Context of a BSS

## P2P Client

P2P (Peer-to-peer) client

## P2P-GO

P2P (Peer-to-peer) Group Owner

## Station (Client)

Alternative name: managed mode Mode when connected to an AP.

## WDS

4address/4-address mode see: [IEEE 4-address](http://www.ieee802.org/1/files/public/802_architecture_group/802-11/4-address-format.doc)

## Links

     * Mode list taken from [[http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/nl80211.h|include/uapi/linux/nl80211.h]]
     * linux-wireless mailing list

---

# Wireless Standards

This article lists common standards and basic features that are relevant to OpenWrt.

## 802.11a

Old standard that operates in 5GHz [frequency band](https://en.wikipedia.org/wiki/Frequency_band)

[IEEE_802.11a-1999](https://en.wikipedia.org/wiki/IEEE_802.11a-1999)

## 802.11b

[IEEE_802.11b-1999](https://en.wikipedia.org/wiki/IEEE_802.11b-1999) Operates in 2.4GHz Band Old standard.

## 802.11g

[](https://en.wikipedia.org/wiki/IEEE_802.11g-2003) Operates in 2.4GHz Band Old standard.

## 802.11n

[IEEE_802.11n-2009](https://en.wikipedia.org/wiki/IEEE_802.11n-2009)

## 802.11ac

[IEEE_802.11ac](https://en.wikipedia.org/wiki/IEEE_802.11ac) Also called "Wifi 5"

## 802.11ad

[IEEE_802.11ad](https://en.wikipedia.org/wiki/IEEE_802.11ad) Not very common in OpenWrt.

## 802.11ax

[IEEE_802.11ax](https://en.wikipedia.org/wiki/IEEE_802.11ax)

Also called "Wifi 6"

### Features in Drivers

Each hardware has certain features that can be queried in OpenWrt by using `iw phy <phy interface> info `

Mismatching features result in compatibility problems and possibly reduced data transfer rates.

example:

    RX LDPC
    HT20/HT40
    SM Power Save disabled
    RX HT20 SGI
    RX HT40 SGI
    TX STBC
    RX STBC 1-stream
    Max AMSDU length: 3839 bytes
    DSSS/CCK HT40

#### MIMO multiple-input and multiple-output

Technology that uses multiple antennas to increase data transfer rates. see also MCS tables

[STBC](https://en.wikipedia.org/wiki/Space%E2%80%93time_block_code) is part of MIMO.

[MU-MIMO](https://en.wikipedia.org/wiki/Multi-user_MIMO)

#### HT, VHT, HE

Required for higher throughput - 802.11n, 802.11ac, 802.11ax standards. HT ... 802.11n , VHT ... 802.11ac, HE ... 802.11ax

HT20 : 20 MHz wide channels HT40: 40 MHz VHT80 : 80 MHz VHT160: 160MHz

see also MCS table

#### MCS Modulation and Coding Scheme

often visualized as a table. The MCS Index is a value that the hardware supports and uses when communicating.

:!: Low data rates mean the higher indexes are not used. Reasons might be configuration or interference.

#### RSDB DBDC

Acronym for Radio Simultan Dual Band, Dual Band Dual Concurrent

Use two frequency bands at the same time by one endpoint.

Supported by: mt76 and potentially brcmfmac ([BCM4359](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/drivers/net/wireless/broadcom?id=d4aef159394d5940bd7158ab789969dab82f7c76) )

Normally radios operate in Single Band Single Concurrent (SBSC) (OpenWrt: 802.11an, 802.11bgn) or are capable of Dual Band Single Concurrent (DBSC): having 2 frequency bands selectable (OpenWrt: 802.11abgn capable).

#### WOW Wake On Wlan

[Wake-on-LAN](https://en.wikipedia.org/wiki/Wake-on-LAN)

## Links

[some MCS Tables](https://www.semfionetworks.com/blog/mcs-table-updated-with-80211ax-data-rates)

---

# Xenomai - real-time framework inside OpenWrt

![cleanup&noheader&nofooter&noeditbtn](/page>meta/infobox/cleanup&noheader&nofooter&noeditbtn) ![wip&noheader&nofooter&noeditbtn](/page>meta/infobox/wip&noheader&nofooter&noeditbtn)

# Xenomai - real-time framework inside OpenWrt

This techref describe a work in progress finalize to support Xenomai (<http://www.xenomai.org/>) real-time framework inside OpenWrt.

:!: This article describe a WIP activity. Don't rely on it. :!:

Thanks to Adeos, Xenomai will receive the interrupts first and decide to handle them or not. If not, they will then be transfered to the regular Linux kernel. Also, Xenomai provides a framework to develop applications which can be easily moved between the Real Time Xenomai environment and the regular Linux system. Moreover, Xeno provides a set of APIs (called "skins") that emulate traditional RTOSes such as VxWorks and pSOS and implement other APIs such as POSIX. Thus, porting third party real time applications to Xenomai is a fairly simple process.[^1]

An example of usage is available on xenomai.org website.

## Pre-condition

Xenomai framework run only on some architecture and generally isn't needed for your purpose; the 2.5.3 version can be used for arm\|x86\|powerpc and only for a specific linux kernel version. Here follows a table that can help you to choise the couple xenomai versione/kernel version per arch.

|                 |         |               |
|:----------------|:--------|--------------:|
| Xenomai version | Arch    | linux version |
| 2.5.3           | arm     |        2.6.33 |
| 2.5.3           | powerpc |        2.6.34 |
| 2.5.3           | x86     |    2.6.34-rc5 |

## Status

Xenomai is intended to be used only for specific purpose and OpenWrt community generally don't support it directly.

[^1]: from <http://www.armadeus.com/wiki/index.php?title=Xenomai>
