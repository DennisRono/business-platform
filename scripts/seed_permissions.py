from __future__ import annotations

import asyncio

from business_platform.core.logging import configure_logging, get_logger


async def seed() -> None:
    configure_logging(debug=True)
    logger = get_logger("scripts.seed_permissions")
    logger.info("No permission seed data defined yet — nothing to seed.")


if __name__ == "__main__":
    asyncio.run(seed())
