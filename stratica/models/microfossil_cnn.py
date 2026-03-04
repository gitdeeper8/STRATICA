"""CNN for microfossil classification.

Based on paper Section 3.3:
- Trained on MIKROTAX and Neptune Sandbox Berlin databases (~2.3 million images)
- 93.4% species-level accuracy on held-out specimens
- Exceeds manual expert performance for rare and poorly preserved taxa
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from torch.utils.data import Dataset, DataLoader


@dataclass
class CNNConfig:
    """Configuration for microfossil CNN."""
    input_channels: int = 3  # RGB
    input_height: int = 224
    input_width: int = 224
    num_classes: int = 150  # Number of microfossil species
    base_filters: int = 64
    dropout: float = 0.3
    confidence_threshold: float = 0.85


class MicrofossilDataset(Dataset):
    """Dataset for microfossil images."""
    
    def __init__(self, images: np.ndarray, labels: np.ndarray, transform=None):
        """
        Args:
            images: Image array [N, H, W, C]
            labels: Label indices [N]
            transform: Optional transforms
        """
        self.images = images
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        
        # Convert to tensor and normalize
        if isinstance(image, np.ndarray):
            if image.max() > 1:
                image = image / 255.0
            image = torch.tensor(image, dtype=torch.float32)
            if image.ndim == 2:  # Grayscale
                image = image.unsqueeze(0).repeat(3, 1, 1)
            elif image.ndim == 3 and image.shape[-1] == 3:  # HWC
                image = image.permute(2, 0, 1)  # CHW
        
        if self.transform:
            image = self.transform(image)
        
        return image, torch.tensor(label, dtype=torch.long)


class ConvBlock(nn.Module):
    """Convolutional block with batch norm and ReLU."""
    
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        return self.relu(self.bn(self.conv(x)))


class MicrofossilCNN(nn.Module):
    """
    CNN for microfossil classification.
    
    Architecture:
    - 5 convolutional blocks with increasing filters
    - Global average pooling
    - Fully connected classifier
    - Achieves 93.4% species-level accuracy
    """
    
    def __init__(self, config: CNNConfig = None):
        super().__init__()
        
        if config is None:
            config = CNNConfig()
        
        self.config = config
        self.num_classes = config.num_classes
        self.confidence_threshold = config.confidence_threshold
        
        # Convolutional layers
        filters = config.base_filters
        
        self.conv1 = ConvBlock(config.input_channels, filters)
        self.conv2 = ConvBlock(filters, filters * 2)
        self.conv3 = ConvBlock(filters * 2, filters * 4)
        self.conv4 = ConvBlock(filters * 4, filters * 8)
        self.conv5 = ConvBlock(filters * 8, filters * 16)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        
        # Global average pooling
        self.gap = nn.AdaptiveAvgPool2d(1)
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(filters * 16, 512),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(256, config.num_classes)
        )
        
        # Attention module for interpretability
        self.attention = nn.Sequential(
            nn.Conv2d(filters * 16, 1, kernel_size=1),
            nn.Sigmoid()
        )
        
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x, return_features=False):
        """
        Forward pass.
        
        Args:
            x: Input images [batch, C, H, W]
            return_features: Whether to return attention maps
        
        Returns:
            Logits or (logits, attention_maps)
        """
        # Convolutional layers with pooling
        x = self.pool(self.conv1(x))
        x = self.pool(self.conv2(x))
        x = self.pool(self.conv3(x))
        x = self.pool(self.conv4(x))
        x = self.pool(self.conv5(x))
        
        # Attention maps
        attn = self.attention(x)
        
        # Global average pooling
        features = self.gap(x)
        features = features.view(features.size(0), -1)
        
        # Classifier
        features = self.dropout(features)
        logits = self.classifier(features)
        
        if return_features:
            return logits, attn
        else:
            return logits
    
    def predict(self, x: torch.Tensor) -> Dict[str, Any]:
        """
        Predict species with confidence scores.
        
        Returns:
            Dictionary with predictions and confidence
        """
        self.eval()
        with torch.no_grad():
            logits = self(x)
            probs = F.softmax(logits, dim=1)
            
            # Get top predictions
            top_probs, top_indices = torch.topk(probs, k=5, dim=1)
            
            # Check confidence threshold
            confident = top_probs[:, 0] >= self.confidence_threshold
        
        return {
            'probabilities': probs.cpu().numpy(),
            'top_classes': top_indices.cpu().numpy(),
            'top_confidences': top_probs.cpu().numpy(),
            'confident': confident.cpu().numpy()
        }
    
    def extract_features(self, x: torch.Tensor) -> np.ndarray:
        """Extract feature vectors for images."""
        self.eval()
        with torch.no_grad():
            # Forward to feature layer
            x = self.pool(self.conv1(x))
            x = self.pool(self.conv2(x))
            x = self.pool(self.conv3(x))
            x = self.pool(self.conv4(x))
            x = self.pool(self.conv5(x))
            features = self.gap(x)
            features = features.view(features.size(0), -1)
        
        return features.cpu().numpy()
    
    def train_step(
        self,
        images: torch.Tensor,
        labels: torch.Tensor,
        optimizer: optim.Optimizer,
        criterion: nn.Module
    ) -> Dict[str, float]:
        """Single training step."""
        self.train()
        optimizer.zero_grad()
        
        # Forward
        logits = self(images)
        loss = criterion(logits, labels)
        
        # Backward
        loss.backward()
        optimizer.step()
        
        # Calculate accuracy
        preds = logits.argmax(dim=1)
        accuracy = (preds == labels).float().mean()
        
        return {
            'loss': loss.item(),
            'accuracy': accuracy.item()
        }
    
    def validate(
        self,
        dataloader: DataLoader,
        criterion: nn.Module
    ) -> Dict[str, float]:
        """Validation loop."""
        self.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0
        
        with torch.no_grad():
            for images, labels in dataloader:
                logits = self(images)
                loss = criterion(logits, labels)
                
                preds = logits.argmax(dim=1)
                total_loss += loss.item() * images.size(0)
                total_correct += (preds == labels).sum().item()
                total_samples += images.size(0)
        
        return {
            'loss': total_loss / total_samples,
            'accuracy': total_correct / total_samples
        }


class MicrofossilClassifier:
    """High-level interface for microfossil classification."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        """
        Initialize classifier.
        
        Args:
            model_path: Path to pre-trained model
            device: 'cpu' or 'cuda'
        """
        self.config = CNNConfig()
        self.model = MicrofossilCNN(self.config)
        self.device = torch.device(device)
        
        if model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=device))
        
        self.model.to(device)
        self.model.eval()
        
        # Class names (simplified - would load from file)
        self.class_names = self._load_class_names()
    
    def _load_class_names(self) -> List[str]:
        """Load class names from reference file."""
        # Simplified - would load from taxonomy database
        return [f"Species_{i}" for i in range(self.config.num_classes)]
    
    def classify_image(
        self,
        image: np.ndarray,
        return_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Classify a single microfossil image.
        
        Args:
            image: Image array [H, W, C] or [H, W]
            return_confidence: Whether to return confidence scores
        
        Returns:
            Dictionary with classification results
        """
        # Preprocess
        if image.ndim == 2:
            image = np.stack([image] * 3, axis=-1)
        
        # Resize if needed
        if image.shape[0] != self.config.input_height or image.shape[1] != self.config.input_width:
            from skimage.transform import resize
            image = resize(image, (self.config.input_height, self.config.input_width))
        
        # Convert to tensor
        if image.max() > 1:
            image = image / 255.0
        
        image_tensor = torch.tensor(image, dtype=torch.float32)
        image_tensor = image_tensor.permute(2, 0, 1).unsqueeze(0)
        image_tensor = image_tensor.to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.model(image_tensor)
            probs = F.softmax(logits, dim=1)
        
        # Get top predictions
        top_probs, top_indices = torch.topk(probs, k=5, dim=1)
        
        results = {
            'top_species': [self.class_names[idx] for idx in top_indices[0].cpu().numpy()],
            'top_confidences': top_probs[0].cpu().numpy().tolist()
        }
        
        if return_confidence:
            results['confidence'] = float(top_probs[0, 0].item())
            results['confident'] = top_probs[0, 0].item() >= self.config.confidence_threshold
        
        return results
    
    def classify_batch(
        self,
        images: np.ndarray,
        batch_size: int = 32
    ) -> Dict[str, np.ndarray]:
        """
        Classify a batch of images.
        
        Args:
            images: Image array [N, H, W, C]
            batch_size: Batch size for processing
        
        Returns:
            Dictionary with predictions
        """
        n_images = len(images)
        all_probs = []
        
        for i in range(0, n_images, batch_size):
            batch = images[i:i+batch_size]
            batch_tensor = []
            
            for img in batch:
                # Preprocess
                if img.ndim == 2:
                    img = np.stack([img] * 3, axis=-1)
                
                if img.shape[0] != self.config.input_height or img.shape[1] != self.config.input_width:
                    from skimage.transform import resize
                    img = resize(img, (self.config.input_height, self.config.input_width))
                
                if img.max() > 1:
                    img = img / 255.0
                
                img_tensor = torch.tensor(img, dtype=torch.float32)
                img_tensor = img_tensor.permute(2, 0, 1)
                batch_tensor.append(img_tensor)
            
            batch_tensor = torch.stack(batch_tensor).to(self.device)
            
            with torch.no_grad():
                logits = self.model(batch_tensor)
                probs = F.softmax(logits, dim=1)
                all_probs.append(probs.cpu().numpy())
        
        all_probs = np.concatenate(all_probs, axis=0)
        top_classes = np.argmax(all_probs, axis=1)
        top_confidences = np.max(all_probs, axis=1)
        
        return {
            'probabilities': all_probs,
            'top_classes': top_classes,
            'top_confidences': top_confidences,
            'confident': top_confidences >= self.config.confidence_threshold
        }
    
    def train(
        self,
        train_images: np.ndarray,
        train_labels: np.ndarray,
        val_images: Optional[np.ndarray] = None,
        val_labels: Optional[np.ndarray] = None,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001
    ) -> Dict[str, List[float]]:
        """
        Train the classifier.
        
        Returns:
            Training history
        """
        # Create datasets
        train_dataset = MicrofossilDataset(train_images, train_labels)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        val_loader = None
        if val_images is not None and val_labels is not None:
            val_dataset = MicrofossilDataset(val_images, val_labels)
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Setup
        self.model.train()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)
        criterion = nn.CrossEntropyLoss()
        
        history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        for epoch in range(epochs):
            # Training
            epoch_loss = 0
            epoch_acc = 0
            n_batches = 0
            
            for images, labels in train_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                metrics = self.model.train_step(images, labels, optimizer, criterion)
                
                epoch_loss += metrics['loss']
                epoch_acc += metrics['accuracy']
                n_batches += 1
            
            avg_loss = epoch_loss / n_batches
            avg_acc = epoch_acc / n_batches
            
            history['train_loss'].append(avg_loss)
            history['train_acc'].append(avg_acc)
            
            # Validation
            if val_loader is not None:
                val_metrics = self.model.validate(val_loader, criterion)
                history['val_loss'].append(val_metrics['loss'])
                history['val_acc'].append(val_metrics['accuracy'])
                scheduler.step(val_metrics['loss'])
                
                print(f"Epoch {epoch+1}/{epochs} - "
                      f"Train Loss: {avg_loss:.4f}, Train Acc: {avg_acc:.4f}, "
                      f"Val Loss: {val_metrics['loss']:.4f}, Val Acc: {val_metrics['accuracy']:.4f}")
            else:
                print(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_loss:.4f}, Train Acc: {avg_acc:.4f}")
        
        return history
