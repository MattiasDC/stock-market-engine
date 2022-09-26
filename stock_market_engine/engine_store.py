import hashlib
import json
import uuid

from simputils.logging import get_logger

from .common import get_signal_detector_factory, get_stock_updater_factory
from .config import get_settings
from .engine import Engine

logger = get_logger(__name__)


def __get_hash(engine):
    hash_components = {}
    hash_components["start_date"] = engine.stock_market.start_date.isoformat()
    hash_components["tickers"] = [t.to_json() for t in engine.stock_market.tickers]
    hash_components["signal_detectors"] = [
        sd.to_json() for sd in engine.signal_detectors
    ]
    hash_components["end_date"] = engine.date.isoformat()
    return hashlib.md5(json.dumps(hash_components).encode("utf-8")).hexdigest()


async def store_engine(engine, redis):
    engine_hash = __get_hash(engine)
    engine_id = await redis.get(engine_hash)
    if engine_id is not None:
        engine = await get_engine(engine_id, redis)
        if engine is not None:
            logger.debug(f"Cache hit for engine modification! id: '{engine_id}'")
            return engine_id

    random_id = uuid.uuid4()
    await redis.set(
        random_id, engine.to_json(), get_settings().redis_engine_expiration_time
    )
    await redis.set(engine_hash, str(random_id))
    return random_id


async def get_engine(engine_id, redis):
    engine_json = await redis.get(str(engine_id))
    if engine_json is None:
        return None
    return Engine.from_json(
        engine_json, get_stock_updater_factory(), get_signal_detector_factory()
    )
