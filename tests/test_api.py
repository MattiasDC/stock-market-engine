import datetime as dt
import json
from http import HTTPStatus

import pytest
from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient
from stock_market.core import OHLC

from stock_market_engine.main import app


def get_client_impl():
    with TestClient(app) as client:
        app.state.redis = FakeRedis()
        while True:
            yield client


@pytest.fixture
def client():
    return next(get_client_impl())


def get_date(client, engine_id):
    response = client.get(f"/getdate/{engine_id}")
    assert response.status_code == HTTPStatus.OK
    return response.text.strip('"')


def test_api(client):
    spy = "SPY"

    response = client.post(
        "/create",
        json={
            "stock_market": {
                "start_date": "2021-01-01",
                "tickers": [{"symbol": spy}],
            },
            "signal_detectors": [],
        },
    )
    assert response.status_code == HTTPStatus.OK
    engine_id = response.text.strip('"')
    assert engine_id is not None

    assert get_date(client, engine_id) == "2021-01-01"

    response = client.post(f"/update/{engine_id}", params={"date": "2021-01-05"})
    assert response.status_code == HTTPStatus.OK
    engine_id = response.json()
    assert get_date(client, engine_id) == "2021-01-05"

    response = client.get(f"/getstartdate/{engine_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.text.strip('"') == "2021-01-01"

    response = client.get(f"/ticker/{engine_id}/{spy}")
    assert response.status_code == HTTPStatus.OK
    ticker_data = OHLC.from_json(response.json())
    assert ticker_data.end == dt.date(2021, 1, 4)

    response = client.get(f"/signals/{engine_id}")
    assert response.status_code == HTTPStatus.OK
    assert json.loads(response.json()) == []

    response = client.get(f"/tickers/{engine_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [spy]

    qqq = "QQQ"
    response = client.post(f"/addticker/{engine_id}/{qqq}")
    assert response.status_code == HTTPStatus.OK
    new_engine_id = response.text.strip('"')

    response = client.get(f"/tickers/{new_engine_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [spy, qqq]

    response = client.post(f"/removeticker/{new_engine_id}/{spy}")
    assert response.status_code == HTTPStatus.OK
    new_engine_id = response.text.strip('"')

    response = client.get(f"/tickers/{new_engine_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [qqq]

    response = client.get("/getsupportedsignaldetectors")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 6

    signal_detector = "Monthly"
    detector_id = 1
    response = client.post(
        f"/addsignaldetector/{engine_id}",
        json={"static_name": signal_detector, "config": json.dumps(detector_id)},
    )
    assert response.status_code == HTTPStatus.OK
    new_engine_id = response.text.strip('"')

    response = client.get(f"/signaldetectors/{new_engine_id}")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1

    response = client.post(f"/removesignaldetector/{new_engine_id}/{detector_id}")
    assert response.status_code == HTTPStatus.OK
    new_engine_id = response.text.strip('"')

    response = client.get(f"/signaldetectors/{new_engine_id}")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0

    response = client.get("/getsupportedindicators")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 3
