#!/usr/bin/env bash
set -eo pipefail

echo "1. 프로젝트 정적 파일 수집 시작.."
poetry run python manage.py collectstatic --no-input
echo ""

echo "2. Database Migration 수행..."
poetry run python manage.py migrate
echo ""

echo "3. Daphne(ASGI) 서버 실행..."
exec poetry run daphne -b 0.0.0.0 -p 8000 config.asgi:application
