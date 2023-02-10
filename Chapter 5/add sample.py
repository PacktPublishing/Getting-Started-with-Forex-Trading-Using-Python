from datetime import datetime

class data:
    def __init__ (self):
        self.series = {}

    def add(self, sample):
        ts = datetime.strptime(sample["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.series[ts] = sample

    def get(self, ts, key):
        return self.series[ts][key]

sample = {
	"type": "TICKER",
	"instrument_id": "eur-usd",
	"timestamp": "2022-07-29T11:10:54.755Z",
	"best_bid": "1.180970",
	"best_ask": "1.181010",
	"trade_id": "0B5WMAAAAAAAAAAS",
	"last_quantity": "1000.0000",
	"last_price": "1.180970",
	"session_open": "1.181070",
	"session_low": "1.180590",
	"session_high": "1.181390"
}
series = data()
series.add(sample)
timestamp = datetime.strptime(sample["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
print(series.get(timestamp, "trade_id"))