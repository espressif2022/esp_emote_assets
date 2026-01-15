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

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    # Set stdout encoding to UTF-8 on Windows
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            # Fallback for older Python versions
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Safe print function for Unicode characters on Windows
def safe_print(message):
    """Print message with fallback for Unicode encoding issues"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe characters
        message_ascii = message.replace('✓', '[OK]').replace('✗', '[FAIL]')
        print(message_ascii)

# Get script directory for relative path calculation
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Base paths - can be overridden by external path
FONTS_BASE_PATH = PROJECT_ROOT
EMOTE_GFX_BASE_PATH = PROJECT_ROOT
BOARDS_BASE_PATH = PROJECT_ROOT
EXTERNAL_BASE_PATH = None  # External path prefix (default: None, use local)

def ensure_dir(directory):
    """Ensure directory exists, create if not"""
    os.makedirs(directory, exist_ok=True)


def get_file_path(base_dir, filename):
    """Get full path for a file, handling 'none' case"""
    if filename == "none":
        return None
    return os.path.join(base_dir, f"{filename}.bin" if not filename.startswith("emojis_") else filename)


def find_path_in_bases(*path_parts, external_base=None, local_base=None):
    """
    Find path in external base first, then fallback to local base.

    Args:
        *path_parts: Path components to join
        external_base: External base path (optional)
        local_base: Local base path (default: PROJECT_ROOT)

    Returns:
        Full path if found, None otherwise
    """
    if local_base is None:
        local_base = PROJECT_ROOT

    # Try external path first if provided
    if external_base:
        external_path = os.path.join(external_base, *path_parts)
        if os.path.exists(external_path):
            return external_path

    # Fallback to local path
    local_path = os.path.join(local_base, *path_parts)
    if os.path.exists(local_path):
        return local_path

    # Return local path even if it doesn't exist (for creation)
    return local_path


def build_assets(text_font, resolution_name, emoji_collection, wakenet_model=None, build_dir=None, final_dir=None, output_filename=None, name_length=None, external_base=None):
    """Build assets.bin using build.py with given parameters"""

    # Prepare arguments for build.py
    cmd = [sys.executable, "build.py"]

    if text_font != "none":
        # Try external path first, then local
        text_font_path = find_path_in_bases('font', f"{text_font}.bin",
                                           external_base=external_base,
                                           local_base=FONTS_BASE_PATH)
        cmd.extend(["--text_font", text_font_path])

    # Find emoji collection path (try external first, then local)
    res_path = find_path_in_bases(emoji_collection,
                                  external_base=external_base,
                                  local_base=EMOTE_GFX_BASE_PATH)
    cmd.extend(["--res_path", res_path])

    # Find resolution path (try external first, then local)
    resolution_path = find_path_in_bases(resolution_name,
                                        external_base=external_base,
                                        local_base=BOARDS_BASE_PATH)
    cmd.extend(["--resolution", resolution_path])

    # Find wakenet model path if specified
    if wakenet_model != "none":
        # Try to find wakenet model in wakenet directory
        wakenet_path = find_path_in_bases('wakenet', wakenet_model,
                                         external_base=external_base,
                                         local_base=PROJECT_ROOT)
        if wakenet_path and os.path.exists(wakenet_path):
            cmd.extend(["--wakenet_model", wakenet_path])
        else:
            print(f"{Colors.YELLOW}Warning: Wakenet model not found: {wakenet_model} (searched: {wakenet_path}){Colors.ENDC}")

    if name_length:
        cmd.extend(["--name_length", name_length])

    # Prepare display info
    display_info = f"{resolution_name}_{text_font}_{emoji_collection}_{wakenet_model}"
    print(f"{Colors.GREEN}Building: {display_info}{Colors.ENDC}")
    # print(f"Command: {' '.join(cmd)}")

    try:
        # Run build.py
        result = subprocess.run(cmd, check=True, cwd=os.path.dirname(__file__))

        # Generate output filename
        if output_filename:
            output_name = output_filename
        else:
            output_name = f"{resolution_name}.bin"

        # Copy generated assets.bin to final directory with new name
        src_path = os.path.join(build_dir, "output", "assets.bin")
        dst_path = os.path.join(final_dir, output_name)

        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            abs_dst_path = os.path.abspath(dst_path)
            safe_print(f"{Colors.GREEN}✓ Generated: {abs_dst_path}{Colors.ENDC}")
            return True
        else:
            safe_print(f"{Colors.RED}✗ Error: generated assets.bin not found{Colors.ENDC}")
            return False

    except subprocess.CalledProcessError as e:
        safe_print(f"{Colors.RED}✗ Build failed: {e}{Colors.ENDC}")
        return False
    except Exception as e:
        safe_print(f"{Colors.RED}✗ Unknown error: {e}{Colors.ENDC}")
        return False


def load_resolution_config(resolution_name, external_base=None):
    """Load configuration from resolution directory (try external first, then local)"""
    config_path = find_path_in_bases(resolution_name, "config.json",
                                     external_base=external_base,
                                     local_base=BOARDS_BASE_PATH)

    if not os.path.exists(config_path):
        print(f"Warning: Config file not found: {config_path}")
        return None, None, None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        text_font = config.get('text_font', 'none')
        emoji_collection = config.get('emoji_collection', 'emoji_large')
        wakenet_model = config.get('wakenet_model', 'none')

        return text_font, emoji_collection, wakenet_model
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return None, None, None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Build multiple SPIFFS assets partitions')
    parser.add_argument('--resolution', nargs='+', help='List of resolution directories to build (e.g., 360_360 320_240)')
    parser.add_argument('--output', help='Output file path for generated .bin file (default: build/final/{resolution}_{font}_{emoji}.bin)')
    parser.add_argument('--name_length', help='Name length for assets (optional, default: "32")')
    parser.add_argument('--external_path', help='External base path prefix for finding resources (default: use local paths only). Searches external path first, then falls back to local.')
    args = parser.parse_args()

    # Get external base path if provided
    external_base = None
    if args.external_path:
        external_base = os.path.abspath(args.external_path)
        if not os.path.isdir(external_base):
            print(f"{Colors.RED}Warning: External path does not exist: {external_base}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Will use local paths only.{Colors.ENDC}")
            external_base = None

    # Print parsed arguments
    print(f"{Colors.GREEN}Build Configuration:{Colors.ENDC}")
    print(f"  Resolution: {args.resolution if args.resolution else 'default (360_360, 320_240, 1024_600)'}")
    print(f"  Output: {args.output if args.output else 'default (build/final/{{resolution}}.bin)'}")
    print(f"  Name Length: {args.name_length if args.name_length else '32'}")
    print(f"  External Path: {external_base if external_base else 'None (using local paths only)'}")

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
        final_dir = os.path.join(script_dir, "build", "final")
        output_filename = None
        ensure_dir(build_dir)
        ensure_dir(final_dir)

    # Track successful builds
    successful_builds = 0

    # Calculate total combinations
    total_combinations = 0

    # Build all combinations with resolutions
    for resolution_name in resolutions:
        # Load configuration for this resolution (try external first, then local)
        text_font, emoji_collection, wakenet_model = load_resolution_config(resolution_name, external_base=external_base)

        if text_font is None or emoji_collection is None:
            print(f"Skipping resolution {resolution_name} due to config error")
            continue

        total_combinations += 1

        if build_assets(text_font, resolution_name, emoji_collection, wakenet_model, build_dir, final_dir, output_filename, args.name_length, external_base):
            successful_builds += 1

    print(f"{Colors.GREEN}Completed! Builds: {successful_builds}/{total_combinations}{Colors.ENDC}")


if __name__ == "__main__":
    main()


