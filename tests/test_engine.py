import datetime
import json

import pandas as pd
import pytest
from stock_market.common.factory import Factory
from stock_market.core import (
    OHLC,
    Sentiment,
    Signal,
    SignalDetector,
    StockMarket,
    StockUpdater,
    Ticker,
    TickerOHLC,
    add_signal,
)

from stock_market_engine.engine import (
    Engine,
    add_signal_detector,
    add_ticker,
    remove_signal_detector,
    remove_ticker,
)


class DummyStockMarketUpdater(StockUpdater):
    def __init__(self):
        super().__init__("DummyUpdater")

    async def update(self, date, stock_market):
        ohlc = OHLC(
            pd.Series([date]),
            pd.Series([1]),
            pd.Series([2]),
            pd.Series([3]),
            pd.Series([4]),
        )
        if Ticker("SPY") in stock_market.tickers:
            stock_market = stock_market.update_ticker(TickerOHLC(Ticker("SPY"), ohlc))
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

    def detect(self, from_date, to_date, stock_market, sequence):
        for date in map(lambda d: d.date(), pd.date_range(from_date, to_date)):
            if date.day == 1:
                sequence = add_signal(
                    sequence, Signal(self.id, self.name, Sentiment.NEUTRAL, date)
                )
        return sequence

    def is_valid(self, stock_market):
        return True

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

    @staticmethod
    def NAME():
        return "DummyDetector"


@pytest.fixture
def spy():
    return Ticker("SPY")


@pytest.fixture
def date():
    return datetime.date(2000, 2, 2)


@pytest.fixture
def stock_market(date, spy):
    return StockMarket(date, [spy])


@pytest.fixture
def stock_updater():
    return DummyStockMarketUpdater()


@pytest.fixture
def engine(stock_market, stock_updater):
    return Engine(stock_market, stock_updater, [DummyMonthlySignalDetector()])


async def test_update(engine, spy):
    date = datetime.date(2000, 5, 1)
    engine = await engine.update(date)
    assert date == engine.stock_market.date
    assert 3 == len(engine.signals.signals)
    last_spy_time_value = engine.stock_market.ohlc(spy).close.time_values.iloc[-1]
    assert date == last_spy_time_value.date
    assert 4 == last_spy_time_value.value


async def test_json(engine):
    factory = Factory()
    factory.register(
        "DummyDetector",
        lambda _: DummyMonthlySignalDetector(),
        DummyMonthlySignalDetector.json_schema(),
    )
    factory.register(
        "DummyUpdater",
        lambda _: DummyStockMarketUpdater(),
        DummyStockMarketUpdater.json_schema(),
    )
    date = datetime.date(2000, 5, 1)
    engine = await engine.update(date)
    from_json = Engine.from_json(engine.to_json(), factory, factory)
    assert engine.stock_market == from_json.stock_market
    assert engine.signals == from_json.signals
    assert engine.signal_detectors == from_json.signal_detectors


async def test_add_ticker(engine):
    QQQ = Ticker("QQQ")
    engine = await add_ticker(engine, QQQ)
    assert QQQ in engine.stock_market.tickers


async def test_remove_ticker(engine, spy):
    engine = await remove_ticker(engine, spy)
    assert spy not in engine.stock_market.tickers


async def test_add_signal_detector(stock_market, stock_updater):
    detector = DummyMonthlySignalDetector()
    engine = Engine(stock_market, stock_updater, [])
    engine = await add_signal_detector(engine, detector)
    assert detector in engine.signal_detectors


async def test_remove_signal_detector(stock_market, stock_updater):
    detector = DummyMonthlySignalDetector()
    engine = Engine(stock_market, stock_updater, [])
    engine = await add_signal_detector(engine, detector)
    engine = await remove_signal_detector(engine, detector.id)
    assert detector not in engine.signal_detectors
