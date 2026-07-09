# gen_strat_1 — test_idea

> Phase: `invention_loop` · round 1 · `gen_strat`
> Run: `run_LOb33NvVGQcB` — Readability Scoring Method
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_strat_1` (sdk_openhands_agent)

### [1] SYSTEM-USER prompt · 2026-07-08 22:28:10 UTC

````
<hypothesis>
Your strategy should advance this hypothesis.

kind: hypothesis
title: Percolation Threshold Readability Model
hypothesis: >-
  Text readability can be quantified as the percolation threshold of a cohesion network constructed from the text. As a reader
  processes a text, they build a mental network where sentences/concepts are nodes and cohesion links (lexical overlap, semantic
  similarity, referential ties) are edges. Readability equals the critical fraction of cohesion links needed for a giant connected
  component to emerge in this network. Texts with low percolation thresholds are easy to read because concepts integrate quickly;
  texts with high thresholds are hard because concepts remain fragmented until late in processing.
motivation: >-
  Current readability formulas (Flesch-Kincaid, BERT-based models) measure surface features or use black-box predictions,
  but they don't model the underlying cognitive process of how readers integrate information. Percolation theory from statistical
  physics provides a natural model: reading comprehension is the process of building a connected mental model. The percolation
  threshold precisely captures how easily this model integrates. This gives a physically interpretable readability metric
  grounded in how the brain actually processes cohesive text.
assumptions:
- >-
  Reader comprehension involves building a connected mental network of concepts from the text
- >-
  Cohesion links (lexical overlap, semantic similarity, reference) correspond to edges in the reader's mental network
- >-
  The ease of comprehension correlates with how quickly the mental network percolates (forms a giant component)
- >-
  The percolation threshold of the text's cohesion network is a measurable proxy for this cognitive integration difficulty
investigation_approach: >-
  1. Construct cohesion networks from English texts: nodes = sentences, edges = cosine similarity of sentence embeddings (SBERT)
  + lexical overlap. 2. Compute percolation threshold by simulating edge addition in random order and measuring when giant
  component emerges (reaches 50% of nodes). 3. Compare percolation threshold against gold-standard readability scores (Flesch-Kincaid,
  human ratings from Newsela/OneStopEnglish datasets). 4. Test whether percolation threshold predicts reading comprehension
  scores better than traditional formulas. 5. Ablate: test with/without semantic edges to isolate effect of cohesion vs. just
  lexical overlap.
success_criteria: >-
  1. Percolation threshold should correlate negatively with established readability scores (easy texts have low thresholds).
  2. Percolation threshold should explain variance in human readability ratings beyond traditional formulas (significant delta
  R²). 3. On sentence-level readability datasets (Weebit, Newsela), percolation threshold should achieve RMSE < 1.5 grade
  levels when used as a feature in a simple linear model. 4. The method should be robust: threshold should be similar across
  multiple random edge-ordering runs (std < 0.05).
related_works:
- >-
  Zhang et al. (2026) 'Automatic text readability assessment for educational content based on graph representation learning'
  (Scientific Reports) - Uses Graph Convolutional Networks on POS-based dependency graphs. Our approach differs fundamentally:
  we use percolation theory to model the DYNAMIC process of comprehension (when does the mental model connect?) rather than
  static graph classification. GCNs learn to predict readability from graph structure; we derive an interpretable physical
  parameter (percolation threshold) that directly models cognitive integration.
- >-
  Ehret (2018) 'Kolmogorov complexity as a universal measure of language complexity' - Uses compression-based complexity.
  Our approach differs: we model TEXT AS A NETWORK and measure connectivity emergence, not information density. Kolmogorov
  complexity captures overall difficulty; percolation threshold captures specifically how fragmented vs. integrated the text
  feels.
- >-
  Cohen et al. on semantic network percolation (creativity research) - Uses k-clique percolation to measure flexibility of
  free association networks. Our work adapts percolation theory to a completely different domain (readability assessment)
  with a different network construction (text cohesion vs. free association) and a different research question (predicting
  readability vs. measuring creativity).
inspiration: >-
  Percolation theory from statistical physics (studying phase transitions in networks) crossed with discourse cohesion theory
  from linguistics. In physics, percolation threshold predicts when a material becomes conductive; in reading, we hypothesize
  it predicts when a text becomes 'comprehensible' (when the reader's mental model forms a connected whole). The key cross-domain
  insight: readability is not a static property of text but emerges from a phase transition in the reader's mental network.
terms:
- term: Percolation threshold
  definition: >-
    In network science, the critical fraction of edges that must be present before a giant connected component emerges spanning
    a significant portion of the network
- term: Cohesion network
  definition: >-
    A graph representation of text where nodes represent sentences or concepts, and edges represent cohesive ties such as
    lexical overlap, semantic similarity, or referential connections
- term: Giant connected component
  definition: >-
    A subgraph that contains a large fraction of all nodes in the network and in which any two nodes are connected by a path
- term: Phase transition
  definition: >-
    In statistical physics, a point at which a system undergoes a qualitative change in behavior (e.g., from disconnected
    to connected) as a parameter crosses a critical threshold
- term: SBERT
  definition: >-
    Sentence-BERT: a modification of BERT that uses siamese/triplet networks to produce semantically meaningful sentence embeddings
    for measuring similarity
summary: >-
  We propose that text readability equals the percolation threshold of the text's cohesion network. Easy texts have low thresholds
  (concepts connect quickly into a coherent mental model); hard texts have high thresholds (concepts remain fragmented). This
  provides a physically interpretable readability metric based on network science.
</hypothesis>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. Use it for study design, proper baselines, and the evaluation/validity norms this field demands.

- **aii-handbook-multi-llm-agents** — Guide for implementing Multi-LLM Agent Systems research using Mirascope orchestration, HuggingFace datasets/evaluation, and proven multi-agent patterns.
</available_domain_handbooks>

<iteration_status>
Current iteration: 1 of 2
Remaining (including this one): 2
</iteration_status>

<previous_strategies>
No previous strategies exist. This is the FIRST iteration.
</previous_strategies>

<dependency_rules>
- depends_on is a list of objects {id, label} — each entry references an existing artifact and tags how it is being used
- "id" can ONLY reference IDs from <existing_artifacts> — never IDs you are proposing (all new artifacts run in parallel)
- "label" is a SHORT free-text type label (a word or two, NOT a sentence) describing what role the dep plays — e.g. "dataset", "validates", "extends", "supersedes". Required on every dep.
- Setting depends_on provides the dependency's out_dependency_files to your artifact at execution time
- If no suitable existing artifacts exist, use empty depends_on
- New artifact IDs are assigned by the system after submission — do not invent IDs for your proposed artifacts
</dependency_rules>

<available_artifact_types>
Artifact types you can plan. Use this to choose the right types for your strategy objectives.

<artifact_types>
RESEARCH
Web research to answer key questions — like a researcher making decisions.
Runtime: LLM Agent, no code execution.
Tools: the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text).
Capabilities: Find, synthesize, and compare information across sources; survey SOTA and best practices.
Deps: REQUIRED none | OPTIONAL other RESEARCH to build on prior findings

EXPERIMENT
Run code to test hypotheses, implement methods, and collect empirical results.
Runtime: Python 3.12, UV (any pip package), isolated workspace, gradual scaling (mini → full data).
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-json (schema validation), aii-openrouter-llms (call any LLM — GPT, Gemini, Llama, etc.), domain-specific as needed.
Capabilities: Implement and run any code-based experiment, compare method vs baselines.
Deps: REQUIRED at least one DATASET | OPTIONAL RESEARCH for methodology guidance

DATASET
Collect, prepare, and merge datasets for experiments and analysis.
Runtime: Python 3.12, UV, isolated workspace.
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-hf-datasets (HuggingFace Hub — ML datasets, many UCI/OpenML/Kaggle mirrors), aii-owid-datasets (Our World in Data — global statistics), aii-json (schema validation). Also any Python source (sklearn.datasets, openml, direct URLs, APIs) — must verify within 300MB limit.
Capabilities: Search, acquire, transform, combine, and standardize data from any available source.
Deps: REQUIRED none | OPTIONAL RESEARCH for guidance on what data to collect

EVALUATION
Evaluate experiment results with metrics, statistical analysis, and validity checks.
Runtime: Python 3.12, UV (any evaluation library), isolated workspace, gradual scaling matching experiment.
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-json (schema validation), aii-openrouter-llms (call any LLM — GPT, Gemini, Llama, etc.), domain-specific as needed.
Capabilities: Compute any quantitative metrics and statistical tests, analyze validity and robustness.
Deps: REQUIRED at least one EXPERIMENT | OPTIONAL DATASET if reference data needed

PROOF
Formally prove mathematical statements in Lean 4 with automated iteration.
Runtime: LLM agent with Lean 4 compiler feedback loop.
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-lean (proof verification, Mathlib search, tactics: ring, linarith, nlinarith, omega, simp, etc.)
Capabilities: Formally verify properties and inequalities, iterative proof development, lemma decomposition.
Deps: REQUIRED none | OPTIONAL RESEARCH for mathematical background
</artifact_types>
</available_artifact_types>

<artifact_executor_scope>
IMPORTANT: Each artifact executor has a focused prompt that guides it to do ONE thing well. It will NOT perform tasks outside its scope — assigning the wrong work to the wrong artifact type wastes an iteration. Match the task to the right executor.

RESEARCH executor scope:
  Output: research_out.json with {answer, sources, follow_up_questions} + research_report.md
  DOES: Web research — search, read, synthesize information from papers/docs/APIs into a structured report
  DOES NOT: Run code, download files, execute scripts, compute anything — no shell/Python access
  Use for literature surveys, API documentation, technical specifications — pure information gathering

EXPERIMENT executor scope:
  Output: method_out.json with results (metrics, predictions, analysis) — the core computational work
  DOES: Implement and run methods/algorithms, compute metrics, compare approaches, produce quantitative results
  DOES NOT: Collect new datasets (depends on DATASET artifacts for input data), write formal proofs
  This is the right artifact for any code that processes data and produces results

DATASET executor scope:
  Output: data_out.json with rows of {input, output, metadata_fold, ...} — raw data only, no derived computations
  DOES: Download/generate datasets, analyze candidates to pick the best ones, standardize to JSON schema (features, labels, folds, metadata), validate schema, split into full/mini/preview
  DOES NOT: Run experiments, train models, compute derived statistics (PID/MI/correlations/synergy matrices) as final output
  If you need to COMPUTE something from data (synergy matrices, MI scores, timing benchmarks), use an EXPERIMENT artifact instead

EVALUATION executor scope:
  Output: eval_out.json with evaluation results
  DOES: Any evaluation of experiment results — metrics, statistical tests, ablations, comparisons, visualizations, robustness checks, error analysis, etc.
  DOES NOT: Implement new methods (use EXPERIMENT), collect data (use DATASET)
  This is for analyzing experiment outputs from any angle

PROOF executor scope:
  Output: Lean 4 proof files (.lean) with verified theorems
  DOES: Write and verify Lean 4 formal proofs with Mathlib, iterative compilation
  DOES NOT: Run Python experiments, collect data, do empirical analysis
  Use only when formal mathematical guarantees are needed
</artifact_executor_scope>

<artifact_planning_rules>
RESEARCH: Plan early — findings guide dataset selection, experiment design, and methodology.
EXPERIMENT: Must depend on at least one DATASET. Define clear metrics and baselines before running. Consider trying multiple method variations rather than a single approach.
DATASET:
- Plan for REAL third-party datasets (HuggingFace, Kaggle, direct-download URLs) — downloadable within time and size constraints
- Describe dataset criteria (domain, size, format) — executors find exact sources, but you can suggest candidates or search directions
- ALWAYS prefer real datasets over synthetic. Synthetic is a LAST RESORT only when no suitable real data exists
EVALUATION: Must depend on at least one EXPERIMENT. Focus on statistical rigor and validity checks.
PROOF: Use only when the hypothesis requires formal mathematical guarantees. Lean 4 + Mathlib.
</artifact_planning_rules>

<existing_artifacts>
None yet (first iteration).
</existing_artifacts>





<task>
Generate 1 research strategy for THIS iteration.

**ARTIFACT LIMIT: Each strategy may contain AT MOST 3 artifact directions.** Focus on the highest-impact artifacts. Quality over quantity.

Each strategy should:
1. Define a clear OBJECTIVE - what novel contribution we're building toward
2. Plan artifacts to execute NOW - specify type, objective, approach, and depends_on for each
3. Account for parallel execution - all strategies and all planned artifacts run simultaneously, their artifacts are combined into one shared pool


</task><user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_LOb33NvVGQcB/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>

---

Output the result as JSON to: `/ai-inventor/aii_data/runs/run_LOb33NvVGQcB/3_invention_loop/iter_1/gen_strat/gen_strat_1/.sdk_openhands_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "ArtifactDep": {
      "description": "A single dependency on an existing artifact, with a short type label.\n\n``id`` and ``label`` are LLM-generated at strategy time. ``label`` is free-text but\nshort \u2014 a word or two naming the type of dependency, not a sentence.\n\n``relation_type`` and ``relation_rationale`` are populated later, in upd_hypo,\nusing the MultiCite citation-function typology (Lauscher et al., NAACL 2022).\nThey are absent at strategy time and may stay absent for legacy runs.",
      "properties": {
        "id": {
          "description": "ID of an existing artifact this artifact depends on",
          "title": "Id",
          "type": "string"
        },
        "label": {
          "description": "Short free-text label naming the type of this dependency (a word or two, not a sentence)",
          "title": "Label",
          "type": "string"
        }
      },
      "required": [
        "id",
        "label"
      ],
      "title": "ArtifactDep",
      "type": "object"
    },
    "ArtifactDirection": {
      "description": "High-level direction for an artifact to execute this iteration.\n\nID is code-assigned (LLMPrompt only \u2014 visible in prompts, not LLM-generated).",
      "properties": {
        "type": {
          "description": "Type of artifact to create",
          "enum": [
            "experiment",
            "research",
            "proof",
            "evaluation",
            "dataset"
          ],
          "title": "Type",
          "type": "string"
        },
        "objective": {
          "description": "What we want to achieve with this artifact",
          "title": "Objective",
          "type": "string"
        },
        "approach": {
          "description": "High-level direction/method",
          "title": "Approach",
          "type": "string"
        },
        "depends_on": {
          "description": "Existing artifacts this depends on, each with a short type label",
          "items": {
            "$ref": "#/$defs/ArtifactDep"
          },
          "title": "Depends On",
          "type": "array"
        }
      },
      "required": [
        "type",
        "objective",
        "approach"
      ],
      "title": "ArtifactDirection",
      "type": "object"
    },
    "Strategy": {
      "description": "A research strategy.\n\nContent fields have LLMPrompt + LLMStructOut markers.\n``id`` is code-assigned (LLMPrompt only \u2014 visible in prompts, not LLM-generated).\n\nID format: gen_strat_idx{N}",
      "properties": {
        "title": {
          "description": "Strategy name in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters).",
          "title": "Title",
          "type": "string"
        },
        "objective": {
          "description": "The novel contribution we're building toward",
          "title": "Objective",
          "type": "string"
        },
        "rationale": {
          "description": "Why this strategy is promising",
          "title": "Rationale",
          "type": "string"
        },
        "artifact_directions": {
          "description": "Artifacts to execute THIS iteration",
          "items": {
            "$ref": "#/$defs/ArtifactDirection"
          },
          "title": "Artifact Directions",
          "type": "array"
        },
        "expected_outcome": {
          "description": "What we'll have after this iteration's artifacts complete",
          "title": "Expected Outcome",
          "type": "string"
        },
        "summary": {
          "default": "",
          "description": "Brief summary of the strategy and its expected contribution",
          "title": "Summary",
          "type": "string"
        }
      },
      "required": [
        "title",
        "objective",
        "rationale",
        "artifact_directions",
        "expected_outcome"
      ],
      "title": "Strategy",
      "type": "object"
    }
  },
  "description": "Top-level wrapper for LLM strategy generation output.",
  "properties": {
    "strategies": {
      "description": "List of generated strategies",
      "items": {
        "$ref": "#/$defs/Strategy"
      },
      "title": "Strategies",
      "type": "array"
    }
  },
  "required": [
    "strategies"
  ],
  "title": "Strategies",
  "type": "object"
}
```

IMPORTANT: This task is NOT complete until you Write `/ai-inventor/aii_data/runs/run_LOb33NvVGQcB/3_invention_loop/iter_1/gen_strat/gen_strat_1/.sdk_openhands_agent_struct_out.json`.
````

### [2] HUMAN-USER prompt · 2026-07-08 22:28:10 UTC

```
Propose a simple, novel machine-learning method for scoring text readability and validate it.
```
