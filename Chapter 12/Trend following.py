import csv
import threading
import queue
import time
import matplotlib.pyplot as plt
from datetime import datetime

class tradingSystemMetadata:
    def __init__(self):
        self.initial_capital = 10000
        self.leverage = 30
        self.market_position = 0
        self.equity = 0
        self.last_price = 0
        self.equity_timeseries = []
        self.list_of_orders = []
        self.F1, self.F2, self.F3 = threading.Event(), threading.Event(), threading.Event()

class slidingWindow:
    def __init__(self, len):
        self.data = [0 for i in range(len)]
    def add(self, element):
        self.data.pop(0)
        self.data.append(element)
    def last(self):
        return self.data[-1]
    def previous(self):
        return self.data[-2]

bar_feed = queue.Queue()
orders_stream = queue.Queue()

System = tradingSystemMetadata()
data_window_small = slidingWindow(5)
data_window_large = slidingWindow(20)
start_time = time.perf_counter()

f = open("/Users/Doctor/Documents/NextCloud/Trading/Books (work in progress)/FX trading with Python/Chapter 11/data/AUDUSD_daily.csv")
csvFile = csv.DictReader(f)
all_data = list(csvFile)
end_time = time.perf_counter()
print(f'Data read in {round(end_time - start_time, 0)} second(s).')

def getBar():
    counter = 0
    for bar in all_data:
        bar['Open'] = float(bar['Open'])
        bar['High'] = float(bar['High'])
        bar['Low'] = float(bar['Low'])
        bar['Close'] = float(bar['Close'])
        bar_feed.put(bar)
        counter += 1
        if counter == 100000:
            break
        if int(counter / 100000) == counter / 100000:
            print('Processed', counter, 'bars')
        System.F1.clear()
        System.F2.set()
        System.F1.wait()
    print('Finished reading data')

def moving_average(data):
	return sum(data) / len(data)

def tradeLogic():
    while True:
        try:
            bar = bar_feed.get(block=True, timeout=1)
        except:
            print('Finished trading logic', datetime.now())
            break
        ####################################
        #     trade logic starts here      #
        ####################################
        open = bar['Open']
        close = bar['Close']
        data_window_small.add(close)
        data_window_large.add(close)
        ma_small = moving_average(data_window_small.data)
        ma_large = moving_average(data_window_large.data)
        if close < ma_small and ma_small < ma_large and System.market_position >= 0:
            order = {}
            order['Type'] = 'Market'
            order['Price'] = close
            order['Side'] = 'Sell'
            if System.market_position == 0:
                order['Size'] = 10000
            else:
                order['Size'] = 20000
            orders_stream.put(order)

        if close > ma_small and ma_small > ma_large and System.market_position <= 0:
            order = {}
            order['Type'] = 'Market'
            order['Price'] = close
            order['Side'] = 'Buy'
            if System.market_position == 0:
                order['Size'] = 10000
            else:
                order['Size'] = 20000
            orders_stream.put(order)
        ####################################
        #       trade logic ends here      #
        ####################################
        bar_feed.put(bar)
        System.F2.clear()
        System.F3.set()
        System.F2.wait()

def emulateBrokerExecution(bar, order):

    if order['Type'] == 'Market':
        # Here we actually receive order status from broker
        order['Status'] = 'Executed'

        # Emulating execution
        if order['Side'] == 'Buy':
            order['Executed Price'] = bar['Close'] + 0.00005
        if order['Side'] == 'Sell':
            order['Executed Price'] = bar['Close']

def processOrders():
    while True:
        try:
            bar = bar_feed.get(block = True, timeout = 1)
        except:
            print('Finished processing orders at', datetime.now())
            break
        System.equity += (bar['Close'] - System.last_price) * System.market_position
        System.equity_timeseries.append(System.equity)
        System.last_price = bar['Close']

        while True:
            try:
                order = orders_stream.get(block = False)
                print('Received order', order)
                emulateBrokerExecution(bar, order)
                if order['Status'] == 'Executed':
                    System.list_of_orders.append(order)
                    print('Order executed', order)
                    System.last_price = order['Executed Price']
                    if order['Side'] == 'Buy':
                        System.market_position = System.market_position + order['Size']
                    if order['Side'] == 'Sell':
                        System.market_position = System.market_position - order['Size']
            except:
                order = 'No order'
                break

        System.F3.clear()
        System.F1.set()
        System.F3.wait()

start_time = time.perf_counter()

incoming_price_thread = threading.Thread(target = getBar)
trading_thread = threading.Thread(target = tradeLogic)
ordering_thread = threading.Thread(target = processOrders)

incoming_price_thread.start()
trading_thread.start()
ordering_thread.start()

while True:
    if incoming_price_thread.is_alive():
        time.sleep(1)
    else:
        total_trades = len(System.list_of_orders)
        print("Total trades:", total_trades)
        print("Average trade:", System.equity / total_trades)
        end_time = time.perf_counter()
        print(f'Backtest complete in {round(end_time - start_time, 0)} second(s).')
        plt.plot(System.equity_timeseries)
        plt.show()
        break