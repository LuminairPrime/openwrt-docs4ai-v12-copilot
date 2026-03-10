# openwrt-docs4ai

OpenWrt documentation collection and condensation pipeline for humans, tooling, and LLM workflows.

## What This Repository Does

This repository pulls documentation from multiple OpenWrt-related sources, normalizes it into stable intermediate layers, and generates compact outputs intended for:

- targeted human lookup
- LLM context ingestion
- IDE and tooling support
- long-term monthly refresh automation

The current development stage is verified stabilization and operational hardening. Local-first validation remains the engineering baseline, and GitHub Actions is now a confirmed remote execution and publication path rather than an unproven future target.

## Source Families

- OpenWrt wiki pages
- `jow-/ucode`
- `openwrt/luci`
- `openwrt/openwrt`
- OpenWrt-adjacent API and example sources extracted from those repositories

## Output Model

Generated artifacts live under `openwrt-condensed-docs/`.

- `L1-raw/` contains normalized raw markdown plus sidecar metadata.
- `L2-semantic/` contains semantic markdown with YAML frontmatter and cross-links.
- Root and per-module outputs contain maps, monoliths, skeletons, HTML landing pages, and telemetry.

The exact output set is defined in `docs/ARCHITECTURE.md` and `docs/specs/v12/`.

## Repository Guidance

- Read `DEVELOPMENT.md` for local setup and testing.
- Read `docs/ARCHITECTURE.md` for repository structure and naming rules.
- Read `docs/specs/v12/` for the active v12 technical specifications.
- Treat `docs/archive/v12/` as historical context only.

## Status

The repository now has both local and remote v12 verification from the 2026-03-09 stabilization pass and the follow-up wiki hardening runs.

- local deterministic smoke coverage is passing
- the sequential local runner is passing
- remote GitHub Actions runs are verified through warm-cache wiki run `22877413563`, with `0` hard failures and `1` soft warning
- push, schedule, and manual workflow runs auto-promote staged generated outputs back into `openwrt-condensed-docs/`; GitHub Pages excludes `L1-raw` and `L2-semantic`
- the remaining work is concentrated in one deferred dockerman ucode soft warning, bounded wiki-derived cleanup, and deciding whether extra corpus telemetry is worth the complexity

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` for details. Generated documentation derives from upstream OpenWrt project sources and retains their respective upstream licensing context.
