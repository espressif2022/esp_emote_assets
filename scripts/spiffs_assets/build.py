#!/usr/bin/env python3
"""
Build the spiffs assets partition

Usage:
    ./build.py --text_font <text_font_file> \
        --resolution <resolution_dir> \
        --res_path <res_path_dir>

Example:
    ./build.py --text_font ../../components/xiaozhi-fonts/build/font_puhui_common_20_4.bin \
        --resolution ../../products/boards/echoear_core_board_v1_2_ctm \
        --res_path ../../esp_emote_gfx/emoji_large
"""

import os
import sys
import shutil
import argparse
import subprocess
import json
from pathlib import Path


def ensure_dir(directory):
    """Ensure directory exists, create if not"""
    os.makedirs(directory, exist_ok=True)


def copy_file(src, dst):
    """Copy file"""
    if os.path.exists(src):
        # Ensure destination directory exists
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            ensure_dir(dst_dir)
        shutil.copy2(src, dst)
        # print(f"Copied: {src} -> {dst}")
    else:
        print(f"Warning: Source file does not exist: {src}")


def copy_directory(src, dst):
    """Copy directory"""
    if os.path.exists(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        # print(f"Copied directory: {src} -> {dst}")
    else:
        print(f"Warning: Source directory does not exist: {src}")


def process_text_font(text_font_file, assets_dir):
    """Process text_font parameter"""
    if not text_font_file:
        return None
    
    # Copy input file to build/assets directory
    font_filename = os.path.basename(text_font_file)
    font_dst = os.path.join(assets_dir, font_filename)
    copy_file(text_font_file, font_dst)
    print(f"Handle text font: {font_filename}")
    
    return font_filename


def process_wakenet_model(wakenet_model_file, assets_dir):
    """Process wakenet_model parameter"""
    if not wakenet_model_file:
        return None

    # Copy input file to build/assets directory
    wakenet_filename = os.path.basename(wakenet_model_file)
    wakenet_dst = os.path.join(assets_dir, wakenet_filename)
    copy_file(wakenet_model_file, wakenet_dst)
    print(f"Handle wakenet model: {wakenet_filename}")

    return wakenet_filename


def load_emoji_config(emoji_collection_dir):
    """Load emoji config from config.json file"""
    config_path = os.path.join(emoji_collection_dir, "emote.json")
    if not os.path.exists(config_path):
        print(f"Warning: Config file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Convert list format to dict for easy lookup
        config_dict = {}
        for item in config_data:
            if "emote" in item:
                config_dict[item["emote"]] = item
        
        return config_dict
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}

def process_board_emoji_collection(emoji_collection_dir, resolution_dir, assets_dir):
    """Process emoji_collection parameter for resolution configuration"""
    if not emoji_collection_dir:
        return []
    
    emoji_config = load_emoji_config(resolution_dir)
    print(f"Loaded emoji config: {len(emoji_config)} entries")
    
    emoji_list = []
    
    for emote_name, config in emoji_config.items():

        if "src" not in config:
            print(f"Error: No src field found for emote '{emote_name}' in config")
            continue
        
        eaf_file_path = os.path.join(emoji_collection_dir, config["src"])
        file_exists = os.path.exists(eaf_file_path)
        
        if not file_exists:
            print(f"Warning: EAF file not found for emote '{emote_name}': {eaf_file_path}")
        else:
            # Copy eaf file to assets directory
            copy_file(eaf_file_path, os.path.join(assets_dir, config["src"]))
        
        # Create emoji entry with src as file (merge file and src)
        emoji_entry = {
            "name": emote_name,
            "file": config["src"]  # Use src as the actual file
        }
        
        eaf_properties = {}
        
        if not file_exists:
            eaf_properties["lack"] = True
        
        if "loop" in config:
            eaf_properties["loop"] = config["loop"]
        
        if "fps" in config:
            eaf_properties["fps"] = config["fps"]
        
        if eaf_properties:
            emoji_entry["eaf"] = eaf_properties
        
        status = "MISSING" if not file_exists else "OK"
        eaf_info = emoji_entry.get('eaf', {})
        # print(f"emote '{emote_name}': file='{emoji_entry['file']}', status={status}, lack={eaf_info.get('lack', False)}, loop={eaf_info.get('loop', 'none')}, fps={eaf_info.get('fps', 'none')}")
        
        emoji_list.append(emoji_entry)
    
    return emoji_list

def process_board_icon_collection(icon_collection_dir, assets_dir):
    """Process emoji_collection parameter"""
    if not icon_collection_dir:
        return []
    
    icon_list = []
    
    for root, dirs, files in os.walk(icon_collection_dir):
        for file in files:
            if file.lower().endswith(('.bin')) or file.lower() == 'listen.eaf':
                src_file = os.path.join(root, file)
                dst_file = os.path.join(assets_dir, file)
                copy_file(src_file, dst_file)
                
                filename_without_ext = os.path.splitext(file)[0]

                icon_list.append({
                    "name": filename_without_ext,
                    "file": file
                })
    
    return icon_list
def process_board_layout(layout_json_file, assets_dir):
    """Process layout_json parameter"""
    if not layout_json_file:
        print(f"Warning: Layout json file not provided")
        return []
    
    #print(f"Processing layout_json: {layout_json_file}")
    #print(f"assets_dir: {assets_dir}")
    
    if os.path.isdir(layout_json_file):
        layout_json_path = os.path.join(layout_json_file, "layout.json")
        if not os.path.exists(layout_json_path):
            print(f"Warning: layout.json not found in directory: {layout_json_file}")
            return []
        layout_json_file = layout_json_path
    elif not os.path.isfile(layout_json_file):
        print(f"Warning: Layout json file not found: {layout_json_file}")
        return []
        
    try:
        with open(layout_json_file, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)  # This validates JSON format
        
        # Return the original JSON data without processing
        count = len(layout_data) if isinstance(layout_data, list) else 'N/A'
        print(f"Loaded JSON: {count} elements")
        return layout_data
        
    except Exception as e:
        print(f"Error reading/processing layout.json: {e}")
        return []

def process_board_collection(resolution_dir, res_path, assets_dir):
    """Process resolution collection - merge icon, emoji, and layout processing"""
    
    # Process all collections
    if os.path.exists(res_path) and os.path.exists(resolution_dir):
        emoji_collection = process_board_emoji_collection(res_path, resolution_dir, assets_dir)
        icon_collection = process_board_icon_collection(res_path, assets_dir)
        layout_json = process_board_layout(resolution_dir, assets_dir)
    else:
        print(f"Warning: EAF directory not found: {res_path} or {resolution_dir}")
        emoji_collection = []
        icon_collection = []
        layout_json = []
    
    return emoji_collection, icon_collection, layout_json

def generate_index_json(assets_dir, text_font, emoji_collection, icon_collection, layout_json, wakenet_model=None):
    """Generate index.json file"""
    index_data = {
        "version": 1
    }

    if wakenet_model:
        model_name = os.path.splitext(wakenet_model)[0]
        index_data[model_name] = wakenet_model
    
    if text_font:
        index_data["text_font"] = text_font
    
    if emoji_collection:
        index_data["emoji_collection"] = emoji_collection

    if icon_collection:
        index_data["icon_collection"] = icon_collection
    
    if layout_json:
        index_data["layout"] = layout_json
        # print(f"layout_json: {layout_json}")
    
    # Write index.json
    index_path = os.path.join(assets_dir, "index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=4, ensure_ascii=False)
    
    #print(f"Generated: {index_path}")
    # print(f"Generated index.json: {index_data}")


def generate_config_json(build_dir, assets_dir, name_length="32"):
    """Generate config.json file"""
    
    config_data = {
        "assets_path": os.path.join(build_dir, "assets"),
        "image_file": os.path.join(build_dir, "output/assets.bin"),
        "support_format": ".png, .gif, .jpg, .bin, .json, .eaf",
        "name_length": name_length,
    }
    
    # Write config.json
    config_path = os.path.join(build_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    #print(f"Generated: {config_path}")
    return config_path


def main():
    parser = argparse.ArgumentParser(description='Build the spiffs assets partition')
    parser.add_argument('--text_font', help='Path to text font file')
    parser.add_argument('--res_path', help='Path to res directory')
    parser.add_argument('--resolution', help='Path to resolution directory')
    parser.add_argument('--name_length', default="32", help='Name length for assets (default: 32)')
    parser.add_argument('--wakenet_model', help='Path to wakenet model file')
    
    args = parser.parse_args()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set directory paths
    build_dir = os.path.join(script_dir, "build/face")
    assets_dir = os.path.join(build_dir, "assets")
    if os.path.exists(assets_dir):
        # Use ignore_errors to handle race conditions where files may be deleted
        # during the removal process
        shutil.rmtree(assets_dir, ignore_errors=True)
    
    # Ensure directories exist
    ensure_dir(build_dir)
    ensure_dir(assets_dir)
    
    # Process each parameter
    text_font = process_text_font(args.text_font, assets_dir)
    wakenet_model = process_wakenet_model(args.wakenet_model, assets_dir)

    if(args.resolution):
        emoji_collection, icon_collection, layout_json = process_board_collection(args.resolution, args.res_path, assets_dir)
    else:
        emoji_collection = []
        icon_collection = []
        layout_json = []
    
    # Generate index.json
    generate_index_json(assets_dir, text_font, emoji_collection, icon_collection, layout_json, wakenet_model)
    
    # Generate config.json
    config_path = generate_config_json(build_dir, assets_dir, args.name_length)
    
    # Use spiffs_assets_gen.py to package final build/assets.bin
    try:
        subprocess.run([
            sys.executable, "spiffs_assets_gen.py", 
            "--config", config_path
        ], check=True, cwd=script_dir)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to package assets.bin: {e}")
        sys.exit(1)
    
    # Copy build/output/assets.bin to build/assets.bin
    # shutil.copy(os.path.join(build_dir, "output", "assets.bin"), os.path.join(build_dir, "assets.bin"))

if __name__ == "__main__":
    main()