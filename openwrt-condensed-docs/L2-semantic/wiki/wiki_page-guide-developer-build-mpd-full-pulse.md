---
title: Building MPD-full with PulseAudio
module: wiki
origin_type: wiki_page
token_count: 391
version: N/A
source_file: L1-raw/wiki/wiki_page-guide-developer-build-mpd-full-pulse.md
last_pipeline_run: '2026-03-09T18:30:57.384548+00:00'
language: text
---
# Building MPD-full with PulseAudio

More information about building from source: [OpenWrt Buildroot - Usage](/docs/guide-developer/toolchain/start)

First you need to follow the HowtoBuild [MPD-full building from source](/docs/guide-developer/build.mpd-full)

Based on the following reference: [BB + MPD-full + PulseAudio, unable to build](https://forum.openwrt.org/viewtopic.php?pid=287809#p287809)  

### 18.06.02

#### The MPD Makefile

In your git clone directory edit the makefile `/openwrt/feeds/packages/sound/mpd/Makefile`.

Detect the area in the Makefile involved with the full MPD installation. Add `+pulseaudio-daemon` to DEPENDS.

      TITLE+= (full)
      DEPENDS+= +libffmpeg +libid3tag +libmms +libupnp +libshout +pulseaudio-daemon
      PROVIDES:=mpd
      VARIANT:=full

Edit the --disable-pulse to **--enable-pulse**

         --disable-nfs \
         --disable-openal \
         --disable-opus \
         --enable-pulse \
         --disable-sidplay \
         --disable-smbclient \
         --disable-sndfile \

Edit the EXTRA_LDFLAGS and add

    -Wl,-rpath-link=$(STAGING_DIR)/usr/lib/pulseaudio 

The complete line looks like that:

      EXTRA_LDFLAGS += $(if $(ICONV_FULL),-liconv,-Wl,--whole-archive -liconv -Wl,--no-whole-archive) -Wl,-rpath-link=$(STAGING_DIR)/usr/lib/pulseaudio

Maybe the path has to be adapted to \$(STAGING_DIR)/opt/lib/pulseaudio.