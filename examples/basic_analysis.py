#!/usr/bin/env python
"""Basic STRATICA analysis example."""

from stratica import StratigraphicAnalyzer
from stratica.config import load_config

def main():
    # Load configuration
    config = load_config('config/default.yaml')
    
    # Initialize analyzer
    analyzer = StratigraphicAnalyzer(config=config)
    
    # Load core data
    data = analyzer.load_core('data/raw/ODP_1209B.csv')
    
    # Compute TCI
    results = analyzer.compute_tci(data)
    
    print(f"TCI Score: {results.tci_composite:.3f}")
    print(f"Classification: {results.classification}")
    
    # Generate profile
    profile = analyzer.generate_profile(results)
    
    return results

if __name__ == "__main__":
    main()
