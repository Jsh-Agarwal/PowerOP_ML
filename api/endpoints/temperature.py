from fastapi import APIRouter, Depends, HTTPException, Security, Body, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from fastapi.responses import JSONResponse

from ..schemas import TemperaturePredictionRequest, TemperaturePredictionResponse, BatchPredictionRequest
from ..services.models.lstm_model import LSTMModel
from ..services.astra_db_service import AstraDBService
from ..utils.exceptions import ModelError, ValidationError
from ..auth import validate_token, oauth2_scheme
from ..services.groq_slm_service import GroqSLMService
from models.model_manager import ModelManager
from ..utils.error_handlers import handle_api_error

router = APIRouter(
    prefix="/api/temperature",  # Keep this prefix
    tags=["Temperature Management"]
)

# Initialize logger
logger = logging.getLogger(__name__)

@router.post("/predict", response_model=TemperaturePredictionResponse)
async def predict_temperature(request: TemperaturePredictionRequest, token: str = Depends(oauth2_scheme)):
    """Generate temperature predictions."""
    try:
        await validate_token(token)
        
        # Process prediction
        model = LSTMModel()
        predictions = await model.predict(request.features, request.timestamps)
        
        # Generate response timestamps if not provided
        if not request.timestamps:
            now = datetime.utcnow()
            timestamps = [now + timedelta(hours=i) for i in range(len(predictions["predictions"]))]
        else:
            timestamps = request.timestamps
            
        return TemperaturePredictionResponse(
            predictions=predictions["predictions"],
            timestamps=timestamps,
            confidence=predictions.get("confidence")
        )
        
    except Exception as e:
        logger.error(f"Temperature prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add new endpoint for model training
@router.post("/train")
async def train_temperature_model(
    training_data: Dict[str, Any],
    token: str = Depends(oauth2_scheme)
):
    """Train temperature prediction model."""
    try:
        await validate_token(token)
        
        model_manager = ModelManager()
        model = model_manager.load_lstm_model(
            input_shape=(24, len(training_data["features"]))
        )
        
        # Train model
        X_train, y_train = model.preprocess_data(
            training_data["data"],
            training_data["feature_columns"],
            training_data["target_column"]
        )
        
        history = model.train(
            X_train,
            y_train,
            epochs=100,
            batch_size=32
        )
        
        # Save trained model
        model_path = model_manager.save_lstm_model(
            model,
            "temperature_predictor",
            {
                "final_loss": history["loss"][-1],
                "final_mae": history["mae"][-1]
            }
        )
        
        return {
            "message": "Model trained successfully",
            "model_path": model_path,
            "metrics": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_temperature_history(
    device_id: str,
    zone_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get historical temperature data."""
    try:
        await validate_token(token)
        
        db = AstraDBService()
        data = await db.get_temperature_data(
            device_id=device_id,
            zone_id=zone_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Convert data to a format that can be JSON serialized
        history = [
            {
                "temperature": reading["temperature"],
                "humidity": reading["humidity"],
                "timestamp": reading["timestamp"].isoformat(),
                "device_id": device_id,
                "zone_id": zone_id
            }
            for reading in data
        ]
        
        return {
            "history": history,
            "device_id": device_id,
            "zone_id": zone_id,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "count": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch history", "message": str(e)}
        )

@router.get("/current")
async def get_current_temperature(
    device_id: str,
    zone_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get real-time temperature data."""
    try:
        await validate_token(token)
        db = AstraDBService()
        
        try:
            data = await db.get_temperature_data(
                device_id=device_id,
                zone_id=zone_id,
                limit=1
            )
            
            if not data or len(data) == 0:
                return JSONResponse(
                    status_code=404,
                    content={"detail": "No current data available"}
                )
            
            reading = data[0]
            return JSONResponse(
                status_code=200,
                content={
                    "temperature": reading["temperature"],
                    "humidity": reading["humidity"],
                    "timestamp": reading["timestamp"].isoformat(),
                    "device_id": device_id,
                    "zone_id": zone_id
                }
            )
            
        finally:
            await db.close()
            
    except Exception as e:
        logger.error(f"Error getting temperature: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@router.post("/batch")
async def batch_predict_temperature(
    batch: BatchPredictionRequest,
    token: str = Depends(oauth2_scheme)
):
    """Process batch of temperature prediction requests."""
    model = None
    try:
        await validate_token(token)
        
        if not batch.requests:
            return JSONResponse(
                status_code=422, 
                content={
                    "status": "error",
                    "detail": "Batch requests cannot be empty"
                }
            )
            
        if len(batch.requests) > 100:
            return JSONResponse(
                status_code=422, 
                content={
                    "status": "error",
                    "detail": "Batch size exceeds maximum of 100"
                }
            )

        results = []
        errors = []
        model = LSTMModel()
        
        # Ensure model is connected
        try:
            await model.connect()
        except Exception as e:
            raise APIError(
                status_code=503,
                detail="Failed to initialize model",
                error_code="MODEL_CONNECTION_ERROR",
                extra={"error": str(e)}
            )
        
        for idx, request in enumerate(batch.requests):
            try:
                predictions = await model.predict(
                    features=request.features,
                    timestamps=request.timestamps
                )
                
                results.append({
                    "id": idx,
                    "device_id": request.device_id,
                    "zone_id": request.zone_id,
                    "predictions": predictions["predictions"],
                    "confidence": predictions.get("confidence", 0.85),
                    "status": "success"
                })
            except Exception as e:
                errors.append({
                    "id": idx,
                    "device_id": request.device_id,
                    "zone_id": request.zone_id,
                    "error": str(e),
                    "status": "failed"
                })
                logger.error(f"Failed to process batch item {idx}: {str(e)}")
                continue
                
        if not results and errors:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "failed",
                    "detail": "All batch predictions failed",
                    "errors": errors
                }
            )
                
        return JSONResponse(
            status_code=200,
            content={
                "status": "completed",
                "summary": {
                    "total": len(batch.requests),
                    "successful": len(results),
                    "failed": len(errors)
                },
                "results": results,
                "errors": errors if errors else None
            }
        )
        
    except Exception as e:
        raise handle_api_error(e, "batch_predict_temperature")
    finally:
        if model:
            await model.close()
