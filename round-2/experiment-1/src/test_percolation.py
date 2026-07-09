#!/usr/bin/env python3
"""Test script to verify percolation threshold computation on small data."""
from loguru import logger
from pathlib import Path
import json
import sys
import numpy as np

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

# Import our method
sys.path.insert(0, str(Path(__file__).parent))
from method import PercolationNetwork, BaselineReadabilityScorer

@logger.catch(reraise=True)
def test_percolation():
    """Test percolation network on sample texts."""
    
    # Test with simple texts of varying complexity
    test_texts = [
        ("Simple", "The cat sat on the mat. The dog ran fast."),
        ("Medium", "The investigation revealed several complications that emerged during the analysis of the experimental data."),
        ("Complex", "Notwithstanding the aforementioned considerations regarding the methodological frameworks employed in contemporary sociolinguistic research, it remains incumbent upon scholars to interrogate the epistemological underpinnings of their analytical paradigms."),
    ]
    
    for name, text in test_texts:
        logger.info(f"\nTesting {name} text:")
        logger.info(f"Text: {text[:100]}...")
        
        network = PercolationNetwork(window_size=3, min_freq=1)
        network.build_network(text)
        threshold = network.compute_percolation_threshold(num_trials=20)
        features = network.get_network_features()
        
        logger.info(f"Percolation threshold: {threshold:.3f}")
        logger.info(f"Features: {features}")
        
        # Clean up
        del network
    
    # Test baseline
    logger.info("\n\nTesting baseline readability formulas:")
    scorer = BaselineReadabilityScorer()
    
    for name, text in test_texts:
        fk = scorer.flesch_kincaid_grade(text)
        logger.info(f"{name} - Flesch-Kincaid Grade: {fk:.1f}")
    
    logger.info("\n" + "="*50)
    logger.info("TEST COMPLETE - Percolation logic verified!")
    logger.info("="*50)

if __name__ == "__main__":
    test_percolation()
