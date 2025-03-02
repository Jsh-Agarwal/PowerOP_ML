from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..services.astra_db_service import AstraDBService
from ..services.weather_service import WeatherService
from ..services.models.lstm_model import LSTMModel
from datetime import datetime
from ..utils.error_handlers import handle_api_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["System"])

@router.get("/api/health")
async def health_check():
    """Check health of all services."""
    try:
        services = {}
        overall_status = "healthy"
        all_services_healthy = True

        # Check each service
        service_checks = {
            "database": AstraDBService(),
            "weather": WeatherService(),
            "ml_model": LSTMModel()
        }

        for service_name, service in service_checks.items():
            try:
                status = await service.health_check()
                services[service_name] = status
                if status["status"] != "healthy":
                    all_services_healthy = False
            except Exception as e:
                logger.error(f"{service_name} health check failed: {str(e)}")
                services[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_checked": datetime.utcnow().isoformat()
                }
                all_services_healthy = False

        response = {
            "status": "healthy" if all_services_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": services
        }

        return JSONResponse(
            status_code=200 if all_services_healthy else 207,
            content=response
        )
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
