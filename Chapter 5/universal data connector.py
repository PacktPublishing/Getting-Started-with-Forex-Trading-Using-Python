file_name = '/Users/Doctor/Documents/NextCloud/Trading/Books (work in progress)/FX trading with Python/Chapter 5/EURUSD 1 Tick.csv'
f = open(file_name)
f.readline()

bars = {}

from datetime import datetime
import threading
import queue
import time

datastream = queue.Queue()


def get_tick():
    tick = {}
    values = f.readline().rstrip("\n").split(",")
    timestamp_string = values[0] + " " + values[1]
    ts = datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S.%f")
    tick[ts] = float(values[2])
    return tick


def emulate_tick_stream():
    while True:
        time.sleep(1)
        temp = get_tick()
        datastream.put(temp)


def trading_algo():
    while True:
        temp = datastream.get()
        # print('Received tick ', temp)


def compressor():
    bar = {}
    while True:
        tick = datastream.get()
        current_time = datetime.now()
        if current_time.second == 0:
            bars[current_time] = dict(bar)
            bar["open"] = tick.values()[0]
            bar["high"] = tick.values()[0]
            bar["low"] = tick.values()[0]
            print(bars)
        else:
            try:
                bar["high"] = max([bar["high"], tick.values()[0]])
                bar["low"] = min([bar["low"], tick.values()[0]])
                bar["close"] = tick.values()[0]
            except:
                print(str(current_time), ' bar forming...')


data_source_thread = threading.Thread(target=emulate_tick_stream)
# data_receiver_thread = threading.Thread(target = trading_algo)
data_receiver_thread = threading.Thread(target=compressor)
data_source_thread.start()
data_receiver_thread.start()