from stock_market.common.factory import Factory
from stock_market.ext.fetcher import register_stock_updater_factories
from stock_market.ext.signal import register_signal_detector_factories


def get_redis(app):
    return app.state.redis


def get_signal_detector_factory():
    return register_signal_detector_factories(Factory())


def get_stock_updater_factory():
    return register_stock_updater_factories(Factory())
