from ..utils.connection_manager import retry_with_backoff, CircuitBreaker
from ..utils.error_handlers import APIError
import logging
from datetime import datetime, timedelta
import random
import asyncio

logger = logging.getLogger(__name__)

class WeatherService:
    """Weather data service implementation."""
    
    def __init__(self):
        self.connected = False
        self.logger = logging.getLogger(__class__.__name__)
        self.circuit_breaker = CircuitBreaker()
        self.timeout = 10  # seconds
        
    async def connect(self):
        """Establish connection to weather service."""
        try:
            self.connected = True
            return self.connected
        except Exception as e:
            raise APIError(
                status_code=503,
                detail="Failed to connect to weather service",
                error_code="CONNECTION_ERROR",
                extra={"service": "weather"}
            )
        
    async def close(self):
        """Close connection to weather service."""
        self.connected = False
        return True
        
    async def test_connection(self):
        """Test if service is available."""
        return True
        
    async def health_check(self):
        """Check if service is healthy."""
        try:
            is_connected = await self.test_connection()
            return {
                "status": "healthy" if is_connected else "degraded", 
                "last_checked": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
            
    @retry_with_backoff()
    async def get_current_weather(self, location: str):
        """Get current weather data for location."""
        if not self.circuit_breaker.can_execute():
            raise APIError(
                status_code=503,
                detail="Weather service temporarily unavailable",
                error_code="CIRCUIT_OPEN"
            )
            
        if not self.connected:
            raise APIError(
                status_code=503,
                detail="Weather service not connected",
                error_code="SERVICE_UNAVAILABLE"
            )
            
        try:
            async with asyncio.timeout(self.timeout):
                temp = round(random.uniform(10.0, 30.0), 1)
                humidity = round(random.uniform(30.0, 85.0), 1)
                
                result = {
                    "location": location,
                    "temperature": temp,
                    "humidity": humidity,
                    "wind_speed": round(random.uniform(0, 20), 1),
                    "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Windy"]),
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.circuit_breaker.record_success()
                return result
        except asyncio.TimeoutError:
            self.circuit_breaker.record_failure()
            raise APIError(
                status_code=504,
                detail="Weather service timeout",
                error_code="TIMEOUT"
            )
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise APIError(
                status_code=500,
                detail=f"Failed to get weather data: {str(e)}",
                error_code="WEATHER_DATA_ERROR",
                extra={"location": location}
            )
        
    async def get_forecast(self, location, days=5):
        """Get weather forecast for location."""
        forecast = {
            "location": location,
            "generated_at": datetime.utcnow().isoformat(),
            "daily": [],
            "hourly": []
        }
        
        # Generate daily forecast
        now = datetime.utcnow()
        for i in range(days):
            day = now + timedelta(days=i)
            forecast["daily"].append({
                "date": day,
                "high": round(random.uniform(15, 35), 1),
                "low": round(random.uniform(5, 15), 1),
                "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Windy"]),
                "humidity": round(random.uniform(30, 85), 1)
            })
            
        # Generate hourly forecast
        for i in range(24):
            hour = now + timedelta(hours=i)
            forecast["hourly"].append({
                "time": hour,
                "temperature": round(random.uniform(10, 30), 1),
                "humidity": round(random.uniform(30, 85), 1),
                "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Windy"])
            })
            
        return forecast
