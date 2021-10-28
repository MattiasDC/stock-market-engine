from stock_market_engine.core.time_series import TimeSeries
from stock_market_engine.ext.indicator.exponential_moving_average import ExponentialMovingAverage
import datetime
import pandas as pd
import unittest

class TestMovingAverage(unittest.TestCase):
						 
	def test_ema(self):
		series = TimeSeries("dummy", pd.DataFrame(data=[[datetime.date(2020, 1, 1), 0],
														[datetime.date(2020,1,2), 10],
														[datetime.date(2020,1,3), 10]]))
		ema = ExponentialMovingAverage(2)
		ema_series = ema(series)
		self.assertEqual(len(ema_series), 3)
		self.assertEqual(ema_series.values.iloc[0], 0)
		self.assertTrue(ema_series.values.iloc[1] > 5)
		self.assertTrue(ema_series.values.iloc[2] > 5)

if __name__ == '__main__':
    unittest.main()