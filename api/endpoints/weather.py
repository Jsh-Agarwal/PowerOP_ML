from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from ..utils.json_encoder import DateTimeEncoder
import json

from ..services.weather_service import WeatherService
from ..auth import oauth2_scheme, validate_token
from ..utils.error_handlers import handle_api_error, APIError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/weather",
    tags=["Weather Data"]
)

@router.get("/current")
async def get_current_weather(
    location: str = Query(..., description="Location to get weather for"),
    token: str = Depends(oauth2_scheme)
):
    """Get current weather data."""
    try:
        await validate_token(token)
        weather = WeatherService()
        await weather.connect()
        data = await weather.get_current_weather(location)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": data
            }
        )
    except Exception as e:
        raise handle_api_error(e, "get_current_weather")

@router.get("/forecast")
async def get_weather_forecast(
    location: str = Query(..., description="Location to get forecast for"),
    days: Optional[int] = Query(5, description="Number of days to forecast"),
    token: str = Depends(oauth2_scheme)
):
    """Get weather forecast."""
    try:
        await validate_token(token)
        weather = WeatherService()
        await weather.connect()
        data = await weather.get_forecast(location, days)
        
        # Use custom encoder for datetime objects
        return JSONResponse(
            content=json.loads(
                json.dumps(data, cls=DateTimeEncoder)
            )
        )
    except Exception as e:
        raise handle_api_error(e, "get_weather_forecast")
