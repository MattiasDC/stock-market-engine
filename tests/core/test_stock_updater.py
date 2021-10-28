import unittest
from stock_market_engine.core.stock_updater import StockUpdater

class TestStockUpdater(unittest.TestCase):
						 
	def test_name(self):
		self.assertEqual(StockUpdater("Test").name, "Test")

if __name__ == '__main__':
    unittest.main()