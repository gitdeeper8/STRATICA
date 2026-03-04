"""PYS - Palynological Yield Score parameter.

Based on paper Section 3.6:
PYS = α * (C_p / C_p,max) + (1-α) * (H' / H'_max)

where α = 0.55
H' = -Σ_j [p_j * ln(p_j)] Shannon-Wiener diversity
Calibrated from 3,200 modern surface samples
"""

import numpy as np
from typing import Dict, Any, Optional

from stratica.parameters.base import ParameterBase


class PalynologicalYieldScore(ParameterBase):
    """
    PYS: Palynological Yield Score (9% weight).
    
    Pollen and spore assemblage diversity encoding terrestrial vegetation cover,
    humidity, and land-surface history. Provides critical constraints on
    continental climate conditions.
    
    Key components:
    - Pollen concentration (grains/g sediment)
    - Taxonomic diversity (Shannon index)
    - Ecological affinity groups (arid, humid, temperate)
    """
    
    def __init__(self, weight: float = 0.09, config: Optional[Dict] = None):
        super().__init__(name="PYS", weight=weight, config=config)
        
        # Mixing coefficient from paper
        self.alpha = self.config.get("alpha", 0.55)
        
        # Diversity index type
        self.diversity_index = self.config.get("diversity_index", "shannon")
        
        # Ecological groups
        self.ecological_groups = {
            "arid": ["Artemisia", "Chenopodiaceae", "Ephedra"],
            "humid": ["Polypodiaceae", "Cyperaceae", "Myrica"],
            "temperate": ["Quercus", "Pinus", "Betula", "Alnus"],
            "tropical": ["Palmae", "Mangrove", "Nypa"],
            "boreal": ["Picea", "Abies", "Larix"],
        }
    
    def compute(self, data: Dict[str, Any]) -> float:
        """
        Compute raw PYS score from palynological data.
        
        Expected data keys:
            - pollen_counts: dict mapping taxa to counts per sample
            - sample_depths: array of depths
            - concentration: pollen concentration [grains/g]
            - preservation: preservation quality index
        
        Returns:
            Raw PYS score (0-1) based on concentration and diversity
        """
        pollen_counts = data.get("pollen_counts", {})
        concentration = data.get("concentration", 0)
        
        if not pollen_counts and concentration == 0:
            return 0.0
        
        # Concentration component
        if concentration > 0:
            # Normalize to typical max concentration (100,000 grains/g)
            conc_score = min(1.0, concentration / 100000)
        else:
            conc_score = 0.0
        
        # Diversity component
        if pollen_counts:
            if self.diversity_index == "shannon":
                h_score = self._shannon_diversity(pollen_counts)
            elif self.diversity_index == "simpson":
                h_score = self._simpson_diversity(pollen_counts)
            else:
                h_score = self._richness_score(pollen_counts)
        else:
            h_score = 0.0
        
        # Combine using alpha from paper
        pys_raw = self.alpha * conc_score + (1 - self.alpha) * h_score
        
        return float(pys_raw)
    
    def _shannon_diversity(self, counts: Dict[str, int]) -> float:
        """Calculate normalized Shannon-Wiener diversity index."""
        total = sum(counts.values())
        if total == 0:
            return 0.0
        
        # Shannon index: H' = -Σ p_i * ln(p_i)
        shannon = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                shannon -= p * np.log(p)
        
        # Normalize by maximum possible (ln n_species)
        n_species = len(counts)
        if n_species <= 1:
            return float(shannon)
        
        h_max = np.log(n_species)
        if h_max > 0:
            return float(np.clip(shannon / h_max, 0, 1))
        else:
            return 0.0
    
    def _simpson_diversity(self, counts: Dict[str, int]) -> float:
        """Calculate Simpson diversity index (1 - D)."""
        total = sum(counts.values())
        if total == 0:
            return 0.0
        
        # Simpson's D = Σ p_i²
        d = 0.0
        for count in counts.values():
            p = count / total
            d += p * p
        
        # Inverse Simpson (1-D) ranges 0-1
        return float(1 - d)
    
    def _richness_score(self, counts: Dict[str, int]) -> float:
        """Simple species richness score."""
        n_species = len(counts)
        # Normalize to typical maximum (50 taxa)
        return float(min(1.0, n_species / 50))
    
    def reconstruct_vegetation(self, counts: Dict[str, int]) -> Dict[str, float]:
        """
        Reconstruct vegetation type proportions based on ecological groups.
        
        Returns:
            Proportions of each ecological group
        """
        total = sum(counts.values())
        if total == 0:
            return {group: 0.0 for group in self.ecological_groups}
        
        group_counts = {group: 0 for group in self.ecological_groups}
        
        for taxon, count in counts.items():
            for group, taxa_list in self.ecological_groups.items():
                if any(t in taxon for t in taxa_list):
                    group_counts[group] += count
                    break
        
        # Convert to proportions
        proportions = {}
        for group, group_count in group_counts.items():
            proportions[group] = group_count / total
        
        return proportions
    
    def humidity_index(self, counts: Dict[str, int]) -> float:
        """
        Calculate humidity index based on arid/humid taxa ratio.
        
        Returns:
            Index from 0 (arid) to 1 (humid)
        """
        total = sum(counts.values())
        if total == 0:
            return 0.5
        
        arid_sum = 0
        humid_sum = 0
        
        for taxon, count in counts.items():
            if any(t in taxon for t in self.ecological_groups["arid"]):
                arid_sum += count
            if any(t in taxon for t in self.ecological_groups["humid"]):
                humid_sum += count
        
        if arid_sum + humid_sum == 0:
            return 0.5
        
        return float(humid_sum / (arid_sum + humid_sum))
    
    def temperature_index(self, counts: Dict[str, int]) -> float:
        """
        Estimate temperature preference from pollen assemblages.
        
        Returns:
            Index from 0 (cold) to 1 (warm)
        """
        total = sum(counts.values())
        if total == 0:
            return 0.5
        
        # Simplified: boreal (cold) vs tropical (warm)
        cold_sum = 0
        warm_sum = 0
        
        for taxon, count in counts.items():
            if any(t in taxon for t in self.ecological_groups["boreal"]):
                cold_sum += count
            if any(t in taxon for t in self.ecological_groups["tropical"]):
                warm_sum += count
            if any(t in taxon for t in self.ecological_groups["temperate"]):
                # Temperate contributes to both
                cold_sum += count * 0.3
                warm_sum += count * 0.3
        
        if cold_sum + warm_sum == 0:
            return 0.5
        
        return float(warm_sum / (cold_sum + warm_sum))
    
    def normalize(self, value: float) -> float:
        """Normalize PYS score to [0,1]."""
        return np.clip(value, 0, 1)
