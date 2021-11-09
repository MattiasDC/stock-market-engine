from stock_market_engine.core.ohlc import OHLC, merge_ohlcs
from stock_market_engine.core.stock_updater import StockUpdater
from stock_market_engine.core.ticker_ohlc import TickerOHLC

import datetime
import json
import yahoo_fin.stock_info as yf

class YahooFinanceStockUpdater(StockUpdater):
	def __init__(self):
		super().__init__("yahoo")

	def __get_period(self, stock_market, ohlc, date):
		start = ohlc.end + datetime.timedelta(days=1)
		end = date
		return start, end

	def __get_ohlc(self, start, end, ticker):
		ticker_hist = yf.get_data(ticker.symbol, start_date=start, end_date=end, interval="1d", index_as_date=False)
		ticker_hist = ticker_hist.reset_index()
			
		if len(ticker_hist.date) == 0:
			return None
		return OHLC(ticker_hist.date,
					ticker_hist.open,
					ticker_hist.high,
					ticker_hist.low,
					ticker_hist.adjclose)

	def update(self, date, stock_market):
		date_exclusive = date + datetime.timedelta(days=1)
		for ticker in stock_market.tickers:
			ohlc = stock_market.ohlc(ticker)
			if ohlc is None:
				start = stock_market.start_date
				end = date_exclusive
			else:
				start, end = self.__get_period(stock_market, ohlc, date_exclusive)

			if start == end:
				continue
			assert start < end
			new_ohlc = self.__get_ohlc(start, end, ticker)
			if new_ohlc is not None:
				stock_market.update_ticker(TickerOHLC(ticker, merge_ohlcs(ohlc, new_ohlc)))

	def __eq__(self, other):
		return isinstance(other, YahooFinanceStockUpdater)