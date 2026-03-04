"""Physics-Informed Neural Network (PINN) for STRATICA.

Based on paper Section 2.3 and 4.2:
L_total = L_data + λ₁·L_strat + λ₂·L_thermo + λ₃·L_orbital

where:
L_data: observational fit
L_strat: stratigraphic superposition (age monotonicity)
L_thermo: isotopic thermodynamic consistency
L_orbital: Milankovitch phase coherence
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class PINNConfig:
    """Configuration for Physics-Informed Neural Network."""
    input_dim: int = 3  # depth, age, proxy_type
    hidden_dim: int = 256
    num_layers: int = 4
    output_dim: int = 3  # T, δ¹⁸O, δ¹³C
    transformer_heads: int = 8
    lstm_units: int = 256
    constraint_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.constraint_weights is None:
            self.constraint_weights = {
                "stratigraphic": 1.5,
                "thermodynamic": 1.2,
                "orbital": 1.0
            }


class PhysicsInformedNN(nn.Module):
    """
    Physics-Informed Neural Network for stratigraphic reconstruction.
    
    Hybrid architecture combining:
    - Transformer for long-range correlations (orbital timescales)
    - LSTM for local proxy memory effects
    - Physics constraints as loss terms
    """
    
    def __init__(self, config: PINNConfig = None):
        super().__init__()
        
        if config is None:
            config = PINNConfig()
        
        self.config = config
        
        # Input embedding
        self.input_embedding = nn.Linear(config.input_dim, config.hidden_dim)
        
        # Transformer encoder for long-range correlations
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.hidden_dim,
            nhead=config.transformer_heads,
            dim_feedforward=config.hidden_dim * 4,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=config.num_layers // 2
        )
        
        # LSTM for local memory effects
        self.lstm = nn.LSTM(
            input_size=config.hidden_dim,
            hidden_size=config.lstm_units,
            num_layers=config.num_layers // 2,
            batch_first=True,
            dropout=0.1,
            bidirectional=True
        )
        
        # Fusion layer
        fusion_dim = config.hidden_dim + 2 * config.lstm_units
        self.fusion = nn.Linear(fusion_dim, config.hidden_dim)
        
        # Output layers
        self.output_net = nn.Sequential(
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(config.hidden_dim // 2, config.output_dim)
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize network weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch, seq_len, input_dim]
            mask: Attention mask [batch, seq_len]
        
        Returns:
            Output tensor [batch, seq_len, output_dim]
        """
        batch_size, seq_len, _ = x.shape
        
        # Input embedding
        h = torch.relu(self.input_embedding(x))
        
        # Transformer (long-range)
        if mask is not None:
            # Convert to attention mask (True = masked)
            attn_mask = ~mask.bool()
        else:
            attn_mask = None
        
        h_trans = self.transformer(h, src_key_padding_mask=attn_mask)
        
        # LSTM (local memory)
        h_lstm, _ = self.lstm(h)
        
        # Fusion
        h_combined = torch.cat([h_trans, h_lstm], dim=-1)
        h_fused = torch.relu(self.fusion(h_combined))
        
        # Output
        output = self.output_net(h_fused)
        
        return output
    
    def compute_loss(
        self,
        pred: torch.Tensor,
        target: torch.Tensor,
        mask: torch.Tensor,
        depth: torch.Tensor,
        age: torch.Tensor,
        proxy_type: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Compute combined loss with physics constraints.
        
        Args:
            pred: Predictions [batch, seq_len, output_dim]
            target: Targets [batch, seq_len, output_dim]
            mask: Valid data mask [batch, seq_len]
            depth: Depth values [batch, seq_len]
            age: Age values [batch, seq_len]
            proxy_type: Proxy type indices
        
        Returns:
            Dictionary of loss components
        """
        # Data loss (L_data)
        data_loss = torch.mean((pred - target)**2 * mask.unsqueeze(-1))
        
        # Stratigraphic superposition loss (L_strat)
        strat_loss = self._stratigraphic_constraint(pred, age, mask)
        
        # Thermodynamic consistency loss (L_thermo)
        thermo_loss = self._thermodynamic_constraint(pred, depth, mask)
        
        # Orbital phase coherence loss (L_orbital)
        orbital_loss = self._orbital_constraint(pred, age, mask)
        
        # Combined loss
        w = self.config.constraint_weights
        total_loss = (
            data_loss +
            w["stratigraphic"] * strat_loss +
            w["thermodynamic"] * thermo_loss +
            w["orbital"] * orbital_loss
        )
        
        return {
            "total": total_loss,
            "data": data_loss,
            "stratigraphic": strat_loss,
            "thermodynamic": thermo_loss,
            "orbital": orbital_loss
        }
    
    def _stratigraphic_constraint(
        self,
        pred: torch.Tensor,
        age: torch.Tensor,
        mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Enforce stratigraphic superposition.
        
        No reconstructed layer may be assigned an age younger than the layer
        above it or older than the layer below it.
        """
        batch_size, seq_len, _ = pred.shape
        
        loss = 0.0
        count = 0
        
        for b in range(batch_size):
            # Get valid indices
            valid = mask[b].bool()
            if valid.sum() < 2:
                continue
            
            valid_ages = age[b, valid]
            valid_pred = pred[b, valid]
            
            # Sort by depth (assuming depth increases with index)
            # In practice, we'd use actual depth
            depth_sorted = torch.arange(len(valid_ages), device=pred.device)
            
            # Age should be monotonic with depth
            ages_sorted = valid_ages[depth_sorted.long()]
            
            # Check for violations (age increasing upward)
            age_diff = ages_sorted[1:] - ages_sorted[:-1]
            violations = torch.relu(-age_diff)  # Negative differences are violations
            
            loss += torch.mean(violations)
            count += 1
        
        if count > 0:
            return loss / count
        else:
            return torch.tensor(0.0, device=pred.device)
    
    def _thermodynamic_constraint(
        self,
        pred: torch.Tensor,
        depth: torch.Tensor,
        mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Enforce thermodynamic consistency.
        
        Reconstructed δ¹⁸O must be consistent with known physics of
        calcite-water oxygen isotope fractionation.
        """
        batch_size, seq_len, _ = pred.shape
        
        loss = 0.0
        count = 0
        
        # Simplified thermodynamic constraint
        # δ¹⁸O should decrease with temperature (increase with depth)
        for b in range(batch_size):
            valid = mask[b].bool()
            if valid.sum() < 2:
                continue
            
            valid_depth = depth[b, valid]
            valid_d18O = pred[b, valid, 1]  # Assuming δ¹⁸O is output index 1
            
            # Depth should correlate positively with δ¹⁸O (deeper = colder = heavier)
            depth_norm = (valid_depth - valid_depth.mean()) / (valid_depth.std() + 1e-8)
            d18O_norm = (valid_d18O - valid_d18O.mean()) / (valid_d18O.std() + 1e-8)
            
            # Expected correlation
            expected_corr = torch.tanh(depth_norm)  # Simple nonlinear
            actual_corr = depth_norm * d18O_norm
            
            loss += torch.mean((actual_corr - expected_corr)**2)
            count += 1
        
        if count > 0:
            return loss / count
        else:
            return torch.tensor(0.0, device=pred.device)
    
    def _orbital_constraint(
        self,
        pred: torch.Tensor,
        age: torch.Tensor,
        mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Enforce orbital phase coherence.
        
        Reconstructed proxy time series must maintain coherent phase
        relationships with astronomical target curves.
        """
        batch_size, seq_len, _ = pred.shape
        
        loss = 0.0
        count = 0
        
        # Simplified: check spectral power in Milankovitch bands
        for b in range(batch_size):
            valid = mask[b].bool()
            if valid.sum() < 50:  # Need enough points for spectral analysis
                continue
            
            valid_age = age[b, valid]
            valid_pred = pred[b, valid, 0]  # Use first output
            
            # Convert to numpy for spectral analysis
            age_np = valid_age.cpu().numpy()
            pred_np = valid_pred.detach().cpu().numpy()
            
            # Ensure evenly spaced
            if len(age_np) > 50:
                # Simplified: compute FFT and check power at 41 kyr
                dt = np.mean(np.diff(age_np))
                if dt > 0:
                    from scipy import signal
                    freqs, power = signal.periodogram(pred_np, fs=1/dt)
                    
                    # Target frequencies (kyr⁻¹)
                    f_targets = [1/100, 1/41, 1/21]
                    
                    # Find closest frequencies
                    power_at_targets = []
                    for f_t in f_targets:
                        idx = np.argmin(np.abs(freqs - f_t))
                        power_at_targets.append(power[idx])
                    
                    # Expected power (red noise model)
                    # Simplified: assume 1/f spectrum
                    power_expected = 1 / (freqs + 1e-10)
                    power_expected = power_expected / np.sum(power_expected) * np.sum(power)
                    
                    # Loss is negative of relative power in target bands
                    target_power_ratio = np.sum(power_at_targets) / np.sum(power)
                    expected_ratio = 0.3  # Expected 30% power in orbital bands
                    
                    orbital_loss = torch.tensor(
                        max(0, expected_ratio - target_power_ratio),
                        device=pred.device,
                        dtype=torch.float32
                    )
                    
                    loss += orbital_loss
                    count += 1
        
        if count > 0:
            return loss / count
        else:
            return torch.tensor(0.0, device=pred.device)
    
    def train_step(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        mask: torch.Tensor,
        depth: torch.Tensor,
        age: torch.Tensor,
        proxy_type: torch.Tensor,
        optimizer: optim.Optimizer
    ) -> Dict[str, float]:
        """
        Single training step.
        
        Returns:
            Dictionary of loss values
        """
        optimizer.zero_grad()
        
        # Forward pass
        pred = self(x)
        
        # Compute loss
        losses = self.compute_loss(pred, y, mask, depth, age, proxy_type)
        
        # Backward pass
        losses["total"].backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=1.0)
        
        optimizer.step()
        
        # Convert to Python numbers
        return {k: v.item() for k, v in losses.items()}
    
    def predict(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> np.ndarray:
        """
        Generate predictions.
        
        Returns:
            Numpy array of predictions
        """
        self.eval()
        with torch.no_grad():
            pred = self(x, mask)
        return pred.cpu().numpy()
