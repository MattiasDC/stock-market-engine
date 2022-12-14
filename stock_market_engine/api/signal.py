import json
import uuid
from http import HTTPStatus

from fastapi import Response
from stock_market.common.factory import Factory
from stock_market.ext.signal import register_signal_detector_factories

import stock_market_engine.engine as eng
from stock_market_engine.api.models import (
    SignalDetectorModel,
    SignalDetectorWithNameModel,
)
from stock_market_engine.common import get_redis
from stock_market_engine.engine_store import get_engine, store_engine


def register_signal_api(app):
    factory = register_signal_detector_factories(Factory())

    @app.get("/getsupportedsignaldetectors")
    async def get_supported_signal_detectors():
        signal_detectors = factory.get_registered_names()
        return [
            {"detector_name": sd, "schema": factory.get_schema(sd)}
            for sd in signal_detectors
        ]

    @app.get("/signaldetectors/{engine_id}")
    async def get_signal_detectors(engine_id: uuid.UUID):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        if engine is None:
            return []

        detectors = engine.signal_detectors
        return [
            SignalDetectorWithNameModel(
                static_name=d.NAME(), name=d.name, config=d.to_json()
            )
            for d in detectors
        ]

    @app.post("/addsignaldetector/{engine_id}")
    async def add_signal_detector(
        engine_id: uuid.UUID, signal_detector: SignalDetectorModel
    ):
        if signal_detector.static_name not in factory.get_registered_names():
            return Response(status_code=HTTPStatus.NO_CONTENT.value)

        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        if engine is None:
            return engine_id

        engine = await eng.add_signal_detector(
            engine,
            factory.create(
                signal_detector.static_name, json.dumps(signal_detector.config)
            ),
        )
        if engine is None:
            return engine_id

        new_engine_id = await store_engine(engine, redis)
        return str(new_engine_id)

    @app.post("/removesignaldetector/{engine_id}/{detector_id}")
    async def remove_signal_detector(engine_id: uuid.UUID, detector_id: int):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        if engine is None:
            return engine_id

        engine = await eng.remove_signal_detector(engine, detector_id)
        if engine is None:
            return engine_id

        new_engine_id = await store_engine(engine, redis)
        return str(new_engine_id)

    @app.get("/signals/{engine_id}")
    async def get_signals_id(engine_id: uuid.UUID):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        if engine is None:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)

        return engine.signals.to_json()
