#!/usr/bin/env python3
"""
Build multiple spiffs assets partitions with different parameter combinations

This script calls build.py with different combinations of:
- text_fonts  
- resolutions

And generates assets.bin files with names like:
font_puhui_common_20_4-360_360.bin

Usage:
    # Build all default resolutions
    ./build_all.py
    
    # Build specific resolutions
    ./build_all.py --resolution 360_360 320_240
    
    # Specify single output file
    ./build_all.py --output /path/to/output.bin
    
    # Combine both options
    ./build_all.py --resolution 360_360 --output /path/to/custom.bin
    
    # Override fonts path with environment variable
    FONTS_PATH=/custom/fonts/path ./build_all.py
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

# Base paths - all local paths
FONTS_BASE_PATH = PROJECT_ROOT
EMOTE_GFX_BASE_PATH = PROJECT_ROOT
BOARDS_BASE_PATH = PROJECT_ROOT

def ensure_dir(directory):
    """Ensure directory exists, create if not"""
    os.makedirs(directory, exist_ok=True)


def get_file_path(base_dir, filename):
    """Get full path for a file, handling 'none' case"""
    if filename == "none":
        return None
    return os.path.join(base_dir, f"{filename}.bin" if not filename.startswith("emojis_") else filename)


def build_assets(text_font, resolution_name, emoji_collection, build_dir, final_dir, output_filename=None):
    """Build assets.bin using build.py with given parameters"""
    
    # Prepare arguments for build.py
    cmd = [sys.executable, "build.py"]
    
    if text_font != "none":
        text_font_path = os.path.join(FONTS_BASE_PATH, 'font/', f"{text_font}.bin")
        cmd.extend(["--text_font", text_font_path])

    print(f"resolution: {resolution_name}")
    
    res_path = os.path.join(EMOTE_GFX_BASE_PATH, emoji_collection)
    print(f"res_path: {res_path}")
    cmd.extend(["--res_path", res_path])

    resolution_path = os.path.join(BOARDS_BASE_PATH, resolution_name)
    cmd.extend(["--resolution", resolution_path])
    
    # Prepare display info
    display_info = f"{resolution_name}_{text_font}_{emoji_collection}"
    print(f"\n{Colors.GREEN}Building: {display_info}{Colors.ENDC}")
    # print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run build.py
        result = subprocess.run(cmd, check=True, cwd=os.path.dirname(__file__))
        
        # Generate output filename
        if output_filename:
            output_name = output_filename
        else:
            output_name = f"{resolution_name}_{text_font}_{emoji_collection}.bin"
        
        # Copy generated assets.bin to final directory with new name
        src_path = os.path.join(build_dir, "output", "assets.bin")
        dst_path = os.path.join(final_dir, output_name)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"{Colors.GREEN}✓ Generated: {output_name}{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.RED}✗ Error: generated assets.bin not found{Colors.ENDC}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}✗ Build failed: {e}{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ Unknown error: {e}{Colors.ENDC}")
        return False


def load_resolution_config(resolution_name):
    """Load configuration from resolution directory"""
    config_path = os.path.join(BOARDS_BASE_PATH, resolution_name, "config.json")
    
    if not os.path.exists(config_path):
        print(f"Warning: Config file not found: {config_path}")
        return None, None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        text_font = config.get('text_font', 'none')
        emoji_collection = config.get('emoji_collection', 'emoji_large')
        
        return text_font, emoji_collection
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return None, None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Build multiple SPIFFS assets partitions')
    parser.add_argument('--resolution', nargs='+', help='List of resolution directories to build (e.g., 360_360 320_240)')
    parser.add_argument('--output', help='Output file path for generated .bin file (default: build/final/{resolution}_{font}_{emoji}.bin)')
    args = parser.parse_args()
    
    # Use command line resolutions or default
    resolutions = args.resolution if args.resolution else [
        "360_360",
        "320_240",
        "1024_600",
    ]
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set directory paths
    build_dir = os.path.join(script_dir, "build/face")
    
    if args.output:
        # Single output file specified
        final_dir = os.path.dirname(args.output)
        output_filename = os.path.basename(args.output)
        ensure_dir(final_dir)
    else:
        # Default: multiple files in build/final directory
        final_dir = os.path.join(build_dir, "final")
        output_filename = None
        ensure_dir(build_dir)
        ensure_dir(final_dir)
    
    print("Start building multiple SPIFFS assets partitions...")
    print(f"Output directory: {final_dir}")
    
    # Track successful builds
    successful_builds = 0
    
    # Calculate total combinations
    total_combinations = 0
    
    # Build all combinations with resolutions
    for resolution_name in resolutions:
        # Load configuration for this resolution
        text_font, emoji_collection = load_resolution_config(resolution_name)
        
        if text_font is None or emoji_collection is None:
            print(f"Skipping resolution {resolution_name} due to config error")
            continue
        
        total_combinations += 1
        
        if build_assets(text_font, resolution_name, emoji_collection, build_dir, final_dir, output_filename):
            successful_builds += 1
    
    print(f"{Colors.GREEN}Completed! Builds: {successful_builds}/{total_combinations}{Colors.ENDC}")


if __name__ == "__main__":
    main()


