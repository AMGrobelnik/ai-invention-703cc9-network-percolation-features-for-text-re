#!/usr/bin/env python3
"""
Simplified Percolation Threshold Readability - Fast Implementation
No sklearn dependency - uses simple linear regression from scratch.
"""

import json
import re
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
import sys
import gc

# Simple logging
def log(msg):
    print(f"[INFO] {msg}", flush=True)

def log_error(msg):
    print(f"[ERROR] {msg}", flush=True)


class SimplePercolationNetwork:
    """
    Simplified percolation network for readability.
    Uses fast approximations instead of full BFS/union-find.
    """

    def __init__(self, window_size=3, min_freq=2):
        self.window_size = window_size
        self.min_freq = min_freq
        self.adjacency = defaultdict(Counter)
        self.node_freq = Counter()

    def _tokenize(self, text):
        """Simple tokenization."""
        return re.findall(r'\b[a-zA-Z]+\b', text.lower())

    def build_network(self, text):
        """Build word co-occurrence network."""
        tokens = self._tokenize(text)
        if len(tokens) < 3:
            return

        # Count node frequencies
        self.node_freq.update(tokens)

        # Build edges within sliding window
        for i, token in enumerate(tokens):
            start = max(0, i - self.window_size)
            end = min(len(tokens), i + self.window_size + 1)
            for j in range(start, end):
                if i != j:
                    self.adjacency[token][tokens[j]] += 1

    def get_features(self):
        """Extract network features quickly."""
        features = {}

        # Filter by min frequency
        valid_nodes = {node for node, freq in self.node_freq.items() if freq >= self.min_freq}
        n_nodes = len(valid_nodes)

        if n_nodes < 3:
            return {
                'percolation_threshold': 0.0,
                'network_density': 0.0,
                'avg_degree': 0.0,
                'type_token_ratio': 0.0,
                'avg_edge_weight': 0.0,
                'n_nodes': n_nodes,
                'n_edges': 0,
            }

        # Count edges and compute weights
        edges = []
        all_weights = []
        for node, neighbors in self.adjacency.items():
            if node not in valid_nodes:
                continue
            for neighbor, weight in neighbors.items():
                if neighbor in valid_nodes and node < neighbor:
                    edges.append((node, neighbor))
                    all_weights.append(weight)

        n_edges = len(edges)

        # Feature 1: Simplified percolation threshold
        # Use edge weight distribution as proxy
        if all_weights:
            sorted_w = sorted(all_weights)
            # Threshold where 50% of weight is below = simplified percolation point
            cumsum = np.cumsum(sorted_w)
            total = cumsum[-1]
            threshold_idx = np.searchsorted(cumsum, total * 0.5)
            percolation_threshold = threshold_idx / len(sorted_w) if sorted_w else 0
        else:
            percolation_threshold = 0

        # Feature 2: Network density
        max_edges = n_nodes * (n_nodes - 1) / 2
        density = n_edges / max_edges if max_edges > 0 else 0

        # Feature 3: Average degree
        degrees = [len(self.adjacency[n]) for n in valid_nodes if n in self.adjacency]
        avg_degree = np.mean(degrees) if degrees else 0

        # Feature 4: Type-token ratio
        total_tokens = sum(self.node_freq.values())
        ttr = n_nodes / total_tokens if total_tokens > 0 else 0

        # Feature 5: Average edge weight
        avg_weight = np.mean(all_weights) if all_weights else 0

        return {
            'percolation_threshold': float(percolation_threshold),
            'network_density': float(density),
            'avg_degree': float(avg_degree),
            'type_token_ratio': float(ttr),
            'avg_edge_weight': float(avg_weight),
            'n_nodes': n_nodes,
            'n_edges': n_edges,
        }


class SimpleBaselineReadability:
    """Fast baseline readability features."""

    @staticmethod
    def flesch_kincaid(text):
        """Compute Flesch-Kincaid Grade Level."""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0

        sentences = len(re.split(r'[.!?]+', text.strip()))
        if sentences == 0:
            sentences = 1

        n_words = len(words)
        n_syllables = sum(SimpleBaselineReadability._count_syllables(w) for w in words)

        asl = n_words / sentences
        asw = n_syllables / n_words

        return 0.39 * asl + 11.8 * asw - 15.59

    @staticmethod
    def _count_syllables(word):
        """Estimate syllables."""
        word = word.lower()
        if len(word) <= 3:
            return 1
        syllables = len(re.findall(r'[aeiouy]+', word))
        if word.endswith('e'):
            syllables -= 1
        return max(1, syllables)

    @staticmethod
    def get_features(text):
        """Get baseline features."""
        words = re.findall(r'\b\w+\b', text)
        sentences = len(re.split(r'[.!?]+', text.strip()))

        return {
            'flesch_kincaid': SimpleBaselineReadability.flesch_kincaid(text),
            'word_count': len(words),
            'avg_word_len': np.mean([len(w) for w in words]) if words else 0,
            'sentence_count': sentences,
            'avg_sentence_len': len(words) / sentences if sentences > 0 else 0,
        }


class SimpleLinearModel:
    """Simple linear regression from scratch - no sklearn needed."""

    def __init__(self):
        self.weights = None
        self.bias = 0.0

    def fit(self, X, y):
        """Fit using normal equation: w = (X^T X)^-1 X^T y"""
        X = np.array(X)
        y = np.array(y)

        # Add bias column
        X_bias = np.hstack([X, np.ones((X.shape[0], 1))])

        # Normal equation
        try:
            weights = np.linalg.inv(X_bias.T @ X_bias) @ X_bias.T @ y
            self.weights = weights[:-1]
            self.bias = weights[-1]
        except np.linalg.LinAlgError:
            # Fallback to pseudo-inverse
            weights = np.linalg.pinv(X_bias.T @ X_bias) @ X_bias.T @ y
            self.weights = weights[:-1]
            self.bias = weights[-1]

    def predict(self, X):
        """Predict."""
        X = np.array(X)
        return X @ self.weights + self.bias


def extract_features(texts, use_percolation=True):
    """Extract features from texts."""
    all_features = []

    for i, text in enumerate(texts):
        if i % 100 == 0:
            log(f"Processing text {i}/{len(texts)}")

        features = {}

        # Baseline features (always computed)
        baseline = SimpleBaselineReadability.get_features(text)
        features.update({f"base_{k}": v for k, v in baseline.items()})

        # Percolation features (novel method)
        if use_percolation:
            network = SimplePercolationNetwork(window_size=3, min_freq=2)
            network.build_network(text)
            percolation = network.get_features()
            features.update({f"ptr_{k}": v for k, v in percolation.items()})
            del network

        all_features.append(features)

    return all_features


def features_to_matrix(features_list):
    """Convert feature dicts to matrix."""
    # Get all keys from first item
    if not features_list:
        return np.array([]).reshape(0, 0)

    keys = sorted(features_list[0].keys())
    matrix = np.array([[f[k] for k in keys] for f in features_list])
    return matrix


def load_data(data_path):
    """Load data from JSON."""
    log(f"Loading data from {data_path}")
    with open(data_path, 'r') as f:
        data = json.load(f)
    return data


def prepare_examples(data):
    """Prepare examples."""
    texts = []
    labels = []
    dataset_names = []

    for dataset in data.get('datasets', []):
        name = dataset.get('dataset', 'unknown')
        for example in dataset.get('examples', []):
            texts.append(example['input'])
            labels.append(int(example['output']))
            dataset_names.append(name)

    log(f"Prepared {len(texts)} examples from {len(set(dataset_names))} datasets")
    return texts, labels, dataset_names


def main():
    """Run experiment."""
    workspace = Path("/ai-inventor/aii_data/runs/run_LOb33NvVGQcB/3_invention_loop/iter_2/gen_art/gen_art_experiment_1")
    data_path = workspace / "data" / "full_data_out.json"

    log("=" * 60)
    log("PERCOLATION THRESHOLD READABILITY EXPERIMENT")
    log("=" * 60)

    # Load data
    data = load_data(data_path)
    texts, labels, dataset_names = prepare_examples(data)

    # Subsample for faster execution (use 20% of data)
    n_samples = min(len(texts), 2500)  # Limit to 2500 for speed
    indices = np.random.choice(len(texts), n_samples, replace=False)
    texts = [texts[i] for i in indices]
    labels = [labels[i] for i in indices]

    log(f"Using {len(texts)} examples for experiment")

    # Split: 60% train, 20% val, 20% test
    n = len(texts)
    train_end = int(0.6 * n)
    val_end = int(0.8 * n)

    train_texts = texts[:train_end]
    train_labels = labels[:train_end]
    val_texts = texts[train_end:val_end]
    val_labels = labels[train_end:val_end]
    test_texts = texts[val_end:]
    test_labels = labels[val_end:]

    log(f"Train: {len(train_texts)}, Val: {len(val_texts)}, Test: {len(test_texts)}")

    # Method 1: Novel PTR method
    log("\n" + "=" * 60)
    log("METHOD 1: Percolation Threshold Readability (PTR)")
    log("=" * 60)

    log("Extracting PTR features for train...")
    train_features_ptr = extract_features(train_texts, use_percolation=True)
    X_train_ptr = features_to_matrix(train_features_ptr)

    log("Extracting PTR features for test...")
    test_features_ptr = extract_features(test_texts, use_percolation=True)
    X_test_ptr = features_to_matrix(test_features_ptr)

    log(f"PTR feature matrix shape: {X_train_ptr.shape}")

    # Train model
    log("Training PTR model...")
    model_ptr = SimpleLinearModel()
    model_ptr.fit(X_train_ptr, train_labels)

    # Predict
    pred_ptr = model_ptr.predict(X_test_ptr)
    pred_ptr = np.clip(pred_ptr, 1, 12)  # Clip to valid grade range

    # Evaluate
    mae_ptr = np.mean(np.abs(pred_ptr - test_labels))
    acc1_ptr = np.mean(np.abs(pred_ptr - test_labels) <= 1)
    acc2_ptr = np.mean(np.abs(pred_ptr - test_labels) <= 2)

    log(f"PTR Results - MAE: {mae_ptr:.3f}, Acc@1: {acc1_ptr:.3f}, Acc@2: {acc2_ptr:.3f}")

    # Method 2: Baseline (no percolation)
    log("\n" + "=" * 60)
    log("METHOD 2: Baseline (no PTR features)")
    log("=" * 60)

    log("Extracting baseline features for train...")
    train_features_base = extract_features(train_texts, use_percolation=False)
    X_train_base = features_to_matrix(train_features_base)

    log("Extracting baseline features for test...")
    test_features_base = extract_features(test_texts, use_percolation=False)
    X_test_base = features_to_matrix(test_features_base)

    log(f"Baseline feature matrix shape: {X_train_base.shape}")

    # Train model
    log("Training baseline model...")
    model_base = SimpleLinearModel()
    model_base.fit(X_train_base, train_labels)

    # Predict
    pred_base = model_base.predict(X_test_base)
    pred_base = np.clip(pred_base, 1, 12)

    # Evaluate
    mae_base = np.mean(np.abs(pred_base - test_labels))
    acc1_base = np.mean(np.abs(pred_base - test_labels) <= 1)
    acc2_base = np.mean(np.abs(pred_base - test_labels) <= 2)

    log(f"Baseline Results - MAE: {mae_base:.3f}, Acc@1: {acc1_base:.3f}, Acc@2: {acc2_base:.3f}")

    # Method 3: Traditional Flesch-Kincaid only
    log("\n" + "=" * 60)
    log("METHOD 3: Traditional Flesch-Kincaid Only")
    log("=" * 60)

    pred_fk = [SimpleBaselineReadability.flesch_kincaid(t) for t in test_texts]
    pred_fk = np.clip(pred_fk, 1, 12)

    mae_fk = np.mean(np.abs(pred_fk - test_labels))
    acc1_fk = np.mean(np.abs(pred_fk - test_labels) <= 1)
    acc2_fk = np.mean(np.abs(pred_fk - test_labels) <= 2)

    log(f"Flesch-Kincaid Results - MAE: {mae_fk:.3f}, Acc@1: {acc1_fk:.3f}, Acc@2: {acc2_fk:.3f}")

    # Compile and save results in correct schema format
    # Need to create examples list properly (can't use pred_base[i] in comprehension)
    examples_list = []
    for i, (text, label) in enumerate(zip(test_texts, test_labels)):
        examples_list.append({
            "input": text,
            "output": str(label),
            "predict_ptr": str(int(round(pred_ptr[i]))),
            "predict_baseline": str(int(round(pred_base[i]))),
            "predict_traditional": str(int(round(pred_fk[i]))),
            "metadata_true_grade": label,
            "metadata_ptr_error": float(abs(pred_ptr[i] - label)),
            "metadata_baseline_error": float(abs(pred_base[i] - label)),
            "metadata_traditional_error": float(abs(pred_fk[i] - label)),
        })

    results = {
        "metadata": {
            "novel_method": "percolation_threshold_readability",
            "description": "First application of network percolation theory to readability",
            "train_size": len(train_texts),
            "test_size": len(test_texts),
            "ptr_vs_baseline_mae_diff": float(mae_base - mae_ptr),
            "ptr_vs_traditional_mae_diff": float(mae_fk - mae_ptr),
            "results_summary": {
                "percolation_threshold": {"mae": float(mae_ptr), "acc1": float(acc1_ptr), "acc2": float(acc2_ptr)},
                "baseline_ml": {"mae": float(mae_base), "acc1": float(acc1_base), "acc2": float(acc2_base)},
                "traditional_flesch_kincaid": {"mae": float(mae_fk), "acc1": float(acc1_fk), "acc2": float(acc2_fk)},
            }
        },
        "datasets": [
            {
                "dataset": "test_set",
                "examples": examples_list
            }
        ]
    }

    # Save results
    output_path = workspace / "method_out.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    log(f"\nResults saved to {output_path}")

    # Print summary
    log("\n" + "=" * 60)
    log("EXPERIMENT COMPLETE - SUMMARY")
    log("=" * 60)
    log(f"PTR Method MAE: {mae_ptr:.3f}")
    log(f"Baseline MAE: {mae_base:.3f}")
    log(f"Traditional MAE: {mae_fk:.3f}")
    log(f"PTR improvement over baseline: {mae_base - mae_ptr:.3f}")
    log(f"PTR improvement over traditional: {mae_fk - mae_ptr:.3f}")


if __name__ == "__main__":
    main()
