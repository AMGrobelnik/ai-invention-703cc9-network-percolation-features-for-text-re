#!/usr/bin/env python3
"""Convert readability datasets to exp_sel_data_out.json schema format."""

from loguru import logger
from pathlib import Path
import json
import sys
import numpy as np
from sklearn.model_selection import train_test_split

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/data_convert.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def convert_to_schema():
    """Convert datasets to the required schema format."""
    output_dir = Path("temp/datasets")

    # Load final splits
    train = json.loads((output_dir / "final_train.json").read_text())
    val = json.loads((output_dir / "final_val.json").read_text())
    test = json.loads((output_dir / "final_test.json").read_text())

    # Combine all data
    all_data = train + val + test

    # Group by dataset
    datasets_grouped = {}
    for item in all_data:
        source = item.get("source", "unknown")
        if source not in datasets_grouped:
            datasets_grouped[source] = []
        datasets_grouped[source].append(item)

    # Create output in schema format
    output = {"datasets": []}

    for dataset_name, examples in datasets_grouped.items():
        logger.info(f"Converting {dataset_name}: {len(examples)} examples")

        dataset_obj = {
            "dataset": dataset_name,
            "examples": []
        }

        for i, example in enumerate(examples):
            # Create example in schema format
            schema_example = {
                "input": example["text"],
                "output": str(example["grade_level"]),
                "metadata_source": dataset_name,
                "metadata_id": example.get("id", f"{dataset_name}_{i}"),
                "metadata_grade_level": example["grade_level"]
            }

            dataset_obj["examples"].append(schema_example)

        output["datasets"].append(dataset_obj)

    # Add top-level metadata
    output["metadata"] = {
        "task": "readability_assessment",
        "description": "Text readability scoring with grade level labels (1-12)",
        "total_examples": len(all_data),
        "num_datasets": len(datasets_grouped),
        "grade_range": [1, 12],
        "format": "input=text, output=grade_level (1-12)"
    }

    # Save output
    output_path = Path("full_data_out.json")
    output_path.write_text(json.dumps(output, indent=2))
    logger.info(f"Saved to {output_path}")
    logger.info(f"Total datasets: {len(output['datasets'])}")
    logger.info(f"Total examples: {sum(len(d['examples']) for d in output['datasets'])}")

    return output

@logger.catch(reraise=True)
def main():
    # Convert datasets to schema
    output = convert_to_schema()

    # Print summary
    print("\n=== CONVERSION SUMMARY ===")
    for dataset in output["datasets"]:
        print(f"{dataset['dataset']}: {len(dataset['examples'])} examples")

    print(f"\nTotal: {output['metadata']['total_examples']} examples")

    # Validate a sample
    print("\n=== SAMPLE (first example) ===")
    if output["datasets"]:
        sample = output["datasets"][0]["examples"][0]
        print(json.dumps(sample, indent=2))

if __name__ == "__main__":
    main()
