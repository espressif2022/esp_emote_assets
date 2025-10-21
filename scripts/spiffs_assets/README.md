# SPIFFS Assets Build Scripts

这些脚本用于构建 SPIFFS assets 分区。

## 使用方法

### 环境变量配置

脚本使用以下环境变量来配置基础路径：

- `XIAOZHI_FONTS_PATH`: 字体文件的基础路径
- `ESP_EMOTE_GFX_PATH`: 表情图形资源的基础路径
- `ESP_BROOKESIA_BOARDS_PATH`: 开发板配置的基础路径

### 选项 1: 使用默认路径

直接运行脚本，使用默认路径：

```bash
./build_all.py
```

### 选项 2: 临时设置环境变量

在命令行中临时设置环境变量：

```bash
XIAOZHI_FONTS_PATH=/custom/fonts/path \
ESP_EMOTE_GFX_PATH=/custom/gfx/path \
ESP_BROOKESIA_BOARDS_PATH=/custom/boards/path \
./build_all.py
```

### 选项 3: 使用 .env 文件

1. 复制示例配置文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，修改路径

3. 在运行前加载环境变量：
```bash
export $(cat .env | xargs)
./build_all.py
```

或者使用 `source`:
```bash
source .env
./build_all.py
```

## 脚本说明

### build_all.py

批量构建多个 SPIFFS assets 分区，使用不同的参数组合（字体和开发板）。

#### 使用方法

```bash
./build_all.py
```

### build.py

单独构建一个 SPIFFS assets 分区。

#### 使用方法

```bash
./build.py --text_font <text_font_file> \
           --resolution <resolution_dir> \
           --res_path <res_path_dir>
```

## 默认路径

如果不设置环境变量，脚本将使用以下默认路径：

- 字体路径: `/home/xuxin/esp_work/esp-brookesia/products/speaker/managed_components/78__xiaozhi-fonts/cbin`
- 资源路径: `/home/xuxin/esp_work/esp_emote_gfx`
- 开发板路径: `/home/xuxin/esp_work/esp-brookesia/products/boards`
