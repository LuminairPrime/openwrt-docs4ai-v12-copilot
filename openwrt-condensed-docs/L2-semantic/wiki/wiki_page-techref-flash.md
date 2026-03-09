---
title: Flash memory
module: wiki
origin_type: wiki_page
token_count: 3087
version: N/A
source_file: L1-raw/wiki/wiki_page-techref-flash.md
last_pipeline_run: '2026-03-09T18:39:45.812572+00:00'
language: text
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