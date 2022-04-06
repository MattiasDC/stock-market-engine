from stock_market.common.factory import Factory
from stock_market.ext.signal import register_signal_detector_factories
from stock_market.ext.updater import register_stock_updater_factories

from .config import get_settings
from .engine import Engine


def get_redis(app):
    return app.state.redis


def get_signal_detector_factory():
    return register_signal_detector_factories(Factory())


def get_stock_updater_factory():
    return register_stock_updater_factories(Factory())


async def store_engine(engine, engine_id, redis):
    await redis.set(
        engine_id, engine.to_json(), get_settings().redis_engine_expiration_time
    )


async def get_engine(engine_id, redis):
    engine_json = await redis.get(str(engine_id))
    if engine_json is None:
        return None
    return Engine.from_json(
        engine_json, get_stock_updater_factory(), get_signal_detector_factory()
    )
