import json
import threading
import queue
from datetime import datetime
from websocket import create_connection

class tradingSystemMetadata:
    def __init__(self):
        self.initial_capital = 10000
        self.leverage = 30
        self.market_position = 0
        self.equity = 0
        self.last_price = 0
        self.equity_timeseries = []

tick_feed_0 = queue.Queue()
tick_feed_1 = queue.Queue()
tick_feed_2 = queue.Queue()
bar_feed = queue.Queue()
orders_stream = queue.Queue()

System = tradingSystemMetadata()

url = "wss://public-data-api.london-demo.lmax.com/v1/web-socket"
subscription_msg = '{"type": "SUBSCRIBE","channels": [{"name": "ORDER_BOOK","instruments": ["eur-usd"]}]}'
data_resolution = 10

def LMAX_connect(url, subscription_msg):
    ws = create_connection(url)
    ws.send(subscription_msg)
    while True:
        tick = json.loads(ws.recv())
        if 'instrument_id' in tick.keys():
            bid = float(tick['bids'][0]['price'])
            ask = float(tick['asks'][0]['price'])
            if ask - bid < 0.001:
                tick_feed_0.put(tick)

def getBarRealtime(resolution):
    last_sample_ts = datetime.now()
    bar = {'Open': 0, 'High': 0, 'Low': 0, 'Close': 0}
    while True:
        tick = tick_feed_0.get(block=True)
        if 'instrument_id' in tick.keys():
            ts = datetime.strptime(tick['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            bid = float(tick['bids'][0]['price'])
            delta = ts - last_sample_ts
            bar['High'] = max([bar['High'], bid])
            bar['Low'] = min([bar['Low'], bid])
            bar['Close'] = bid # Note that we update price BEFORE checking the condition to start a new bar!
            if delta.seconds >= resolution - 1:
                if bar['Open'] != 0:
                    bar_feed.put(bar)
                last_sample_ts = ts
                bar = {'Open': bid, 'High': bid, 'Low': bid, 'Close': bid}
        tick_feed_1.put(tick)


def tradeLogic():
    while True:
        tick = tick_feed_1.get()
        try:
            bar = bar_feed.get(block=False)
            print('Got bar: ', bar)
            ####################################
            #     trade logic starts here      #
            ####################################
            open = bar['Open']
            close = bar['Close']
            if close > open and System.market_position >= 0:
                order = {}
                order['Type'] = 'Market'
                order['Price'] = close
                order['Side'] = 'Sell'
                if System.market_position == 0:
                    order['Size'] = 10000
                else:
                    order['Size'] = 20000
                orders_stream.put(order)
                print(order)

            if close < open and System.market_position <= 0:
                order = {}
                order['Type'] = 'Market'
                order['Price'] = close
                order['Side'] = 'Buy'
                if System.market_position == 0:
                    order['Size'] = 10000
                else:
                    order['Size'] = 20000
                orders_stream.put(order)
                print(order)
            ####################################
            #       trade logic ends here      #
            ####################################
        except:
            pass
        tick_feed_2.put(tick)

def emulateBrokerExecution(tick, order):
    if order['Type'] == 'Market':
        if order['Side'] == 'Buy':
            current_liquidity = float(tick['asks'][0]['quantity'])
            price = float(tick['asks'][0]['price'])
            if order['Size'] <= current_liquidity:
                order['Executed Price'] = price
                order['Status'] = 'Executed'
            else:
                order['Status'] = 'Rejected'
        if order['Side'] == 'Sell':
            current_liquidity = float(tick['bids'][0]['quantity'])
            price = float(tick['bids'][0]['price'])
            if order['Size'] <= current_liquidity:
                order['Executed Price'] = price
                order['Status'] = 'Executed'
            else:
                order['Status'] = 'Rejected'

def processOrders(): # In production this should be called with every new tick, separate feed
    while True:
        tick = tick_feed_2.get(block = True)
        current_price = float(tick['bids'][0]['price'])

        System.equity += (current_price - System.last_price) * System.market_position
        System.equity_timeseries.append(System.equity)
        System.last_price = current_price
        print(tick['timestamp'], "Price:", current_price, "Equity:", System.equity)

        while True:
            try:
                order = orders_stream.get(block = False)
                available_funds = (System.initial_capital + System.equity) * System.leverage - System.market_position / System.leverage
                if order['Size'] < available_funds:
                    emulateBrokerExecution(tick, order)
                if order['Status'] == 'Executed':
                    System.last_price = order['Executed Price']
                    print('Executed at ', str(System.last_price), 'current price = ', str(current_price), 'order price = ', str(order['Executed Price']))
                    if order['Side'] == 'Buy':
                        System.market_position = System.market_position + order['Size']
                    if order['Side'] == 'Sell':
                        System.market_position = System.market_position - order['Size']
                elif order['Status'] == 'Rejected':
                    orders_stream.put(order)
            except:
                order = 'No order'
                break

data_receiver_thread = threading.Thread(target = LMAX_connect, args = (url, subscription_msg))
incoming_price_thread = threading.Thread(target = getBarRealtime, args = (data_resolution,))
trading_thread = threading.Thread(target = tradeLogic)
ordering_thread = threading.Thread(target = processOrders)

data_receiver_thread.start()
incoming_price_thread.start()
trading_thread.start()
ordering_thread.start()
