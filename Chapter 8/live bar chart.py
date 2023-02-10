import json
import threading
import queue

import matplotlib.pyplot as plt
import pandas
import mplfinance as mpf

from websocket import create_connection
from datetime import datetime


class sliding_window:
    def __init__(self, length):
        self.data = ([0]*length)
    def add(self, element):
        self.data.append(element)
        self.data.pop(0)

url = "wss://public-data-api.london-demo.lmax.com/v1/web-socket"
subscription_msg = '{"type": "SUBSCRIBE","channels": [{"name": "ORDER_BOOK","instruments": ["eur-usd"]}]}'

pipe = queue.Queue()
data_for_chart = queue.Queue()
window_size = 10
bids = sliding_window(window_size)
asks = sliding_window(window_size)

def LMAX_connect():
    ws = create_connection(url)
    ws.send(subscription_msg)
    result = ws.recv()
    while True:
        result = ws.recv()
        result = json.loads(result)
        pipe.put(result)

def get_ticks():
    while True:
        tick = pipe.get()
        if 'bids' in tick.keys():
            bid = float(tick['bids'][0]['price'])
            ask = float(tick['asks'][0]['price'])
            bids.add(bid)
            asks.add(ask)
            print(tick)

def make_bars():
    bars = pandas.DataFrame(columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
    bars.set_index('Timestamp', inplace=True)

    resolution = 10
    last_sample_ts = 0

    while True:
        tick = pipe.get()

        if 'bids' in tick.keys():
            bid = float(tick['bids'][0]['price'])
            ask = float(tick['asks'][0]['price'])
            bids.add(bid)
            asks.add(ask)

        ts = datetime.strptime(tick['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
        last_bid = float(tick['bids'][0]['price'])

        if last_sample_ts == 0:
            last_sample_ts = ts
            open = high = low = close = last_bid

        delta = ts - last_sample_ts
        print("Received tick: ", tick)

        if delta.seconds >= resolution:
        # if bids.data[-1] > asks.data[-2] or asks.data[-1] < bids.data[-2]:
            bar = pandas.DataFrame([[open, high, low, close]], columns = ['Open', 'High', 'Low', 'Close'], index = [ts])
            bars = pandas.concat([bars, bar])
            last_sample_ts = ts
            open = high = low = close = last_bid

            if len(bars) > 300:
                bars = bars.iloc[1:, :]

            data_for_chart.put(bars)
        else:
            high = max([high, last_bid])
            low = min([low, last_bid])
            close = last_bid

data_receiver_thread = threading.Thread(target = LMAX_connect)
data_receiver_thread.start()

trading_algo_thread = threading.Thread(target = make_bars)
trading_algo_thread.start()

fig = mpf.figure()
myaxes = fig.add_subplot(1,1,1)

while True:
    chart_data = data_for_chart.get()
    myaxes.clear()
    mpf.plot(chart_data, ax = myaxes, type='candle', block = False)
    plt.pause(1)
