from aioredis import Redis, from_url

from utils.logging import get_logger

from .config import Settings

logger = get_logger(__name__)
global_settings = Settings()

async def init_redis_pool() -> Redis:
    redis = await from_url(global_settings.redis_url,
        				   encoding="utf-8",
        				   db=global_settings.redis_db,
        				   decode_responses=True)
    logger.info("Initialized redis")
    return redis