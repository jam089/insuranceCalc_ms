FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.8.4
WORKDIR /app
COPY ../pyproject.toml ../poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi
COPY app/. .


FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder / /app
COPY app/.env .env
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
