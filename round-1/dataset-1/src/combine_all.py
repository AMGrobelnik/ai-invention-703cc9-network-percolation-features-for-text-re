#!/usr/bin/env python3
"""Combine all datasets and create final standardized output."""

from loguru import logger
from pathlib import Path
import json
import sys
from sklearn.model_selection import train_test_split
import numpy as np

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/combine.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def main():
    output_dir = Path("temp/datasets")

    # Load all datasets
    datasets = []

    # 1. Combined dataset (OneStopEnglish, FinRAD, CEFR)
    combined_path = output_dir / "combined_readability_dataset.json"
    if combined_path.exists():
        data = json.loads(combined_path.read_text())
        datasets.extend(data)
        logger.info(f"Loaded {len(data)} from combined dataset")

    # 2. Additional dataset (CommonLit, Wikipedia Simple)
    additional_path = output_dir / "additional_readability_dataset.json"
    if additional_path.exists():
        data = json.loads(additional_path.read_text())
        datasets.extend(data)
        logger.info(f"Loaded {len(data)} from additional dataset")

    # 3. Load train/val/test splits if they exist (to avoid re-splitting)
    # Actually, let's create new unified splits

    logger.info(f"Total examples: {len(datasets)}")

    # Standardize format
    standardized = []
    for i, item in enumerate(datasets):
        if "text" not in item or not item["text"]:
            continue
        if "grade_level" not in item or item["grade_level"] is None:
            continue

        grade = int(item["grade_level"])
        if grade < 1 or grade > 12:
            continue

        standardized.append({
            "text": str(item["text"]).strip(),
            "grade_level": grade,
            "source": item.get("source", "unknown"),
            "id": item.get("id", f"item_{i}")
        })

    logger.info(f"Standardized: {len(standardized)} valid examples")

    # Check grade distribution
    grade_dist = {}
    for item in standardized:
        grade = item["grade_level"]
        grade_dist[grade] = grade_dist.get(grade, 0) + 1

    logger.info(f"Grade distribution: {dict(sorted(grade_dist.items()))}")

    # Create 70/15/15 splits with stratification
    # First split: train vs (val + test)
    train, temp = train_test_split(
        standardized,
        test_size=0.30,
        random_state=42,
        stratify=[d["grade_level"] for d in standardized]
    )

    # Second split: val vs test
    val, test = train_test_split(
        temp,
        test_size=0.50,
        random_state=42,
        stratify=[d["grade_level"] for d in temp]
    )

    logger.info(f"Final splits - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    # Save final splits
    (output_dir / "final_train.json").write_text(json.dumps(train, indent=2))
    (output_dir / "final_val.json").write_text(json.dumps(val, indent=2))
    (output_dir / "final_test.json").write_text(json.dumps(test, indent=2))

    # Generate variants for final splits
    for split_name in ["final_train", "final_val", "final_test"]:
        split_path = output_dir / f"{split_name}.json"

        # Full
        # (already saved above)

        # Mini: first 3
        data = json.loads(split_path.read_text())
        mini_path = output_dir / f"mini_{split_name}.json"
        mini_path.write_text(json.dumps(data[:3], indent=2))

        # Preview: first 3 with truncated strings
        preview_data = []
        for item in data[:3]:
            preview_item = {}
            for key, value in item.items():
                if isinstance(value, str) and len(value) > 200:
                    preview_item[key] = value[:200] + "..."
                else:
                    preview_item[key] = value
            preview_data.append(preview_item)
        preview_path = output_dir / f"preview_{split_name}.json"
        preview_path.write_text(json.dumps(preview_data, indent=2))

        logger.info(f"Generated variants for {split_name}")

    # Create final manifest
    manifest = {
        "datasets_used": [
            {
                "name": "OneStopEnglish",
                "source": "SetFit/onestop_english",
                "size": 567,
                "grade_range": [3, 11]
            },
            {
                "name": "FinRAD",
                "source": "sohomghosh/FinRAD_Financial_Readability_Assessment_Dataset",
                "size": 13112,
                "grade_range": "1-12 (FK grade)"
            },
            {
                "name": "CEFR-SP",
                "source": "edesaras/CEFR-Sentence-Level-Annotations",
                "size": 7178,
                "grade_range": [1, 10]
            },
            {
                "name": "CommonLit",
                "source": "casey-martin/CommonLit-Ease-of-Readability",
                "size": 4724,
                "grade_range": [1, 12]
            },
            {
                "name": "Wikipedia Simple",
                "source": "pszemraj/simple_wikipedia",
                "size": 2000,
                "grade_range": [7, 7]
            }
        ],
        "total_examples": len(standardized),
        "final_splits": {
            "train": len(train),
            "val": len(val),
            "test": len(test)
        },
        "grade_distribution": grade_dist,
        "format": {
            "fields": ["text", "grade_level", "source", "id"],
            "description": "text: string, grade_level: int 1-12, source: dataset name, id: unique identifier"
        }
    }

    (output_dir / "final_manifest.json").write_text(json.dumps(manifest, indent=2))
    logger.info(f"Created final manifest")

    # Validate: check all fields present, no nulls
    logger.info("Validating dataset...")
    issues = 0
    for i, item in enumerate(standardized):
        if not item.get("text"):
            logger.warning(f"Item {i} has empty text")
            issues += 1
        if item.get("grade_level") is None:
            logger.warning(f"Item {i} has null grade_level")
            issues += 1
        if not isinstance(item.get("grade_level"), int):
            logger.warning(f"Item {i} grade_level is not int")
            issues += 1
        if item.get("grade_level", 0) < 1 or item.get("grade_level", 0) > 12:
            logger.warning(f"Item {i} grade_level out of range")
            issues += 1

    if issues == 0:
        logger.info("✓ Validation PASSED - no issues found")
    else:
        logger.warning(f"✗ Validation found {issues} issues")

    # Check total size
    total_size = sum(len(json.dumps(item)) for item in standardized)
    logger.info(f"Total dataset size: {total_size / 1024 / 1024:.2f} MB")
    if total_size < 300 * 1024 * 1024:  # 300MB
        logger.info("✓ Size check PASSED (< 300MB)")
    else:
        logger.warning("✗ Size check FAILED (> 300MB)")

if __name__ == "__main__":
    main()
