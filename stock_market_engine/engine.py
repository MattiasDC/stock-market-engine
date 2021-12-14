import datetime as dt
import json
import pandas as pd

from stock_market.core import SignalSequence, merge_signals
from stock_market.core import StockMarket

class Engine:
	def __init__(self,
				 stock_market,
				 stock_market_updater,
				 signal_detectors):
		self.__stock_market = stock_market
		self.__stock_market_updater = stock_market_updater
		self.__signal_detectors = signal_detectors
		self.__signals = [SignalSequence() for _ in range(len(self.__signal_detectors))]

	def update(self, date):
		current_end = self.stock_market.date
		self.__stock_market = self.stock_market_updater.update(date, self.stock_market)

		for i, (detector, signals) in enumerate(zip(self.signal_detectors, self.__signals)):
			self.__signals[i] = detector.detect(current_end, date, self.stock_market, self.signals)

	@property
	def stock_market_updater(self):
		return self.__stock_market_updater

	@property
	def signal_detectors(self):
		return self.__signal_detectors

	@property
	def stock_market(self):
		return self.__stock_market
		
	@property
	def signals(self):
		return merge_signals(*self.__signals)

	def to_json(self):
		stock_market_updater_json = {"name": self.stock_market_updater.name,
									 "config": self.stock_market_updater.to_json()}
		signal_detectors_json = [{"name" : detector.name,
					       		  "config": detector.to_json()} for detector in self.signal_detectors]
		return json.dumps({"stock_market" : self.stock_market.to_json(),
					       "signals" : [signal_sequence.to_json() for signal_sequence in self.__signals],
					       "stock_updater" : stock_market_updater_json,
					       "signal_detectors" : signal_detectors_json})

	@staticmethod
	def from_json(json_str, stock_updater_factory, signal_detector_factory):
		json_obj = json.loads(json_str)
		engine = Engine(StockMarket.from_json(json_obj["stock_market"]),
				 	    stock_updater_factory.create(json_obj["stock_updater"]["name"], json_obj["stock_updater"]["config"]),
				        [signal_detector_factory.create(config["name"], config["config"]) for config in json_obj["signal_detectors"]])
		engine.__signals = [SignalSequence.from_json(signal_sequence) for signal_sequence in json_obj["signals"]]
		return engine

def add_ticker(engine, ticker):
	return Engine(engine.stock_market.add_ticker(ticker),
				  engine.stock_market_updater,
				  engine.signal_detectors)

def remove_ticker(engine, ticker):
	return Engine(engine.stock_market.remove_ticker(ticker),
				  engine.stock_market_updater,
				  engine.signal_detectors)

def add_signal_detector(engine, detector):
	if detector in engine.signal_detectors:
		return None
	if detector.id in [d.id for d in engine.signal_detectors]:
		return None
	detectors = engine.signal_detectors + [detector]
	return Engine(engine.stock_market,
		   		  engine.stock_market_updater,
		   		  detectors)

def remove_signal_detector(engine, detector_id):
	if detector_id not in [d.id for d in engine.signal_detectors]:
		return None
	detectors = [d for d in engine.signal_detectors if d.id != detector_id]
	return Engine(engine.stock_market,
		   		  engine.stock_market_updater,
		   		  detectors)