import uuid
from fastapi import Response
from http import HTTPStatus

from stock_market.core.ticker import Ticker

from stock_market_engine.common import get_engine, store_temporary, store_engine, get_redis
from stock_market_engine.engine import Engine
import stock_market_engine.engine as eng

def register_stock_market_api(app):
	@app.get("/getdate/{engine_id}")
	async def get_date(engine_id : uuid.UUID):
		engine = await get_engine(engine_id, get_redis(app))
		return engine.stock_market.date
	
	@app.get("/getstartdate/{engine_id}")
	async def get_start_date(engine_id : uuid.UUID):
		engine = await get_engine(engine_id, get_redis(app))
		return engine.stock_market.start_date
	
	@app.get("/tickers/{engine_id}")
	async def get_tickers(engine_id : uuid.UUID):
		engine = await get_engine(engine_id, get_redis(app))
		return [ticker.symbol for ticker in engine.stock_market.tickers]
	
	@app.get("/ticker/{engine_id}/{ticker_id}")
	async def get_ticker_data_id(engine_id : uuid.UUID, ticker_id : str):
		redis = get_redis(app)
		engine = await get_engine(engine_id, redis)
		ohlc = engine.stock_market.ohlc(Ticker(ticker_id))
		random_id = await store_temporary(ohlc, redis)
		if random_id is None:
			return Response(status_code=HTTPStatus.NO_CONTENT.value)
		return random_id
	
	@app.get("/signals/{engine_id}")
	async def get_signals_id(engine_id : uuid.UUID):
		redis = get_redis(app)
		engine = await get_engine(engine_id, redis)
		random_id = await store_temporary(engine.signals, redis)
		if random_id is None:
			return Response(status_code=HTTPStatus.NO_CONTENT.value)
		return random_id
	
	@app.post("/addticker/{engine_id}/{ticker_id}")
	async def add_ticker(engine_id : uuid.UUID, ticker_id : str):
		redis = get_redis(app)
		engine = await get_engine(engine_id, redis)
		ticker = Ticker(ticker_id)
		if ticker in engine.stock_market.tickers:
			return Response(status_code=HTTPStatus.NO_CONTENT.value)
	
		eng.add_ticker(engine, ticker)
		new_engine_id = str(uuid.uuid4())
		await store_engine(engine, new_engine_id, redis)
		return new_engine_id
	
	@app.post("/removeticker/{engine_id}/{ticker_id}")
	async def remove_ticker(engine_id : uuid.UUID, ticker_id : str):
		redis = get_redis(app)
		engine = await get_engine(engine_id, redis)
		ticker = Ticker(ticker_id)
		if ticker not in engine.stock_market.tickers:
			return Response(status_code=HTTPStatus.NO_CONTENT.value)
	
		engine = Engine(engine.stock_market.remove_ticker(ticker),
						engine.stock_market_updater,
						engine.signal_detectors)
		new_engine_id = str(uuid.uuid4())
		await store_engine(engine, new_engine_id, redis)
		return new_engine_id
	