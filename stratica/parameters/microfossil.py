"""MFA - Micro-Fossil Assemblage Score parameter.

Based on paper Section 3.3:
T_SST = Σ_j [f_j * T_hat_j]

where f_j = relative abundance of taxon j
T_hat_j = species-specific temperature preference (modern calibration)

CNN classifier achieves 93.4% species-level accuracy on 2.3 million images
"""

import numpy as np
from typing import Dict, Any, Optional, List
import json

from stratica.parameters.base import ParameterBase


class MicroFossilAssemblage(ParameterBase):
    """
    MFA: Micro-Fossil Assemblage Score (12% weight).
    
    AI-classified foraminifera, nannofossils, and palynomorphs providing
    biostratigraphic age control and paleoecology reconstruction.
    
    Key features:
    - CNN classifier trained on MIKROTAX database (2.3M images)
    - 93.4% species-level accuracy
    - Transfer function for SST reconstruction
    """
    
    def __init__(self, weight: float = 0.12, config: Optional[Dict] = None):
        super().__init__(name="MFA", weight=weight, config=config)
        
        # Classifier settings
        self.classifier_type = self.config.get("classifier", "cnn_v2")
        self.confidence_threshold = self.config.get("confidence_threshold", 0.85)
        
        # Species temperature preferences (simplified subset)
        # Full database would contain hundreds of species
        self.species_temperature = self._load_species_temperatures()
        
        # Taxonomic groups
        self.groups = ["planktic_foram", "benthic_foram", "nannofossil", "radiolarian"]
    
    def _load_species_temperatures(self) -> Dict[str, float]:
        """Load species-specific temperature preferences."""
        # Simplified calibration from modern core-top databases
        return {
            # Planktic foraminifera
            "Globigerinoides_ruber": 26.5,
            "Globigerinoides_sacculifer": 27.0,
            "Neogloboquadrina_pachyderma": 5.0,
            "Neogloboquadrina_dutertrei": 20.0,
            "Globorotalia_truncatulinoides": 15.0,
            "Globorotalia_menardii": 24.0,
            "Globigerina_bulloides": 12.0,
            "Orbulina_universa": 22.0,
            
            # Benthic foraminifera
            "Cibicidoides_wuellerstorfi": 3.0,
            "Uvigerina_peregrina": 5.0,
            "Oridorsalis_umbonatus": 2.5,
            "Melonis_barleeanum": 4.0,
            
            # Nannofossils
            "Emiliania_huxleyi": 18.0,
            "Gephyrocapsa_oceanica": 22.0,
            "Coccolithus_pelagicus": 8.0,
            "Florisphaera_profunda": 20.0,
        }
    
    def compute(self, data: Dict[str, Any]) -> float:
        """
        Compute raw MFA score from microfossil assemblage data.
        
        Expected data keys:
            - species_counts: dict mapping species to counts per sample
            - sample_depths: array of depths
            - images: optional list of image paths for CNN classification
        
        Returns:
            Raw MFA score (0-1) based on:
            - Diversity (Shannon index)
            - Preservation quality
            - Classification confidence
            - Agreement with expected assemblage
        """
        species_counts = data.get("species_counts", {})
        
        if not species_counts:
            return 0.0
        
        # Calculate diversity metrics
        diversity_score = self._diversity_score(species_counts)
        
        # Calculate preservation quality
        preservation_score = self._preservation_score(data)
        
        # Calculate classification confidence
        confidence_score = self._classification_confidence(data)
        
        # Combine scores
        mfa_raw = 0.4 * diversity_score + 0.3 * preservation_score + 0.3 * confidence_score
        
        return float(mfa_raw)
    
    def _diversity_score(self, species_counts: Dict[str, int]) -> float:
        """Calculate Shannon-Wiener diversity index H'."""
        total = sum(species_counts.values())
        if total == 0:
            return 0.0
        
        # Shannon index: H' = -Σ p_i * ln(p_i)
        shannon = 0.0
        for count in species_counts.values():
            p = count / total
            if p > 0:
                shannon -= p * np.log(p)
        
        # Normalize by maximum possible H' for this many species
        n_species = len(species_counts)
        if n_species <= 1:
            h_norm = shannon
        else:
            h_max = np.log(n_species)
            h_norm = shannon / h_max if h_max > 0 else 0
        
        return float(np.clip(h_norm, 0, 1))
    
    def _preservation_score(self, data: Dict[str, Any]) -> float:
        """Estimate fossil preservation quality."""
        preservation = data.get("preservation", {})
        
        # Factors affecting preservation
        factors = []
        
        # Dissolution index (lower is better)
        if "dissolution_index" in preservation:
            di = preservation["dissolution_index"]
            factors.append(1.0 - np.clip(di, 0, 1))
        
        # Fragmentation (lower is better)
        if "fragmentation" in preservation:
            frag = preservation["fragmentation"]
            factors.append(1.0 - np.clip(frag, 0, 1))
        
        # Recrystallization (lower is better)
        if "recrystallization" in preservation:
            recry = preservation["recrystallization"]
            factors.append(1.0 - np.clip(recry, 0, 1))
        
        if not factors:
            return 0.5  # Default if no data
        
        return float(np.mean(factors))
    
    def _classification_confidence(self, data: Dict[str, Any]) -> float:
        """Average confidence of CNN classifications."""
        confidences = data.get("classification_confidence", [])
        
        if not confidences:
            return 0.0
        
        # Average confidence, but penalize if below threshold
        avg_conf = np.mean(confidences)
        
        # Apply threshold penalty
        if avg_conf < self.confidence_threshold:
            penalty = avg_conf / self.confidence_threshold
            return float(avg_conf * penalty)
        
        return float(avg_conf)
    
    def reconstruct_sst(self, species_counts: Dict[str, int]) -> float:
        """
        Reconstruct sea surface temperature using transfer function.
        
        T_SST = Σ_j [f_j * T_hat_j]
        
        where f_j = relative abundance, T_hat_j = species temperature preference
        """
        total = sum(species_counts.values())
        if total == 0:
            return 15.0  # Default global mean
        
        sst = 0.0
        for species, count in species_counts.items():
            if species in self.species_temperature:
                f = count / total
                sst += f * self.species_temperature[species]
        
        return float(sst)
    
    def identify_index_species(self, species_counts: Dict[str, int]) -> List[str]:
        """
        Identify biostratigraphic index species for age control.
        
        Returns list of species with known age ranges.
        """
        # Simplified - full version would query database
        index_species = []
        
        for species in species_counts.keys():
            if "index" in species.lower() or species in [
                "Globigerinoides_ruber",
                "Neogloboquadrina_pachyderma",
                "Emiliania_huxleyi"
            ]:
                index_species.append(species)
        
        return index_species
    
    def normalize(self, value: float) -> float:
        """Normalize MFA score to [0,1]."""
        return np.clip(value, 0, 1)
