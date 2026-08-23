"""Background worker entrypoint — STUB.

Launched by ``Dockerfile.worker``. Intended to consume a job queue (Redis /
broker) and run long-running or scheduled work off the request path, reusing
the ``services/`` layer. Currently idles so the worker image boots cleanly.
"""

from __future__ import annotations

import asyncio

from business_platform.core.config import settings
from business_platform.core.logging import configure_logging, get_logger


async def main() -> None:
    configure_logging(debug=settings.DEBUG)
    logger = get_logger("business_platform.worker")
    logger.info("Worker started (env=%s). No jobs wired yet; idling.", settings.ENVIRONMENT)
    # Will subscribe to the job queue and dispatch work to services/ here.
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
