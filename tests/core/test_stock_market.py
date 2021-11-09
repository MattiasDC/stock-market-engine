import datetime
import pandas as pd
import unittest
from stock_market_engine.core import OHLC
from stock_market_engine.core import Ticker
from stock_market_engine.core import TickerOHLC
from stock_market_engine.core import StockMarket

class TestStockMarket(unittest.TestCase):

	def setUp(self):
		self.spy = Ticker('SPY')
		self.raw_data = pd.read_csv("tests/data/SPY.csv")
		self.ohlc = OHLC(self.raw_data.Date,
						 self.raw_data.Open,
						 self.raw_data.High,
						 self.raw_data.Low,
						 self.raw_data.Close)
		self.date = datetime.date(2000, 2, 2)

	def test_start_date(self):
		sm = StockMarket(self.date, [self.spy])
		self.assertEqual(sm.start_date, self.date)

	def test_tickers(self):
		sm = StockMarket(self.date, [self.spy])
		self.assertEqual(sm.tickers, [self.spy])

	def test_ohlc_and_update_ticker(self):
		sm = StockMarket(self.date, [self.spy])
		self.assertEqual(sm.ohlc(self.spy), None)
		sm.update_ticker(TickerOHLC(self.spy, self.ohlc))
		self.assertEqual(sm.ohlc(self.spy).start, sm.start_date)
		self.assertEqual(sm.ohlc(self.spy).end, self.ohlc.end)

	def test_date(self):
		sm = StockMarket(self.date, [self.spy])
		self.assertEqual(sm.date, self.date)
		sm.update_ticker(TickerOHLC(self.spy, self.ohlc))
		self.assertEqual(sm.date, self.ohlc.end)

	def test_eq(self):
		sm = StockMarket(self.date, [self.spy])
		self.assertEqual(sm, sm)
		self.assertNotEqual(sm, 0)

	def test_json(self):
		sm = StockMarket(self.date, [self.spy])
		sm.update_ticker(TickerOHLC(self.spy, self.ohlc))
		self.assertEqual(sm, StockMarket.from_json(sm.to_json()))

if __name__ == '__main__':
    unittest.main()