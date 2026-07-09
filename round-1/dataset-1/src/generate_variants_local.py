#!/usr/bin/env python3
"""Generate mini and preview versions locally."""

from pathlib import Path
import json
import sys

def generate_variants(input_path):
    """Generate full/mini/preview variants."""
    input_path = Path(input_path)
    data = json.loads(input_path.read_text())

    if not isinstance(data, dict) or "datasets" not in data:
        print("Error: Input must be a dict with 'datasets' key")
        return

    base_name = input_path.stem

    # Full: already exists (input file)

    # Mini: first 3 examples from each dataset
    mini_data = {"datasets": [], "metadata": data.get("metadata", {})}
    for dataset in data["datasets"][:3]:  # First 3 datasets
        mini_dataset = {
            "dataset": dataset["dataset"],
            "examples": dataset["examples"][:3]
        }
        mini_data["datasets"].append(mini_dataset)

    mini_path = input_path.parent / f"mini_{base_name}.json"
    mini_path.write_text(json.dumps(mini_data, indent=2))
    print(f"Created: {mini_path}")

    # Preview: mini with truncated strings
    preview_data = {"datasets": [], "metadata": data.get("metadata", {})}
    for dataset in mini_data["datasets"]:
        preview_dataset = {"dataset": dataset["dataset"], "examples": []}
        for example in dataset["examples"]:
            preview_example = {}
            for key, value in example.items():
                if isinstance(value, str) and len(value) > 200:
                    preview_example[key] = value[:200] + "..."
                else:
                    preview_example[key] = value
            preview_dataset["examples"].append(preview_example)
        preview_data["datasets"].append(preview_dataset)

    preview_path = input_path.parent / f"preview_{base_name}.json"
    preview_path.write_text(json.dumps(preview_data, indent=2))
    print(f"Created: {preview_path}")

if __name__ == "__main__":
    generate_variants("full_data_out.json")
