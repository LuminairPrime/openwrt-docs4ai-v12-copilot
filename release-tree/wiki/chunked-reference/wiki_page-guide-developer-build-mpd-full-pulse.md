---
title: Building MPD-full with PulseAudio
module: wiki
origin_type: wiki_page
token_count: 390
source_file: L1-raw/wiki/wiki_page-guide-developer-build-mpd-full-pulse.md
last_pipeline_run: '2026-03-28T09:11:39.723949+00:00'
source_url: https://openwrt.org/docs/guide-developer/build.mpd-full.pulse
language: text
ai_summary: This document provides a guide for building MPD-full with PulseAudio on OpenWrt. It outlines the necessary modifications to the Makefile, including adding dependencies for PulseAudio and adjusting compilation flags. Key changes include adding `+pulseaudio-daemon` to DEPENDS and enabling PulseAudio in the configuration. Additionally, it specifies the need to modify the EXTRA_LDFLAGS to include the correct library path for PulseAudio.
ai_when_to_use: Use this guide when you need to build MPD-full with PulseAudio support on OpenWrt, particularly when customizing audio playback capabilities.
ai_related_topics:
- Makefile
- DEPENDS
- EXTRA_LDFLAGS
---

> **Source:** [https://openwrt.org/docs/guide-developer/build.mpd-full.pulse](https://openwrt.org/docs/guide-developer/build.mpd-full.pulse)
> **Kind:** wiki_page | **Method:** scraped
> **Normalized:** 2026-03-28

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
