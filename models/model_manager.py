import os
from pathlib import Path
from datetime import datetime
import joblib
import json
from typing import Dict, Any, Optional
from .lstm_model import LSTMModel
from utils.exceptions import ModelError

class ModelManager:
    """Manages model persistence and loading."""
    
    def __init__(self):
        """Initialize model manager."""
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.lstm_dir = self.models_dir / "lstm"
        self.lstm_dir.mkdir(exist_ok=True)
        
        # Model metadata
        self.metadata_file = self.models_dir / "model_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load model metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save model metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=4)
    
    def get_latest_model(self, model_type: str) -> Optional[str]:
        """Get path to latest model of specified type."""
        if model_type in self.metadata:
            return self.metadata[model_type].get('latest_path')
        return None
    
    def save_lstm_model(
        self,
        model: LSTMModel,
        model_name: str,
        metrics: Dict[str, float]
    ) -> str:
        """
        Save LSTM model with metadata.
        
        Args:
            model: Trained LSTM model
            model_name: Name identifier for the model
            metrics: Training metrics
        
        Returns:
            Path to saved model
        """
        try:
            # Create timestamp-based directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_dir = self.lstm_dir / f"{model_name}_{timestamp}"
            model_dir.mkdir(exist_ok=True)
            
            # Save model and scaler
            model_path = model_dir / "model.h5"
            scaler_path = model_dir / "scaler.joblib"
            
            model.save_model(str(model_path), str(scaler_path))
            
            # Update metadata
            self.metadata['lstm'] = {
                'latest_path': str(model_dir),
                'name': model_name,
                'timestamp': timestamp,
                'metrics': metrics
            }
            self._save_metadata()
            
            return str(model_dir)
            
        except Exception as e:
            raise ModelError(f"Failed to save LSTM model: {str(e)}")
    
    def load_lstm_model(
        self,
        input_shape: tuple,
        model_dir: Optional[str] = None
    ) -> LSTMModel:
        """
        Load LSTM model from saved files.
        
        Args:
            input_shape: Shape for new model if needed
            model_dir: Optional specific model directory
            
        Returns:
            Loaded LSTM model
        """
        try:
            # Use latest model if no specific directory provided
            if not model_dir:
                model_dir = self.get_latest_model('lstm')
            
            if not model_dir or not os.path.exists(model_dir):
                # Create new model if no saved model exists
                model = LSTMModel(input_shape=input_shape)
                return model
            
            # Load existing model
            model = LSTMModel(input_shape=input_shape)
            model_path = os.path.join(model_dir, "model.h5")
            scaler_path = os.path.join(model_dir, "scaler.joblib")
            
            model.load_model(model_path, scaler_path)
            return model
            
        except Exception as e:
            raise ModelError(f"Failed to load LSTM model: {str(e)}")
