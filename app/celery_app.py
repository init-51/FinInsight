"""Celery application configuration for FinInsight.

This module initializes and configures the Celery application for
handling asynchronous tasks like portfolio backtesting.
"""

from celery import Celery
from celery.signals import setup_logging as celery_setup_logging
from app.config import settings
from app.logging_config import setup_logging as configure_logging

# Initialize Celery app
celery_app = Celery(
    "fininsight",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)


@celery_setup_logging.connect
def configure_celery_logging(**kwargs):
    """Apply shared logging configuration when the worker initializes logging."""
    configure_logging()


# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Route tasks to specific queues
celery_app.conf.task_routes = {
    "app.tasks.backtest.*": {"queue": "backtest"}
}

# Optional: Configure task result backend
celery_app.conf.result_backend = settings.REDIS_URL

# This will make sure the app is only initialized once
celery_app.set_default()
