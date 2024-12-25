FROM python:3.12-slim AS builder
EXPOSE 8000
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.8.4
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi
COPY app/ .
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
