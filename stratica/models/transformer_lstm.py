"""Transformer-LSTM hybrid model for temporal back-casting.

Based on paper Section 4:
- Transformer for long-range temporal correlations (405 kyr and 2.4 Myr cycles)
- LSTM for local proxy memory effects (δ¹³C reservoir adjustment ~5-10 kyr)
- Hybrid architecture for gap filling in geological records
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class TransformerLSTMConfig:
    """Configuration for Transformer-LSTM model."""
    input_dim: int = 1  # proxy value
    hidden_dim: int = 128
    num_layers: int = 3
    num_heads: int = 4
    dropout: float = 0.1
    max_seq_len: int = 1000
    lstm_units: int = 64
    output_dim: int = 1  # reconstructed proxy


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer."""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe.unsqueeze(0))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input."""
        return x + self.pe[:, :x.size(1)]


class TransformerLSTM(nn.Module):
    """
    Transformer-LSTM hybrid for temporal back-casting.
    
    Handles:
    - Long-range orbital cycles (405 kyr, 2.4 Myr) via transformer
    - Local memory effects (5-10 kyr) via LSTM
    - Gap filling in incomplete geological records
    """
    
    def __init__(self, config: TransformerLSTMConfig = None):
        super().__init__()
        
        if config is None:
            config = TransformerLSTMConfig()
        
        self.config = config
        
        # Input projection
        self.input_proj = nn.Linear(config.input_dim, config.hidden_dim)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(config.hidden_dim, config.max_seq_len)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.hidden_dim,
            nhead=config.num_heads,
            dim_feedforward=config.hidden_dim * 4,
            dropout=config.dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=config.num_layers
        )
        
        # LSTM for local memory
        self.lstm = nn.LSTM(
            input_size=config.hidden_dim,
            hidden_size=config.lstm_units,
            num_layers=2,
            batch_first=True,
            dropout=config.dropout,
            bidirectional=True
        )
        
        # Attention-based fusion
        self.attention = nn.MultiheadAttention(
            embed_dim=config.hidden_dim + 2 * config.lstm_units,
            num_heads=config.num_heads,
            dropout=config.dropout,
            batch_first=True
        )
        
        # Output layers
        self.output_net = nn.Sequential(
            nn.Linear(config.hidden_dim + 2 * config.lstm_units, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim, config.output_dim)
        )
        
        # Gap mask embedding
        self.mask_embedding = nn.Embedding(2, config.hidden_dim)
        
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights."""
        for name, param in self.named_parameters():
            if 'weight' in name and param.dim() >= 2:
                nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
        return_attention: bool = False
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor [batch, seq_len, input_dim]
            mask: Gap mask (1 = observed, 0 = gap) [batch, seq_len]
            return_attention: Whether to return attention weights
        
        Returns:
            Reconstructed tensor [batch, seq_len, output_dim]
        """
        batch_size, seq_len, _ = x.shape
        
        # Input projection
        h = self.input_proj(x)
        
        # Add mask embedding if provided
        if mask is not None:
            mask_emb = self.mask_embedding(mask.long())
            h = h + mask_emb
        
        # Positional encoding
        h = self.pos_encoder(h)
        
        # Transformer (long-range)
        # Create padding mask for transformer (True = masked)
        if mask is not None:
            src_key_padding_mask = (mask == 0)  # Gaps are masked
        else:
            src_key_padding_mask = None
        
        h_trans = self.transformer(h, src_key_padding_mask=src_key_padding_mask)
        
        # LSTM (local memory)
        h_lstm, _ = self.lstm(h)
        
        # Concatenate
        h_combined = torch.cat([h_trans, h_lstm], dim=-1)
        
        # Self-attention fusion
        h_attn, attn_weights = self.attention(h_combined, h_combined, h_combined)
        
        # Output
        output = self.output_net(h_attn)
        
        if return_attention:
            return output, attn_weights
        else:
            return output
    
    def backcast(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        max_iterations: int = 100,
        tolerance: float = 1e-4
    ) -> np.ndarray:
        """
        Fill gaps in time series using iterative back-casting.
        
        Args:
            x: Input tensor with gaps [batch, seq_len, input_dim]
            mask: Gap mask (1 = observed, 0 = gap)
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
        
        Returns:
            Filled tensor
        """
        self.eval()
        
        with torch.no_grad():
            # Initialize with linear interpolation
            x_filled = x.clone()
            for b in range(x.size(0)):
                for i in range(x.size(2)):
                    observed_idx = torch.where(mask[b, :] == 1)[0].cpu().numpy()
                    observed_vals = x[b, observed_idx, i].cpu().numpy()
                    
                    if len(observed_idx) > 1:
                        from scipy import interpolate
                        f = interpolate.interp1d(
                            observed_idx, observed_vals,
                            kind='linear',
                            bounds_error=False,
                            fill_value='extrapolate'
                        )
                        all_idx = np.arange(x.size(1))
                        x_filled[b, :, i] = torch.tensor(f(all_idx), device=x.device)
            
            # Iterative refinement
            for iteration in range(max_iterations):
                x_old = x_filled.clone()
                
                # Forward pass
                x_recon = self(x_filled, mask)
                
                # Update only gap positions
                for b in range(x.size(0)):
                    for i in range(x.size(1)):
                        if mask[b, i] == 0:  # Gap
                            x_filled[b, i] = x_recon[b, i]
                
                # Check convergence
                diff = torch.max(torch.abs(x_filled - x_old))
                if diff < tolerance:
                    break
        
        return x_filled.cpu().numpy()
    
    def temporal_attention_weights(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> np.ndarray:
        """
        Extract temporal attention weights for interpretability.
        
        Shows which time points are most influential for reconstruction.
        """
        self.eval()
        with torch.no_grad():
            _, attn_weights = self(x, mask, return_attention=True)
        
        return attn_weights.cpu().numpy()


class TemporalBackcast:
    """High-level interface for temporal back-casting."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize back-casting model.
        
        Args:
            model_path: Path to pre-trained model weights
        """
        self.config = TransformerLSTMConfig()
        self.model = TransformerLSTM(self.config)
        
        if model_path:
            self.model.load_state_dict(torch.load(model_path))
        
        self.model.eval()
    
    def fill_gaps(
        self,
        timeseries: np.ndarray,
        mask: Optional[np.ndarray] = None,
        **kwargs
    ) -> np.ndarray:
        """
        Fill gaps in time series.
        
        Args:
            timeseries: Time series array [seq_len] or [batch, seq_len, features]
            mask: Gap mask (1 = observed, 0 = gap) same shape as timeseries
        
        Returns:
            Filled time series
        """
        # Convert to tensor
        if timeseries.ndim == 1:
            timeseries = timeseries.reshape(1, -1, 1)
        elif timeseries.ndim == 2:
            timeseries = timeseries.reshape(timeseries.shape[0], timeseries.shape[1], 1)
        
        x = torch.tensor(timeseries, dtype=torch.float32)
        
        if mask is None:
            # Assume all observed
            mask = torch.ones_like(x[:, :, 0])
        else:
            if mask.ndim == 1:
                mask = mask.reshape(1, -1)
            elif mask.ndim == 2 and mask.shape[0] != x.size(0):
                mask = mask.reshape(1, -1)
            mask = torch.tensor(mask, dtype=torch.float32)
        
        # Fill gaps
        filled = self.model.backcast(x, mask, **kwargs)
        
        # Return in original shape
        if timeseries.shape[0] == 1 and timeseries.shape[2] == 1:
            return filled[0, :, 0]
        elif timeseries.shape[2] == 1:
            return filled[:, :, 0]
        else:
            return filled
    
    def uncertainty_estimate(
        self,
        timeseries: np.ndarray,
        mask: np.ndarray,
        n_samples: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Estimate uncertainty in gap filling using Monte Carlo dropout.
        
        Returns:
            Mean and standard deviation of predictions
        """
        # Enable dropout during inference
        self.model.train()
        
        x = torch.tensor(timeseries, dtype=torch.float32)
        m = torch.tensor(mask, dtype=torch.float32)
        
        predictions = []
        for _ in range(n_samples):
            with torch.no_grad():
                pred = self.model(x, m)
            predictions.append(pred.numpy())
        
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        self.model.eval()
        
        return mean_pred, std_pred
