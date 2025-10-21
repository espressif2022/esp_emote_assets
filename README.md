# ESP Emote Assets

ESP Emote Assets 是一个用于管理 ESP-IDF 项目中表情和图形资源的组件。

## 功能特性

- 支持多种分辨率配置 (360_360, 320_240 等)
- 支持多种字体配置
- 支持多种表情集合 (emoji_large, emoji_small)
- 自动生成 SPIFFS 资源分区
- 提供构建脚本用于批量生成资源

## 目录结构

```
esp_emote_assets/
├── 360_360/                 # 360x360 分辨率配置
│   ├── config.json         # 分辨率配置文件
│   └── layout.json         # 布局配置文件
├── 320_240/                 # 320x240 分辨率配置
│   ├── config.json
│   └── layout.json
├── emoji_large/             # 大尺寸表情资源
├── emoji_small/             # 小尺寸表情资源
├── scripts/                 # 构建脚本
│   └── spiffs_assets/
│       ├── build.py        # 单个资源构建脚本
│       └── build_all.py   # 批量构建脚本
└── idf_component.yml       # ESP-IDF 组件配置
```

## 使用方法

### 1. 作为 ESP-IDF 组件使用

在你的项目 `idf_component.yml` 中添加依赖：

```yaml
dependencies:
  espressif/esp_emote_assets:
    version: "1.0.0"
```

### 2. 构建资源

```bash
# 构建所有配置的资源
cd scripts/spiffs_assets
./build_all.py

# 构建特定分辨率
./build.py --text_font <font_file> --resolution <resolution_dir> --res_path <emoji_dir>
```

## 配置说明

每个分辨率目录下的 `config.json` 文件格式：

```json
{
    "text_font": "font_puhui_common_20_4",
    "emoji_collection": "emoji_large"
}
```

## 环境变量

- `FONTS_PATH`: 字体文件路径
- `EMOTE_PATH`: 表情资源路径  
- `BOARD_PATH`: 分辨率配置路径
