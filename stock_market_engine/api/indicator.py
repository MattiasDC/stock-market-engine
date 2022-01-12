from stock_market.common.factory import Factory
from stock_market.ext.indicator import register_indicator_factories


def register_indicator_api(app):
    factory = register_indicator_factories(Factory())

    @app.get("/getsupportedindicators")
    async def get_supported_indicators():
        indicators = factory.get_registered_names()
        return [
            {"indicator_name": indicator, "schema": factory.get_schema(indicator)}
            for indicator in indicators
        ]
