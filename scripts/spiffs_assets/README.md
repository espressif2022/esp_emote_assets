# SPIFFS Assets Build Scripts

These scripts are used to build SPIFFS assets partitions for ESP-IDF projects.

## Usage

### build_all.py - Batch Build Script

Build multiple SPIFFS assets partitions with different parameter combinations.

```bash
# Build all default resolutions
./build_all.py

# Build specific resolutions
./build_all.py --resolution 360_360 320_240

# Specify single output file
./build_all.py --output /path/to/output.bin

# Combine both options
./build_all.py --resolution 360_360 --output /path/to/custom.bin
```

### build.py - Single Build Script

Build a single SPIFFS assets partition.

```bash
./build.py --text_font <text_font_file> \
           --resolution <resolution_dir> \
           --res_path <res_path_dir>
```

### build_boot.py - Boot Animation Script

Build boot animation assets independently.

```bash
# Build boot animation with default output path
./build_boot.py --src boot_animation_360_360.eaf

# Build boot animation with custom output path
./build_boot.py --src boot_animation_360_360.eaf --output ./final/boot_360_360.bin

# Build boot animation for 320x240
./build_boot.py --src boot_animation_320_240.eaf
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

### Directory Structure

```
esp_emote_assets/
├── 360_360/                 # 360x360 resolution config
│   ├── config.json         # Resolution configuration
│   └── layout.json         # Layout configuration
├── 320_240/                 # 320x240 resolution config
├── emoji_large/             # Large emoji resources
├── emoji_small/             # Small emoji resources
├── boot/                    # Boot animation files
│   ├── boot_animation_360_360.eaf
│   └── boot_animation_320_240.eaf
└── scripts/
    └── spiffs_assets/
        ├── build.py        # Single build script
        ├── build_all.py    # Batch build script
        └── build_boot.py   # Boot animation script
```

## Path Configuration

All paths are configured in the scripts, no environment variables needed.

- **Fonts**: External dependency path
- **Resources**: Local project paths using relative paths
- **Configurations**: Local project paths using relative paths

## Output Files

Generated files follow these naming patterns:

- **Resolution assets**: `{resolution}_{font}_{emoji}.bin`
- **Boot animations**: Custom filename specified with `--output`
- **Single file mode**: Custom filename specified with `--output`
