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
        self.F1, self.F2, self.F3 = threading.Event(), threading.Event(), threading.Event()


bar_feed = queue.Queue()
orders_stream = queue.Queue()

System = tradingSystemMetadata()
start_time = time.perf_counter()
f = open("/Volumes/Storage HDD/Data/LMAX EUR_USD 1 Minute.txt")
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
        if counter == 10:
            break
        System.F1.clear()
        System.F2.set()
        System.F1.wait()
    print('Finished reading data')

def tradeLogic():
    while True:
        try:
            bar = bar_feed.get(block=True, timeout=1)
        except:
            break
        ####################################
        #     trade logic starts here      #
        ####################################
        order = {}
        open = bar['Open']
        close = bar['Close']
        if close > open and System.market_position >= 0:

            order['Type'] = 'Market'
            order['Price'] = close
            order['Side'] = 'Sell'
            if System.market_position == 0:
                order['Size'] = 10000
            else:
                order['Size'] = 20000
            orders_stream.put(order)

        if close < open and System.market_position <= 0:
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
        order['Status'] = 'Executed'
        if order['Side'] == 'Buy':
            order['Executed Price'] = bar['Close']
        if order['Side'] == 'Sell':
            order['Executed Price'] = bar['Close']


def processOrders():
    while True:
        try:
            bar = bar_feed.get(block=True, timeout=1)
        except:
            break

        System.equity += (bar['Close'] - System.last_price) * System.market_position
        System.equity_timeseries.append(System.equity)
        System.last_price = bar['Close']

        while True:
            try:
                order = orders_stream.get(block=False)
                emulateBrokerExecution(bar, order)
                if order['Status'] == 'Executed':
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
incoming_price_thread = threading.Thread(target=getBar)
trading_thread = threading.Thread(target=tradeLogic)
ordering_thread = threading.Thread(target=processOrders)

incoming_price_thread.start()
trading_thread.start()
ordering_thread.start()


while True:
    if incoming_price_thread.is_alive():
        time.sleep(1)
    else:
        end_time = time.perf_counter()
        print(f'Backtest complete in {round(end_time - start_time, 0)} second(s).')
        plt.plot(System.equity_timeseries)
        plt.show()
        break
