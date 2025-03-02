#!/bin/bash
cd /home/site/wwwroot
gunicorn --bind=0.0.0.0 --timeout 600 api.main:app --workers 4 --access-logfile '-' --error-logfile '-'
