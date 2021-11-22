import uuid

from stock_market_engine.common import get_engine, store_engine, get_redis

def register_signal_api(app):
	@app.get("/getsupportedsignaldetectors")
	async def get_supported_signal_detectors():
		pass