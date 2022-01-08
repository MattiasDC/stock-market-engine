import datetime as dt
from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient
from http import HTTPStatus
import json
import unittest

from stock_market.core import OHLC

from stock_market_engine.main import app

class TestApi(unittest.TestCase):

    def get_client_impl(self):
        with TestClient(app) as client:
            app.state.redis = FakeRedis()
            while True:
                yield client

    def get_client(self):
    	return next(self.get_client_impl())


    def get_date(self, client, engine_id):
        response = client.get(f"/getdate/{engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        return response.text.strip("\"")

    def test_api(self):
        client = self.get_client()
        spy = "SPY"

        response = client.post("/create", json=
            {
              "stock_market": {
                "start_date": "2021-01-01",
                "tickers": [
                  {
                    "symbol": spy
                  }
                ]
              },
              "signal_detectors": []
            })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        engine_id = response.text.strip("\"")
        self.assertNotEqual(engine_id, None)

        self.assertEqual(self.get_date(client, engine_id), "2021-01-01")

        response = client.post(f"/update/{engine_id}", params={"date" : "2021-01-04"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.get_date(client, engine_id), "2021-01-04")

        response = client.get(f"/getstartdate/{engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.text.strip("\""), "2021-01-01")

        response = client.get(f"/ticker/{engine_id}/{spy}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        ticker_data = OHLC.from_json(response.json())
        self.assertEqual(ticker_data.end, dt.date(2021, 1, 4))

        response = client.get(f"/signals/{engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(json.loads(response.json()), [])

        response = client.get(f"/tickers/{engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), [spy])

        qqq = "QQQ"
        response = client.post(f"/addticker/{engine_id}/{qqq}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        new_engine_id = response.text.strip("\"")

        response = client.get(f"/tickers/{new_engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), [spy, qqq])

        response = client.post(f"/removeticker/{new_engine_id}/{spy}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        new_engine_id = response.text.strip("\"")
        
        response = client.get(f"/tickers/{new_engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), [qqq])

        response = client.get(f"/getsupportedsignaldetectors")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json()), 5)


        signal_detector = "Monthly"
        detector_id = 1
        response = client.post(f"/addsignaldetector/{engine_id}", json={"static_name" : signal_detector,
        																"config" : json.dumps(detector_id)})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        new_engine_id = response.text.strip("\"")

        response = client.get(f"/signaldetectors/{new_engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json()), 1)

        response = client.post(f"/removesignaldetector/{new_engine_id}/{detector_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        new_engine_id = response.text.strip("\"")
        
        response = client.get(f"/signaldetectors/{new_engine_id}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json()), 0)

        response = client.get(f"/getsupportedindicators")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json()), 3)