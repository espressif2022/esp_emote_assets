#!/usr/bin/env python3
"""
Build boot animation assets

Usage:
    ./build_boot.py --src <boot_animation_file> [--output <output_file>]
    
Examples:
    # Use default output path
    ./build_boot.py --src boot_animation_360_360.eaf
    
    # Specify custom output path
    ./build_boot.py --src boot_animation_360_360.eaf --output ./final/aaaa.bin
"""

import os
import sys
import shutil
import subprocess
import argparse
import json
from pathlib import Path

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Get script directory for relative path calculation
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Base paths
BOOT_BASE_PATH = PROJECT_ROOT
EMOTE_GFX_BASE_PATH = PROJECT_ROOT

def ensure_dir(directory):
    """Ensure directory exists, create if not"""
    os.makedirs(directory, exist_ok=True)

def find_boot_file(boot_name):
    """Find boot animation file in boot directory"""
    boot_dir = os.path.join(BOOT_BASE_PATH, 'boot')
    
    # Try different extensions
    extensions = ['.eaf', '.bin', '']
    
    for ext in extensions:
        boot_path = os.path.join(boot_dir, f"{boot_name}{ext}")
        if os.path.exists(boot_path):
            return boot_path
    
    # If not found, return the path with .eaf extension for error reporting
    return os.path.join(boot_dir, f"{boot_name}.eaf")

def build_boot_assets(boot_file, output_file):
    """Build boot assets independently - just copy and package"""
    
    # Find the actual boot file
    boot_path = find_boot_file(boot_file)
    
    if not os.path.exists(boot_path):
        print(f"{Colors.RED}✗ Boot file not found: {boot_path}{Colors.ENDC}")
        return False

    # Get script directory for build path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(script_dir, "build")
    assets_dir = os.path.join(build_dir, "assets")
    
    # Clean and create directories
    if os.path.exists(assets_dir):
        shutil.rmtree(assets_dir)
    ensure_dir(build_dir)
    ensure_dir(assets_dir)
    
    # Copy boot file to assets directory
    boot_filename = os.path.basename(boot_path)
    boot_dst = os.path.join(assets_dir, boot_filename)
    shutil.copy2(boot_path, boot_dst)
    
    # Generate config.json for SPIFFS packaging
    config_data = {
        "include_path": os.path.join(script_dir, "build/include"),
        "assets_path": os.path.join(script_dir, "build/assets"),
        "image_file": os.path.join(script_dir, "build/output/assets.bin"),
        "lvgl_ver": "9.3.0",
        "assets_size": "0x400000",
        "support_format": ".png, .gif, .jpg, .bin, .json, .eaf",
        "name_length": "32",
        "split_height": "0",
        "support_qoi": False,
        "support_spng": False,
        "support_sjpg": False,
        "support_sqoi": False,
        "support_raw": False,
        "support_raw_dither": False,
        "support_raw_bgr": False
    }
    
    config_path = os.path.join(build_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    
    # Use spiffs_assets_gen.py to package final build/assets.bin
    try:
        subprocess.run([
            sys.executable, "spiffs_assets_gen.py", 
            "--config", config_path
        ], check=True, cwd=script_dir)
        print("Successfully packaged assets.bin")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to package assets.bin: {e}")
        return False
    
    # Copy build/output/assets.bin to final output file
    src_path = os.path.join(build_dir, "output", "assets.bin")
    
    if os.path.exists(src_path):
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        ensure_dir(output_dir)
        
        # Copy to final location
        shutil.copy2(src_path, output_file)
        print(f"{Colors.GREEN}✓ Generated: {output_file}{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}✗ Error: generated assets.bin not found{Colors.ENDC}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Build boot animation assets')
    parser.add_argument('--src', required=True, help='Boot animation file name (e.g., boot_animation_360_360.eaf)')
    parser.add_argument('--output', help='Output file path for generated .bin file (default: build/final/{src_filename}.bin)')
    args = parser.parse_args()
    
    # Set default output path if not provided
    if not args.output:
        # Get script directory for default output path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(script_dir, "build")
        final_dir = os.path.join(build_dir, "final")
        
        # Create filename from source file
        src_name = os.path.splitext(args.src)[0]  # Remove extension
        args.output = os.path.join(final_dir, f"{src_name}.bin")
    
    print(f"{Colors.BLUE}Boot Assets Builder{Colors.ENDC}")
    print(f"Source file: {args.src}")
    print(f"Output: {args.output}")
    print("=" * 60)
    
    # Build boot assets
    if build_boot_assets(args.src, args.output):
        print(f"{Colors.GREEN}Build completed successfully!{Colors.ENDC}")
    else:
        print(f"{Colors.RED}Build failed!{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
