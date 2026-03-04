"""TDM - Thermal Diffusion Model parameter.

Based on paper Section 3.8:
dT/dt = κ * d²T/dz² + A(z) / (ρ * C_p)

where:
κ = thermal diffusivity [m²/s]
A = radiogenic heat production [W/m³]
ρ * C_p = volumetric heat capacity
"""

import numpy as np
from typing import Dict, Any, Optional

from stratica.parameters.base import ParameterBase
from stratica.utils.constants import THERMAL_DIFFUSIVITY


class ThermalDiffusionModel(ParameterBase):
    """
    TDM: Thermal Diffusion Model (8% weight).
    
    Models heat flow and thermal evolution of sedimentary basins,
    providing constraints on burial depth, thermal maturity, and
    radiogenic heat production.
    
    Key applications:
    - Burial history reconstruction
    - Thermal maturity for hydrocarbon generation
    - Paleogeothermal gradient estimation
    """
    
    def __init__(self, weight: float = 0.08, config: Optional[Dict] = None):
        super().__init__(name="TDM", weight=weight, config=config)
        
        self.kappa = self.config.get("kappa", THERMAL_DIFFUSIVITY["kappa_sediment"])
        self.radiogenic = self.config.get("radiogenic", THERMAL_DIFFUSIVITY["radiogenic_avg"])
        self.heat_capacity = self.config.get("heat_capacity", THERMAL_DIFFUSIVITY["heat_capacity"])
        
        self.heat_flow_model = self.config.get("heat_flow_model", "steady_state")
    
    def compute(self, data: Dict[str, Any]) -> float:
        """
        Compute raw TDM score from thermal data.
        
        Expected data keys:
            - depth: array of depths [m]
            - temperature: array of measured temperatures [°C]
            - thermal_conductivity: array [W/m/K]
            - heat_flow: surface heat flow [mW/m²]
            - age: array of ages [Ma]
        
        Returns:
            Raw TDM score (0-1) based on model-data fit
        """
        depth = np.array(data.get("depth", []))
        temp = np.array(data.get("temperature", []))
        
        if len(depth) < 3 or len(temp) < 3:
            return 0.0
        
        # Calculate geothermal gradient
        gradient, r_squared = self._calculate_gradient(depth, temp)
        
        # Predict temperatures using diffusion model
        if "heat_flow" in data:
            heat_flow = data["heat_flow"]
            k = data.get("thermal_conductivity", 2.0)
            
            # Steady-state: T(z) = T_surface + (q/k) * z
            if isinstance(heat_flow, (int, float)):
                q = heat_flow * 1e-3  # mW/m² to W/m²
                T_pred = data.get("surface_temp", 10) + (q / k) * depth
                
                # Calculate RMS error
                if len(T_pred) == len(temp):
                    rms_error = np.sqrt(np.mean((temp - T_pred)**2))
                    
                    # Score based on RMS (lower is better)
                    if rms_error < 5:
                        model_score = 1.0
                    elif rms_error < 10:
                        model_score = 0.7
                    elif rms_error < 20:
                        model_score = 0.4
                    else:
                        model_score = 0.1
                else:
                    model_score = 0.5
            else:
                model_score = 0.5
        else:
            model_score = 0.5
        
        # Combine gradient quality and model fit
        tdm_raw = 0.3 * r_squared + 0.7 * model_score
        
        return float(tdm_raw)
    
    def _calculate_gradient(self, depth: np.ndarray, temp: np.ndarray) -> tuple:
        """Calculate geothermal gradient and fit quality."""
        if len(depth) < 2:
            return 0.0, 0.0
        
        # Linear regression
        coeffs = np.polyfit(depth, temp, 1)
        gradient = coeffs[0] * 1000  # Convert to °C/km
        
        # Calculate R²
        temp_pred = np.polyval(coeffs, depth)
        ss_res = np.sum((temp - temp_pred)**2)
        ss_tot = np.sum((temp - np.mean(temp))**2)
        
        if ss_tot > 0:
            r_squared = 1 - ss_res / ss_tot
        else:
            r_squared = 0.0
        
        return float(gradient), float(r_squared)
    
    def solve_1d_heat_equation(
        self,
        depth: np.ndarray,
        time: np.ndarray,
        boundary_temp: float = 10,
        basal_heat_flow: float = 60,
        **kwargs
    ) -> np.ndarray:
        """
        Solve 1D heat diffusion equation.
        
        dT/dt = κ * d²T/dz² + A/(ρCp)
        
        Returns:
            Temperature array [time, depth]
        """
        nz = len(depth)
        nt = len(time)
        
        dz = depth[1] - depth[0] if nz > 1 else 1.0
        dt = time[1] - time[0] if nt > 1 else 1e3 * 365 * 24 * 3600  # seconds
        
        # Stability criterion
        stability = self.kappa * dt / dz**2
        if stability > 0.5:
            # Reduce dt for stability
            dt = 0.4 * dz**2 / self.kappa
            nt = int((time[-1] - time[0]) / dt) + 1
            time_new = np.linspace(time[0], time[-1], nt)
        else:
            time_new = time
            nt = len(time_new)
        
        # Initialize temperature array
        T = np.zeros((nt, nz))
        T[0, :] = boundary_temp + basal_heat_flow * 1e-3 * depth / 2  # Initial guess
        
        # Radiogenic heat production term
        A = self.radiogenic * np.ones(nz)
        
        # Time stepping
        for i in range(1, nt):
            T[i, 1:-1] = T[i-1, 1:-1] + self.kappa * dt / dz**2 * (
                T[i-1, 2:] - 2*T[i-1, 1:-1] + T[i-1, :-2]
            ) + A[1:-1] * dt / self.heat_capacity
            
            # Boundary conditions
            T[i, 0] = boundary_temp  # Surface
            T[i, -1] = T[i, -2] + basal_heat_flow * 1e-3 * dz / 2  # Basal heat flow
        
        if nt != len(time):
            # Interpolate back to original time points
            from scipy import interpolate
            f = interpolate.interp1d(time_new, T, axis=0, kind='linear')
            T = f(time)
        
        return T
    
    def estimate_burial_depth(
        self,
        temperature: float,
        gradient: float,
        surface_temp: float = 10
    ) -> float:
        """Estimate burial depth from temperature."""
        if gradient <= 0:
            return 0.0
        
        depth = (temperature - surface_temp) / (gradient / 1000)  # km
        return float(depth)
    
    def thermal_maturity(self, temperature: float, time_myr: float) -> str:
        """
        Estimate thermal maturity for hydrocarbons.
        
        Simplified vitrinite reflectance proxy.
        """
        # Time-temperature index (simplified)
        tti = time_myr * np.exp((temperature - 100) / 50)
        
        if tti < 15:
            return "immature"
        elif tti < 75:
            return "oil_window"
        elif tti < 200:
            return "gas_window"
        else:
            return "overmature"
    
    def normalize(self, value: float) -> float:
        """Normalize TDM score to [0,1]."""
        return np.clip(value, 0, 1)
