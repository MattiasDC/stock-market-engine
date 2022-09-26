import uuid
from http import HTTPStatus

from fastapi import Response
from stock_market.core.ticker import Ticker

import stock_market_engine.engine as eng
from stock_market_engine.common import get_redis
from stock_market_engine.engine_store import get_engine, store_engine


def register_stock_market_api(app):
    @app.get("/getdate/{engine_id}")
    async def get_date(engine_id: uuid.UUID):
        engine = await get_engine(engine_id, get_redis(app))
        if not engine:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        return engine.date

    @app.get("/getstartdate/{engine_id}")
    async def get_start_date(engine_id: uuid.UUID):
        engine = await get_engine(engine_id, get_redis(app))
        if not engine:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        return engine.stock_market.start_date

    @app.get("/tickers/{engine_id}")
    async def get_tickers(engine_id: uuid.UUID):
        engine = await get_engine(engine_id, get_redis(app))
        if not engine:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        return [ticker.symbol for ticker in engine.stock_market.tickers]

    @app.get("/ticker/{engine_id}/{ticker_id}")
    async def get_ticker_ohlc(engine_id: uuid.UUID, ticker_id: str):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)

        if not engine:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        ohlc = engine.stock_market.ohlc(Ticker(ticker_id))
        if ohlc is None:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        return ohlc.to_json()

    @app.get("/signals/{engine_id}")
    async def get_signals(engine_id: uuid.UUID):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        if not engine:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        return engine.signals.to_json()

    @app.post("/addticker/{engine_id}/{ticker_id}")
    async def add_ticker(engine_id: uuid.UUID, ticker_id: str):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        if not engine:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        ticker = Ticker(ticker_id)
        if ticker in engine.stock_market.tickers:
            return engine_id

        engine = await eng.add_ticker(engine, ticker)
        new_engine_id = await store_engine(engine, redis)
        return str(new_engine_id)

    @app.post("/removeticker/{engine_id}/{ticker_id}")
    async def remove_ticker(engine_id: uuid.UUID, ticker_id: str):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        if not engine:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        ticker = Ticker(ticker_id)
        if ticker not in engine.stock_market.tickers:
            return engine_id

        engine = await eng.remove_ticker(engine, ticker)
        new_engine_id = await store_engine(engine, redis)
        return str(new_engine_id)
