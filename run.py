import uvicorn
import sys
from pathlib import Path

# Add project root to Python path
root_path = str(Path(__file__).parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from api.main import app

if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )
