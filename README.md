# ESP Emote Assets

ESP Emote Assets is a component for managing emoji and graphics resources in ESP-IDF projects.

## Features

- Support for multiple resolution configurations (1024_600, 360_360, 320_240)
- Support for multiple font configurations (14pt, 16pt, 20pt, 30pt)
- Support for multiple emoji collections (emoji_large, emoji_small)
- Support for wake word models (wakenet_model)
- Automatic SPIFFS assets partition generation
- CMake integration for ESP-IDF projects

## Directory Structure

```
esp_emote_assets/
├── 1024_600/               # 1024x600 resolution config
│   ├── config.json         # Resolution configuration
│   ├── emote.json          # Emote configuration
│   └── layout.json         # Layout configuration
├── 320_240/                # 320x240 resolution config
│   ├── config.json
│   ├── emote.json
│   └── layout.json
├── 360_360/                # 360x360 resolution config
│   ├── config.json
│   ├── emote.json
│   └── layout.json
├── emoji_large/            # Large emoji resources
├── emoji_small/            # Small emoji resources
├── font/                   # Font files
│   ├── font_puhui_common_14_1.bin # From 78/xiaozhi-fonts
│   ├── font_puhui_common_16_4.bin
│   ├── font_puhui_common_20_4.bin
│   └── font_puhui_common_30_4.bin
├── wakenet/                # Wake word model files
│   └── srmodels.bin         # Speech recognition model file (specified in config.json)
├── scripts/                # Build scripts
│   └── spiffs_assets/
│       ├── build.py        # Single resource build script
│       ├── build_all.py    # Batch build script
│       └── spiffs_assets_gen.py  # SPIFFS assets generator
├── CMakeLists.txt          # CMake configuration
└── idf_component.yml       # ESP-IDF component configuration
```

## Usage

### 1. As ESP-IDF Component

Add dependency to your project's `idf_component.yml`:

```yaml
dependencies:
  espressif/esp_emote_assets:
    version: "0.1.0"
```

### 2. Build Resources

#### Quick Start (Recommended)

Use `build_all.py` which automatically reads configuration from `config.json`:

```bash
cd scripts/spiffs_assets

# Build all default resolutions (360_360, 320_240, 1024_600)
./build_all.py

# Build specific resolution(s)
./build_all.py --resolution 360_360

# Build with custom output file
./build_all.py --resolution 360_360 --output /path/to/output.bin

# Build with external assets path
./build_all.py --resolution 360_360 --external_path /path/to/external

# Build with custom name length
./build_all.py --resolution 360_360 --name_length 32
```

**Parameters:**
- `--resolution`: Resolution(s) to build (default: all)
- `--output`: Custom output file path (default: `build/final/{resolution}.bin`)
- `--name_length`: File name length limit (default: 32)
- `--external_path`: External assets directory (searches external first, then local)

#### CMake Integration

Use the CMake function in your project's `CMakeLists.txt`:

```cmake
set(RESOLUTION "360_360")
set(ASSETS_FILE "${CMAKE_BINARY_DIR}/assets.bin")

# Build assets bin file
build_speaker_assets_bin("anim_icon" ${RESOLUTION} ${ASSETS_FILE} ${CONFIG_MMAP_FILE_NAME_LENGTH})

# Flash to partition
esptool_py_flash_to_partition(flash "anim_icon" "${ASSETS_FILE}")
```

## Configuration

### Resolution Configuration

Each resolution directory contains a `config.json` file:

```json
{
    "text_font": "font_puhui_common_20_4",
    "emoji_collection": "emoji_large",
    "wakenet_model": "srmodels.bin"
}
```

**Fields:**
- `text_font`: Font file name (without `.bin`), located in `font/` directory
- `emoji_collection`: Emoji directory name (e.g., `emoji_large`), located at component root
- `wakenet_model`: Model file name (e.g., `srmodels.bin`), located in `wakenet/` directory

## Resource Paths

Resources are searched in the following order:
1. External path (if `--external_path` is specified)
2. Component local directories

**Local paths:**
- Configs: `{component_root}/{resolution}/` (e.g., `360_360/config.json`)
- Emojis: `{component_root}/{emoji_collection}/` (e.g., `emoji_large/`)
- Fonts: `{component_root}/font/` (e.g., `font/font_puhui_common_20_4.bin`)
- Models: `{component_root}/wakenet/` (e.g., `wakenet/srmodels.bin`)

**Output files:**
- Default: `build/final/{resolution}.bin` (e.g., `360_360.bin`)
- Custom: Path specified by `--output`
