import dateparser
import datetime
import json
from pydantic import BaseModel, Json, constr
from typing import List

from stock_market.core import StockMarket
from stock_market.core import Ticker

from .config import get_settings
from .engine import Engine

class TickerModel(BaseModel):
	symbol : constr(max_length=get_settings().max_ticker_symbol_length)

	def create(self):
		return Ticker(self.symbol)

class StockMarketModel(BaseModel):
	start_date: datetime.date
	tickers: List[TickerModel]

	def create(self):
		return StockMarket(self.start_date, [ticker.create() for ticker in self.tickers])

class SignalDetectorModel(BaseModel):
	name : str
	config : Json

	def create(self, factory):
		return factory.create(self.name, json.dumps(self.config))

class SignalsDetectorsModel(BaseModel):
	signal_detectors: List[SignalDetectorModel]

	def create(self, factory):
		return [detector_config.create(factory) for detector_config in self.signal_detectors]

class EngineModel(BaseModel):
	stock_market: StockMarketModel
	signal_detectors: SignalsDetectorsModel

	def create(self, stock_updater_factory, signal_detector_factory):
		sm = self.stock_market.create()
		signal_detectors = self.signal_detectors.create(signal_detector_factory)
		stock_updater = stock_updater_factory.create(get_settings().stock_updater, None)
		return Engine(sm, stock_updater, signal_detectors)