# Readability Dataset Collection - Final Report

## Summary

Successfully collected and standardized 6 readability datasets with 29,581 total examples.

## Datasets Included

| Dataset | Source | Size | Grade Range | Description |
|----------|--------|------|-------------|-------------|
| OneStopEnglish | SetFit/onestop_english | 567 | 3-11 | Texts at 3 reading levels (Elementary/Intermediate/Advanced) |
| FinRAD | sohomghosh/FinRAD_Financial_Readability_Assessment_Dataset | 13,112 | 1-12 | Financial term definitions with FK readability |
| CEFR-SP | edesaras/CEFR-Sentence-Level-Annotations | 7,178 | 1-10 | Sentences annotated with CEFR levels |
| CommonLit | casey-martin/CommonLit-Ease-of-Readability | 4,724 | 1-12 | Literary excerpts with multiple readability metrics |
| Wikipedia Simple | pszemraj/simple_wikipedia | 2,000 | 7 | Simple Wikipedia articles (middle school level) |
| WikiLarge | bogdancazan/wikilarge-text-simplification | 2,000 | 7-11 | Paired normal/simple sentences |

## Final Splits

- **Train**: 20,706 examples (70%)
- **Validation**: 4,437 examples (15%)
- **Test**: 4,438 examples (15%)

## Data Format

Each example has the standardized format:
```json
{
  "text": "string (clean plain text)",
  "grade_level": "int 1-12",
  "source": "string (dataset name)",
  "id": "string (unique identifier)"
}
```

## Grade Distribution

- Grade 1: 730 (2.5%)
- Grade 2: 1,864 (6.3%)
- Grade 3: 512 (1.7%)
- Grade 4: 3,114 (10.5%)
- Grade 5: 555 (1.9%)
- Grade 6: 2,668 (9.0%)
- Grade 7: 4,066 (13.7%)
- Grade 8: 1,690 (5.7%)
- Grade 9: 1,589 (5.4%)
- Grade 10: 1,689 (5.7%)
- Grade 11: 3,057 (10.3%)
- Grade 12: 8,047 (27.2%)

## Validation Results

✓ All items have required fields (text, grade_level, source, id)
✓ No null values in required fields
✓ All grade_level values are integers in range 1-12
✓ Total size: 15.41 MB (well under 300MB limit)
✓ Train/val/test splits stratifed by grade_level

## File Locations

- **Final train split**: `temp/datasets/final_train.json`
- **Final val split**: `temp/datasets/final_val.json`
- **Final test split**: `temp/datasets/final_test.json`
- **Manifest**: `temp/datasets/final_manifest.json`
- **Mini variants**: `temp/datasets/mini_final_*.json`
- **Preview variants**: `temp/datasets/preview_final_*.json`

## Notes

1. Newsela and Weebit corpora were not available on HuggingFace or GitHub (require special access)
2. CommonLit dataset provides high-quality excerpts with educator-assigned reading levels
3. Wikipedia Simple provides approximatly grade 7 texts
4. All datasets have been verified to have >100 downloads and clear documentation
5. Ground-truth labels come from educators (not algorithm-derived) for OneStopEnglish, CommonLit, and CEFR-SP

## Next Steps

The datasets are ready for use in readability assessment experiments. The standardized format allows for easy loading and processing.
