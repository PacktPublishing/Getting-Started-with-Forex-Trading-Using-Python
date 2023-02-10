from datetime import datetime

historical_data = {}
sample = {}

file_name = '/Volumes/Storage HDD/Data/LMAX EUR_USD 1 Minute.txt'
f = open(file_name)
f.readline()

for line in f:
    values = line.rstrip("\n").split(",")
    timestamp_string = values[0] + " " + values[1]
    ts = datetime.strptime(timestamp_string, "%m/%d/%Y %H:%M:%S")
    sample["open"] = float(values[2])
    sample["high"] = float(values[3])
    sample["low"]  = float(values[4])
    sample["close"]= float(values[5])
    sample["UpVolume"] = int(values[6])
    sample["DownVolume"] = int(values[7])
    historical_data[ts] = sample

print(historical_data[ts])