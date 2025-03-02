"""API endpoints package initialization."""
from .temperature import router as temperature_router
from .optimization import router as optimization_router
from .monitoring import router as monitoring_router
from .weather import router as weather_router

__all__ = [
    'temperature_router',
    'optimization_router',
    'monitoring_router',
    'weather_router'
]
