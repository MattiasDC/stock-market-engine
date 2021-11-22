import uuid

from .config import get_settings
from stock_market_engine.api.engine import Engine
from stock_market_engine.common.factory import Factory
from stock_market_engine.ext.signal import register_signal_detector_factories 
from stock_market_engine.ext.updater import register_stock_updater_factories 

def get_redis(app):
	return app.state.redis
	
def get_signal_detector_factory():
	return register_signal_detector_factories(Factory())

def get_stock_updater_factory():
	return register_stock_updater_factories(Factory())
	
async def store_temporary(o, redis):
	if o is None:
		return None
	random_id = str(uuid.uuid4())
	await redis.set(random_id, o.to_json(), get_settings().redis_temporary_expiration_time)
	return random_id

async def store_engine(engine, engine_id, redis):
	await redis.set(engine_id, engine.to_json(), get_settings().redis_engine_expiration_time)

async def get_engine(engine_id, redis):
	engine_json = await redis.get(str(engine_id))
	return Engine.from_json(engine_json, get_stock_updater_factory(), get_signal_detector_factory())