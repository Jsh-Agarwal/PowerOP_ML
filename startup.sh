#!/bin/bash
cd /home/site/wwwroot
echo "Current directory: $(pwd)"
echo "Listing directory contents:"
ls -la

echo "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Starting Gunicorn with debug logging..."
exec gunicorn api.main:app \
    --bind=0.0.0.0:8000 \
    --timeout 600 \
    --workers 4 \
    --log-level debug \
    --error-logfile /dev/stderr \
    --access-logfile /dev/stdout \
    --capture-output
