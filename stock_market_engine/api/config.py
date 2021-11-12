import datetime as dt
from functools import cache
import os
from pydantic import AnyUrl, BaseSettings

from stock_market_engine.common.logging import get_logger

logger = get_logger(__name__)

class Settings(BaseSettings):
    redis_url: AnyUrl = os.environ.get("REDIS_URL", "redis://redis")
    redis_port: int = os.getenv("REDIS_PORT", 6379)
    redis_db: int = os.getenv("REDIS_DB", 0)
    redis_temporary_expiration_time : dt.timedelta = dt.timedelta(minutes=os.getenv("REDIS_TEMPORARY_EXPIRATION_MINUTES", 60))
    redis_engine_expiration_time : dt.timedelta = dt.timedelta(days=os.getenv("REDIS_ENGINE_EXPIRATION_DAYS", 30))
    stock_updater: str = os.getenv("STOCK_UPDATER", "yahoo")
    max_ticker_symbol_length : int = os.getenv("MAX_TICKER_SYMBOL_LENGTH", 10)

@cache
def get_settings() -> BaseSettings:
    logger.info("Loading config settings from the environment...")
    return Settings()