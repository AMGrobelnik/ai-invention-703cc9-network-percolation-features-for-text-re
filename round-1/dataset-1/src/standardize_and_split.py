#!/usr/bin/env python3
"""Standardize and split readability datasets."""

from loguru import logger
from pathlib import Path
import json
import sys
from sklearn.model_selection import train_test_split

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/process.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def standardize_format(data, min_grade=1, max_grade=12):
    """Standardize dataset format to {text, grade_level, source, id}."""
    standardized = []

    for i, item in enumerate(data):
        # Skip items without required fields
        if "text" not in item or not item["text"]:
            continue

        # Get grade level
        grade = item.get("grade_level", None)
        if grade is None:
            continue

        # Clamp grade to valid range
        grade = max(min_grade, min(max_grade, int(grade)))

        standardized.append({
            "text": str(item["text"]).strip(),
            "grade_level": grade,
            "source": item.get("source", "unknown"),
            "id": item.get("id", f"item_{i}")
        })

    return standardized

@logger.catch(reraise=True)
def create_splits(data, test_size=0.15, val_size=0.15, random_state=42):
    """Create 70/15/15 train/val/test splits."""
    # First split: train vs (val + test)
    train, temp = train_test_split(
        data,
        test_size=(val_size + test_size),
        random_state=random_state,
        stratify=[d["grade_level"] for d in data]
    )

    # Second split: val vs test
    val, test = train_test_split(
        temp,
        test_size=0.5,
        random_state=random_state,
        stratify=[d["grade_level"] for d in temp]
    )

    return train, val, test

@logger.catch(reraise=True)
def main():
    import numpy as np

    # Load combined dataset
    input_path = Path("temp/datasets/combined_readability_dataset.json")
    data = json.loads(input_path.read_text())
    logger.info(f"Loaded {len(data)} examples")

    # Standardize format
    standardized = standardize_format(data)
    logger.info(f"Standardized to {len(standardized)} valid examples")

    # Check grade distribution
    grade_dist = {}
    for item in standardized:
        grade = item["grade_level"]
        grade_dist[grade] = grade_dist.get(grade, 0) + 1

    logger.info(f"Grade distribution: {dict(sorted(grade_dist.items()))}")

    # Create splits
    train, val, test = create_splits(standardized)
    logger.info(f"Split sizes - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    # Save splits
    output_dir = Path("temp/datasets")
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "train.json").write_text(json.dumps(train, indent=2))
    (output_dir / "val.json").write_text(json.dumps(val, indent=2))
    (output_dir / "test.json").write_text(json.dumps(test, indent=2))

    logger.info(f"Saved splits to {output_dir}")

    # Generate full/mini/preview variants using aii-json skill
    import subprocess
    skill_dir = "/ai-inventor/.claude/skills/aii-json"

    for split_name in ["train", "val", "test"]:
        split_path = output_dir / f"{split_name}.json"
        cmd = [
            f"{skill_dir}/../.ability_client_venv/bin/python",
            f"{skill_dir}/scripts/aii_json_format_mini_preview.py",
            "--input", str(split_path),
            "--output-dir", str(output_dir)
        ]
        logger.info(f"Generating variants for {split_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Generated variants for {split_name}")
        else:
            logger.error(f"Failed to generate variants: {result.stderr}")

    # Create manifest
    manifest = {
        "datasets": [
            {
                "name": "OneStopEnglish",
                "source": "HuggingFace (SetFit/onestop_english)",
                "size": 567,
                "grade_range": [3, 11],
                "description": "Texts at three reading levels (Elementary/Intermediate/Advanced)"
            },
            {
                "name": "FinRAD",
                "source": "HuggingFace (sohomghosh/FinRAD_Financial_Readability_Assessment_Dataset)",
                "size": 13112,
                "grade_range": "variable (FK grade)",
                "description": "Financial term definitions with readability metrics"
            },
            {
                "name": "CEFR-SP",
                "source": "HuggingFace (edesaras/CEFR-Sentence-Level-Annotations)",
                "size": 7178,
                "grade_range": [1, 10],
                "description": "Sentences annotated with CEFR levels"
            }
        ],
        "total_examples": len(standardized),
        "splits": {
            "train": len(train),
            "val": len(val),
            "test": len(test)
        },
        "grade_distribution": grade_dist
    }

    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    logger.info(f"Created manifest at {output_dir / 'manifest.json'}")

if __name__ == "__main__":
    import random
    main()
