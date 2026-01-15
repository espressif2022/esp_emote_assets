# Changelog

All notable changes to the ESP Emote GFX component will be documented in this file.

## [0.1.1] - 2026-01-15
- Add window support

## [0.1.0] - 2026-01-05
- Add support for wake word models (wakenet_model) in config.json
- Delete build_boot.py

## [0.0.3~4] - 2025-12-16
- Remove Pillow dependency to reduce build dependencies

## [0.0.3~3] - 2025-12-6
- Add external path support for build scripts
  - Support `--external_path` parameter in `build_all.py` and `build_boot.py`
  - Search external path first, fallback to local paths if not found
  - Allows importing resources (resolutions, emoji collections, fonts, boot animations) from external directories

## [0.0.3~1] - 2025-12-01
- Remove invalid conversion code
- Change 320*240 layout, add qrcode

## [0.0.3] - 2025-11-17
- Add cmake function of 'build_speaker_assets_bin' and 'build_boot_assets_bin'

