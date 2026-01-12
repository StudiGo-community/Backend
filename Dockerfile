FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /studigo

RUN apt-get update && apt-get install -y \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

# (중요) 컨테이너 내부에 venv 만들지 않게
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /studigo/
RUN poetry install --no-interaction --no-ansi --no-root --with dev

COPY . /studigo/
