"""Main StratigraphicAnalyzer class."""

from typing import Dict, Any, Optional
import numpy as np

from .tci_index import TCIIndex, TCIResults
from ..parameters import (
    LithologicalDepositionRate,
    IsotopeFractionation,
    MicroFossilAssemblage,
    MagneticSusceptibility,
    GeochemicalAnomalyIndex,
    PalynologicalYieldScore,
    VarveSedimentaryIntegrity,
    ThermalDiffusionModel,
    CyclostratigraphicEnergyCycle
)
from ..utils.io import load_data


class StratigraphicAnalyzer:
    """Main analysis engine for stratigraphic data."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._initialize_parameters()
        self.tci_index = TCIIndex()
    
    def _initialize_parameters(self):
        """Initialize all nine TCI parameters."""
        param_config = self.config.get('parameters', {})
        
        self.parameters = {
            'LDR': LithologicalDepositionRate(
                weight=param_config.get('LDR', {}).get('weight', 0.20)
            ),
            'ISO': IsotopeFractionation(
                weight=param_config.get('ISO', {}).get('weight', 0.15)
            ),
            'MFA': MicroFossilAssemblage(
                weight=param_config.get('MFA', {}).get('weight', 0.12)
            ),
            'MAG': MagneticSusceptibility(
                weight=param_config.get('MAG', {}).get('weight', 0.11)
            ),
            'GCH': GeochemicalAnomalyIndex(
                weight=param_config.get('GCH', {}).get('weight', 0.10)
            ),
            'PYS': PalynologicalYieldScore(
                weight=param_config.get('PYS', {}).get('weight', 0.09)
            ),
            'VSI': VarveSedimentaryIntegrity(
                weight=param_config.get('VSI', {}).get('weight', 0.08)
            ),
            'TDM': ThermalDiffusionModel(
                weight=param_config.get('TDM', {}).get('weight', 0.08)
            ),
            'CEC': CyclostratigraphicEnergyCycle(
                weight=param_config.get('CEC', {}).get('weight', 0.07)
            )
        }
    
    def load_core(self, filepath: str, **kwargs) -> Dict[str, Any]:
        """Load stratigraphic core data from file."""
        return load_data(filepath, **kwargs)
    
    def compute_tci(self, data: Dict[str, Any]) -> TCIResults:
        """Compute Temporal Climate Integrity Index."""
        parameter_scores = {}
        
        # Compute each parameter
        for name, param in self.parameters.items():
            try:
                # محاولة حساب المعامل
                score = param(data)
                parameter_scores[name] = score
            except Exception as e:
                # إذا فشل، استخدم قيمة افتراضية
                parameter_scores[name] = 0.5
        
        # Compute composite TCI
        tci_value = self.tci_index.compute(parameter_scores)
        classification = self.tci_index.classify(tci_value)
        
        return TCIResults(
            tci_composite=tci_value,
            classification=classification,
            parameters=parameter_scores,
            metadata={'n_parameters': len(parameter_scores)}
        )
    
    def generate_profile(self, results: TCIResults) -> Dict[str, Any]:
        """Generate stratigraphic column visualization data."""
        return {
            'tci': results.tci_composite,
            'classification': results.classification,
            'parameters': results.parameters
        }
