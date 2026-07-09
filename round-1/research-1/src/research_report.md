# Readability Assessment Methods and Metrics Literature Review

## Summary

Comprehensive literature review of readability assessment methods covering: (1) Traditional formulas (Flesch-Kincaid, Dale-Chall, SMOG, ARI) with exact equations and limitations; (2) Modern ML approaches including BERT-based models, hybrid models (neural + linguistic features), and graph-based approaches with benchmark results; (3) Standard evaluation metrics (RMSE, Pearson r, Spearman ρ, accuracy, F1, QWK) with interpretation guidelines; (4) Standard datasets (OneStopEnglish, Weebit, CLEAR, Newsela, WSJ) with sizes, grade ranges, and access instructions; (5) Benchmark results from SOTA papers; (6) Recommended evaluation protocol for the percolation threshold readability model; (7) Gaps and opportunities where the novel percolation model can contribute. The research identifies that traditional formulas rely on surface features and have limited construct validity, while modern ML approaches achieve high performance (F1 >92% on Weebit, >99% on OneStopEnglish) but lack interpretability. The percolation threshold model offers opportunities in physical interpretability, dynamic comprehension modeling, and robust cohesion network construction.

## Research Findings

## Comprehensive Answer: Readability Assessment Methods and Metrics

### Executive Summary

Readability assessment has evolved from traditional surface-level formulas to sophisticated ML approaches. Traditional formulas (Flesch-Kincaid, Dale-Chall, SMOG, ARI) rely on word length, sentence length, and syllable counts but have significant limitations in construct validity [1][2][3][4][14]. Modern ML approaches using BERT embeddings, hybrid models (combining linguistic features with neural predictions), and graph-based methods achieve substantially better performance, with F1 scores of 92.73% on Weebit and 99.41% on OneStopEnglish [5][6].

### 1. Traditional Readability Formulas

#### 1.1 Flesch-Kincaid Grade Level [1]
**Formula:** `FKGL = 0.39 × (total words / total sentences) + 11.8 × (total syllables / total words) - 15.59`
**Output:** U.S. grade level (theoretical range: -3.40 to unbounded)
**Limitations:** Ignores semantics, cohesion, and reader factors; unreliable for texts < 300 words; assumes well-formed sentences [14].

#### 1.2 Dale-Chall Readability Formula [2][15]
**Formula:** `Raw Score = 0.1579 × (percentage of difficult words) + 0.0496 × (average sentence length)`. If percentage of difficult words > 5%, add 3.6365.
**Difficult Words:** Words NOT on the Dale list of ~3,000 words familiar to 80% of U.S. fourth-graders.
**Advantages:** Uses familiar word list rather than syllable count; better for beginning readers.

#### 1.3 SMOG Readability Index [3]
**Formula:** `SMOG = 1.0430 × √(number of polysyllables × 30 / number of sentences) + 3.1291`
**Simplified Method:** Count polysyllabic words (3+ syllables) in three 10-sentence samples, take square root of nearest perfect square, add 3.
**Validity:** 0.985 correlation with comprehension of test materials; standard error of 1.5159 grades [16].
**Limitation:** Requires at least 30 sentences; statistically invalid for shorter texts.

#### 1.4 Automated Readability Index (ARI) [4]
**Formula:** `ARI = 4.71 × (characters / words) + 0.5 × (words / sentences) - 21.43`
**Output:** Integer grade level (1 = Kindergarten, 14 = College student).
**Advantage:** Uses characters instead of syllables (faster computer calculation).

#### 1.5 Limitations of Traditional Formulas [14][17]
1. **Surface-level features only:** Rely on proxies (syllables, sentence length) that don't capture semantic complexity, cohesion, discourse structure.
2. **Ignore reader factors:** Don't account for prior knowledge, motivation, language background.
3. **Require substantial text:** Unreliable for passages < 300 words.
4. **Assume well-formed text:** Perform poorly on Web texts, social media, noisy data.
5. **Limited construct validity:** Traditional formulas explain only 80% of variability through vocabulary; miss syntax, cohesion, cognition [18].

### 2. Modern ML Approaches

#### 2.1 Feature-Based Approaches [7][19]
**Linguistic Features (typically 100-200+ features):**
- **Lexical:** Type-token ratio, vocabulary richness measures, word frequency, Academic Word List percentage
- **Syntactic:** Parse tree depth, clauses per sentence, t-units, dependent clauses, phrase lengths
- **Morphological:** Part-of-speech tags, verb forms, affixes
- **Discourse:** Cohesion markers, coreference links
- **Psycholinguistic:** Word concreteness, imageability, age-of-acquisition

**Performance on Weebit dataset [19]:**
- All features (42): Pearson r = 0.92, RMSE = 0.54
- Syntax-only features (25): Pearson r = 0.88, RMSE = 0.64
- Lexical-only features (17): Pearson r = 0.84, RMSE = 0.78
- Traditional-only features (3): Pearson r = 0.66, RMSE = 1.06

#### 2.2 BERT-Based Approaches [5][20]
**BERT Embeddings for ARA (Imperial, 2021) [5]:**
- Extract BERT sentence embeddings using mean pooling
- Concatenate with handcrafted linguistic features
- Train with traditional ML algorithms (SVM, Random Forest, Logistic Regression)
- **Results:** Combined features outperform individual approaches
  - OneStopEnglish: 0.732 F1 (Logistic Regression)
  - Common Core Exemplars: 0.893 F1 (SVM)
  - Low-resource Filipino: 12.4% F1 improvement

**Unified BERT Model with Feature Projection (Li et al., 2022) [6]:**
- BERT-FP-LBL model integrates feature projection with length-balanced loss
- **Results:** 
  - Weebit: 92.73% F1
  - OneStopEnglish: 99.41% F1
  - Cambridge: 87.73% F1
  - ChineseLR: 78.75% F1
  - Spearman correlation: 0.836 (matches human experts)

#### 2.3 Hybrid Models [6][21]
**Architectures:**
1. **Concatenated Model:** Linguistic features appended to BERT input as text
2. **Hard Label Model:** Neural model predictions used as additional features for traditional classifier
3. **Soft Label Model:** Probability distributions from neural model combined with linguistic features

**Results on Sentence-Level ARA (Liu & Lee, 2023) [21]:**
- WSJ dataset: Hybrid (Hard Label) achieves 0.729 accuracy (13% absolute improvement over previous SOTA)
- OneStopEnglish: Hybrid (Soft Label) achieves 0.581 accuracy
- BERT-based models outperform traditional linguistic-only models

#### 2.4 Graph-Based Approaches [22]
**Graph Representation Learning (Zhang et al., 2026) [22]:**
- Construct text graphs with words as nodes, syntactic dependencies as weighted edges
- Edge weights based on POS tags of intermediate words
- Use Graph Convolutional Networks (GCN) with BERT embeddings
- Bayesian Optimization for hyperparameter tuning
- **Results on CLEAR dataset:** R² = 0.9729

### 3. Evaluation Metrics and Protocols

#### 3.1 Standard Metrics [7][8][12]

**For Regression (continuous readability scores):**
1. **RMSE (Root Mean Square Error):** Average deviation in grade levels between predicted and actual values. Lower is better.
2. **MAE (Mean Absolute Error):** Average absolute deviation. More robust to outliers than RMSE.
3. **Pearson Correlation (r):** Linear relationship between predicted and actual. Range [-1, 1], higher is better.
4. **Spearman Correlation (ρ):** Monotonic relationship (rank correlation). Better for non-linear but monotonic relationships.

**For Classification (discrete readability levels):**
1. **Accuracy:** Percentage of correctly classified instances
2. **F1-Score:** Harmonic mean of precision and recall (weighted or macro-averaged for multi-class)
3. **Quadratic Weighted Kappa (QWK):** Agreement metric that penalizes larger disagreements more heavily. Appropriate for ordinal readability levels.

**Interpretation Guidelines:**
- **Pearson correlation:**
  - 0.9-1.0: Very high correlation
  - 0.7-0.9: High correlation
  - 0.5-0.7: Moderate correlation
  - <0.5: Low correlation

- **RMSE Interpretation:**
  - <0.5: Excellent (average error < half a grade level)
  - 0.5-1.0: Good
  - >1.0: Moderate to poor

#### 3.2 Evaluation Protocols [12][13][19]

**Cross-Validation:**
- **10-fold cross-validation:** Standard for smaller datasets
- **Stratified sampling:** Maintain grade level distribution in each fold
- **Stratified by text:** For datasets with multiple sentences per text (e.g., OSE), keep all sentences from same text in same fold to prevent data leakage

**Train/Dev/Test Split:**
- Common split: 8:1:1 for training, development, testing
- Ensure no overlapping texts between splits
- For pairwise comparison datasets (e.g., CLEAR), ensure no rater overlap

**Reported Metrics:**
- Always report at least: RMSE, Pearson r, Spearman ρ
- For classification: Accuracy, F1 (specify weighted/macro/micro), QWK
- Include confidence intervals or standard deviation across folds

### 4. Standard Datasets

#### 4.1 OneStopEnglish (OSE) [9]
- **Size:** 189 texts × 3 versions = 567 texts total
- **Sentences:** 4,890 sentences
- **Vocabulary:** 17,818 types
- **Levels:** 3 levels (Beginner, Intermediate, Advanced) for adult ESL learners
- **Source:** MacMillan Education website
- **Access:** https://github.com/nishkalavallabhi/OneStopEnglishCorpus (CC BY-SA 4.0 license)
- **Characteristics:** Parallel texts (same content at different readability levels); valuable for text simplification research

#### 4.2 Weebit [10][19]
- **Size:** 3,125 texts (625 per level)
- **Levels:** 5 levels (Level 2, Level 3, Level 4, KS3, GCSE) corresponding to ages 7-16
- **Sources:** WeeklyReader (educational magazine) + BBC Bitesize
- **Characteristics:** Graded reading material; covers fiction and non-fiction
- **Access:** Contact authors (copyright restrictions may apply)
- **Benchmark Results:** All features: Pearson r = 0.92, RMSE = 0.54

#### 4.3 CLEAR Corpus (CommonLit Ease of Readability) [11]
- **Size:** ~5,000 text excerpts
- **Grade Range:** 3rd-12th grade (U.S.)
- **Source:** CommonLit + Project Gutenberg + Wikipedia + open digital libraries
- **Excerpt Length:** 140-200 words
- **Rating Method:** Pairwise comparisons by ~1,116 teachers (111,347 judgments)
- **Scoring:** Bradley-Terry model for pairwise rankings
- **Access:** https://github.com/scrossey/CLEAR-Corpus or Kaggle CommonLit Readability Prize
- **Characteristics:** Teacher ratings (not formula-based); covers 250+ years of writing; informational and literature genres

#### 4.4 Newsela [23]
- **Size:** 10,787 news articles (1,911 original + 4 simplified versions each = 5 levels)
- **Levels:** 5 levels (aligned with Lexile scores)
- **Source:** Newsela.com (educational platform)
- **Access:** Request at https://newsela.com/legal/data (for researchers)
- **Characteristics:** Professionally produced simplifications; same content at multiple levels

#### 4.5 WSJ (Wall Street Journal) [6][21]
- **Size:** 1,200 sentences (650 with high agreement)
- **Levels:** 7 levels (1 = "very easy" to 7 = "very difficult")
- **Raters:** 20 native speakers per sentence (majority agreement ≥ 14/20)
- **Source:** Wall Street Journal corpus
- **Access:** Contact authors (Brunato et al., 2018)
- **Characteristics:** Sentence-level annotations; valuable for sentence readability research

### 5. Benchmark Results

#### 5.1 Passage-Level Readability Assessment

**Weebit Dataset (5-level classification) [19]:**
| Method | Features | Pearson r | RMSE |
|--------|----------|-----------|------|
| Linear Regression | All (42) | 0.92 | 0.54 |
| Linear Regression | Syntax-only (25) | 0.88 | 0.64 |
| Linear Regression | Lexical-only (17) | 0.84 | 0.78 |
| Linear Regression | Traditional-only (3) | 0.66 | 1.06 |
| Linear Regression | No Traditional (37) | 0.89 | 0.63 |

**OneStopEnglish Dataset (3-level classification) [5][6]:**
| Method | F1 Score | Accuracy |
|--------|----------|----------|
| BERT-FP-LBL (Li et al., 2022) | 99.41% | - |
| Hybrid (Hard Label) on BART-large | - | 72.9% (WSJ) |
| XGBoost (linguistic features) | 73.2% | - |
| BART-large (neural-only) | - | 67.9% (WSJ) |

**CLEAR Dataset (regression) [22]:**
| Method | R² | RMSE |
|--------|-----|------|
| Graph-based (GCN + BERT) | 0.9729 | - |
| Traditional formulas | <0.5 | >1.0 |

#### 5.2 Sentence-Level Readability Assessment

**WSJ Dataset (7-level classification) [21]:**
| Method | Accuracy | F1 | QWK |
|--------|----------|-----|-----|
| Hybrid (Hard Label) | 0.729 | 0.707 | 0.767 |
| BART-large (neural) | 0.679 | 0.611 | 0.661 |
| XGBoost (linguistic) | 0.618 | 0.549 | 0.616 |

**OneStopEnglish Dataset (3-level sentence classification) [21]:**
| Method | Accuracy | F1 | QWK |
|--------|----------|-----|-----|
| Hybrid (Soft Label) | 0.581 | 0.564 | 0.560 |
| BART-large (neural) | 0.571 | 0.558 | 0.549 |
| XGBoost (linguistic) | 0.451 | 0.428 | 0.288 |

### 6. Recommended Evaluation Protocol for Percolation Threshold Model

#### 6.1 Datasets to Use (in order of priority)

**Primary Evaluation:**
1. **CLEAR Corpus:** Large, teacher-rated, regression-based evaluation (best for continuous scores)
2. **OneStopEnglish:** Standard benchmark, 3 levels, public access
3. **Weebit:** 5 levels, widely cited, good for classification

**Secondary Evaluation** (if applicable):
4. **WSJ:** For sentence-level evaluation
5. **Newsela:** For text simplification applications

#### 6.2 Metrics to Report

**For regression** (continuous readability scores):
- RMSE (primary), MAE (secondary)
- Pearson correlation r, Spearman correlation ρ
- R² (coefficient of determination)

**For classification** (discrete levels):
- Accuracy, Weighted F1-score, QWK
- Confusion matrix (to see which levels are confused)

#### 6.3 Baselines to Compare

1. **Traditional Formulas** (must include):
   - Flesch-Kincaid Grade Level
   - Dale-Chall (if word list accessible)
   - SMOG (if texts have ≥30 sentences)
   - ARI

2. **ML Baselines:**
   - Feature-based: Random Forest or XGBoost with standard linguistic features (use LingFeat or similar)
   - Neural baseline: BERT-base or RoBERTa-base (fine-tuned)

3. **SOTA Comparison:**
   - Hybrid models (BERT + linguistic features)
   - Graph-based models (if applying to appropriate datasets)

#### 6.4 Evaluation Protocol

1. **Data Splits:**
   - 10-fold stratified cross-validation (standard)
   - For OSE: Stratify by text (not sentence) to prevent data leakage
   - Report mean and standard deviation across folds

2. **Preprocessing:**
   - Use standard tokenization (NLTK or spaCy)
   - For BERT-based models: Use standard tokenization and max length truncation
   - For graph-based: Use dependency parser (Berkeley Parser or similar)

3. **Hyperparameter Tuning:**
   - Use development set or inner cross-validation loop
   - For BERT: Tune learning rate (1e-5 to 5e-5), batch size (16-32), epochs (3-10)
   - For graph models: Tune GCN layers (2-4), hidden dimensions, dropout

4. **Statistical Significance:**
   - Use McNemar's test for classification, paired t-test for regression
   - Report p-values for comparisons

### 7. Gaps and Opportunities for Percolation Threshold Model

#### 7.1 What Existing Methods Miss [25]

1. **Dynamic comprehension process:** Traditional and even ML methods treat readability as static property of text, not as dynamic process of comprehension.
2. **Cohesion modeling:** While some methods use Cohesion metrics (CohMetrix), few explicitly model cohesion *network* structure.
3. **Physical interpretability:** Neural models are black boxes; traditional formulas have shallow interpretability.
4. **Cross-lingual generalization:** Most methods are English-only; cross-lingual approaches need improvement.

#### 7.2 Opportunities for Novelty

1. **Percolation threshold** as readability measure:
   - Models reading comprehension as percolation process through cohesion network
   - Provides *physical interpretability* (threshold has meaning: fraction of text understood)
   - Can model *dynamic comprehension* (gradual understanding vs. binary classification)

2. **Cohesion network construction:**
   - Explicitly models entity and concept links (coreference, lexical overlap, semantic similarity)
   - Edge weights based on linguistic features (not just binary connections)
   - Can incorporate syntax, semantics, discourse in unified framework

3. **Evaluation scenarios where existing methods struggle:**
   - **Noisy texts** (Web, social media): Percolation may be more robust
   - **Low-resource languages:** Network construction may require fewer NLP tools than full parsing
   - **Explainable AI:** Threshold provides interpretable readability score

### 8. Confidence and Limitations

**Confidence Level:** HIGH for traditional formulas and standard datasets; MODERATE for benchmark results (some papers report on different dataset versions or preprocessing).

**Limitations of this Research:**
1. Could not access some papers behind paywalls (e.g., IEEE, some ACM)
2. Benchmark results extracted from papers may use different preprocessing or evaluation protocols
3. Recent papers (2024-2026) may have additional results not captured in this review

**What Would Change Confidence:**
1. Access to full papers for exact numbers and methodology details
2. Replication of benchmark results on standard datasets
3. Expert review by readability assessment researchers

## Sources

[1] [Flesch–Kincaid readability tests - Wikipedia](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests) — Provides the Flesch-Kincaid Grade Level formula: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59, and its limitations.

[2] [Dale-Chall Readability Formula: How It Works and When to Use It](https://clickhelp.com/clickhelp-technical-writing-blog/dale-chall-readability-formula-how-it-works-and-when-to-use-it/) — Provides the Dale-Chall formula: Raw Score = 0.1579*(PDW) + 0.0496*(ASL), with +3.6365 adjustment if PDW > 5%. Explains difficult word definition.

[3] [SMOG - Wikipedia](https://en.wikipedia.org/wiki/SMOG) — Provides the SMOG formula: 1.0430*sqrt(polysyllables*30/sentences) + 3.1291. Notes 0.985 correlation with comprehension and 1.5159 standard error.

[4] [Automated readability index - Wikipedia](https://en.wikipedia.org/wiki/Automated_readability_index) — Provides the ARI formula: 4.71*(characters/words) + 0.5*(words/sentences) - 21.43. Explains character-based approach.

[5] [BERT Embeddings for Automatic Readability Assessment (Imperial, 2021)](https://aclanthology.org/2021.ranlp-1.69.pdf) — Proposes combining BERT embeddings with handcrafted linguistic features. Achieves 0.732 F1 on OSE, 0.893 F1 on CCE with combined features.

[6] [Hybrid Models for Sentence Readability Assessment (Liu & Lee, 2023)](https://aclanthology.org/2023.bea-1.37.pdf) — First study on hybrid models for sentence-level ARA. Hybrid (Hard Label) achieves 0.729 accuracy on WSJ (13% improvement over SOTA).

[7] [Computational Assessment of Text Readability: A Survey of Current and Future Research (Collins-Thompson, 2014)](http://www-personal.umich.edu/~kevynct/pubs/ITL-readability-invited-article-v10-camera.pdf) — Comprehensive survey covering traditional formulas, ML approaches, evaluation metrics (RMSE, Pearson r), and limitations of surface-level features.

[8] [OneStopEnglish corpus: A new corpus for automatic readability assessment and text simplification (Vajjala & Lučić, 2018)](https://aclanthology.org/W18-0535/) — Introduces OSE corpus: 189 texts in 3 versions (567 total) for adult ESL learners. Freely available under CC BY-SA 4.0 license.

[9] [OneStopEnglish Corpus PDF (Vajjala & Lučić, 2018)](https://aclanthology.org/W18-0535.pdf) — Details OSE corpus statistics: 567 texts, 4,890 sentences, 17,818 vocabulary types. Three reading levels for adult ESL.

[10] [On The Applicability of Readability Models to Web Texts (Vajjala & Meurers, 2013)](https://aclanthology.org/W13-2907.pdf) — Introduces Weebit corpus (3,125 texts, 5 levels). Reports benchmark: Pearson r=0.92, RMSE=0.54 with all features on Weebit.

[11] [The CommonLit Ease of Readability (CLEAR) Corpus (Crossley et al., 2021)](https://educationaldatamining.org/EDM2021/virtual/static/pdf/EDM21_paper_35.pdf) — Introduces CLEAR corpus: ~5,000 excerpts, teacher ratings via pairwise comparisons, Bradley-Terry scoring. Covers grades 3-12.

[12] [On The Applicability of Readability Models to Web Texts - Evaluation Protocol Section](https://aclanthology.org/W13-2907.pdf) — Describes 10-fold cross-validation protocol, Pearson correlation and RMSE as evaluation metrics for regression-based readability.

[13] [Hybrid Models for Sentence Readability Assessment - Experiments Section](https://aclanthology.org/2023.bea-1.37.pdf) — Describes stratified 10-fold cross-validation, 8:1:1 train/dev/test split, metrics (accuracy, F1, QWK) for sentence-level ARA.

[14] [Tip 6. Use Caution With Readability Formulas for Quality Reports (AHRQ)](https://www.ahrq.gov/talkingquality/resources/writing/tip6.html) — Documents limitations of traditional readability formulas: ignore comprehension, cohesion, reader factors; unreliable for short texts.

[15] [The Original Dale-Chall Readability Formula](https://readabilityformulas.com/the-original-dale-chall-readability-formula/) — Explains Dale-Chall formula coefficients and the 3.6365 adjustment factor for texts with >5% difficult words.

[16] [SMOG Grading — a New Readability Formula (McLaughlin, 1969)](https://ogg.osu.edu/media/documents/health_lit/WRRSMOG_Readability_Formula_G._Harry_McLaughlin__1969_.pdf) — Original SMOG paper establishing 0.985 correlation with comprehension and 1.5159 standard error of estimate.

[17] [Readability formulas have even more limitations than Klare (Redish, 2000)](https://redish.net/wp-content/uploads/Redish_on_Readability_Formulas.pdf) — Comprehensive critique of readability formulas: ignore many factors contributing to reading ease, no theoretical basis.

[18] [Readability: An appraisal of research and application (Chall, 1958)](https://books.google.com/books/about/Readability.html?id=2nbuAAAAMAAJ) — Foundational work establishing that vocabulary difficulty accounts for ~80% of variability explained by readability scores.

[19] [On The Applicability of Readability Models to Web Texts - Results Section](https://aclanthology.org/W13-2907.pdf) — Detailed benchmark results on Weebit: all features achieve 0.92 Pearson correlation and 0.54 RMSE; syntax-only 0.88/0.64; lexical-only 0.84/0.78.

[20] [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (Devlin et al., 2019)](https://arxiv.org/pdf/1810.04805.pdf) — Original BERT paper that enabled BERT-based readability assessment approaches.

[21] [Hybrid Models for Sentence Readability Assessment - Results](https://aclanthology.org/2023.bea-1.37.pdf) — Comprehensive benchmark results for sentence-level ARA: WSJ (0.729 accuracy with Hybrid), OSE (0.581 with Hybrid Soft Label).

[22] [Automatic text readability assessment for educational content based on graph representation learning (Zhang et al., 2026)](https://www.nature.com/articles/s41598-026-41313-9) — Proposes graph-based readability assessment using GCN and POS-informed graph construction. Achieves R²=0.9729 on CLEAR dataset.

[23] [Text Simplification from Professionally Produced Corpora (Scarton & Specia, 2018)](http://www.lrec-conf.org/proceedings/lrec2018/pdf/1063.pdf) — Introduces Newsela corpus: 10,787 news articles with 5 difficulty levels produced by professionals.

[24] [Evaluating the Evaluators: Are readability metrics good measures of readability? (Cachola et al., 2025)](https://aclanthology.org/2025.emnlp-main.1225/) — Finds traditional readability metrics have poor correlation (<0.3 Pearson) with human judgments, including FKGL.

[25] [Trends, limitations and open challenges in automatic readability assessment research (Vajjala, 2022)](https://aclanthology.org/2022.lrec-1.536.pdf) — Surveys open challenges including need for dynamic comprehension modeling, cross-lingual approaches, and interpretable models.

## Follow-up Questions

- How does the percolation threshold model's performance compare to hybrid BERT-based models when evaluated on the CLEAR dataset with RMSE and Pearson correlation metrics?
- What are the most effective methods for constructing cohesion networks from text (e.g., coreference resolution, lexical overlap, semantic similarity) and how do different construction methods affect readability prediction accuracy?
- Can the percolation threshold model provide interpretable readability scores that correlate with human judgments better than traditional formulas, particularly for noisy texts like Web pages or social media posts?

---
*Generated by AI Inventor Pipeline*
