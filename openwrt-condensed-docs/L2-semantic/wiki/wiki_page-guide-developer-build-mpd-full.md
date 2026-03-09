---
title: MPD-full building from source
module: wiki
origin_type: wiki_page
token_count: 386
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-build-mpd-full.md
last_pipeline_run: '2026-03-09T18:30:57.384548+00:00'
language: text
---
# MPD-full building from source

More information about building from source: [OpenWrt Buildroot - Usage](/docs/guide-developer/toolchain/start)

Based on the following reference:  
[Help on compiling MPD full](https://forum.openwrt.org/viewtopic.php?pid=158385#p158385)  
If you build from source you will only be able to select the MPD-mini from the make menuconfig interface.  
To display and enable the full version in the menuconfig interface, you'll have to edit the MPD Makefile.

### Barrier Breaker and Chaos Calmer

1.  In your git clone directory edit `/openwrt/feeds/packages/sound/mpd/Makefile`.  
    It is a good idea to make a backup copy before starting.
2.  Detect the area in the Makefile involved with the full MPD installation and edit `+libffmpeg` to `+libffmpeg-full`
3.  Save the file

Orignal file:

      TITLE+= (full)
      DEPENDS+= \
       +AUDIO_SUPPORT:alsa-lib \
       +libaudiofile +BUILD_PATENTED:libfaad2 +libffmpeg +libid3tag \
       +libmms +libogg +libsndfile +libvorbis
      PROVIDES:=mpd
      VARIANT:=full

Edited file:

      TITLE+= (full)
      DEPENDS+= \
       +AUDIO_SUPPORT:alsa-lib \
       +libaudiofile +BUILD_PATENTED:libfaad2 +libffmpeg-full +libid3tag \
       [+libmms +libogg +libsndfile +libvorbis 
      PROVIDES:=mpd
      VARIANT:=full

Now if you start `make menuconfig`, you'll have the choice to build the full or the mini MPD version