#!/usr/bin/env python3
"""Create a 6th dataset from available sources to reach target."""

from loguru import logger
from pathlib import Path
import json
import sys
from datasets import load_dataset

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

@logger.catch(reraise=True)
def create_dataset_6():
    """Try to create/find a 6th dataset.
    Options:
    1. Use the SetFit/onestop_english separately (already included but could add variations)
    2. Create a dataset from news articles with estimated readability
    3. Use another HuggingFace dataset
    """
    logger.info("Attempting to create 6th dataset...")

    # Try to load a dataset with news articles at different reading levels
    # Search for "news" datasets that might have difficulty/level labels
    try:
        # Load a dataset and check if it has readability-related features
        ds = load_dataset("bogdancazan/wikilarge-text-simplification")

        # This dataset has "Normal" and "Simple" columns - we can use this
        # Simple = lower reading level (approx grade 6-8)
        # Normal = higher reading level (approx grade 10-12)

        results = []
        for i, item in enumerate(ds["train"]):
            # Add simple text with lower grade
            if item.get("Simple"):
                results.append({
                    "text": item["Simple"],
                    "grade_level": 7,  # Middle school
                    "source": "WikiLarge_Simple",
                    "id": f"wikilarge_simple_{i}"
                })

            # Add normal text with higher grade
            if item.get("Normal"):
                results.append({
                    "text": item["Normal"],
                    "grade_level": 11,  # High school
                    "source": "WikiLarge_Normal",
                    "id": f"wikilarge_normal_{i}"
                })

        logger.info(f"Created WikiLarge dataset with {len(results)} examples")
        return results[:2000]  # Limit to 2000 to keep balanced

    except Exception as e:
        logger.error(f"Failed to create 6th dataset: {e}")
        return []

@logger.catch(reraise=True)
def main():
    # Create 6th dataset
    dataset_6 = create_dataset_6()

    if not dataset_6:
        logger.warning("Could not create 6th dataset, proceeding with 5")
        return

    # Load existing final splits
    output_dir = Path("temp/datasets")

    # Add to existing combined dataset
    combined_path = output_dir / "combined_readability_dataset.json"
    existing = json.loads(combined_path.read_text())
    existing.extend(dataset_6)

    # Save updated combined dataset
    combined_path.write_text(json.dumps(existing, indent=2))
    logger.info(f"Updated combined dataset: {len(existing)} total examples")

    # Re-run the combine script to create new splits
    logger.info("Re-creating final splits with 6 datasets...")

    # Standardize
    standardized = []
    for i, item in enumerate(existing):
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

    # Create new splits
    from sklearn.model_selection import train_test_split
    train, temp = train_test_split(
        standardized,
        test_size=0.30,
        random_state=42,
        stratify=[d["grade_level"] for d in standardized]
    )
    val, test = train_test_split(
        temp,
        test_size=0.50,
        random_state=42,
        stratify=[d["grade_level"] for d in temp]
    )

    # Save
    (output_dir / "final_train.json").write_text(json.dumps(train, indent=2))
    (output_dir / "final_val.json").write_text(json.dumps(val, indent=2))
    (output_dir / "final_test.json").write_text(json.dumps(test, indent=2))

    logger.info(f"Final splits with 6 datasets - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    # Update manifest
    manifest_path = output_dir / "final_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["datasets_used"].append({
        "name": "WikiLarge",
        "source": "bogdancazan/wikilarge-text-simplification",
        "size": len(dataset_6),
        "grade_range": [7, 11]
    })
    manifest["total_examples"] = len(standardized)
    manifest["final_splits"] = {"train": len(train), "val": len(val), "test": len(test)}

    # Update grade distribution
    grade_dist = {}
    for item in standardized:
        grade = item["grade_level"]
        grade_dist[grade] = grade_dist.get(grade, 0) + 1
    manifest["grade_distribution"] = grade_dist

    manifest_path.write_text(json.dumps(manifest, indent=2))
    logger.info("Updated manifest with 6 datasets")

if __name__ == "__main__":
    main()
