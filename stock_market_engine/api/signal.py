import uuid

from stock_market_engine.common import get_engine, store_engine, get_redis

from stock_market.common.factory import Factory
from stock_market.ext.signal import register_signal_detector_factories

def register_signal_api(app):
	factory = register_signal_detector_factories(Factory())

	@app.get("/getsupportedsignaldetectors")
	async def get_supported_signal_detectors():
		signal_detectors = factory.get_registered_names()
		return [{'name' : sd, 'schema' : factory.get_schema(sd) } for sd in signal_detectors]