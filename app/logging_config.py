"""Central logging configuration using structlog for JSON output."""

import logging

import structlog

_CONFIGURED = False


def setup_logging(level: int = logging.INFO) -> None:
    """Configure structlog and the standard logging framework.

    Args:
        level: Root logging level. Defaults to logging.INFO.
    """
    global _CONFIGURED

    if _CONFIGURED:
        return

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            timestamper,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            timestamper,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("celery").setLevel(logging.INFO)

    _CONFIGURED = True
