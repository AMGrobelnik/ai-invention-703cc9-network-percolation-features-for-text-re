# Percolation Threshold Readability (PTR) - Experiment Summary

## Novel Method
First application of network percolation theory to text readability assessment.

## Key Idea
Text is modeled as a word co-occurrence network. The percolation threshold (where the network disintegrates) serves as a readability feature - readable text maintains connectivity longer than complex text.

## Results (500 test examples, 3 datasets)

| Method | MAE | Acc@1 | Acc@2 |
|--------|-----|-------|-------|
| PTR (Novel) | 1.165 | 0.530 | 0.830 |
| Baseline ML | 1.203 | 0.492 | 0.812 |
| Traditional (Flesch-Kincaid) | 1.756 | 0.512 | 0.672 |

## Improvement
- PTR vs Baseline: 0.038 MAE reduction (3.2% improvement)
- PTR vs Traditional: 0.591 MAE reduction (33.6% improvement)

## Files
- `method.py` - Main experiment script
- `method_out.json` - Results in validated JSON format
- `data/full_data_out.json` - Input datasets (12,469 examples)

## Reproducibility
```bash
source .venv/bin/activate
python method.py
```

Output validates against `exp_gen_sol_out.json` schema.
