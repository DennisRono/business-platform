from __future__ import annotations

import logging
import sys

_CONFIGURED = False

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(*, debug: bool = False) -> None:
    """Configure the root logger once, idempotently."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Tame noisy third-party loggers to WARNING regardless of app level.
    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)
