from datetime import datetime
import threading
import queue
import time

class sliding_window:
    def __init__(self, length):
        self.data = ([0] * length)

    def add(self, element):
        self.data.append(element)
        self.data.pop(0)


file_name = '/Volumes/Storage HDD/Data/LMAX EUR_USD 1 Minute.txt'
f = open(file_name)
f.readline()

close = sliding_window(5)
high = sliding_window(5)
low = sliding_window(5)
sw = sliding_window(5)

datastream = queue.Queue()


def get_tick():
    tick = {}
    values = f.readline().rstrip("\n").split(",")
    timestamp_string = values[0] + " " + values[1]
    ts = datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S.%f")
    tick[ts] = float(values[2])
    return tick


def get_sample(f):
    sample = {}
    values = f.readline().rstrip("\n").split(",")
    timestamp_string = "0" + values[0] + " " + values[1]
    ts = datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S")
    sample["open"] = float(values[2])
    sample["high"] = float(values[3])
    sample["low"] = float(values[4])
    sample["close"] = float(values[5])
    sample["UpVolume"] = int(values[6])
    sample["DownVolume"] = int(values[7])
    sample["Datetime"] = ts
    return sample


def emulate_tick_stream():
    while True:
        time.sleep(1)
        datastream.put(get_tick())


def emulate_bar_stream():
    while True:
        time.sleep(1)
        datastream.put(get_sample(f))


def retrieve_ticks():
    while True:
        print(datastream.get())


def retrieve_bars():
    while True:
        data_point = datastream.get()
        sw.add(data_point)
        close.add(data_point["close"])
        high.add(data_point["high"])
        low.add(data_point["low"])
        ma = moving_average(close.data)
        stoch = stochastic(high.data, low.data, close.data)
        print("Bar retrieved", close.data[-1], ma, stoch)

def moving_average(data):
    return sum(data) / len(data)


def stochastic(high, low, close):
    max_price = max(high)
    min_price = min(low)
    return (close[-1] - min_price) / (max_price - min_price)


def stochastic_ts(timeseries):
    s = 0
    try:
        high = [x["high"] for x in timeseries.data]
        low = [x["low"] for x in timeseries.data]
        close = [x["close"] for x in timeseries.data]
        max_price = max(high)
        min_price = min(low)
        s = (close[-1] - min_price) / (max_price - min_price)
    except:
        print("Collecting data...")
    return s


data_source_thread = threading.Thread(target=emulate_bar_stream)
data_receiver_thread = threading.Thread(target=retrieve_bars)
data_source_thread.start()
data_receiver_thread.start()


