# SPIFFS Assets Build Scripts

These scripts are used to build SPIFFS assets partitions for ESP-IDF projects.

## Usage

### build_all.py - Batch Build Script

Build multiple SPIFFS assets partitions with different parameter combinations.

```bash
# Build all default resolutions
python build_all.py

# Build specific resolutions
python build_all.py --resolution 360_360 320_240

# Specify single output file
python build_all.py --output /path/to/output.bin

# Combine both options
python build_all.py --resolution 360_360 --output /path/to/custom.bin
```

### build.py - Single Build Script

Build a single SPIFFS assets partition.

```bash
python build.py --text_font <text_font_file> \
                --resolution <resolution_dir> \
                --res_path <res_path_dir> \
                --name_length <name_length>
```

**Parameters:**
- `--text_font`: Path to text font file (required)
- `--resolution`: Path to resolution directory (required)
- `--res_path`: Path to res directory (required)
- `--name_length`: Name length for assets (optional, default: "32")

### build_boot.py - Boot Animation Script

Build boot animation assets independently.

```bash
# Build boot animation with default output path
python build_boot.py --src anim_360_360

# Build boot animation with custom output path
python build_boot.py --src anim_360_360 --output ./final/boot_360_360.bin

# Build boot animation with custom name length
python build_boot.py --src anim_360_360 --name_length 64
```

**Parameters:**
- `--src`: Boot animation file name (e.g., boot_animation_360_360.eaf) (required)
- `--output`: Output file path for generated .bin file (optional, default: build/final/{src_filename}.bin)
- `--name_length`: Name length for assets (optional, default: "32")

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
│   ├── emote.json          # Emote configuration
│   └── layout.json         # Layout configuration
├── 320_240/                 # 320x240 resolution config
│   ├── config.json
│   ├── emote.json
│   └── layout.json
├── 1024_600/                # 1024x600 resolution config
│   ├── config.json
│   ├── emote.json
│   └── layout.json
├── emoji_large/             # Large emoji resources
├── emoji_small/             # Small emoji resources
├── font/                    # Font files
│   ├── font_puhui_common_14_1.bin
│   ├── font_puhui_common_16_4.bin
│   ├── font_puhui_common_20_4.bin
│   └── font_puhui_common_30_4.bin
├── boot/                    # Boot animation files
│   └── anim_360_360.eaf
└── scripts/
    └── spiffs_assets/
        ├── build.py        # Single build script
        ├── build_all.py    # Batch build script
        ├── build_boot.py   # Boot animation script
        └── spiffs_assets_gen.py  # SPIFFS assets generator
```

## Path Configuration

All paths are configured in the scripts, no environment variables needed.

- **Fonts**: Local `font/` directory in project root
- **Resources**: Local project paths (`emoji_large/`, `emoji_small/`)
- **Configurations**: Local project paths (resolution directories)

## Output Files

Generated files follow these naming patterns:

- **Resolution assets**: `{resolution}_{font}_{emoji}.bin`
- **Boot animations**: Custom filename specified with `--output`
- **Single file mode**: Custom filename specified with `--output`
