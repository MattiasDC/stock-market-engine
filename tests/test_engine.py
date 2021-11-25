import datetime
import json
import pandas as pd
import unittest

from stock_market_engine.engine import Engine, add_ticker, remove_ticker, add_signal_detector, remove_signal_detector
from stock_market.common.factory import Factory
from stock_market.core import add_signal,\
							  OHLC,\
							  TickerOHLC,\
							  Ticker,\
							  Signal,\
							  SignalDetector,\
							  SignalSequence,\
							  StockMarket,\
							  StockUpdater

class DummyStockMarketUpdater(StockUpdater):
	def __init__(self):
		super().__init__("DummyUpdater")

	def update(self, date, stock_market):
		 ohlc = OHLC(pd.Series([date]), pd.Series([1]), pd.Series([2]), pd.Series([3]), pd.Series([4]))
		 stock_market = stock_market.update_ticker(TickerOHLC(Ticker('SPY'), ohlc))
		 return stock_market

	def to_json(self):
		return json.dumps({})

	@staticmethod
	def from_json(json_str):
		return DummyStockMarketUpdater()

	@staticmethod
	def json_schema():
		return {}

class DummyMonthlySignalDetector(SignalDetector):
	def __init__(self):
		super().__init__(1, "DummyDetector")

	def detect(self, date, stock_market):
		sequence = SignalSequence()
		if date.day == 1:
			sequence = add_signal(sequence, Signal(self.id, self.name, date))
		return sequence

	def update(self, date, stock_market):
		pass

	def __eq__(self, other):
		return isinstance(other, DummyMonthlySignalDetector)

	def to_json(self):
		return json.dumps({})

	@staticmethod
	def from_json(json_str):
		return DummyMonthlySignalDetector()

	@staticmethod
	def json_schema():
		return {}

class TestEngine(unittest.TestCase):

	def setUp(self):
		self.spy = Ticker('SPY')
		self.date = datetime.date(2000, 2, 2)
		self.stock_market = StockMarket(self.date, [self.spy])
		self.stock_updater = DummyStockMarketUpdater()
		self.engine = Engine(self.stock_market, self.stock_updater, [DummyMonthlySignalDetector()])

	def test_update(self):
		date = datetime.date(2000, 5, 1)
		self.engine.update(date)
		self.assertEqual(date, self.engine.stock_market.date)
		self.assertEqual(3, len(self.engine.signals.signals))
		last_spy_time_value = self.engine.stock_market.ohlc(self.spy).close.time_values.iloc[-1]
		self.assertEqual(date, last_spy_time_value.date)
		self.assertEqual(4, last_spy_time_value.value)

	def test_json(self):
		factory = Factory()
		factory.register("DummyDetector", lambda _: DummyMonthlySignalDetector(), DummyMonthlySignalDetector.json_schema())
		factory.register("DummyUpdater", lambda _: DummyStockMarketUpdater(), DummyStockMarketUpdater.json_schema())
		from_json = Engine.from_json(self.engine.to_json(), factory, factory)
		self.assertEqual(self.engine.stock_market, from_json.stock_market)
		self.assertEqual(self.engine.signals, from_json.signals)

	def test_add_ticker(self):
		QQQ = Ticker("QQQ")
		engine = add_ticker(self.engine, QQQ)
		self.assertTrue(QQQ in engine.stock_market.tickers)

	def test_remove_ticker(self):
		engine = remove_ticker(self.engine, self.spy)
		self.assertFalse(self.spy in engine.stock_market.tickers)

	def test_add_signal_detector(self):
		detector = DummyMonthlySignalDetector()
		engine = Engine(self.stock_market, self.stock_updater, [])
		engine = add_signal_detector(engine, detector)
		self.assertTrue(detector in engine.signal_detectors)

	def test_remove_signal_detector(self):
		detector = DummyMonthlySignalDetector()
		engine = Engine(self.stock_market, self.stock_updater, [])
		engine = add_signal_detector(engine, detector)
		engine = remove_signal_detector(engine, detector.id)
		self.assertFalse(detector in engine.signal_detectors)

if __name__ == '__main__':
    unittest.main()