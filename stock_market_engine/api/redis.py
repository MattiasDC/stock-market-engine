from aioredis import Redis, from_url
from .config import Settings
from .utils import get_logger

logger = get_logger(__name__)
global_settings = Settings()

async def init_redis_pool() -> Redis:
    redis = await from_url(global_settings.redis_url,
        				   encoding="utf-8",
        				   db=global_settings.redis_db,
        				   decode_responses=True)
    logger.info("Initialized redis")
    return redis