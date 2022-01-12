import datetime as dt
import json

from stock_market.core import SignalSequence, StockMarket, merge_signals


class Engine:
    def __init__(
        self,
        stock_market,
        stock_market_updater,
        signal_detectors,
        signal_sequences=None,
        date=None,
    ):
        self.__stock_market = stock_market
        self.__stock_market_updater = stock_market_updater
        self.__signal_detectors = signal_detectors
        self.__signal_sequences = signal_sequences
        if signal_sequences is None:
            self.__signal_sequences = [
                SignalSequence() for _ in range(len(self.__signal_detectors))
            ]
        self.__date = stock_market.date if date is None else date

    def update(self, date):
        new_stock_market = self.stock_market_updater.update(date, self.stock_market)
        signal_sequences = []

        for detector, signal_sequence in zip(
            self.signal_detectors, self.signal_sequences
        ):
            from_date = new_stock_market.start_date
            if signal_sequence.signals:
                from_date = signal_sequence.signals[-1].date + dt.timedelta(days=1)
            signal_sequences.append(
                detector.detect(from_date, date, new_stock_market, signal_sequence)
            )

        return Engine(
            new_stock_market,
            self.stock_market_updater,
            self.signal_detectors,
            signal_sequences,
            date,
        )

    @property
    def date(self):
        return self.__date

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
        return merge_signals(*self.__signal_sequences)

    @property
    def signal_sequences(self):
        return self.__signal_sequences

    def to_json(self):
        stock_market_updater_json = {
            "name": self.stock_market_updater.name,
            "config": self.stock_market_updater.to_json(),
        }
        signal_detectors_json = [
            {"name": detector.NAME(), "config": detector.to_json()}
            for detector in self.signal_detectors
        ]
        return json.dumps(
            {
                "stock_market": self.stock_market.to_json(),
                "signal_sequences": [
                    signal_sequence.to_json()
                    for signal_sequence in self.signal_sequences
                ],
                "stock_updater": stock_market_updater_json,
                "signal_detectors": signal_detectors_json,
            }
        )

    @staticmethod
    def from_json(json_str, stock_updater_factory, signal_detector_factory):
        json_obj = json.loads(json_str)
        engine = Engine(
            StockMarket.from_json(json_obj["stock_market"]),
            stock_updater_factory.create(
                json_obj["stock_updater"]["name"], json_obj["stock_updater"]["config"]
            ),
            [
                signal_detector_factory.create(config["name"], config["config"])
                for config in json_obj["signal_detectors"]
            ],
        )
        engine.__signal_sequences = [
            SignalSequence.from_json(signal_sequence)
            for signal_sequence in json_obj["signal_sequences"]
        ]
        return engine


def add_ticker(engine, ticker):
    new_engine = Engine(
        engine.stock_market.add_ticker(ticker),
        engine.stock_market_updater,
        engine.signal_detectors,
        engine.signal_sequences,
    )
    new_engine = new_engine.update(engine.date)
    return new_engine


def remove_ticker(engine, ticker):
    stock_market = engine.stock_market.remove_ticker(ticker)
    new_engine = Engine(
        stock_market,
        engine.stock_market_updater,
        [sd for sd in engine.signal_detectors if sd.is_valid(stock_market)],
        [
            ss
            for i, ss in enumerate(engine.signal_sequences)
            if engine.signal_detectors[i].is_valid(stock_market)
        ],
    )
    new_engine = new_engine.update(engine.date)
    return new_engine


def add_signal_detector(engine, detector):
    assert detector.is_valid(engine.stock_market), (detector, engine.stock_market)
    if detector in engine.signal_detectors:
        return None
    if detector.id in [d.id for d in engine.signal_detectors]:
        return None
    detectors = engine.signal_detectors + [detector]
    new_engine = Engine(
        engine.stock_market,
        engine.stock_market_updater,
        detectors,
        engine.signal_sequences + [SignalSequence()],
    )
    new_engine = new_engine.update(engine.date)
    return new_engine


def remove_signal_detector(engine, detector_id):
    ids = [d.id for d in engine.signal_detectors]
    if detector_id not in ids:
        return None
    i = ids.index(detector_id)
    detectors = engine.signal_detectors.copy()
    del detectors[i]
    sequences = engine.signal_sequences.copy()
    del sequences[i]
    new_engine = Engine(
        engine.stock_market, engine.stock_market_updater, detectors, sequences
    )
    new_engine = new_engine.update(engine.date)
    return new_engine
