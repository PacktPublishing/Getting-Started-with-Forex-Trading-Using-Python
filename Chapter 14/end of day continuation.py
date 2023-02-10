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
        self.orders_buffer = []
        self.number_of_trades = 0
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
        if int(counter / 100000) == counter / 100000:
            print('Processed', counter, 'bars')
        System.F1.clear()
        System.F2.set()
        System.F1.wait()
    print('Finished reading data')

def tradeLogic():
    ref_close = 0
    while True:
        try:
            bar = bar_feed.get(block=True, timeout=1)
        except:
            print('Finished trading logic', datetime.now())
            break
        ####################################
        #     trade logic starts here      #
        ####################################
        close = bar['Close']

        if bar['Time'] == '23:00:00':
            ref_close = close

        if bar['Time'] == '22:50:00' and System.market_position == 0:
            order = {}
            order['Type'] = 'Market'
            order['Price'] = close
            if close < ref_close:
                order['Side'] = 'Sell'
            if close > ref_close:
                order['Side'] = 'Buy'
            order['Size'] = 10000
            order['Status'] = 'Created'
            orders_stream.put(order)

            order = {}
            order['Type'] = 'Limit'
            if close < ref_close:
                order['Side'] = 'Buy'
                order['Price'] = close - 0.0005
            if close > ref_close:
                order['Side'] = 'Sell'
                order['Price'] = close + 0.0005
            order['Size'] = 10000
            order['Status'] = 'Created'
            orders_stream.put(order)

            order = {}
            order['Type'] = 'Stop'
            if close < ref_close:
                order['Side'] = 'Buy'
                order['Price'] = close + 0.005
            if close > ref_close:
                order['Side'] = 'Sell'
                order['Price'] = close - 0.005
            order['Size'] = 10000
            order['Status'] = 'Created'
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

        # Emulating bad execution
        if order['Side'] == 'Buy':
            order['Executed Price'] = bar['Close']
        if order['Side'] == 'Sell':
            order['Executed Price'] = bar['Close']

    if order['Type'] == 'Limit':
        # print('Begin processing limit order', Broker.orders_list)
        if order['Status'] == 'Created':
            # Here we actually send orders to the API
            order['Status'] = 'Submitted'

        if order['Status'] == 'Submitted':
            if order['Side'] == 'Buy' and bar['Low'] <= order['Price']:
                order['Status'] = 'Executed'
                order['Executed Price'] = min(order['Price'], bar['Open'])
            if order['Side'] == 'Sell' and bar['High'] >= order['Price']:
                order['Status'] = 'Executed'
                order['Executed Price'] = max(order['Price'], bar['Open'])

    if order['Type'] == 'Stop':
        # print('Begin processing limit order', Broker.orders_list)
        if order['Status'] == 'Created':
            # Here we actually send orders to the API
            order['Status'] = 'Submitted'

        if order['Status'] == 'Submitted':
            if order['Side'] == 'Buy' and bar['High'] >= order['Price']:
                order['Status'] = 'Executed'
                order['Executed Price'] = max(order['Price'], bar['Open'])
            if order['Side'] == 'Sell' and bar['Low'] <= order['Price']:
                order['Status'] = 'Executed'
                order['Executed Price'] = min(order['Price'], bar['Open'])

def processOrders():
    while True:
        try:
            bar = bar_feed.get(block = True, timeout = 1)
        except:
            print('Finished processing orders at', datetime.now())
            break
        # print('Received bar', bar)

        # print('Equity = ', System.equity)
        System.orders_buffer = []

        while True:
            try:
                order = orders_stream.get(block = False)
                # print('Received order', order)
                # print('Orders queue:', list(orders_stream.queue))
                emulateBrokerExecution(bar, order)
                # print('New order status:', order['Status'])
                if order['Status'] == 'Executed':
                    System.list_of_orders.append(order)
                    System.equity += (order['Executed Price'] - System.last_price) * System.market_position
                    if order['Side'] == 'Buy':
                        System.market_position = System.market_position + order['Size']
                        if System.market_position != 0:
                            System.number_of_trades += 1
                    if order['Side'] == 'Sell':
                        System.market_position = System.market_position - order['Size']
                        if System.market_position != 0:
                            System.number_of_trades += 1
                    System.last_price = order['Executed Price']
                    # the following block implements contingent limit and stop orders
                    if order['Type'] == 'Limit' or order['Type'] == 'Stop':
                        System.orders_buffer = []
                        orders_stream.queue.clear()

                if order['Status'] == 'Submitted':
                    # print('Order submitted', order)
                    System.orders_buffer.append(order)

                    # break
            except:
                for order in System.orders_buffer:
                    orders_stream.put(order)
                break
        System.equity += (bar['Close'] - System.last_price) * System.market_position
        System.equity_timeseries.append(System.equity)
        System.last_price = bar['Close']

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
        print("Total trades:", System.number_of_trades)
        print("Average trade:", System.equity / System.number_of_trades)
        end_time = time.perf_counter()
        print(f'Backtest complete in {round(end_time - start_time, 0)} second(s).')
        plt.plot(System.equity_timeseries)
        plt.show()
        break