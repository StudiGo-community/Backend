set -eo pipefail  # 실패하면 더 진행하지 않음 -> 왜 실패했는지 조사 가능

COLOR_GREEN=`tput setaf 2;`  # 초록색 출력
COLOR_NC=`tput sgr0;`        # 색상 초기화

# -----------------------------------------------------------
# Black (CI: poetry run black . --check)
# -----------------------------------------------------------
echo "Starting Black (check)"
poetry run black . --check
echo "OK"

# -----------------------------------------------------------
# Isort (CI: poetry run isort . --check-only)
# -----------------------------------------------------------
echo "Starting Isort (check-only)"
poetry run isort . --check-only
echo "OK"

# -----------------------------------------------------------
# Mypy (CI: poetry run mypy .)
# -----------------------------------------------------------
echo "Starting Mypy"
poetry run mypy .
echo "OK"

# -----------------------------------------------------------
# Django Check (CI와 동일 env 사용)
# -----------------------------------------------------------
echo "Starting Django check"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings}"
export DATABASE_URL="${DATABASE_URL:-postgres://postgres:postgres@localhost:5432/studigo}"

poetry run python manage.py check
echo "OK"

echo "${COLOR_GREEN}CI checks passed successfully!${COLOR_NC}"