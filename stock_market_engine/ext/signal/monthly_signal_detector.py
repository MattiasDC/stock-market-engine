import json

from stock_market_engine.core import add_signal
from stock_market_engine.core import Signal
from stock_market_engine.core import SignalDetector

class MonthlySignalDetector(SignalDetector):
	def __init__(self, identifier):
		super().__init__(identifier, MonthlySignalDetector.name)

	def detect(self, date, stock_market, sequence):
		if date.day == 1:
			sequence = add_signal(sequence, Signal(self.id, self.name, date))
		return sequence

	def __eq__(self, other):
		if not isinstance(other, MonthlySignalDetector):
			return False
		return self.id == other.id

	@staticmethod
	def name():
		return "monthly"

	def to_json(self):
		return json.dumps({"id" : self.id})

	@staticmethod
	def from_json(json_str):
		return MonthlySignalDetector(json.loads(json_str)["id"])