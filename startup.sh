#!/bin/bash

# Enable bash strict mode and logging
set -euxo pipefail

echo "=== Deployment Info ===="
echo "Timestamp: $(date)"
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "User: $(whoami)"
echo "Memory info: $(free -h)"
echo "Disk space: $(df -h)"

echo "=== Directory Contents ===="
ls -la

echo "=== Python Environment ===="
python -m pip freeze

echo "=== Installing Dependencies ===="
python -m pip install --upgrade pip
python -m pip install -r requirements.txt 2>&1 | tee pip_install.log

echo "=== Verifying Installation ===="
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
python -c "import uvicorn; print('Uvicorn version:', uvicorn.__version__)"
python -c "import gunicorn; print('Gunicorn version:', gunicorn.__version__)"

echo "=== Starting Gunicorn ===="
exec gunicorn api.main:app \
    --bind=0.0.0.0:8000 \
    --timeout 600 \
    --workers 4 \
    --log-level debug \
    --error-logfile /dev/stderr \
    --access-logfile /dev/stdout \
    --capture-output \
    --logger-class=gunicorn.glogging.Logger \
    --max-requests 1000 \
    --reload 2>&1 | tee gunicorn.log
