FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./alembic.ini .
COPY ./migrations ./migrations

ENV PYTHONPATH=/app

EXPOSE 8000
