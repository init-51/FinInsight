#!/bin/sh
set -e

alembic upgrade head

celery -A app.celery_app worker --loglevel=info -Q backtest &
CELERY_PID=$!

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

trap "kill $CELERY_PID $UVICORN_PID" TERM INT

wait $UVICORN_PID

