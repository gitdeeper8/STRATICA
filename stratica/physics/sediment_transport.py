"""Sediment transport and mass balance equations.

Based on paper Section 3.1:
d(ρ_b)/dt = -d(M_dot)/dz + S(z,t)

where:
ρ_b = bulk density [kg/m³]
M_dot = mass flux [kg/m²/yr]
S = source/sink term
"""

import numpy as np
from typing import Tuple, Optional, Callable
from scipy import integrate


class SedimentTransport:
    """Sediment transport and mass balance calculations."""
    
    def __init__(self, rho_g: float = 2650, phi_0: float = 0.5, c: float = 5e-4):
        """
        Initialize sediment transport model.
        
        Args:
            rho_g: Grain density [kg/m³] (default: 2650 for quartz)
            phi_0: Surface porosity (default: 0.5)
            c: Compaction coefficient [m⁻¹] (default: 5e-4)
        """
        self.rho_g = rho_g
        self.phi_0 = phi_0
        self.c = c
    
    def bulk_density(self, porosity: np.ndarray) -> np.ndarray:
        """Calculate bulk density from porosity."""
        return self.rho_g * (1 - porosity)
    
    def porosity(self, bulk_density: np.ndarray) -> np.ndarray:
        """Calculate porosity from bulk density."""
        return 1 - bulk_density / self.rho_g
    
    def athy_compaction(self, depth: np.ndarray) -> np.ndarray:
        """
        Athy's compaction law: φ(z) = φ_0 * exp(-c * z)
        
        Args:
            depth: Depth array [m]
        
        Returns:
            Porosity at each depth
        """
        return self.phi_0 * np.exp(-self.c * depth)
    
    def decompact_thickness(
        self,
        current_thickness: float,
        top_depth: float,
        bottom_depth: float,
        n_points: int = 100
    ) -> float:
        """
        Calculate decompacted thickness at surface.
        
        Uses conservation of solid volume:
        ∫ (1-φ(z)) dz = constant
        
        Args:
            current_thickness: Current layer thickness [m]
            top_depth: Top depth [m]
            bottom_depth: Bottom depth [m]
            n_points: Number of integration points
        
        Returns:
            Decompacted thickness at surface [m]
        """
        # Current porosity profile
        z_current = np.linspace(top_depth, bottom_depth, n_points)
        phi_current = self.athy_compaction(z_current)
        
        # Solid volume fraction
        solid_current = np.trapz(1 - phi_current, z_current)
        
        # At surface, porosity = φ_0
        solid_surface = (1 - self.phi_0) * current_thickness
        
        # Decompacted thickness preserves solid volume
        decompacted = solid_current / (1 - self.phi_0)
        
        return float(decompacted)
    
    def sedimentation_rate(
        self,
        mass_flux: float,
        bulk_density: float
    ) -> float:
        """
        Calculate sedimentation rate from mass flux.
        
        Args:
            mass_flux: Sediment mass flux [kg/m²/yr]
            bulk_density: Bulk density [kg/m³]
        
        Returns:
            Sedimentation rate [m/yr]
        """
        if bulk_density <= 0:
            return 0.0
        
        return mass_flux / bulk_density
    
    def mass_balance_1d(
        self,
        z: np.ndarray,
        t: np.ndarray,
        initial_porosity: np.ndarray,
        source_term: Optional[Callable] = None,
        boundary_flux: Tuple[float, float] = (0, 0)
    ) -> np.ndarray:
        """
        Solve 1D mass balance equation:
        d(ρ_b)/dt = -d(M_dot)/dz + S(z,t)
        
        Args:
            z: Depth grid [m]
            t: Time grid [yr]
            initial_porosity: Initial porosity profile
            source_term: Function S(z,t) returning source/sink
            boundary_flux: Mass flux at top and bottom [kg/m²/yr]
        
        Returns:
            Bulk density evolution [n_time, n_depth]
        """
        nz = len(z)
        nt = len(t)
        dz = z[1] - z[0] if nz > 1 else 1.0
        
        # Initial bulk density
        rho_b = np.zeros((nt, nz))
        rho_b[0] = self.bulk_density(initial_porosity)
        
        # Time stepping
        for i in range(1, nt):
            dt = t[i] - t[i-1]
            
            # Flux gradient term
            if nz > 2:
                # Simple diffusion-like term (simplified)
                flux_gradient = np.zeros(nz)
                flux_gradient[1:-1] = (
                    rho_b[i-1, 2:] - 2*rho_b[i-1, 1:-1] + rho_b[i-1, :-2]
                ) / dz**2 * 1e-6  # Diffusivity factor
                
                # Apply boundary fluxes
                flux_gradient[0] = boundary_flux[0] / dz
                flux_gradient[-1] = -boundary_flux[1] / dz
            else:
                flux_gradient = np.zeros(nz)
            
            # Source term
            if source_term is not None:
                S = source_term(z, t[i])
            else:
                S = np.zeros(nz)
            
            # Update
            rho_b[i] = rho_b[i-1] + dt * (-flux_gradient + S)
            
            # Ensure positivity
            rho_b[i] = np.maximum(rho_b[i], 100)
        
        return rho_b
    
    def basin_subsidence(
        self,
        sediment_thickness: np.ndarray,
        water_depth: np.ndarray,
        isostasy_factor: float = 0.7
    ) -> np.ndarray:
        """
        Calculate total basin subsidence including isostatic compensation.
        
        Args:
            sediment_thickness: Sediment thickness through time [m]
            water_depth: Water depth through time [m]
            isostasy_factor: Isostatic compensation factor (0.6-0.8)
        
        Returns:
            Total subsidence [m]
        """
        # Airy isostasy: subsidence = sediment_thickness * (ρ_m - ρ_s)/(ρ_m - ρ_w)
        # Simplified: use factor
        tectonic_subsidence = sediment_thickness * isostasy_factor
        
        return tectonic_subsidence + water_depth
    
    def sediment_supply_rate(
        self,
        drainage_area: float,
        erosion_rate: float,
        trapping_efficiency: float = 0.5
    ) -> float:
        """
        Estimate sediment supply rate from drainage basin.
        
        Args:
            drainage_area: Drainage basin area [km²]
            erosion_rate: Erosion rate [mm/yr]
            trapping_efficiency: Fraction trapped in basin (0-1)
        
        Returns:
            Sediment supply rate [kg/yr]
        """
        # Convert units
        area_m2 = drainage_area * 1e6
        erosion_m_per_yr = erosion_rate * 1e-3
        
        # Volume eroded per year
        volume_eroded = area_m2 * erosion_m_per_yr
        
        # Mass (assuming density 2650 kg/m³)
        mass_eroded = volume_eroded * self.rho_g
        
        return mass_eroded * trapping_efficiency
