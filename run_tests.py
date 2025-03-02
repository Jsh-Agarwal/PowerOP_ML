import sys
from pathlib import Path
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import logging
from api.utils.logging_config import setup_logging

# Add project root to Python path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

async def run_api_tests():
    """Run tests for all API endpoints."""
    logger.info("Starting API tests")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get authentication token
            token_response = await session.post(
                "http://localhost:8000/token",
                data={
                    "username": "test",
                    "password": "test"
                }
            )
            token_data = await token_response.json()
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}"
            }

            # Test endpoints
            test_cases = [
                # Existing endpoints
                {
                    "name": "Health Check",
                    "method": "GET",
                    "url": "http://localhost:8000/api/health"
                },
                # ... existing test cases ...

                # New endpoints
                {
                    "name": "Anomaly Detection",
                    "method": "POST",
                    "url": f"http://localhost:8000/api/analysis/anomaly/detect/test_system",
                    "json": [{  # Changed format to match endpoint
                        "timestamp": datetime.now().isoformat(),
                        "temperature": 23.5,
                        "humidity": 50.0,
                        "power": 1000.0,
                        "pressure": 101.3
                    }]
                },
                {
                    "name": "Daily Temperature Analysis",
                    "method": "GET",
                    "url": "http://localhost:8000/api/analysis/temperature/daily/test_system",
                    "params": {
                        "date": datetime.now().date().isoformat()
                    }
                },
                {
                    "name": "Cost Analysis",
                    "method": "GET",
                    "url": "http://localhost:8000/api/analysis/cost/test_system",
                    "params": {
                        "start_time": (datetime.now() - timedelta(days=7)).isoformat(),
                        "end_time": datetime.now().isoformat()
                    }
                },
                {
                    "name": "LLM Analysis",
                    "method": "POST",
                    "url": "http://localhost:8000/api/analysis/optimize/llm/test_system",
                    "json": {  # Changed format to match endpoint
                        "query": "Analyze system efficiency",
                        "context": {
                            "temperature": 23.5,
                            "power": 1000.0,
                            "runtime_hours": 24
                        }
                    }
                }
            ]

            results = []
            for test in test_cases:
                try:
                    if test["method"] == "GET":
                        response = await session.get(
                            test["url"],
                            headers=headers,
                            params=test.get("params")
                        )
                    else:
                        response = await session.post(
                            test["url"],
                            headers=headers,
                            json=test.get("json")
                        )

                    results.append({
                        "name": test["name"],
                        "status": response.status,
                        "success": response.status in [200, 201, 207],
                        "response": await response.json()
                    })

                except Exception as e:
                    results.append({
                        "name": test["name"],
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    })

            # Enhanced logging for results
            for result in results:
                log_level = logging.INFO if result["success"] else logging.ERROR
                logger.log(
                    log_level,
                    f"Test '{result['name']}' - Status: {result['status']}",
                    extra={
                        "test_name": result["name"],
                        "status": result["status"],
                        "success": result["success"],
                        "response": result.get("response"),
                        "error": result.get("error")
                    }
                )

            # Save test results
            with open(TEST_DATA_DIR / "test_results.json", "w") as f:
                json.dump(results, f, indent=2)

            return results
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    results = asyncio.run(run_api_tests())
    
    # Print results summary
    print("\nTest Results Summary:")
    print("=====================")
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"{status} {result['name']}: {result['status']}")
