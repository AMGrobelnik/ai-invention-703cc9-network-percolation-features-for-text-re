#!/usr/bin/env python3
"""Download and process readability datasets."""

from loguru import logger
from pathlib import Path
import json
import sys
from datasets import load_dataset

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/download.log", rotation="30 MB", level="DEBUG")

@logger.catch(reraise=True)
def download_onestop_english():
    """Download and process OneStopEnglish dataset."""
    logger.info("Downloading OneStopEnglish dataset...")
    ds = load_dataset("SetFit/onestop_english")

    # Map labels: 0=Elementary, 1=Intermediate, 2=Advanced
    # Map to grade levels: Elementary=3, Intermediate=7, Advanced=11
    grade_map = {0: 3, 1: 7, 2: 11}
    label_text_map = {0: "Elementary", 1: "Intermediate", 2: "Advanced"}

    results = []
    for split_name in ds.keys():
        for i, item in enumerate(ds[split_name]):
            results.append({
                "text": item["text"],
                "grade_level": grade_map[item["label"]],
                "source": "OneStopEnglish",
                "id": f"onestop_{split_name}_{i}",
                "label_text": label_text_map[item["label"]]
            })

    logger.info(f"OneStopEnglish: {len(results)} examples")
    return results

@logger.catch(reraise=True)
def download_finrad():
    """Download and process FinRAD dataset."""
    logger.info("Downloading FinRAD dataset...")
    ds = load_dataset("sohomghosh/FinRAD_Financial_Readability_Assessment_Dataset")

    results = []
    for i, item in enumerate(ds["train"]):
        # Use assigned_readability or compute from Flesch-Kincaid grade
        grade = item.get("flesch_kincaid_grade", None)
        if grade is not None:
            # Clamp to 1-12 range
            grade = max(1, min(12, int(grade)))

        results.append({
            "text": item["definitions"],
            "grade_level": grade,
            "source": "FinRAD",
            "id": f"finrad_{i}",
            "term": item.get("terms", ""),
            "flesch_reading_ease": item.get("flesch_reading_ease", None),
            "smog_index": item.get("smog_index", None)
        })

    logger.info(f"FinRAD: {len(results)} examples")
    return results

@logger.catch(reraise=True)
def download_cefr_sentences():
    """Download CEFR sentence annotations."""
    logger.info("Downloading CEFR sentences...")
    ds = load_dataset("edesaras/CEFR-Sentence-Level-Annotations")

    # Map CEFR levels to grades (approximate)
    # A1=1, A2=2, B1=4, B2=6, C1=8, C2=10
    cefr_to_grade = {
        1: 1,  # A1
        2: 2,  # A2
        3: 4,  # B1
        4: 6,  # B2
        5: 8,  # C1
        6: 10, # C2
    }

    results = []
    for i, item in enumerate(ds["train"]):
        # Average the two annotators' ratings
        annotator_1 = item.get("Annotator I", None)
        annotator_2 = item.get("Annotator II", None)

        if annotator_1 is not None and annotator_2 is not None:
            avg_grade = (annotator_1 + annotator_2) / 2
            grade = cefr_to_grade.get(int(avg_grade), None)
        elif annotator_1 is not None:
            grade = cefr_to_grade.get(int(annotator_1), None)
        else:
            grade = None

        results.append({
            "text": item["text"],
            "grade_level": grade,
            "source": "CEFR-SP",
            "id": f"cefr_{i}",
            "annotator_1": annotator_1,
            "annotator_2": annotator_2
        })

    logger.info(f"CEFR Sentences: {len(results)} examples")
    return results

@logger.catch(reraise=True)
def main():
    output_dir = Path("temp/datasets")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_datasets = {}

    # Download each dataset
    try:
        all_datasets["onestop_english"] = download_onestop_english()
    except Exception as e:
        logger.error(f"Failed to download OneStopEnglish: {e}")

    try:
        all_datasets["finrad"] = download_finrad()
    except Exception as e:
        logger.error(f"Failed to download FinRAD: {e}")

    try:
        all_datasets["cefr_sentences"] = download_cefr_sentences()
    except Exception as e:
        logger.error(f"Failed to download CEFR sentences: {e}")

    # Save combined dataset
    combined = []
    for dataset_name, examples in all_datasets.items():
        combined.extend(examples)

    output_path = output_dir / "combined_readability_dataset.json"
    output_path.write_text(json.dumps(combined, indent=2))
    logger.info(f"Saved {len(combined)} total examples to {output_path}")

    # Generate statistics
    logger.info("Dataset statistics:")
    for dataset_name, examples in all_datasets.items():
        valid_grades = [e["grade_level"] for e in examples if e["grade_level"] is not None]
        logger.info(f"  {dataset_name}: {len(examples)} examples, {len(valid_grades)} with valid grades")

if __name__ == "__main__":
    main()
