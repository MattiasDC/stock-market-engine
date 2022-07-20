import datetime
import hashlib
import uuid
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Response
from utils.logging import get_logger

from .api import (
    EngineModel,
    register_indicator_api,
    register_signal_api,
    register_stock_market_api,
)
from .common import (
    get_engine,
    get_redis,
    get_signal_detector_factory,
    get_stock_updater_factory,
    store_engine,
)
from .redis import init_redis_pool

logger = get_logger(__name__)

app = FastAPI(title="Stock Market Engine")


@app.on_event("startup")
async def startup_event():
    app.state.redis = init_redis_pool()


def get_hash(engine_config):
    json_config = engine_config.json()
    return hashlib.md5(json_config.encode("utf-8")).hexdigest()


async def get_cached_engine_id(engine_config, redis):
    engine_id = await redis.get(get_hash(engine_config))
    return engine_id


@app.post("/create")
async def create_engine(engine_config: EngineModel):
    redis = get_redis(app)
    engine_id = await get_cached_engine_id(engine_config, redis)
    if engine_id is not None:
        logger.debug(
            f"Create engine cache hit for '{engine_id}' with config '{engine_config}'"
        )
        return engine_id

    engine = engine_config.create(
        get_stock_updater_factory(), get_signal_detector_factory()
    )
    if engine is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Incorrect engine configuration!"
        )

    random_id = str(uuid.uuid4())

    await store_engine(engine, random_id, redis)
    await redis.set(get_hash(engine_config), random_id)
    return random_id


@app.post("/update/{engine_id}")
async def update_engine(engine_id: uuid.UUID, date: datetime.date):
    engine = await get_engine(engine_id, get_redis(app))
    if not engine:
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    new_engine = await engine.update(date)
    random_id = str(uuid.uuid4())
    await store_engine(new_engine, random_id, get_redis(app))
    return random_id


register_indicator_api(app)
register_signal_api(app)
register_stock_market_api(app)
