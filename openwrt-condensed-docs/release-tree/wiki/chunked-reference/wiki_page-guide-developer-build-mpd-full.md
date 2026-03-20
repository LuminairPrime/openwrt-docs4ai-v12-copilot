---
title: MPD-full building from source
module: wiki
origin_type: wiki_page
token_count: 383
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-build-mpd-full.md
last_pipeline_run: '2026-03-20T01:28:00.439321+00:00'
language: text
ai_summary: The MPD-full building from source guide provides instructions for enabling the full version of the Music Player Daemon (MPD) in OpenWrt by modifying the Makefile. Users must edit the MPD Makefile located in the OpenWrt feeds directory to change the dependency from `+libffmpeg` to `+libffmpeg-full`. After saving the changes, the full MPD version will be available in the `make menuconfig` interface alongside the mini version. This process is particularly relevant for users building from source who want access to the full feature set of MPD.
ai_when_to_use: This guide is useful when you need to build the full version of MPD from source in OpenWrt, particularly if you require additional audio features not available in the mini version.
ai_related_topics:
- Makefile
- make menuconfig
- MPD
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
