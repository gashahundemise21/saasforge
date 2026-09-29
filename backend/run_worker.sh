#!/bin/bash
echo "Starting SaaSForge Celery Worker..."
celery -A app.worker.celery_app worker --loglevel=info
