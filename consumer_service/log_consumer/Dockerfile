FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.8.4
WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi --no-root
COPY ./consumer_service ./consumer_service/


FROM python:3.12-slim
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/consumer_service ./consumer_service/
WORKDIR /consumer_service/log_consumer
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/consumer_service/log_consumer
EXPOSE 8000
CMD ["sh", "-c", "python main.py"]