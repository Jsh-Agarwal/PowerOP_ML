from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from uuid import UUID

class TemperaturePredictionRequest(BaseModel):
    device_id: str = Field(..., description="Device ID")
    zone_id: str = Field(..., description="Zone ID")
    timestamps: Optional[List[datetime]] = Field(None, description="Timestamps for prediction")
    features: Dict[str, Any] = Field(..., description="Feature values")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

    @validator('features')
    def validate_features(cls, features):
        required_features = {'temperature', 'humidity', 'power'}
        if not all(f in features for f in required_features):
            raise ValueError(f"Missing required features. Expected: {required_features}")
        return features

class TemperaturePredictionResponse(BaseModel):
    predictions: List[float] = Field(..., description="Predicted temperatures")
    timestamps: List[datetime] = Field(..., description="Prediction timestamps")
    confidence: Optional[float] = Field(None, description="Confidence score")
    min_values: Optional[List[float]] = Field(None, description="Minimum predicted values")
    max_values: Optional[List[float]] = Field(None, description="Maximum predicted values")

class BatchPredictionRequest(BaseModel):
    requests: List[TemperaturePredictionRequest]

    @validator('requests')
    def validate_batch(cls, v):
        if not v:
            raise ValueError("Batch must contain at least one request")
        if len(v) > 100:  # Add reasonable limit
            raise ValueError("Batch size exceeds maximum limit of 100")
        return v

class OptimizationRequest(BaseModel):
    system_id: str = Field(..., description="System ID")
    target_metric: str = Field(..., description="Optimization target metric")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optimization constraints")
    current_state: Dict[str, Any] = Field(..., description="Current system state")
    objectives: Optional[List[str]] = Field(None, description="Optimization objectives")

class ScheduleRequest(BaseModel):
    system_id: str
    target_metric: str
    current_state: Dict[str, float]
    start_time: datetime
    end_time: datetime
    interval: int = 60
    constraints: Optional[Dict[str, Any]] = None

class ScheduleOptimizationRequest(BaseModel):
    system_id: str = Field(..., description="System identifier")
    target_metric: str = Field(..., description="Target metric for optimization")
    current_state: Dict[str, float] = Field(..., description="Current system state")
    start_time: datetime = Field(..., description="Schedule start time")
    end_time: datetime = Field(..., description="Schedule end time")
    interval: int = Field(
        default=60,
        ge=15,
        le=1440,
        description="Schedule interval in minutes"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default={},
        description="Optimization constraints"
    )

    @validator('target_metric')
    def validate_target_metric(cls, v):
        allowed = {'energy', 'comfort', 'cost', 'efficiency'}
        if v not in allowed:
            raise ValueError(f'target_metric must be one of {allowed}')
        return v

    @validator('current_state')
    def validate_state(cls, v):
        required = {'temperature', 'humidity', 'power'}
        missing = required - v.keys()
        if missing:
            raise ValueError(f'Missing required state parameters: {missing}')
        return v

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class OptimizationResponse(BaseModel):
    recommendations: List[str] = Field(..., description="Optimization recommendations")
    expected_savings: Dict[str, str] = Field(..., description="Expected savings")
    confidence_score: float = Field(..., description="Confidence score")

class ScheduleEntry(BaseModel):
    timestamp: datetime
    setpoint: float
    mode: str
    expected_load: float

class ScheduleResponse(BaseModel):
    schedule: List[ScheduleEntry] = Field(..., description="Optimized schedule entries")
    total_energy_savings: float = Field(..., description="Total expected energy savings")
    comfort_impact: float = Field(
        ..., 
        description="Expected impact on comfort (0-100)", 
        ge=0, 
        le=100
    )
    recommendations: List[Dict[str, Union[str, float]]] = Field(..., description="Schedule recommendations")
    expected_savings: float = Field(..., description="Expected savings")
    confidence_score: float = Field(..., description="Confidence score")

class SystemStatusResponse(BaseModel):
    system_id: str = Field(..., description="System ID")
    status: str = Field(..., description="Current status")
    metrics: Dict[str, float] = Field(..., description="Current metrics")
    last_updated: datetime = Field(..., description="Last update timestamp")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    components: Dict[str, str] = Field(..., description="Component statuses")
    timestamp: str = Field(..., description="Timestamp")

class AnomalyDetectionRequest(BaseModel):
    system_id: str = Field(..., description="System identifier")
    data: List[Dict[str, Any]] = Field(..., description="Time series data points")
    threshold: float = Field(
        default=0.95,
        gt=0,
        le=1,
        description="Anomaly detection threshold"
    )

    class Config:
        schema_extra = {
            "example": {
                "system_id": "test_system",
                "data": [{
                    "timestamp": "2025-03-01T00:00:00Z",
                    "temperature": 23.5,
                    "humidity": 50.0,
                    "power": 1000.0,
                    "pressure": 101.3
                }],
                "threshold": 0.95
            }
        }

class AnomalyDetectionResponse(BaseModel):
    system_id: str
    anomalies: List[Dict[str, Any]]
    summary: Dict[str, Any]

class DailyAnalysisRequest(BaseModel):
    system_id: str
    date: Optional[datetime] = None

class CostAnalysisRequest(BaseModel):
    system_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class LLMAnalysisRequest(BaseModel):
    system_id: str
    query: str
    context: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "system_id": "test_system",
                "query": "Analyze system efficiency",
                "context": {
                    "temperature": 23.5,
                    "power": 1000.0,
                    "runtime_hours": 24
                }
            }
        }
