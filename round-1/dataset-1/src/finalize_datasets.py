#!/usr/bin/env python3
"""Final dataset combination and cleanup."""

from loguru import logger
from pathlib import Path
import json
import sys
from datasets import load_dataset
from sklearn.model_selection import train_test_split

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

@logger.catch(reraise=True)
def load_all_datasets():
    """Load all 6 datasets."""
    all_examples = []

    # 1. OneStopEnglish
    logger.info("Loading OneStopEnglish...")
    ds = load_dataset("SetFit/onestop_english")
    grade_map = {0: 3, 1: 7, 2: 11}
    for split in ds.keys():
        for i, item in enumerate(ds[split]):
            all_examples.append({
                "text": item["text"],
                "grade_level": grade_map[item["label"]],
                "source": "OneStopEnglish",
                "id": f"onestop_{split}_{i}"
            })

    # 2. FinRAD
    logger.info("Loading FinRAD...")
    ds = load_dataset("sohomghosh/FinRAD_Financial_Readability_Assessment_Dataset")
    for i, item in enumerate(ds["train"]):
        fk = item.get("flesch_kincaid_grade")
        if fk is not None:
            grade = max(1, min(12, int(fk)))
            all_examples.append({
                "text": item["definitions"],
                "grade_level": grade,
                "source": "FinRAD",
                "id": f"finrad_{i}"
            })

    # 3. CEFR-SP
    logger.info("Loading CEFR-SP...")
    ds = load_dataset("edesaras/CEFR-Sentence-Level-Annotations")
    cefr_to_grade = {1: 1, 2: 2, 3: 4, 4: 6, 5: 8, 6: 10}
    for i, item in enumerate(ds["train"]):
        ann1 = item.get("Annotator I")
        ann2 = item.get("Annotator II")
        if ann1 is not None:
            avg = int((ann1 + ann2) / 2) if ann2 is not None else int(ann1)
            grade = cefr_to_grade.get(avg, None)
            if grade:
                all_examples.append({
                    "text": item["text"],
                    "grade_level": grade,
                    "source": "CEFR-SP",
                    "id": f"cefr_{i}"
                })

    # 4. CommonLit
    logger.info("Loading CommonLit...")
    ds = load_dataset("casey-martin/CommonLit-Ease-of-Readability")
    for split in ds.keys():
        for i, item in enumerate(ds[split]):
            fk = item.get("Flesch-Kincaid-Grade-Level")
            if fk is not None:
                grade = max(1, min(12, int(fk)))
                all_examples.append({
                    "text": item.get("Excerpt", ""),
                    "grade_level": grade,
                    "source": "CommonLit",
                    "id": f"commonlit_{split}_{i}"
                })

    # 5. Wikipedia Simple
    logger.info("Loading Wikipedia Simple...")
    ds = load_dataset("pszemraj/simple_wikipedia", split="train", streaming=True)
    count = 0
    for item in ds:
        if count >= 2000:
            break
        text = item.get("text", "")
        if text and len(text) > 100:
            all_examples.append({
                "text": text[:2000],
                "grade_level": 7,
                "source": "Wikipedia_Simple",
                "id": f"wiki_simple_{count}"
            })
            count += 1

    # 6. WikiLarge
    logger.info("Loading WikiLarge...")
    ds = load_dataset("bogdancazan/wikilarge-text-simplification")
    count_simple = 0
    count_normal = 0
    for item in ds["train"]:
        if count_simple < 1000 and item.get("Simple"):
            all_examples.append({
                "text": item["Simple"],
                "grade_level": 7,
                "source": "WikiLarge_Simple",
                "id": f"wikilarge_simple_{count_simple}"
            })
            count_simple += 1
        if count_normal < 1000 and item.get("Normal"):
            all_examples.append({
                "text": item["Normal"],
                "grade_level": 11,
                "source": "WikiLarge_Normal",
                "id": f"wikilarge_normal_{count_normal}"
            })
            count_normal += 1
        if count_simple >= 1000 and count_normal >= 1000:
            break

    logger.info(f"Total loaded: {len(all_examples)} examples")
    return all_examples

@logger.catch(reraise=True)
def main():
    output_dir = Path("temp/datasets")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all datasets
    all_examples = load_all_datasets()

    # Filter valid examples
    valid = []
    for i, item in enumerate(all_examples):
        if item.get("text") and item.get("grade_level") and 1 <= item["grade_level"] <= 12:
            valid.append(item)

    logger.info(f"Valid examples: {len(valid)}")

    # Create 70/15/15 splits
    train, temp = train_test_split(
        valid,
        test_size=0.30,
        random_state=42,
        stratify=[d["grade_level"] for d in valid]
    )
    val, test = train_test_split(
        temp,
        test_size=0.50,
        random_state=42,
        stratify=[d["grade_level"] for d in temp]
    )

    # Save final splits
    (output_dir / "final_train.json").write_text(json.dumps(train, indent=2))
    (output_dir / "final_val.json").write_text(json.dumps(val, indent=2))
    (output_dir / "final_test.json").write_text(json.dumps(test, indent=2))

    logger.info(f"Final splits - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    # Generate mini/preview
    for split_name in ["final_train", "final_val", "final_test"]:
        data = json.loads((output_dir / f"{split_name}.json").read_text())

        # Mini
        (output_dir / f"mini_{split_name}.json").write_text(json.dumps(data[:3], indent=2))

        # Preview
        preview = []
        for item in data[:3]:
            p = {}
            for k, v in item.items():
                if isinstance(v, str) and len(v) > 200:
                    p[k] = v[:200] + "..."
                else:
                    p[k] = v
            preview.append(p)
        (output_dir / f"preview_{split_name}.json").write_text(json.dumps(preview, indent=2))

    # Create final manifest
    sources = {}
    for item in valid:
        src = item["source"]
        sources[src] = sources.get(src, 0) + 1

    grade_dist = {}
    for item in valid:
        g = item["grade_level"]
        grade_dist[g] = grade_dist.get(g, 0) + 1

    manifest = {
        "datasets": [
            {"name": src, "size": cnt} for src, cnt in sorted(sources.items())
        ],
        "total_examples": len(valid),
        "splits": {"train": len(train), "val": len(val), "test": len(test)},
        "grade_distribution": dict(sorted(grade_dist.items())),
        "format": {"fields": ["text", "grade_level", "source", "id"]}
    }

    (output_dir / "final_manifest.json").write_text(json.dumps(manifest, indent=2))
    logger.info("✓ Dataset collection complete!")

if __name__ == "__main__":
    main()
