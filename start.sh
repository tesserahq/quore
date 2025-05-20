#!/bin/bash
set -e

echo "🔧 Running Alembic migrations..."
poetry run alembic upgrade head

echo "🚀 Starting Quore..."
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000