"""Isotope fractionation thermodynamics.

Based on paper Section 3.2 and 4.2:
- Shackleton-O'Neil paleotemperature equation
- Multi-proxy Bayesian inversion
- Thermodynamic consistency constraints
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from scipy import stats, optimize


class IsotopeThermodynamics:
    """Isotope fractionation calculations and thermodynamic constraints."""
    
    def __init__(self):
        # Paleotemperature equation coefficients
        self.a0 = 16.9
        self.a1 = -4.38
        self.a2 = 0.10
        
        # Fractionation factors
        self.alpha_calcite_water = 1.0285  # at 25°C
        self.R_vpdb = 0.011237  # 13C/12C ratio for VPDB standard
        
    def paleotemperature_shackleton(
        self,
        d18O_calcite: float,
        d18O_sw: float = 0.0
    ) -> float:
        """
        Shackleton-O'Neil paleotemperature equation.
        
        T(°C) = 16.9 - 4.38*(δ¹⁸O_c - δ¹⁸O_sw) + 0.10*(δ¹⁸O_c - δ¹⁸O_sw)²
        
        Valid for 0-30°C.
        
        Args:
            d18O_calcite: δ¹⁸O of calcite (‰ VPDB)
            d18O_sw: δ¹⁸O of seawater (‰ VSMOW), default 0
        
        Returns:
            Temperature in °C
        """
        delta = d18O_calcite - d18O_sw
        T = self.a0 + self.a1 * delta + self.a2 * delta**2
        
        # Clamp to valid range
        T = np.clip(T, 0, 40)
        
        return float(T)
    
    def fractionation_factor(self, T: float, mineral: str = "calcite") -> float:
        """
        Calculate oxygen isotope fractionation factor.
        
        Args:
            T: Temperature [°C]
            mineral: "calcite", "aragonite", or "dolomite"
        
        Returns:
            Fractionation factor α
        """
        T_kelvin = T + 273.15
        
        if mineral == "calcite":
            # O'Neil et al. (1969)
            ln_alpha = (2.78e6 / T_kelvin**2 - 2.89) / 1000
        elif mineral == "aragonite":
            # Grossman & Ku (1986)
            ln_alpha = (2.67e6 / T_kelvin**2 - 2.43) / 1000
        elif mineral == "dolomite":
            # Vasconcelos et al. (2005)
            ln_alpha = (2.73e6 / T_kelvin**2 - 0.26) / 1000
        else:
            raise ValueError(f"Unknown mineral: {mineral}")
        
        return np.exp(ln_alpha)
    
    def delta_to_ratio(self, delta: float, standard: str = "VPDB") -> float:
        """
        Convert δ value to isotope ratio.
        
        δ = (R_sample / R_standard - 1) * 1000
        
        Args:
            delta: δ value in ‰
            standard: "VPDB" or "VSMOW"
        
        Returns:
            Isotope ratio R
        """
        if standard == "VPDB":
            R_std = self.R_vpdb
        elif standard == "VSMOW":
            R_std = 0.0020052  # 18O/16O for VSMOW
        else:
            raise ValueError(f"Unknown standard: {standard}")
        
        return R_std * (1 + delta / 1000)
    
    def ratio_to_delta(self, R: float, standard: str = "VPDB") -> float:
        """Convert isotope ratio to δ value."""
        if standard == "VPDB":
            R_std = self.R_vpdb
        elif standard == "VSMOW":
            R_std = 0.0020052
        else:
            raise ValueError(f"Unknown standard: {standard}")
        
        return (R / R_std - 1) * 1000
    
    def carbon_isotope_fractionation(
        self,
        T: float,
        source: str = "dissolved_inorganic_carbon"
    ) -> float:
        """
        Carbon isotope fractionation during photosynthesis.
        
        Args:
            T: Temperature [°C]
            source: Carbon source
        
        Returns:
            Fractionation ε [‰]
        """
        T_kelvin = T + 273.15
        
        if source == "dissolved_inorganic_carbon":
            # Romanek et al. (1992)
            epsilon = 1000 * (11.98 - 0.12 * T)
        elif source == "atmospheric_CO2":
            epsilon = 1000 * (4.3 - 0.1 * T)
        else:
            epsilon = 0
        
        return float(epsilon)
    
    def thermodynamic_constraint(
        self,
        d18O_calcite: np.ndarray,
        d13C_calcite: np.ndarray,
        T_reconstructed: np.ndarray
    ) -> float:
        """
        Enforce thermodynamic consistency between isotopes and temperature.
        
        Used in loss function L_thermo.
        
        Returns:
            Constraint violation score (0 = consistent, >0 = violation)
        """
        if len(d18O_calcite) == 0 or len(T_reconstructed) == 0:
            return 0.0
        
        # Predict δ¹⁸O from temperature
        d18O_predicted = np.zeros_like(T_reconstructed)
        for i, T in enumerate(T_reconstructed):
            # Invert paleotemperature equation
            # Solve for delta given T
            # T = a0 + a1*delta + a2*delta²
            # => a2*delta² + a1*delta + (a0 - T) = 0
            a = self.a2
            b = self.a1
            c = self.a0 - T
            
            discriminant = b**2 - 4*a*c
            if discriminant >= 0:
                delta1 = (-b + np.sqrt(discriminant)) / (2*a)
                delta2 = (-b - np.sqrt(discriminant)) / (2*a)
                # Choose reasonable value
                d18O_predicted[i] = min(delta1, delta2, key=abs)
            else:
                d18O_predicted[i] = 0
        
        # Calculate RMS mismatch
        if len(d18O_calcite) == len(d18O_predicted):
            mismatch = np.sqrt(np.mean((d18O_calcite - d18O_predicted)**2))
        else:
            mismatch = 0
        
        return float(mismatch)
    
    def bayesian_inversion(
        self,
        d18O: np.ndarray,
        d13C: np.ndarray,
        delta47: Optional[np.ndarray] = None,
        mgca: Optional[np.ndarray] = None,
        n_samples: int = 10000
    ) -> Dict[str, Any]:
        """
        Multi-proxy Bayesian inversion for temperature and ice volume.
        
        Uses MCMC sampling to estimate posterior distributions.
        
        Returns:
            Dictionary with posterior means and uncertainties
        """
        # Simplified MCMC implementation
        # Full version would use PyMC or emcee
        
        # Initialize samples
        T_samples = np.random.normal(20, 10, n_samples)
        ice_volume_samples = np.random.normal(0, 50, n_samples)  # m sea-level
        
        # Likelihood from δ¹⁸O
        d18O_pred = np.zeros(n_samples)
        for i, T in enumerate(T_samples):
            # Simplified relationship
            d18O_pred[i] = (self.a0 - T) / self.a1  # Linear approximation
        
        # Calculate weights from δ¹⁸O
        d18O_error = np.abs(d18O_pred - np.mean(d18O))
        weights = np.exp(-0.5 * (d18O_error / np.std(d18O))**2)
        
        # Update with clumped isotopes if available
        if delta47 is not None and len(delta47) > 0:
            delta47_mean = np.mean(delta47)
            # Δ47 gives T independent of ice volume
            T_delta47 = (0.9 - delta47_mean) / 0.004
            weights *= np.exp(-0.5 * ((T_samples - T_delta47) / 3)**2)
        
        # Update with Mg/Ca if available
        if mgca is not None and len(mgca) > 0:
            mgca_mean = np.mean(mgca)
            T_mgca = np.log(mgca_mean / 0.9) / 0.1
            weights *= np.exp(-0.5 * ((T_samples - T_mgca) / 4)**2)
        
        # Normalize weights
        weights /= np.sum(weights)
        
        # Resample according to weights
        indices = np.random.choice(n_samples, n_samples, p=weights)
        T_posterior = T_samples[indices]
        ice_posterior = ice_volume_samples[indices]
        
        return {
            "temperature": {
                "mean": float(np.mean(T_posterior)),
                "std": float(np.std(T_posterior)),
                "ci_lower": float(np.percentile(T_posterior, 2.5)),
                "ci_upper": float(np.percentile(T_posterior, 97.5))
            },
            "ice_volume": {
                "mean": float(np.mean(ice_posterior)),
                "std": float(np.std(ice_posterior)),
                "ci_lower": float(np.percentile(ice_posterior, 2.5)),
                "ci_upper": float(np.percentile(ice_posterior, 97.5))
            },
            "n_effective": int(np.sum(weights)**2 / np.sum(weights**2))
        }
    
    def ice_volume_correction(
        self,
        d18O_measured: float,
        ice_volume_m: float
    ) -> float:
        """
        Correct δ¹⁸O for ice volume effect.
        
        Each 10 m sea-level change ≈ 0.1 ‰ δ¹⁸O.
        
        Args:
            d18O_measured: Measured δ¹⁸O [‰]
            ice_volume_m: Ice volume in meters sea-level equivalent
        
        Returns:
            Ice-volume corrected δ¹⁸O [‰]
        """
        correction = ice_volume_m * 0.01  # 0.01 ‰ per meter
        return d18O_measured - correction
