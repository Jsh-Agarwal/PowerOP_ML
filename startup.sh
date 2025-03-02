#!/bin/bash
cd /home/site/wwwroot

echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 api.main:app --workers 4 --access-logfile '-' --error-logfile '-' --log-level debug
