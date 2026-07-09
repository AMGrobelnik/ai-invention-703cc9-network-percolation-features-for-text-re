#!/usr/bin/env python3
"""Download and process additional readability datasets."""

from loguru import logger
from pathlib import Path
import json
import sys
from datasets import load_dataset

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/download2.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def download_commonlit():
    """Download and process CommonLit Readability dataset."""
    logger.info("Downloading CommonLit dataset...")
    ds = load_dataset("casey-martin/CommonLit-Ease-of-Readability")

    results = []
    for split_name in ds.keys():
        for i, item in enumerate(ds[split_name]):
            # Get Flesch-Kincaid grade level
            fk_grade = item.get("Flesch-Kincaid-Grade-Level", None)

            # Also check Lexile band and convert to grade if available
            lexile = item.get("Lexile Band", None)

            # Use FK grade, clamp to 1-12
            if fk_grade is not None:
                grade = max(1, min(12, int(fk_grade)))
            else:
                grade = None

            results.append({
                "text": item.get("Excerpt", ""),
                "grade_level": grade,
                "source": "CommonLit",
                "id": f"commonlit_{split_name}_{i}",
                "author": item.get("Author", ""),
                "title": item.get("Title", ""),
                "lexile_band": lexile,
                "flesch_reading_ease": item.get("Flesch-Reading-Ease", None)
            })

    # Filter out items without text or grade
    valid = [r for r in results if r["text"] and r["grade_level"] is not None]
    logger.info(f"CommonLit: {len(results)} examples, {len(valid)} valid")
    return valid

@logger.catch(reraise=True)
def create_wikipedia_simple_dataset(num_samples=2000):
    """Create a dataset from Wikipedia Simple vs Regular Wikipedia.
    Simple Wikipedia articles are generally written at a lower reading level.
    """
    logger.info("Creating Wikipedia Simple vs Regular dataset...")

    try:
        # Load Simple Wikipedia
        simple_wiki = load_dataset("pszemraj/simple_wikipedia", split="train", streaming=True)

        results = []
        count = 0
        for item in simple_wiki:
            if count >= num_samples:
                break

            text = item.get("text", "")
            if not text or len(text) < 100:
                continue

            # Simple Wikipedia ≈ grade 6-8
            results.append({
                "text": text[:2000],  # Truncate very long texts
                "grade_level": 7,  # Approximate middle school level
                "source": "Wikipedia_Simple",
                "id": f"wiki_simple_{count}"
            })
            count += 1

        logger.info(f"Wikipedia Simple: {len(results)} examples")
        return results

    except Exception as e:
        logger.error(f"Failed to create Wikipedia Simple dataset: {e}")
        return []

@logger.catch(reraise=True)
def create_gutenberg_dataset(num_samples=1000):
    """Create a dataset from Project Gutenberg texts with estimated reading levels.
    This is a fallback option - uses FK formula to estimate grade level.
    """
    logger.info("Creating Project Gutenberg dataset (with FK estimates)...")

    # This is a simplified version - in practice, you'd need to
    # download from Project Gutenberg and compute readability
    # For now, return empty as this is last resort per the plan

    logger.warning("Project Gutenberg dataset creation not implemented (last resort)")
    return []

@logger.catch(reraise=True)
def main():
    output_dir = Path("temp/datasets")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_datasets = {}

    # Download CommonLit
    try:
        all_datasets["commonlit"] = download_commonlit()
    except Exception as e:
        logger.error(f"Failed to download CommonLit: {e}")

    # Create Wikipedia Simple dataset
    try:
        all_datasets["wikipedia_simple"] = create_wikipedia_simple_dataset()
    except Exception as e:
        logger.error(f"Failed to create Wikipedia Simple dataset: {e}")

    # Save combined dataset
    combined = []
    for dataset_name, examples in all_datasets.items():
        combined.extend(examples)

    if combined:
        output_path = output_dir / "additional_readability_dataset.json"
        output_path.write_text(json.dumps(combined, indent=2))
        logger.info(f"Saved {len(combined)} additional examples to {output_path}")

        # Print statistics
        for dataset_name, examples in all_datasets.items():
            if examples:
                grades = [e["grade_level"] for e in examples if e["grade_level"] is not None]
                logger.info(f"  {dataset_name}: {len(examples)} examples, "
                          f"grade range: {min(grades) if grades else 'N/A'}-{max(grades) if grades else 'N/A'}")

    return combined

if __name__ == "__main__":
    main()
