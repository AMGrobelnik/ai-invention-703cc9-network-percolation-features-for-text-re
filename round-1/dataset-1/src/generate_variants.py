#!/usr/bin/env python3
"""Generate full/mini/preview variants for JSON files."""

from pathlib import Path
import json
import sys

def generate_variants(input_path, output_dir=None):
    """Generate full/mini/preview variants of a JSON file."""
    input_path = Path(input_path)
    
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
    
    # Load data
    data = json.loads(input_path.read_text())
    
    if not isinstance(data, list):
        print(f"Error: {input_path} must contain a top-level array")
        return
    
    base_name = input_path.stem
    
    # Full: identical copy
    full_path = output_dir / f"full_{base_name}.json"
    full_path.write_text(json.dumps(data, indent=2))
    
    # Mini: first 3 items
    mini_path = output_dir / f"mini_{base_name}.json"
    mini_data = data[:3]
    mini_path.write_text(json.dumps(mini_data, indent=2))
    
    # Preview: first 3 items with truncated strings
    preview_path = output_dir / f"preview_{base_name}.json"
    preview_data = []
    for item in data[:3]:
        preview_item = {}
        for key, value in item.items():
            if isinstance(value, str) and len(value) > 200:
                preview_item[key] = value[:200] + "..."
            else:
                preview_item[key] = value
        preview_data.append(preview_item)
    preview_path.write_text(json.dumps(preview_data, indent=2))
    
    print(f"Generated: {full_path.name}, {mini_path.name}, {preview_path.name}")

if __name__ == "__main__":
    for split in ["train", "val", "test"]:
        path = f"temp/datasets/{split}.json"
        generate_variants(path)
    
    # Also generate for combined dataset
    generate_variants("temp/datasets/combined_readability_dataset.json")
