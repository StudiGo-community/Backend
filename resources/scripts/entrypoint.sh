#!/usr/bin/env bash
set -eo pipefail

echo "1. 프로젝트 정적 파일 수집 시작.."
poetry run python manage.py collectstatic --no-input
echo ""

echo "2. Database Migration 수행..."
poetry run python manage.py migrate
echo ""

echo "3. Uvicorn(ASGI) 서버 실행..."
exec poetry run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 3
