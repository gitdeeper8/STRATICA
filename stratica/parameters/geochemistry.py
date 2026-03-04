"""GCH - Geochemical Anomaly Index parameter.

Based on paper Section 3.5:
GCH_i = (C_i - μ_background) / σ_background

where C_i = concentration at horizon i
μ, σ computed over 500 kyr pre-event baseline

Detects:
- Bolide impacts (Ir, Pt anomalies >5σ)
- Ocean anoxic events (Mo, U enrichment >3σ)
- Volcanism (Hg anomalies)
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple

from stratica.parameters.base import ParameterBase
from stratica.utils.constants import GEOchemical_ANOMALY


class GeochemicalAnomalyIndex(ParameterBase):
    """
    GCH: Geochemical Anomaly Index (10% weight).
    
    Trace element signatures detecting catastrophic events in Earth history:
    - Iridium (Ir) anomalies for bolide impacts (KT boundary)
    - Molybdenum (Mo) and Uranium (U) for ocean anoxic events
    - Mercury (Hg) for Large Igneous Province volcanism
    - Platinum group elements for impact characterization
    """
    
    def __init__(self, weight: float = 0.10, config: Optional[Dict] = None):
        super().__init__(name="GCH", weight=weight, config=config)
        
        # Anomaly thresholds from paper
        self.background_window = self.config.get(
            "background_window", 
            GEOchemical_ANOMALY["background_window"]
        )
        self.ir_threshold = self.config.get(
            "ir_threshold", 
            GEOchemical_ANOMALY["iridium_threshold"]
        )
        self.mo_threshold = self.config.get(
            "mo_threshold", 
            GEOchemical_ANOMALY["molybdenum_threshold"]
        )
        self.u_threshold = self.config.get(
            "u_threshold", 
            GEOchemical_ANOMALY["uranium_threshold"]
        )
        self.hg_threshold = self.config.get(
            "hg_threshold", 
            GEOchemical_ANOMALY["mercury_threshold"]
        )
        
        # Elements of interest
        self.impact_elements = ["Ir", "Pt", "Os", "Ru", "Rh", "Pd"]
        self.anoxia_elements = ["Mo", "U", "V", "Cr", "Co", "Ni"]
        self.volcanic_elements = ["Hg", "As", "Sb", "Tl"]
        self.redox_elements = ["Fe", "Mn", "S", "Ce", "Eu"]
    
    def compute(self, data: Dict[str, Any]) -> float:
        """
        Compute raw GCH score from geochemical data.
        
        Expected data keys:
            - depth: array of depths [m]
            - age: array of ages [ka]
            - elements: dict mapping element to concentration array
            - units: concentration units (ppm, ppb, etc.)
        
        Returns:
            Raw GCH score (0-1) based on:
            - Maximum anomaly strength
            - Number of anomalous elements
            - Event type classification confidence
        """
        depth = np.array(data.get("depth", []))
        age = np.array(data.get("age", []))
        elements = data.get("elements", {})
        
        if not elements or len(depth) == 0:
            return 0.0
        
        # Calculate anomalies for each element
        all_anomalies = []
        event_scores = []
        
        for element, conc in elements.items():
            if element in self.impact_elements:
                anomaly = self._calculate_anomaly(conc, age, self.ir_threshold)
                all_anomalies.append(anomaly)
                if anomaly["max_sigma"] > self.ir_threshold:
                    event_scores.append(anomaly["max_sigma"] / 10)
            
            elif element in self.anoxia_elements:
                anomaly = self._calculate_anomaly(conc, age, self.mo_threshold)
                all_anomalies.append(anomaly)
                if anomaly["max_sigma"] > self.mo_threshold:
                    event_scores.append(anomaly["max_sigma"] / 6)
            
            elif element in self.volcanic_elements:
                anomaly = self._calculate_anomaly(conc, age, self.hg_threshold)
                all_anomalies.append(anomaly)
                if anomaly["max_sigma"] > self.hg_threshold:
                    event_scores.append(anomaly["max_sigma"] / 6)
        
        if not all_anomalies:
            return 0.0
        
        # Maximum anomaly strength
        max_sigma = max([a["max_sigma"] for a in all_anomalies])
        
        # Number of anomalous elements
        n_anomalous = sum([a["n_anomalies"] > 0 for a in all_anomalies])
        element_score = min(1.0, n_anomalous / 3)
        
        # Event score
        event_score = np.mean(event_scores) if event_scores else 0
        
        # Combine
        gch_raw = 0.5 * min(1.0, max_sigma / 10) + 0.25 * element_score + 0.25 * event_score
        
        return float(gch_raw)
    
    def _calculate_anomaly(
        self, 
        concentrations: np.ndarray, 
        ages: np.ndarray,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Calculate anomaly statistics for an element.
        
        Uses 500 kyr pre-event baseline for background.
        """
        if len(concentrations) < 10 or len(ages) < 10:
            return {
                "max_sigma": 0.0,
                "n_anomalies": 0,
                "anomaly_depths": [],
                "background_mean": 0.0,
                "background_std": 1.0
            }
        
        # Sort by age
        sort_idx = np.argsort(ages)
        ages_sorted = ages[sort_idx]
        conc_sorted = concentrations[sort_idx]
        
        # Calculate background from oldest part (pre-event)
        oldest_age = np.min(ages_sorted)
        background_mask = ages_sorted < oldest_age + self.background_window
        
        if np.sum(background_mask) < 5:
            # Not enough background data, use all data with outlier removal
            conc_clean = conc_sorted[
                (conc_sorted > np.percentile(conc_sorted, 5)) & 
                (conc_sorted < np.percentile(conc_sorted, 95))
            ]
            background_mean = np.mean(conc_clean)
            background_std = np.std(conc_clean)
        else:
            background_mean = np.mean(conc_sorted[background_mask])
            background_std = np.std(conc_sorted[background_mask])
        
        # Calculate sigma anomalies
        sigma = (conc_sorted - background_mean) / (background_std + 1e-10)
        
        # Find anomalies above threshold
        anomaly_mask = sigma > threshold
        anomaly_indices = np.where(anomaly_mask)[0]
        
        return {
            "max_sigma": float(np.max(sigma)) if len(sigma) > 0 else 0,
            "n_anomalies": int(np.sum(anomaly_mask)),
            "anomaly_depths": [],  # Would need depth array
            "background_mean": float(background_mean),
            "background_std": float(background_std)
        }
    
    def detect_event_type(self, elements: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Classify event type based on element anomalies.
        
        Returns:
            Probabilities for each event type
        """
        scores = {
            "impact": 0.0,
            "ocean_anoxia": 0.0,
            "volcanism": 0.0,
            "background": 1.0
        }
        
        # Check impact elements (Ir, Pt)
        impact_count = 0
        for elem in self.impact_elements:
            if elem in elements and len(elements[elem]) > 0:
                anomaly = self._calculate_anomaly(
                    elements[elem], 
                    np.arange(len(elements[elem])),  # dummy ages
                    self.ir_threshold
                )
                if anomaly["max_sigma"] > self.ir_threshold:
                    impact_count += 1
                    scores["impact"] += anomaly["max_sigma"] / 20
        
        # Check anoxia elements (Mo, U)
        anoxia_count = 0
        for elem in self.anoxia_elements:
            if elem in elements and len(elements[elem]) > 0:
                anomaly = self._calculate_anomaly(
                    elements[elem],
                    np.arange(len(elements[elem])),
                    self.mo_threshold
                )
                if anomaly["max_sigma"] > self.mo_threshold:
                    anoxia_count += 1
                    scores["ocean_anoxia"] += anomaly["max_sigma"] / 12
        
        # Check volcanic elements (Hg)
        volcanic_count = 0
        for elem in self.volcanic_elements:
            if elem in elements and len(elements[elem]) > 0:
                anomaly = self._calculate_anomaly(
                    elements[elem],
                    np.arange(len(elements[elem])),
                    self.hg_threshold
                )
                if anomaly["max_sigma"] > self.hg_threshold:
                    volcanic_count += 1
                    scores["volcanism"] += anomaly["max_sigma"] / 12
        
        # Normalize based on count
        if impact_count > 0:
            scores["impact"] /= impact_count
        if anoxia_count > 0:
            scores["ocean_anoxia"] /= anoxia_count
        if volcanic_count > 0:
            scores["volcanism"] /= volcanic_count
        
        # Background probability
        max_event = max(scores["impact"], scores["ocean_anoxia"], scores["volcanism"])
        scores["background"] = max(0, 1 - max_event)
        
        # Normalize to sum to 1
        total = sum(scores.values())
        if total > 0:
            for key in scores:
                scores[key] /= total
        
        return scores
    
    def normalize(self, value: float) -> float:
        """Normalize GCH score to [0,1]."""
        return np.clip(value, 0, 1)
