"""Sediment compaction models.

Based on paper Section 3.1:
- Athy's compaction law: φ(z) = φ_0 * exp(-c * z)
- Porosity-depth relationships
- Decompaction calculations
"""

import numpy as np
from typing import Dict, Optional, Tuple
from scipy import integrate, optimize


class CompactionModel:
    """Sediment compaction calculations."""
    
    def __init__(
        self,
        phi_0: float = 0.5,
        c: float = 5e-4,
        lithology: str = "siliciclastic"
    ):
        """
        Initialize compaction model.
        
        Args:
            phi_0: Surface porosity
            c: Compaction coefficient [m⁻¹]
            lithology: "siliciclastic", "carbonate", or "shale"
        """
        self.phi_0 = phi_0
        self.c = c
        self.lithology = lithology
        
        # Lithology-specific parameters
        if lithology == "siliciclastic":
            self.phi_0 = 0.5
            self.c = 5e-4
        elif lithology == "carbonate":
            self.phi_0 = 0.7
            self.c = 3e-4
        elif lithology == "shale":
            self.phi_0 = 0.6
            self.c = 4e-4
    
    def athy_porosity(self, depth: np.ndarray) -> np.ndarray:
        """
        Athy's law: φ(z) = φ_0 * exp(-c * z)
        
        Args:
            depth: Depth array [m]
        
        Returns:
            Porosity at each depth
        """
        return self.phi_0 * np.exp(-self.c * depth)
    
    def inverse_athy(self, porosity: np.ndarray) -> np.ndarray:
        """
        Inverse of Athy's law: z = -(1/c) * ln(φ/φ_0)
        
        Args:
            porosity: Porosity array
        
        Returns:
            Depth [m]
        """
        return -(1/self.c) * np.log(porosity / self.phi_0)
    
    def solid_thickness(
        self,
        top_depth: float,
        bottom_depth: float,
        n_points: int = 100
    ) -> float:
        """
        Calculate solid equivalent thickness.
        
        ∫ (1 - φ(z)) dz
        
        Args:
            top_depth: Top depth [m]
            bottom_depth: Bottom depth [m]
            n_points: Number of integration points
        
        Returns:
            Solid thickness [m]
        """
        z = np.linspace(top_depth, bottom_depth, n_points)
        phi = self.athy_porosity(z)
        solid = np.trapz(1 - phi, z)
        
        return float(solid)
    
    def decompact(
        self,
        current_thickness: float,
        current_top: float,
        current_bottom: float,
        target_top: float = 0
    ) -> float:
        """
        Decompact layer to different burial depth.
        
        Conserves solid volume:
        ∫ (1 - φ(z)) dz = constant
        
        Args:
            current_thickness: Current layer thickness [m]
            current_top: Current top depth [m]
            current_bottom: Current bottom depth [m]
            target_top: Target top depth [m]
        
        Returns:
            Decompacted thickness at target depth [m]
        """
        # Current solid thickness
        solid_current = self.solid_thickness(current_top, current_bottom)
        
        # Find bottom depth that gives same solid thickness
        def solid_diff(bottom):
            solid = self.solid_thickness(target_top, bottom)
            return solid - solid_current
        
        try:
            result = optimize.root_scalar(
                solid_diff,
                bracket=[target_top + 1, target_top + 10 * current_thickness]
            )
            target_bottom = result.root
            target_thickness = target_bottom - target_top
        except:
            # Fallback: approximate
            target_thickness = solid_current / (1 - self.phi_0)
        
        return float(target_thickness)
    
    def burial_history(
        self,
        layer_depths: np.ndarray,
        layer_thicknesses: np.ndarray,
        ages: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Reconstruct burial history through time.
        
        Args:
            layer_depths: Current depths of layer tops [m]
            layer_thicknesses: Current layer thicknesses [m]
            ages: Ages at which to reconstruct [Ma]
        
        Returns:
            Dictionary with reconstructed depths and thicknesses
        """
        n_layers = len(layer_depths)
        n_ages = len(ages)
        
        # Sort by depth
        sort_idx = np.argsort(layer_depths)
        depths_sorted = layer_depths[sort_idx]
        thick_sorted = layer_thicknesses[sort_idx]
        
        # Current bottoms
        bottoms_sorted = depths_sorted + thick_sorted
        
        # Reconstructed arrays
        recon_depths = np.zeros((n_ages, n_layers))
        recon_thicks = np.zeros((n_ages, n_layers))
        
        # For each age, decompact all layers to shallower depth
        for i, age in enumerate(ages):
            # Simple linear interpolation of burial depth
            burial_factor = age / np.max(ages) if np.max(ages) > 0 else 1
            
            for j in range(n_layers):
                # Current depth at this age (simplified)
                if j == 0:
                    top = depths_sorted[j] * burial_factor
                else:
                    # Top of lower layer is bottom of upper layer
                    top = recon_depths[i, j-1] + recon_thicks[i, j-1]
                
                # Decompact this layer
                bottom = self.decompact(
                    thick_sorted[j],
                    depths_sorted[j],
                    bottoms_sorted[j],
                    top
                ) + top
                
                recon_depths[i, j] = top
                recon_thicks[i, j] = bottom - top
        
        return {
            "depths": recon_depths,
            "thicknesses": recon_thicks,
            "ages": ages
        }
    
    def porosity_from_resistivity(
        self,
        resistivity: np.ndarray,
        formation_factor: float = 0.8,
        water_resistivity: float = 0.1
    ) -> np.ndarray:
        """
        Estimate porosity from resistivity log.
        
        Using Archie's law: F = a / φ^m
        
        Args:
            resistivity: Formation resistivity [ohm-m]
            formation_factor: Formation factor exponent (a)
            water_resistivity: Pore water resistivity [ohm-m]
        
        Returns:
            Porosity estimate
        """
        # Simplified Archie: φ = (a * R_w / R_t)^(1/m)
        m = 2.0  # Cementation exponent
        
        phi = (formation_factor * water_resistivity / resistivity) ** (1/m)
        
        return np.clip(phi, 0, self.phi_0)
    
    def velocity_to_porosity(
        self,
        velocity: np.ndarray,
        v_matrix: float = 5500,
        v_fluid: float = 1500
    ) -> np.ndarray:
        """
        Estimate porosity from sonic velocity.
        
        Using Wyllie time-average equation:
        1/v = (1-φ)/v_matrix + φ/v_fluid
        
        Args:
            velocity: Compressional wave velocity [m/s]
            v_matrix: Matrix velocity [m/s]
            v_fluid: Fluid velocity [m/s]
        
        Returns:
            Porosity estimate
        """
        inv_v = 1 / velocity
        inv_v_matrix = 1 / v_matrix
        inv_v_fluid = 1 / v_fluid
        
        phi = (inv_v - inv_v_matrix) / (inv_v_fluid - inv_v_matrix)
        
        return np.clip(phi, 0, self.phi_0)
    
    def density_to_porosity(
        self,
        density: np.ndarray,
        rho_matrix: float = 2650,
        rho_fluid: float = 1000
    ) -> np.ndarray:
        """
        Estimate porosity from bulk density.
        
        ρ_b = (1-φ)ρ_matrix + φ ρ_fluid
        
        Args:
            density: Bulk density [kg/m³]
            rho_matrix: Matrix density [kg/m³]
            rho_fluid: Fluid density [kg/m³]
        
        Returns:
            Porosity estimate
        """
        phi = (rho_matrix - density) / (rho_matrix - rho_fluid)
        
        return np.clip(phi, 0, self.phi_0)
    
    def compaction_coefficient_from_data(
        self,
        depth: np.ndarray,
        porosity: np.ndarray
    ) -> float:
        """
        Estimate compaction coefficient c from porosity-depth data.
        
        Fit φ = φ_0 * exp(-c * z)
        
        Returns:
            Estimated c [m⁻¹]
        """
        if len(depth) < 3:
            return self.c
        
        # Take log
        log_phi = np.log(np.clip(porosity, 0.01, 0.9))
        
        # Linear fit
        coeffs = np.polyfit(depth, log_phi, 1)
        c_fitted = -coeffs[0]
        
        if c_fitted > 0:
            return float(c_fitted)
        else:
            return self.c
