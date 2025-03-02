from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..auth import oauth2_scheme, validate_token
from ..utils.error_handlers import handle_api_error
from ..services.system_controller import SystemController
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/control",
    tags=["System Control"]
)

class TemperatureControl(BaseModel):
    system_id: str
    temperature: float
    mode: Optional[str] = "cool"  # cool, heat, auto

class PowerControl(BaseModel):
    system_id: str
    state: bool  # True for on, False for off

@router.post("/temperature")
async def set_temperature(
    control: TemperatureControl,
    token: str = Depends(oauth2_scheme)
):
    """Set temperature for AC system."""
    try:
        await validate_token(token)
        controller = SystemController()
        result = await controller.set_temperature(
            system_id=control.system_id,
            temperature=control.temperature,
            mode=control.mode
        )
        return result
    except Exception as e:
        raise handle_api_error(e, "set_temperature")

@router.post("/power")
async def set_power_state(
    control: PowerControl,
    token: str = Depends(oauth2_scheme)
):
    """Turn system on/off."""
    try:
        await validate_token(token)
        controller = SystemController()
        result = await controller.set_power(
            system_id=control.system_id,
            state=control.state
        )
        return result
    except Exception as e:
        raise handle_api_error(e, "set_power_state")

@router.post("/temperature/increment/{system_id}")
async def increment_temperature(
    system_id: str,
    step: float = 0.5,
    token: str = Depends(oauth2_scheme)
):
    """Increment temperature by step."""
    try:
        await validate_token(token)
        controller = SystemController()
        result = await controller.adjust_temperature(system_id, step)
        return result
    except Exception as e:
        raise handle_api_error(e, "increment_temperature")

@router.post("/temperature/decrement/{system_id}")
async def decrement_temperature(
    system_id: str,
    step: float = 0.5,
    token: str = Depends(oauth2_scheme)
):
    """Decrement temperature by step."""
    try:
        await validate_token(token)
        controller = SystemController()
        result = await controller.adjust_temperature(system_id, -step)
        return result
    except Exception as e:
        raise handle_api_error(e, "decrement_temperature")
