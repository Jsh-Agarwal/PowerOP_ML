from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import logging
from fastapi.responses import JSONResponse
import json

from ..schemas import SystemStatusResponse, HealthResponse
from ..services.astra_db_service import AstraDBService
from ..services.weather_service import WeatherService
from ..services.models.lstm_model import LSTMModel
from ..utils.json_encoder import DateTimeEncoder  # Added this import
from ..auth import validate_token, oauth2_scheme
from ..utils.error_handlers import handle_api_error

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/status",  # Keep this prefix
    tags=["System Monitoring"]
)

@router.get("/system/{system_id}", response_model=SystemStatusResponse)
async def get_system_status(
    system_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get current system status and metrics."""
    try:
        await validate_token(token)
        
        db = AstraDBService()
        status = await db.get_system_status(
            system_id=system_id,
            limit=1
        )
        await db.close()
        
        if not status:
            raise HTTPException(status_code=404, detail="System not found")
            
        latest = status[0]
        return SystemStatusResponse(
            system_id=system_id,
            status=latest["status"],
            metrics={
                "active_power": latest["active_power"],
                "energy_consumption": latest["energy_consumption"],
                "pressure_high": latest["pressure_high"],
                "pressure_low": latest["pressure_low"]
            },
            last_updated=latest["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check endpoint."""
    try:
        components = {
            "database": "unhealthy",
            "ml_model": "unhealthy",
            "weather_service": "unhealthy",
            "optimization_service": "unhealthy"
        }

        # Simplified health checks for faster response
        async def run_checks():
            try:
                # Basic database check
                db = AstraDBService()
                await db.test_connection()
                components["database"] = "healthy"
                await db.close()
            except:
                pass

            try:
                # Basic model check 
                model = LSTMModel()
                if await model.test():
                    components["ml_model"] = "healthy"
            except:
                pass

            try:
                # Basic weather service check
                weather = WeatherService()
                if await weather.test_connection():
                    components["weather_service"] = "healthy"
                await weather.close()
            except:
                pass

            try:
                # Basic optimization check
                components["optimization_service"] = "healthy"
            except:
                pass

        await run_checks()

        return {
            "status": "ok" if all(v == "healthy" for v in components.values()) else "degraded",
            "version": "1.0.0",
            "components": components,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_system_metrics(
    system_id: str,
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    token: str = Depends(oauth2_scheme)
):
    """Get system performance metrics."""
    try:
        await validate_token(token)
        db = AstraDBService()
        await db.connect()
        
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
            
        metrics = await db.get_system_metrics(
            system_id=system_id,
            start_time=start_time,
            end_time=end_time
        )
        
        summary = calculate_metrics_summary(
            metrics["metrics"], 
            start_time, 
            end_time
        )
        
        return JSONResponse(
            status_code=200,
            content=json.loads(
                json.dumps(
                    {
                        "status": "success",
                        "data": metrics,
                        "summary": summary,
                        "system_id": system_id,
                        "period": {
                            "start": start_time.isoformat(),
                            "end": end_time.isoformat()
                        }
                    },
                    cls=DateTimeEncoder
                )
            )
        )
    except Exception as e:
        raise handle_api_error(e, "get_system_metrics")

def calculate_metrics_summary(metrics, start_time, end_time):
    """Calculate summary statistics from metrics data."""
    if not metrics:
        return {
            "total_energy": 0,
            "avg_power": 0,
            "efficiency": 0,
            "duration": 0
        }
        
    total_energy = sum(m.get("energy_consumption", 0) for m in metrics)
    avg_power = sum(m.get("active_power", 0) for m in metrics) / len(metrics)
    efficiency = sum(m.get("efficiency", 0) for m in metrics) / len(metrics)
    
    duration = 0
    if start_time and end_time:
        duration = (end_time - start_time).total_seconds() / 3600  # hours
        
    return {
        "total_energy": round(total_energy, 2),
        "avg_power": round(avg_power, 2),
        "efficiency": round(efficiency, 2),
        "duration": round(duration, 2)
    }