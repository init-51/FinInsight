#!/bin/sh
set -e

alembic upgrade head

celery -A app.celery_app worker --loglevel=info -Q backtest &
CELERY_PID=$!

trap "kill $CELERY_PID" TERM INT

uvicorn app.main:app --host 0.0.0.0 --port 8000
EXIT_CODE=$?

kill $CELERY_PID >/dev/null 2>&1 || true
wait $CELERY_PID >/dev/null 2>&1 || true

exit $EXIT_CODE

