import json
import threading
import queue
import matplotlib.pyplot as plt

from websocket import create_connection

class sliding_window:
    def __init__(self, length):
        self.data = ([0]*length)
    def add(self, element):
        self.data.append(element)
        self.data.pop(0)

def LMAX_connect(url, subscription_msg, ticks_queue):
    ws = create_connection(url)
    ws.send(subscription_msg)

    while True:
        tick = json.loads(ws.recv())
        ticks_queue.put(tick)

def get_ticks(ticks_queue):
    while True:
        tick = ticks_queue.get()
        if 'bids' in tick.keys():
            bid = float(tick['bids'][0]['price'])
            ask = float(tick['asks'][0]['price'])
            bids.add(bid)
            asks.add(ask)
            print(bid, ask)

url = "wss://public-data-api.london-demo.lmax.com/v1/web-socket"
subscription_msg = '{"type": "SUBSCRIBE","channels": [{"name": "ORDER_BOOK","instruments": ["eur-usd"]}]}'

pipe = queue.Queue()
window_size = 30
bids = sliding_window(window_size)
asks = sliding_window(window_size)

data_receiver_thread = threading.Thread(target = LMAX_connect, args = (url, subscription_msg, pipe))
data_receiver_thread.start()

trading_algo_thread = threading.Thread(target = get_ticks, args = (pipe,))
trading_algo_thread.start()

while bids.data[0] == 0:
    pass

buy_signals_x = []
buy_signals_y = []
sell_signals_x = []
sell_signals_y = []

fig = plt.figure()
ax = fig.add_subplot()
line1, = ax.plot(bids.data)
line2, = ax.plot(asks.data)
line3, = ax.plot(buy_signals_x, buy_signals_y, 'g^')
line4, = ax.plot(sell_signals_x, sell_signals_y, 'mv')

while True:
    buy_signals_x = []
    buy_signals_y = []
    sell_signals_x = []
    sell_signals_y = []
    for i in range(1, window_size):
        if bids.data[i] > asks.data[i - 1]:
            buy_signals_x.append(i)
            buy_signals_y.append(bids.data[i] - 0.0001)
        if asks.data[i] < bids.data[i - 1]:
            sell_signals_x.append(i)
            sell_signals_y.append(asks.data[i] + 0.0001)

    line1.set_ydata(bids.data)
    line2.set_ydata(asks.data)
    line3.set_xdata(buy_signals_x)
    line3.set_ydata(buy_signals_y)
    line4.set_xdata(sell_signals_x)
    line4.set_ydata(sell_signals_y)

    plt.ylim(min(bids.data) - 0.0001, max(asks.data) + 0.0001)

    fig.canvas.draw()
    plt.pause(1)