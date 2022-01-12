import uuid

from stock_market.core.ticker import Ticker

from stock_market_engine.common import get_engine, store_engine, get_redis
import stock_market_engine.engine as eng


def register_stock_market_api(app):
    @app.get("/getdate/{engine_id}")
    async def get_date(engine_id: uuid.UUID):
        engine = await get_engine(engine_id, get_redis(app))
        return engine.stock_market.date

    @app.get("/getstartdate/{engine_id}")
    async def get_start_date(engine_id: uuid.UUID):
        engine = await get_engine(engine_id, get_redis(app))
        return engine.stock_market.start_date

    @app.get("/tickers/{engine_id}")
    async def get_tickers(engine_id: uuid.UUID):
        engine = await get_engine(engine_id, get_redis(app))
        return [ticker.symbol for ticker in engine.stock_market.tickers]

    @app.get("/ticker/{engine_id}/{ticker_id}")
    async def get_ticker_data_id(engine_id: uuid.UUID, ticker_id: str):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        ohlc = engine.stock_market.ohlc(Ticker(ticker_id))
        if ohlc is None:
            return
        return ohlc.to_json()

    @app.get("/signals/{engine_id}")
    async def get_signals_id(engine_id: uuid.UUID):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        return engine.signals.to_json()

    @app.post("/addticker/{engine_id}/{ticker_id}")
    async def add_ticker(engine_id: uuid.UUID, ticker_id: str):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        ticker = Ticker(ticker_id)
        if ticker in engine.stock_market.tickers:
            return engine_id

        engine = eng.add_ticker(engine, ticker)
        new_engine_id = str(uuid.uuid4())
        await store_engine(engine, new_engine_id, redis)
        return new_engine_id

    @app.post("/removeticker/{engine_id}/{ticker_id}")
    async def remove_ticker(engine_id: uuid.UUID, ticker_id: str):
        redis = get_redis(app)
        engine = await get_engine(engine_id, redis)
        ticker = Ticker(ticker_id)
        if ticker not in engine.stock_market.tickers:
            return engine_id

        engine = eng.remove_ticker(engine, ticker)
        new_engine_id = str(uuid.uuid4())
        await store_engine(engine, new_engine_id, redis)
        return new_engine_id
