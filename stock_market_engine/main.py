import datetime
import uuid
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Response

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

app = FastAPI(title="Stock Market Engine")


@app.on_event("startup")
async def startup_event():
    app.state.redis = init_redis_pool()


@app.post("/create")
async def create_engine(engine_config: EngineModel):
    engine = engine_config.create(
        get_stock_updater_factory(), get_signal_detector_factory()
    )
    if engine is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Incorrect engine configuration!"
        )

    engine_id = await store_engine(engine, get_redis(app))
    return engine_id


@app.post("/update/{engine_id}")
async def update_engine(engine_id: uuid.UUID, date: datetime.date):
    engine = await get_engine(engine_id, get_redis(app))
    if not engine:
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
    new_engine = await engine.update(date)
    engine_id = await store_engine(new_engine, get_redis(app))
    return engine_id


register_indicator_api(app)
register_signal_api(app)
register_stock_market_api(app)
