FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /studigo

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치 및 설정
RUN pip install --no-cache-dir poetry

# 가상환경 X
RUN poetry config virtualenvs.create false

# 의존성 먼저 복사 (캐시 활용)
COPY pyproject.toml poetry.lock ./

# 프로덕션 의존성만 설치 (--with dev 제거)
RUN poetry install --no-interaction --no-ansi --no-root

# 소스 코드 복사
COPY . .

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

RUN chmod +x ./resource/scripts/entrypoint.sh

# 기본 실행 명령어 (* docker run 시 orverride 가능)
CMD ["entrypoint.sh"]
