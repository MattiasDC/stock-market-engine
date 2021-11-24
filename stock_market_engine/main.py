import datetime
from fastapi import FastAPI
import uuid

from .common import get_signal_detector_factory, get_stock_updater_factory, store_engine, get_redis, get_engine
from .models import EngineModel
from .redis import init_redis_pool
from .api.stock_market import register_stock_market_api
from .api.signal import register_signal_api

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.redis = await init_redis_pool()

@app.post("/create")
async def create_engine(engine_config: EngineModel):
	engine = engine_config.create(get_stock_updater_factory(), get_signal_detector_factory())
	random_id = str(uuid.uuid4())

	await store_engine(engine, random_id, get_redis(app))
	return random_id

@app.post("/update/{engine_id}")
async def update_engine(engine_id : uuid.UUID, date : datetime.date):
	engine = await get_engine(engine_id, get_redis(app))
	engine.update(date)
	await store_engine(engine, str(engine_id), get_redis(app))

register_stock_market_api(app)
register_signal_api(app)