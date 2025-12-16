"""
Simplified assets packer for ESP Emote:
- Filter files by suffix
- Merge them into a single binary (with a small mmap table header)

All image format conversion and C header generation logic has been removed.
"""

import os
import argparse
import json
import shutil
import math
import sys
from dataclasses import dataclass
from typing import List
from datetime import datetime

GREEN = "\033[1;32m"
RED = "\033[1;31m"
RESET = "\033[0m"


@dataclass
class AssetCopyConfig:
    assets_path: str
    target_path: str
    support_format: List[str]


@dataclass
class PackModelsConfig:
    target_path: str
    image_file: str
    assets_path: str
    name_length: int


def compute_checksum(data: bytes) -> int:
    return sum(data) & 0xFFFF


def sort_key(filename: str):
    basename, extension = os.path.splitext(filename)
    return extension, basename


def pack_assets(config: PackModelsConfig) -> None:
    """
    Merge all files in target_path into a single mmap binary.
    """

    target_path = config.target_path
    out_file = config.image_file
    assets_path = config.assets_path
    max_name_len = config.name_length

    merged_data = bytearray()
    file_info_list = []
    skip_files = ["config.json", "lvgl_image_converter"]

    file_list = sorted(os.listdir(target_path), key=sort_key)
    for filename in file_list:
        if filename in skip_files:
            continue

        file_path = os.path.join(target_path, filename)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Image processing removed, set width/height to 0
        width, height = 0, 0

        file_info_list.append((file_name, len(merged_data), file_size, width, height))

        # Add 0x5A5A prefix to merged_data
        merged_data.extend(b"\x5A" * 2)

        with open(file_path, "rb") as bin_file:
            bin_data = bin_file.read()

        merged_data.extend(bin_data)

    total_files = len(file_info_list)

    mmap_table = bytearray()
    for file_name, offset, file_size, width, height in file_info_list:
        if len(file_name) > int(max_name_len):
            print(
                f"\033[1;33mWarn:\033[0m "
                f'"{file_name}" exceeds {max_name_len} bytes and will be truncated.'
            )
        fixed_name = file_name.ljust(int(max_name_len), "\0")[: int(max_name_len)]
        mmap_table.extend(fixed_name.encode("utf-8"))
        mmap_table.extend(file_size.to_bytes(4, byteorder="little"))
        mmap_table.extend(offset.to_bytes(4, byteorder="little"))
        mmap_table.extend(width.to_bytes(2, byteorder="little"))
        mmap_table.extend(height.to_bytes(2, byteorder="little"))

    combined_data = mmap_table + merged_data
    combined_checksum = compute_checksum(combined_data)
    combined_data_length = len(combined_data).to_bytes(4, byteorder="little")
    header_data = total_files.to_bytes(4, byteorder="little") + combined_checksum.to_bytes(
        4, byteorder="little"
    )
    final_data = header_data + combined_data_length + combined_data

    with open(out_file, "wb") as output_bin:
        output_bin.write(final_data)

    # print(f"All bin files have been merged into {os.path.basename(out_file)}")


def copy_assets(config: AssetCopyConfig) -> None:
    """
    Copy assets from assets_path to target_path if their suffix matches
    any entry in support_format. No conversion is performed.
    """
    format_tuple = tuple(config.support_format)
    assets_path = config.assets_path
    target_path = config.target_path

    for filename in os.listdir(assets_path):
        if any(filename.endswith(suffix) for suffix in format_tuple):
            source_file = os.path.join(assets_path, filename)
            target_file = os.path.join(target_path, filename)
            shutil.copyfile(source_file, target_file)
        else:
            print(f"No match found for file: {filename}, format_tuple: {format_tuple}")


def process_assets_build(config_data: dict) -> None:
    """
    Build assets:
    - Filter files in assets_path by suffix (support_format)
    - Copy them to target_path
    - Merge them into a single mmap binary + header
    """
    assets_path = config_data["assets_path"]
    image_file = config_data["image_file"]
    target_path = os.path.dirname(image_file)
    name_length = config_data["name_length"]
    support_format = [fmt.strip() for fmt in config_data["support_format"].split(",")]

    copy_config = AssetCopyConfig(
        assets_path=assets_path,
        target_path=target_path,
        support_format=support_format,
    )

    pack_config = PackModelsConfig(
        target_path=target_path,
        image_file=image_file,
        assets_path=assets_path,
        name_length=name_length,
    )

    print("--support_format:", support_format)

    if not os.path.exists(target_path):
        os.makedirs(target_path, exist_ok=True)
    for filename in os.listdir(target_path):
        file_path = os.path.join(target_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    copy_assets(copy_config)
    pack_assets(pack_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move and Pack assets (simplified).")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config_data = json.load(f)

    # Only build assets image; no longer support merging into app binary.
    process_assets_build(config_data)

