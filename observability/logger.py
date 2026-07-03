"""
Logging configuration.

This module configures the application's structured logging using
Structlog. Logs are emitted in JSON format to support centralized log
aggregation and observability platforms.
"""

import logging
import structlog

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()