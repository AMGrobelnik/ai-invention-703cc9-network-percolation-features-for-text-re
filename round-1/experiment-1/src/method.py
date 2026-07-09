#!/usr/bin/env python3
"""
Percolation Threshold Readability Model Experiment

Implements cohesion network construction from text using SBERT embeddings and lexical overlap,
computes percolation thresholds, and compares against traditional readability formulas.
"""

import sys
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np
import pandas as pd
from loguru import logger
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer
import textstat
import networkx as nx
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Optional imports with fallbacks
HAS_SBERT = False
try:
    from sentence_transformers import SentenceTransformer
    # Test if we can create a model (may download on first use)
    SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/tmp/sbert_cache')
    HAS_SBERT = True
    logger.info("SBERT is available")
except Exception as e:
    logger.warning(f"sentence-transformers not available: {e}, using TF-IDF fallback")
    HAS_SBERT = False

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")


# Download NLTK data if needed
for resource in ['tokenizers/punkt', 'corpora/stopwords', 'taggers/averaged_perceptron_tagger', 'corpora/wordnet']:
    try:
        nltk.data.find(resource)
    except LookupError:
        nltk.download(resource.split('/')[-1], quiet=True)


@dataclass
class TextData:
    """Container for text data with metadata."""
    text_id: str
    content: str
    grade_level: float
    metadata: Dict[str, Any]


class CohesionNetworkBuilder:
    """Builds cohesion networks from text using SBERT and lexical overlap."""
    
    def __init__(self, sbert_model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize with SBERT model and NLP tools."""
        if HAS_SBERT:
            logger.info(f"Loading SBERT model: {sbert_model_name}")
            self.sbert_model = SentenceTransformer(sbert_model_name)
        else:
            logger.warning("SBERT not available, will use TF-IDF fallback")
            self.sbert_model = None
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def segment_sentences(self, text: str) -> List[str]:
        """Segment text into sentences, filtering short ones."""
        sentences = sent_tokenize(text)
        filtered = [s.strip() for s in sentences if len(s.split()) >= 5]
        return filtered
    
    def compute_semantic_edges(self, sentences: List[str], threshold: float = 0.5) -> List[Tuple[int, int, float]]:
        """Compute semantic edges based on SBERT or TF-IDF cosine similarity."""
        if len(sentences) < 2:
            return []
        
        if self.sbert_model is not None:
            return self._compute_sbert_edges(sentences, threshold)
        else:
            return self._compute_tfidf_edges(sentences, threshold)
    
    def _compute_sbert_edges(self, sentences: List[str], threshold: float) -> List[Tuple[int, int, float]]:
        """Compute edges using SBERT embeddings."""
        embeddings = self.sbert_model.encode(sentences, show_progress_bar=False)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-8)
        similarity_matrix = np.dot(normalized, normalized.T)
        
        edges = []
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                if similarity_matrix[i, j] > threshold:
                    edges.append((i, j, float(similarity_matrix[i, j])))
        
        return edges
    
    def _compute_tfidf_edges(self, sentences: List[str], threshold: float) -> List[Tuple[int, int, float]]:
        """Compute edges using TF-IDF similarity as fallback."""
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(sentences)
            similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
            
            edges = []
            for i in range(len(sentences)):
                for j in range(i + 1, len(sentences)):
                    if similarity_matrix[i, j] > threshold:
                        edges.append((i, j, float(similarity_matrix[i, j])))
            
            return edges
        except Exception as e:
            logger.warning(f"TF-IDF fallback failed: {e}")
            return []
    
    def compute_lexical_edges(self, sentences: List[str], threshold: float = 0.3) -> List[Tuple[int, int, float]]:
        """Compute lexical overlap edges between sentences using NLTK."""
        edges = []
        
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                overlap = self._compute_lexical_overlap(sentences[i], sentences[j])
                if overlap > threshold:
                    edges.append((i, j, overlap))
        
        return edges
    
    def _compute_lexical_overlap(self, sent1: str, sent2: str) -> float:
        """Compute lexical overlap between two sentences using NLTK."""
        tokens1 = pos_tag(sent1.split())
        tokens2 = pos_tag(sent2.split())
        
        content_words1 = set()
        content_words2 = set()
        
        for word, tag in tokens1:
            if tag.startswith(('NN', 'VB', 'JJ')) and word.lower() not in self.stop_words:
                content_words1.add(self.lemmatizer.lemmatize(word.lower()))
        
        for word, tag in tokens2:
            if tag.startswith(('NN', 'VB', 'JJ')) and word.lower() not in self.stop_words:
                content_words2.add(self.lemmatizer.lemmatize(word.lower()))
        
        if len(content_words1) == 0 and len(content_words2) == 0:
            return 0.0
        
        intersection = len(content_words1.intersection(content_words2))
        union = len(content_words1.union(content_words2))
        
        return intersection / union if union > 0 else 0.0
    
    def build_network(self, text: str, 
                     sbert_threshold: float = 0.5,
                     lexical_threshold: float = 0.3) -> Tuple[nx.Graph, List[str]]:
        """Build cohesion network from text."""
        sentences = self.segment_sentences(text)
        
        if len(sentences) < 2:
            logger.warning(f"Too few sentences ({len(sentences)}), creating empty network")
            G = nx.Graph()
            G.add_nodes_from(range(len(sentences)))
            return G, sentences
        
        semantic_edges = self.compute_semantic_edges(sentences, sbert_threshold)
        lexical_edges = self.compute_lexical_edges(sentences, lexical_threshold)
        
        edge_dict = {}
        for i, j, weight in semantic_edges:
            edge_dict[(i, j)] = max(edge_dict.get((i, j), 0), weight)
        
        for i, j, weight in lexical_edges:
            edge_dict[(i, j)] = max(edge_dict.get((i, j), 0), weight)
        
        G = nx.Graph()
        G.add_nodes_from(range(len(sentences)))
        for (i, j), weight in edge_dict.items():
            G.add_edge(i, j, weight=weight)
        
        logger.info(f"Built network: {len(sentences)} nodes, {len(edge_dict)} edges")
        return G, sentences


class PercolationAnalyzer:
    """Computes percolation thresholds for networks."""
    
    def __init__(self, num_random_orderings: int = 50):
        self.num_random_orderings = num_random_orderings
    
    def compute_percolation_threshold(self, G: nx.Graph, 
                                      giant_component_fraction: float = 0.5) -> Tuple[float, float]:
        """Compute percolation threshold for a network."""
        if G.number_of_nodes() < 2:
            return 0.0, 0.0
        
        edges = list(G.edges())
        n_nodes = G.number_of_nodes()
        threshold_target = int(n_nodes * giant_component_fraction)
        
        p_c_values = []
        
        for _ in range(self.num_random_orderings):
            random.shuffle(edges)
            
            parent = list(range(n_nodes))
            component_size = [1] * n_nodes
            max_component_size = 1
            p_c = 1.0
            
            for k, (u, v) in enumerate(edges):
                root_u = self._find(parent, u)
                root_v = self._find(parent, v)
                
                if root_u != root_v:
                    if component_size[root_u] < component_size[root_v]:
                        root_u, root_v = root_v, root_u
                    
                    parent[root_v] = root_u
                    component_size[root_u] += component_size[root_v]
                    
                    if component_size[root_u] > max_component_size:
                        max_component_size = component_size[root_u]
                
                if max_component_size >= threshold_target:
                    p_c = (k + 1) / len(edges)
                    break
            
            p_c_values.append(p_c)
        
        return float(np.mean(p_c_values)), float(np.std(p_c_values))
    
    def _find(self, parent: List[int], x: int) -> int:
        """Find with path compression."""
        if parent[x] != x:
            parent[x] = self._find(parent, parent[x])
        return parent[x]


class BaselineReadabilityMetrics:
    """Computes traditional readability metrics."""
    
    def compute_all_metrics(self, text: str) -> Dict[str, float]:
        """Compute all baseline readability metrics."""
        metrics = {}
        
        try:
            metrics['flesch_kincaid'] = textstat.flesch_kincaid_grade(text)
        except:
            metrics['flesch_kincaid'] = np.nan
        
        try:
            metrics['dale_chall'] = textstat.dale_chall_readability_score(text)
        except:
            metrics['dale_chall'] = np.nan
        
        try:
            metrics['gunning_fog'] = textstat.gunning_fog(text)
        except:
            metrics['gunning_fog'] = np.nan
        
        try:
            metrics['smog'] = textstat.smog_index(text)
        except:
            metrics['smog'] = np.nan
        
        try:
            metrics['coleman_liau'] = textstat.coleman_liau_index(text)
        except:
            metrics['coleman_liau'] = np.nan
        
        return metrics


class DatasetLoader:
    """Loads readability datasets."""
    
    def create_synthetic_dataset(self, num_texts_per_grade: int = 50) -> List[TextData]:
        """Create synthetic dataset with varying complexity."""
        logger.info("Creating synthetic dataset with controlled cohesion")
        
        texts = []
        
        # Create texts with different cohesion patterns
        # Simple texts: high cohesion -> low p_c (need few edges to connect)
        # Complex texts: low cohesion -> high p_c (need many edges to connect)
        
        for grade in range(1, 13):
            for i in range(num_texts_per_grade):
                # Control cohesion through repeated vs unique content
                if grade <= 3:
                    # Very high cohesion - repeat same sentence with minor variations
                    base_words = ['The', 'cat', 'is', 'on', 'the', 'mat']
                    sentences = []
                    for j in range(random.randint(3, 5)):
                        words = base_words.copy()
                        # Minor variation
                        if j > 0:
                            words[random.randint(0, len(words)-1)] = random.choice(['dog', 'rug', 'floor', 'table'])
                        sentences.append(' '.join(words) + '.')
                    text = ' '.join(sentences)
                    
                elif grade <= 6:
                    # Medium cohesion - some shared words
                    word_sets = [
                        ['animals', 'play', 'in', 'the', 'garden'],
                        ['children', 'run', 'through', 'the', 'park'],
                        ['birds', 'fly', 'over', 'the', 'trees'],
                        ['fish', 'swim', 'in', 'the', 'water']
                    ]
                    sentences = []
                    for j in range(random.randint(4, 6)):
                        words = random.choice(word_sets)
                        sentences.append(' '.join(words) + '.')
                    text = ' '.join(sentences)
                    
                elif grade <= 9:
                    # Low cohesion - different topics
                    topics = [
                        ['The', 'experiment', 'demonstrated', 'significant', 'results'],
                        ['Researchers', 'analyzed', 'complex', 'data', 'patterns'],
                        ['Students', 'learned', 'about', 'scientific', 'methods'],
                        ['Technology', 'improves', 'educational', 'outcomes', 'today'],
                        ['Government', 'policies', 'affect', 'economic', 'growth']
                    ]
                    sentences = []
                    for j in range(random.randint(5, 8)):
                        words = random.choice(topics)
                        sentences.append(' '.join(words) + '.')
                    text = ' '.join(sentences)
                    
                else:
                    # Very low cohesion - completely different words per sentence
                    complex_topics = [
                        ['Philosophical', 'methodologies', 'underpin', 'ontological', 'frameworks'],
                        ['Socioeconomic', 'variables', 'correlate', 'with', 'demographic', 'shifts'],
                        ['Computational', 'algorithms', 'optimize', 'stochastic', 'processes'],
                        ['Neurobiological', 'pathways', 'mediate', 'cognitive', 'functions'],
                        ['Anthropological', 'theories', 'explain', 'cultural', 'evolution'],
                        ['Thermodynamic', 'principles', 'govern', 'molecular', 'interactions'],
                        ['Linguistic', 'structures', 'facilitate', 'semantic', 'comprehension']
                    ]
                    sentences = []
                    for j in range(random.randint(6, 10)):
                        words = random.choice(complex_topics)
                        sentences.append(' '.join(words) + '.')
                    text = ' '.join(sentences)
                
                texts.append(TextData(
                    text_id=f"synthetic_{grade}_{i}",
                    content=text,
                    grade_level=float(grade),
                    metadata={'source': 'synthetic'}
                ))
        
        logger.info(f"Created {len(texts)} synthetic examples")
        return texts


class CorrelationAnalyzer:
    """Analyzes correlations between readability metrics and ground truth."""
    
    def compute_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute correlations between metrics and grade level."""
        results = {}
        
        valid_data = df.dropna(subset=['p_c_mean', 'grade_level'])
        
        if len(valid_data) > 2:
            pearson_r, p_value = stats.pearsonr(valid_data['p_c_mean'], valid_data['grade_level'])
            spearman_r, spearman_p = stats.spearmanr(valid_data['p_c_mean'], valid_data['grade_level'])
            
            results['percolation_vs_grade'] = {
                'pearson_r': float(pearson_r),
                'p_value': float(p_value),
                'spearman_r': float(spearman_r),
                'spearman_p': float(spearman_p)
            }
        
        baseline_cols = ['flesch_kincaid', 'dale_chall', 'gunning_fog', 'smog', 'coleman_liau']
        baseline_comparisons = {}
        
        for col in baseline_cols:
            if col in df.columns and df[col].notna().sum() > 2:
                valid = df.dropna(subset=[col, 'grade_level'])
                if len(valid) > 2:
                    r, p = stats.pearsonr(valid[col], valid['grade_level'])
                    baseline_comparisons[col] = {
                        'pearson_r': float(r),
                        'p_value': float(p)
                    }
        
        results['baseline_comparisons'] = baseline_comparisons
        
        return results
    
    def run_regression_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run regression analysis to predict grade level."""
        results = {}
        
        valid_cols = ['p_c_mean', 'flesch_kincaid', 'dale_chall', 'gunning_fog', 'smog', 'coleman_liau', 'grade_level']
        valid_df = df[valid_cols].dropna()
        
        if len(valid_df) < 10:
            logger.warning("Not enough valid data for regression")
            return results
        
        X = valid_df[['p_c_mean']].values
        y = valid_df['grade_level'].values
        
        model_simple = LinearRegression()
        model_simple.fit(X, y)
        
        y_pred = model_simple.predict(X)
        r2_simple = r2_score(y, y_pred)
        rmse_simple = np.sqrt(mean_squared_error(y, y_pred))
        
        results['simple_model'] = {
            'r2': float(r2_simple),
            'rmse': float(rmse_simple),
            'coefficient': float(model_simple.coef_[0]),
            'intercept': float(model_simple.intercept_)
        }
        
        baseline_cols = ['flesch_kincaid', 'dale_chall', 'gunning_fog', 'smog', 'coleman_liau']
        X_multi = valid_df[['p_c_mean'] + baseline_cols].values
        
        model_multi = LinearRegression()
        model_multi.fit(X_multi, y)
        
        y_pred_multi = model_multi.predict(X_multi)
        r2_multi = r2_score(y, y_pred_multi)
        rmse_multi = np.sqrt(mean_squared_error(y, y_pred_multi))
        
        results['combined_model'] = {
            'r2': float(r2_multi),
            'rmse': float(rmse_multi),
            'delta_r2': float(r2_multi - r2_simple)
        }
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model_test = LinearRegression()
        model_test.fit(X_train, y_train)
        y_test_pred = model_test.predict(X_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
        
        results['test_evaluation'] = {
            'rmse': float(rmse_test),
            'r2': float(r2_score(y_test, y_test_pred))
        }
        
        return results


class ExperimentRunner:
    """Main experiment runner."""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("Initializing experiment components")
        self.network_builder = CohesionNetworkBuilder()
        self.percolation_analyzer = PercolationAnalyzer(num_random_orderings=50)
        self.baseline_metrics = BaselineReadabilityMetrics()
        self.dataset_loader = DatasetLoader()
        self.correlation_analyzer = CorrelationAnalyzer()
    
    def run_experiment(self, texts: List[TextData], ablation_mode: str = 'full') -> pd.DataFrame:
        """Run full experiment on a list of texts."""
        logger.info(f"Starting experiment with {len(texts)} texts (mode: {ablation_mode})")
        
        results = []
        
        for i, text_data in enumerate(texts):
            logger.info(f"Processing text {i+1}/{len(texts)}: {text_data.text_id}")
            
            try:
                result = self._process_single_text(text_data, ablation_mode)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {text_data.text_id}: {e}")
                continue
        
        df = pd.DataFrame(results)
        return df
    
    def _process_single_text(self, text_data: TextData, ablation_mode: str) -> Dict[str, Any]:
        """Process a single text and return all metrics."""
        result = {
            'text_id': text_data.text_id,
            'grade_level': text_data.grade_level,
            'n_sentences': 0,
            'n_edges': 0,
        }
        
        if ablation_mode == 'semantic_only':
            sbert_threshold = 0.5
            lexical_threshold = 1.0
        elif ablation_mode == 'lexical_only':
            sbert_threshold = 1.0
            lexical_threshold = 0.3
        else:
            sbert_threshold = 0.5
            lexical_threshold = 0.3
        
        G, sentences = self.network_builder.build_network(
            text_data.content,
            sbert_threshold=sbert_threshold,
            lexical_threshold=lexical_threshold
        )
        
        result['n_sentences'] = len(sentences)
        result['n_edges'] = G.number_of_edges()
        
        if len(sentences) >= 2:
            p_c_mean, p_c_std = self.percolation_analyzer.compute_percolation_threshold(G)
            result['p_c_mean'] = p_c_mean
            result['p_c_std'] = p_c_std
        else:
            result['p_c_mean'] = 0.0
            result['p_c_std'] = 0.0
        
        baseline = self.baseline_metrics.compute_all_metrics(text_data.content)
        result.update(baseline)
        
        return result
    
    def save_results(self, df: pd.DataFrame, correlations: Dict, regression: Dict, 
                     robustness: Dict, output_file: str = 'method_out.json'):
        """Save all results to JSON file in exp_gen_sol_out schema format."""
        logger.info(f"Saving results to {output_file}")
        
        # Convert to expected schema format
        examples = []
        for _, row in df.iterrows():
            # output = ground truth, predict_percolation = our prediction
            actual_grade = row.get('grade_level', 0)
            pred_grade = row.get('p_c_mean', 0) * 12  # Simple scaling
            example = {
                "input": f"Text ID: {row.get('text_id', '')}",
                "output": str(actual_grade),
                "predict_percolation": str(round(pred_grade, 2))
            }
            examples.append(example)
        
        output = {
            "metadata": {
                "method": "percolation_readability",
                "correlations": correlations,
                "regression": regression,
                "robustness": robustness
            },
            "datasets": [
                {
                    "dataset": "synthetic_readability",
                    "examples": examples
                }
            ]
        }
        
        output_path = self.output_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
        
        # Also save detailed CSV for easy inspection
        csv_path = self.output_dir / 'results.csv'
        df.to_csv(csv_path, index=False)
        
        return output_path


@logger.catch(reraise=True)
def main():
    """Main entry point for the experiment."""
    logger.info("Starting Percolation Threshold Readability Experiment")
    
    # Initialize experiment runner
    runner = ExperimentRunner(output_dir=".")
    
    # Create synthetic dataset
    logger.info("Creating synthetic dataset")
    all_texts = runner.dataset_loader.create_synthetic_dataset(num_texts_per_grade=20)
    
    logger.info(f"Total texts loaded: {len(all_texts)}")
    
    # Run experiment
    df = runner.run_experiment(all_texts, ablation_mode='full')
    
    # Compute correlations
    correlations = runner.correlation_analyzer.compute_correlations(df)
    
    # Run regression
    regression = runner.correlation_analyzer.run_regression_analysis(df)
    
    # Run robustness checks
    robustness = {
        'mean_std_across_texts': float(df['p_c_std'].mean()) if 'p_c_std' in df.columns else 0.0,
        'ablation_results': {}
    }
    
    # Ablation study
    for mode in ['full', 'semantic_only', 'lexical_only']:
        ablation_df = runner.run_experiment(all_texts[:20], ablation_mode=mode)
        ablation_corr = runner.correlation_analyzer.compute_correlations(ablation_df)
        robustness['ablation_results'][mode] = ablation_corr.get('percolation_vs_grade', {})
    
    # Save results
    output_path = runner.save_results(df, correlations, regression, robustness)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("=" * 60)
    
    if 'percolation_vs_grade' in correlations:
        r = correlations['percolation_vs_grade']['pearson_r']
        p = correlations['percolation_vs_grade']['p_value']
        logger.info(f"Percolation vs Grade Correlation: r={r:.3f}, p={p:.3f}")
    
    if 'simple_model' in regression:
        r2 = regression['simple_model']['r2']
        rmse = regression['simple_model']['rmse']
        logger.info(f"Simple Model: R²={r2:.3f}, RMSE={rmse:.3f}")
    
    logger.info(f"Results saved to: {output_path}")
    logger.info("Experiment completed successfully!")


if __name__ == "__main__":
    main()
