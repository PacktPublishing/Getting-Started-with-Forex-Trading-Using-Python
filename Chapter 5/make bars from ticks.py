from datetime import datetime

file_name = "/Users/Doctor/Documents/NextCloud/Trading/Books (work in progress)/FX trading with Python/Chapter 5/EURUSD 1 Tick.csv"
f = open(file_name)
f.readline()

bars = {}
bar = {}

resolution = 60

values = f.readline().rstrip("\n").split(",")
timestamp_string = values[0] + " " + values[1]
last_sample_ts = datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S.%f")

for line in f:
    values = line.rstrip("\n").split(",")
    timestamp_string = values[0] + " " + values[1]
    ts = datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S.%f")
    delta = ts - last_sample_ts
    if delta.seconds >= resolution:
        bars[ts] = dict(bar)
        bar["open"] = float(values[2])
        bar["high"] = float(values[2])
        bar["low"] = float(values[2])
        last_sample_ts = ts
    else:
        try:
            bar["high"] = max([bar["high"], float(values[2])])
            bar["low"] = min([bar["low"], float(values[2])])
            bar["close"] = float(values[2])
        except:
            print('first bar forming...')

print(list(bars.items())[-4:])
