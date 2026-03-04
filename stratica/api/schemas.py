"""Pydantic schemas for STRATICA API."""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Create dummy BaseModel for when pydantic not available
    class BaseModel:
        pass


if PYDANTIC_AVAILABLE:
    class CoreDataSchema(BaseModel):
        """Schema for core data input."""
        depth: List[float] = Field(..., description="Depth values [m]")
        age: Optional[List[float]] = Field(None, description="Age values [ka]")
        values: Dict[str, List[float]] = Field(..., description="Parameter values")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
        
        @validator('depth')
        def depth_not_empty(cls, v):
            if not v:
                raise ValueError('Depth cannot be empty')
            return v
        
        @validator('age')
        def age_matches_depth(cls, v, values):
            if v is not None and 'depth' in values:
                if len(v) != len(values['depth']):
                    raise ValueError('Age must have same length as depth')
            return v
    
    
    class ParameterSchema(BaseModel):
        """Schema for parameter computation."""
        name: str = Field(..., description="Parameter name (LDR, ISO, etc.)")
        data: Dict[str, Any] = Field(..., description="Input data for parameter")
        options: Optional[Dict[str, Any]] = Field(None, description="Parameter options")
        
        @validator('name')
        def validate_name(cls, v):
            valid_names = ['LDR', 'ISO', 'MFA', 'MAG', 'GCH', 'PYS', 'VSI', 'TDM', 'CEC']
            if v.upper() not in valid_names:
                raise ValueError(f'Invalid parameter name. Must be one of {valid_names}')
            return v.upper()
    
    
    class TCIResultSchema(BaseModel):
        """Schema for TCI computation results."""
        tci_composite: float = Field(..., ge=0, le=1, description="Composite TCI score")
        classification: str = Field(..., description="TCI classification")
        parameters: Dict[str, float] = Field(..., description="Individual parameter scores")
        functional: bool = Field(..., description="Whether TCI meets functional threshold")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Additional results")
        
        @validator('classification')
        def validate_classification(cls, v):
            valid = ['optimal', 'good', 'moderate', 'marginal', 'dysfunctional']
            if v not in valid:
                raise ValueError(f'Classification must be one of {valid}')
            return v
    
    
    class BackcastSchema(BaseModel):
        """Schema for back-casting request."""
        timeseries: List[float] = Field(..., description="Time series values")
        age: Optional[List[float]] = Field(None, description="Age points")
        mask: Optional[List[bool]] = Field(None, description="Observed data mask")
        method: str = Field('pinn', description="Back-casting method")
        uncertainty: bool = Field(False, description="Include uncertainty estimates")
        
        @validator('timeseries')
        def timeseries_not_empty(cls, v):
            if not v:
                raise ValueError('Timeseries cannot be empty')
            return v
    
    
    class ValidationSchema(BaseModel):
        """Schema for validation request."""
        values: List[float] = Field(..., description="Values to validate")
        reference: List[float] = Field(..., description="Reference values")
        tolerance: float = Field(0.1, description="Tolerance for validation")
        
        @validator('values')
        def values_not_empty(cls, v):
            if not v:
                raise ValueError('Values cannot be empty')
            return v
        
        @validator('reference')
        def reference_matches_values(cls, v, values):
            if 'values' in values and len(v) != len(values['values']):
                raise ValueError('Reference must have same length as values')
            return v
    
    
    class BasinSchema(BaseModel):
        """Schema for basin information."""
        name: str = Field(..., description="Basin name")
        location: str = Field(..., description="Geographic location")
        lat: Optional[float] = Field(None, description="Latitude")
        lon: Optional[float] = Field(None, description="Longitude")
        tci: Optional[float] = Field(None, ge=0, le=1, description="TCI score")
        age_range: Optional[tuple] = Field(None, description="Age range [Ma]")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    
    class ErrorSchema(BaseModel):
        """Schema for error responses."""
        error: str = Field(..., description="Error message")
        code: int = Field(..., description="Error code")
        details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    
    class HealthSchema(BaseModel):
        """Schema for health check."""
        status: str = Field(..., description="Service status")
        version: str = Field(..., description="API version")
        timestamp: datetime = Field(default_factory=datetime.now)
        
else:
    # Placeholder classes when pydantic not available
    class CoreDataSchema:
        pass
    
    class ParameterSchema:
        pass
    
    class TCIResultSchema:
        pass
    
    class BackcastSchema:
        pass
    
    class ValidationSchema:
        pass
    
    class BasinSchema:
        pass
    
    class ErrorSchema:
        pass
    
    class HealthSchema:
        pass
