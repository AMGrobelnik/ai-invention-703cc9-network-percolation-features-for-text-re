#!/usr/bin/env python3
"""Select THE BEST 3 datasets for final output."""

from pathlib import Path
import json
import sys

# BEST 3 datasets based on domain requirements:
# 1. OneStopEnglish - educator-created texts at 3 levels
# 2. CommonLit - educator-assigned readability levels
# 3. CEFR-SP - annotated by english education professionals

BEST_DATASETS = ["OneStopEnglish", "CommonLit", "CEFR-SP"]

def main():
    # Load full data
    data = json.loads(Path("full_data_out.json").read_text())

    # Filter to best 3
    best_data = {
        "datasets": [],
        "metadata": data.get("metadata", {})
    }

    for dataset in data["datasets"]:
        if dataset["dataset"] in BEST_DATASETS:
            best_data["datasets"].append(dataset)
            print(f"✓ Included: {dataset['dataset']} ({len(dataset['examples'])} examples)")

    # Update metadata
    best_data["metadata"]["selected_datasets"] = BEST_DATASETS
    best_data["metadata"]["total_examples"] = sum(len(d["examples"]) for d in best_data["datasets"])
    best_data["metadata"]["selection_criteria"] = "Ground-truth labels from educators (not algorithm-derived)"

    # Save final output
    Path("full_data_out.json").write_text(json.dumps(best_data, indent=2))
    print(f"\nFinal output: {best_data['metadata']['total_examples']} examples from {len(BEST_DATASETS)} datasets")

    # Generate preview
    preview = {"datasets": [], "metadata": best_data["metadata"]}
    for dataset in best_data["datasets"]:
        preview_dataset = {"dataset": dataset["dataset"], "examples": []}
        for example in dataset["examples"][:3]:
            preview_example = {}
            for key, value in example.items():
                if isinstance(value, str) and len(value) > 200:
                    preview_example[key] = value[:200] + "..."
                else:
                    preview_example[key] = value
            preview_dataset["examples"].append(preview_example)
        preview["datasets"].append(preview_dataset)

    Path("preview_full_data_out.json").write_text(json.dumps(preview, indent=2))
    print("✓ Created preview_full_data_out.json")

if __name__ == "__main__":
    main()
