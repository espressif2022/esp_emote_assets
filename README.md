# ESP Emote Assets

ESP Emote Assets is a component for managing emoji and graphics resources in ESP-IDF projects.

## Features

- Support for multiple resolution configurations (360_360, 320_240, etc.)
- Support for multiple font configurations
- Support for multiple emoji collections (emoji_large, emoji_small)
- Automatic SPIFFS assets partition generation
- Build scripts for batch resource generation
- Independent boot animation support

## Directory Structure

```
esp_emote_assets/
├── 360_360/                 # 360x360 resolution config
│   ├── config.json         # Resolution configuration
│   └── layout.json         # Layout configuration
├── 320_240/                 # 320x240 resolution config
│   ├── config.json
│   └── layout.json
├── emoji_large/             # Large emoji resources
├── emoji_small/             # Small emoji resources
├── boot/                    # Boot animation files
│   ├── boot_animation_360_360.eaf
│   └── boot_animation_320_240.eaf
├── scripts/                 # Build scripts
│   └── spiffs_assets/
│       ├── build.py        # Single resource build script
│       ├── build_all.py    # Batch build script
│       └── build_boot.py   # Boot animation script
└── idf_component.yml       # ESP-IDF component configuration
```

## Usage

### 1. As ESP-IDF Component

Add dependency to your project's `idf_component.yml`:

```yaml
dependencies:
  espressif/esp_emote_assets:
    version: "1.0.0"
```

### 2. Build Resources

```bash
# Build all configured resources
cd scripts/spiffs_assets
./build_all.py

# Build specific resolution
./build.py --text_font <font_file> --resolution <resolution_dir> --res_path <emoji_dir>

# Build boot animation
./build_boot.py --src boot_animation_360_360.eaf

```

## Configuration

### Resolution Configuration

Each resolution directory contains a `config.json` file:

```json
{
    "text_font": "font_puhui_common_20_4",
    "emoji_collection": "emoji_large"
}
```

### Boot Animation Files

Boot animation files should be placed in the `boot/` directory with naming convention:
- `boot_animation_360_360.eaf` - Boot animation for 360x360 resolution
- `boot_animation_320_240.eaf` - Boot animation for 320x240 resolution

## Path Configuration

All paths are configured in the scripts, no environment variables needed.

## Output Files

Generated files follow these naming patterns:

- **Resolution assets**: `{resolution}_{font}_{emoji}.bin`
- **Boot animations**: `{src_filename}.bin` (default) or custom filename
- **Single file mode**: Custom filename specified with `--output`
