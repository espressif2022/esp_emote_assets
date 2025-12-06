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

# Base paths - can be overridden by external path
BOOT_BASE_PATH = PROJECT_ROOT
EMOTE_GFX_BASE_PATH = PROJECT_ROOT
EXTERNAL_BASE_PATH = None  # External path prefix (default: None, use local)

def ensure_dir(directory):
    """Ensure directory exists, create if not"""
    os.makedirs(directory, exist_ok=True)

def find_boot_file(boot_name, external_base=None):
    """
    Find boot animation file in boot directory.
    Tries external path first, then falls back to local path.
    """
    # Try external path first if provided
    if external_base:
        external_boot_dir = os.path.join(external_base, 'boot')
        extensions = ['.eaf', '.bin', '']
        for ext in extensions:
            boot_path = os.path.join(external_boot_dir, f"{boot_name}{ext}")
            if os.path.exists(boot_path):
                return boot_path
    
    # Fallback to local path
    boot_dir = os.path.join(BOOT_BASE_PATH, 'boot')
    
    # Try different extensions
    extensions = ['.eaf', '.bin', '']
    
    for ext in extensions:
        boot_path = os.path.join(boot_dir, f"{boot_name}{ext}")
        if os.path.exists(boot_path):
            return boot_path
    
    # If not found, return the path with .eaf extension for error reporting
    return os.path.join(boot_dir, f"{boot_name}.eaf")

def build_boot_assets(boot_file, output_file, name_length="32", external_base=None):
    """Build boot assets independently - just copy and package"""
    
    # Find the actual boot file (try external first, then local)
    boot_path = find_boot_file(boot_file, external_base=external_base)
    
    if not os.path.exists(boot_path):
        print(f"{Colors.RED}✗ Boot file not found: {boot_path}{Colors.ENDC}")
        return False

    # Get script directory for build path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(script_dir, "build/boot")
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
        "assets_path": os.path.join(build_dir, "assets"),
        "image_file": os.path.join(build_dir, "output/assets.bin"),
        "support_format": ".eaf",
        "name_length": name_length,
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
    parser.add_argument('--name_length', default="32", help='Name length for assets (default: 32)')
    parser.add_argument('--external_path', help='External base path prefix for finding boot files (default: use local paths only). Searches external path first, then falls back to local.')
    args = parser.parse_args()
    
    # Get external base path if provided
    external_base = None
    if args.external_path:
        external_base = os.path.abspath(args.external_path)
        if not os.path.isdir(external_base):
            print(f"{Colors.RED}Warning: External path does not exist: {external_base}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Will use local paths only.{Colors.ENDC}")
            external_base = None
    
    # Set default output path if not provided
    if not args.output:
        # Get script directory for default output path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(script_dir, "build")
        final_dir = os.path.join(build_dir, "final")
        
        # Create filename from source file
        src_name = os.path.splitext(args.src)[0]  # Remove extension
        args.output = os.path.join(final_dir, f"{src_name}.bin")
    
    # Print parsed arguments
    print(f"{Colors.GREEN}Build Configuration:{Colors.ENDC}")
    print(f"  Source: {args.src}")
    print(f"  Output: {args.output}")
    print(f"  Name Length: {args.name_length}")
    print(f"  External Path: {external_base if external_base else 'None (using local paths only)'}")
    
    # Build boot assets
    if build_boot_assets(args.src, args.output, args.name_length, external_base=external_base):
        print(f"{Colors.GREEN}Completed!{Colors.ENDC}")
    else:
        print(f"{Colors.RED}Build failed!{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
