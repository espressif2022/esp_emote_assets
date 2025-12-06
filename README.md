# ESP Emote Assets

ESP Emote Assets is a component for managing emoji and graphics resources in ESP-IDF projects.

## Features

- Support for multiple resolution configurations (1024_600, 360_360, 320_240)
- Support for multiple font configurations (14pt, 16pt, 20pt, 30pt)
- Support for multiple emoji collections (emoji_large, emoji_small)
- Automatic SPIFFS assets partition generation
- Build scripts for batch resource generation
- Independent boot animation support
- CMake integration for ESP-IDF projects

## Directory Structure

```
esp_emote_assets/
├── 1024_600/               # 1024x600 resolution config
│   ├── config.json         # Resolution configuration
│   └── layout.json         # Layout configuration
├── 320_240/                # 320x240 resolution config
│   ├── config.json
│   └── layout.json
├── 360_360/                # 360x360 resolution config
│   ├── config.json
│   └── layout.json
├── emoji_large/            # Large emoji resources
├── emoji_small/            # Small emoji resources
├── font/                   # Font files
│   ├── font_puhui_common_14_1.bin # From 78/xiaozhi-fonts
│   ├── font_puhui_common_16_4.bin
│   ├── font_puhui_common_20_4.bin
│   └── font_puhui_common_30_4.bin
├── boot/                   # Boot animation files
│   └── anim_360_360.eaf
├── scripts/                # Build scripts
│   └── spiffs_assets/
│       ├── build.py        # Single resource build script
│       ├── build_all.py    # Batch build script
│       ├── build_boot.py   # Boot animation script
│       ├── spiffs_assets_gen.py  # SPIFFS assets generator
│       └── README.md       # Build scripts documentation
├── CMakeLists.txt          # CMake configuration
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
./build_boot.py --src anim_360_360.eaf

# Build with external path (searches external path first, then falls back to local)
./build_all.py --resolution 360_360 --external_path /path/to/external/assets
./build_boot.py --src anim_360_360.eaf --external_path /path/to/external/assets

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

Boot animation files should be placed in the `boot/` directory. Current files:
- `anim_360_360.eaf` - Boot animation for 360x360 resolution

The build script supports automatic file discovery with extensions: `.eaf`.

## Path Configuration

### Default Local Paths

By default, all resources are searched in the component's local directories:
- Resolution configs: `{component_root}/{resolution_name}/` (e.g., `360_360/`, `320_240/`)
- Emoji collections: `{component_root}/{emoji_collection}/` (e.g., `emoji_large/`, `emoji_small/`)
- Font files: `{component_root}/font/`
- Boot animations: `{component_root}/boot/`

### External Path Support

You can specify an external base path prefix using the `--external_path` option. The build scripts will:
1. **First** search in the external path for resources
2. **Fallback** to local paths if not found in external path

This allows you to:
- Use custom assets from external directories
- Override specific resources while keeping others local
- Share assets across multiple projects

**Example:**
```bash
# External path structure:
/path/to/external/
├── 360_360/
│   ├── config.json
│   └── layout.json
├── emoji_large/
│   └── ...
├── font/
│   └── ...
└── boot/
    └── anim_360_360.eaf

# Build using external path
./build_all.py --resolution 360_360 --external_path /path/to/external
```

**CMake Usage:**
```cmake
# Pass external path as 5th argument
build_speaker_assets_bin("assets" "360_360" "${ASSETS_FILE}" "${NAME_LENGTH}" "/path/to/external")
build_boot_assets_bin("boot" "anim_360_360.eaf" "${BOOT_FILE}" "${NAME_LENGTH}" "/path/to/external")
```

## Output Files

Generated files follow these naming patterns:

- **Resolution assets**: `{resolution}_{font}_{emoji}.bin`
- **Boot animations**: `{src_filename}.bin` (default) or custom filename
- **Single file mode**: Custom filename specified with `--output`
