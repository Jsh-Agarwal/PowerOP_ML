from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional
from fastapi.responses import JSONResponse
import logging

from ..services.groq_slm_service import GroqSLMService
from ..auth import oauth2_scheme, validate_token
from ..utils.error_handlers import handle_api_error, APIError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/groq",
    tags=["Groq LLM Service"]
)

@router.get("/context/{context_id}")
async def get_context(
    context_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get optimization context."""
    try:
        await validate_token(token)
        service = GroqSLMService()
        await service.connect()
        
        context = await service.get_context(context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Context not found")
            
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": context
            }
        )
    except Exception as e:
        raise handle_api_error(e, "get_context")

@router.post("/optimize")
async def optimize_with_groq(
    request: Dict[str, Any] = Body(..., example={
        "prompt": "Optimize HVAC system for energy efficiency",
        "context": {
            "current_temperature": 24.0,
            "target_temperature": 22.0,
            "power_consumption": 1200.0
        }
    }),
    token: str = Depends(oauth2_scheme)
):
    """Run optimization using Groq."""
    try:
        await validate_token(token)
        service = GroqSLMService()
        await service.connect()
        
        result = await service.optimize(request)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": result
            }
        )
    except Exception as e:
        raise handle_api_error(e, "optimize_with_groq")
