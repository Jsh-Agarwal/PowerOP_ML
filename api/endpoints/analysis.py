from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import logging
import json

from ..auth import oauth2_scheme, validate_token
from ..utils.error_handlers import handle_api_error
from ..services.cost_analyzer import CostAnalyzer
from ..services.groq_slm_service import GroqSLMService
from ..utils.json_encoder import DateTimeEncoder
from ..services.models.autoencoder import AutoEncoderModel

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analysis",
    tags=["System Analysis"]
)

@router.get("/temperature/daily/{system_id}")
async def get_daily_temperature(
    system_id: str,
    date: Optional[datetime] = Query(None, description="Analysis date (YYYY-MM-DD)"),
    token: str = Depends(oauth2_scheme)
):
    """Get temperature history and analysis for a specific day."""
    try:
        await validate_token(token)
        
        if not date:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
        analyzer = CostAnalyzer()
        result = await analyzer.get_temperature_history(
            system_id=system_id,
            start_time=date,
            end_time=date + timedelta(days=1)
        )
        
        return JSONResponse(
            content=json.loads(
                json.dumps(result, cls=DateTimeEncoder)
            )
        )
    except Exception as e:
        raise handle_api_error(e, "get_daily_temperature")

@router.get("/cost/{system_id}")
async def get_cost_analysis(
    system_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get detailed cost analysis for specified time period."""
    try:
        await validate_token(token)
        analyzer = CostAnalyzer()
        
        result = await analyzer.analyze_cost(
            system_id=system_id,
            start_time=start_time,
            end_time=end_time
        )
        
        return JSONResponse(
            content=json.loads(
                json.dumps(result, cls=DateTimeEncoder)
            )
        )
    except Exception as e:
        raise handle_api_error(e, "get_cost_analysis")

@router.post("/optimize/llm/{system_id}")
async def analyze_with_llm(
    system_id: str,
    query: str = Body(..., description="Analysis query"),
    context: Dict[str, Any] = Body(
        ...,
        example={
            "temperature": 23.5,
            "power": 1000.0,
            "runtime_hours": 24
        }
    ),
    token: str = Depends(oauth2_scheme)
):
    """Analyze system using Groq LLM."""
    try:
        await validate_token(token)
        groq = GroqSLMService()
        await groq.connect()
        
        result = await groq.analyze(
            system_id=system_id,
            query=query,
            context=context
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": result
            }
        )
            
    except Exception as e:
        raise handle_api_error(e, "analyze_with_llm")

@router.post("/anomaly/detect/{system_id}")
async def detect_anomalies(
    system_id: str,
    data: List[Dict[str, Any]] = Body(
        ...,
        example=[{
            "timestamp": "2025-03-01T00:00:00Z",
            "temperature": 23.5,
            "humidity": 50.0,
            "power": 1000.0,
            "pressure": 101.3
        }]
    ),
    threshold: float = Query(
        default=0.95,
        gt=0,
        lt=1,
        description="Anomaly detection threshold (0-1)"
    ),
    token: str = Depends(oauth2_scheme)
):
    """Detect anomalies in system data using AutoEncoder model."""
    try:
        await validate_token(token)
        
        if not data:
            raise HTTPException(
                status_code=422,
                detail="No data provided for analysis"
            )
            
        model = AutoEncoderModel()
        await model.connect()
        
        try:
            anomalies = await model.detect_anomalies(
                data=data,
                threshold=threshold
            )
            
            # Convert bool values to strings for JSON serialization
            response = {
                "system_id": system_id,
                "anomalies": [
                    {
                        "timestamp": entry["timestamp"],
                        "is_anomaly": str(entry["is_anomaly"]).lower(),  # Convert bool to string
                        "score": float(entry["anomaly_score"]),  # Ensure score is float
                        "details": entry.get("details", {}),
                        "metrics": {
                            k: v for k, v in entry.items() 
                            if k not in ["timestamp", "is_anomaly", "anomaly_score", "details"]
                        }
                    }
                    for entry in anomalies
                ],
                "summary": {
                    "total_points": len(data),
                    "anomalies_found": sum(1 for a in anomalies if a["is_anomaly"]),
                    "threshold_used": float(threshold)  # Ensure threshold is float
                }
            }
            
            return JSONResponse(
                status_code=200,
                content=json.loads(json.dumps(response, cls=DateTimeEncoder))  # Use DateTimeEncoder
            )
            
        finally:
            await model.close()
            
    except Exception as e:
        raise handle_api_error(e, "detect_anomalies")