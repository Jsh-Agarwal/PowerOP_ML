from fastapi import APIRouter, Depends, Query, Body
from typing import Optional, Dict, Any
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel
from datetime import datetime
import json

from ..schemas import OptimizationRequest, OptimizationResponse, ScheduleResponse
from ..services.groq_slm_service import GroqSLMService
from ..auth import oauth2_scheme, validate_token
from ..utils.error_handlers import handle_api_error
from ..utils.json_encoder import DateTimeEncoder  # Changed this line

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/optimize",
    tags=["System Optimization"]
)

@router.post("/system")
async def optimize_system(request: OptimizationRequest, token: str = Depends(oauth2_scheme)):
    """Generate system-wide optimization recommendations."""
    try:
        await validate_token(token)
        groq = GroqSLMService()
        
        # Connect to service
        await groq.connect()
        
        result = await groq.optimize_system(
            system_id=request.system_id,
            current_state=request.current_state,
            constraints=request.constraints
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": result
            }
        )
    except Exception as e:
        raise handle_api_error(e, "optimize_system")

@router.post("/comfort")
async def optimize_comfort(request: OptimizationRequest, token: str = Depends(oauth2_scheme)):
    """Generate comfort-focused optimization."""
    try:
        await validate_token(token)
        groq = GroqSLMService()
        
        # Connect to service
        await groq.connect()
        
        result = await groq.optimize_comfort(
            system_id=request.system_id,
            current_state=request.current_state,
            constraints=request.constraints
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": result
            }
        )
    except Exception as e:
        raise handle_api_error(e, "optimize_comfort")

@router.post("/energy")
async def optimize_energy(request: OptimizationRequest, token: str = Depends(oauth2_scheme)):
    """Generate energy-focused optimization."""
    try:
        await validate_token(token)
        groq = GroqSLMService()
        
        # Connect to service
        await groq.connect()
        
        result = await groq.optimize_energy(
            system_id=request.system_id,
            current_state=request.current_state,
            constraints=request.constraints
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": result
            }
        )
    except Exception as e:
        raise handle_api_error(e, "optimize_energy")

class ScheduleOptimizationRequest(BaseModel):
    system_id: str
    target_metric: str
    current_state: Dict[str, float]
    start_time: datetime
    end_time: datetime
    interval: int = 60
    constraints: Optional[Dict[str, Any]] = None

@router.post("/schedule")
async def optimize_schedule(
    request: ScheduleOptimizationRequest = Body(
        ...,
        examples=[{
            "system_id": "test_system",
            "target_metric": "energy",
            "current_state": {
                "temperature": 23.5,
                "humidity": 50.0,
                "power": 1000.0
            },
            "start_time": "2025-03-01T00:00:00Z",
            "end_time": "2025-03-02T00:00:00Z",
            "interval": 60
        }]
    ),
    token: str = Depends(oauth2_scheme)
):
    """Optimize system schedule."""
    try:
        await validate_token(token)
        groq = GroqSLMService()
        await groq.connect()
        
        result = await groq.optimize_schedule(
            system_id=request.system_id,
            target_metric=request.target_metric,
            current_state=request.current_state,
            start_time=request.start_time,
            end_time=request.end_time,
            interval=request.interval,
            constraints=request.constraints
        )
        
        # Ensure proper response format
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": json.loads(
                    json.dumps(result, cls=DateTimeEncoder)
                )
            }
        )
    except Exception as e:
        raise handle_api_error(e, "optimize_schedule")
