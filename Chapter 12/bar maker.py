import csv
from datetime import datetime

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

source_file = open("/Volumes/Storage HDD/Data/LMAX AUD_USD 1 Minute.txt")
dest_file = open("/Users/Doctor/Documents/NextCloud/Trading/Books (work in progress)/FX trading with Python/Chapter 11/data/AUDUSD_daily.csv", "w")
csvFile = csv.DictReader(source_file)
all_data = list(csvFile)
dest_file.write(("Date,Time,Open,High,Low,Close\n"))

timestamp = slidingWindow(2)

bar = {'Open': 0, 'High': 0, 'Low': 0, 'Close': 0}

for sample in all_data:
    open = float(sample[' <Open>'])
    high = float(sample[' <High>'])
    low = float(sample[' <Low>'])
    close = float(sample[' <Close>'])
    ts = datetime.strptime(sample['<Date>'] + 'T' + sample[' <Time>'] + 'Z', "%m/%d/%YT%H:%M:%SZ")
    timestamp.add(ts)

    if timestamp.previous() != 0:
        if (timestamp.last().date() != timestamp.previous().date() and str(timestamp.last().time()) != '00:00:00') or (str(timestamp.previous().time()) == '00:00:00'):
            if bar['Open'] != 0:
                dest_file.write(','.join(map(str,[*bar.values()])) + "\n")
            bar = {'Date': timestamp.last().date(), 'Time': timestamp.last().time(), 'Open': open, 'High': high, 'Low': low, 'Close': close}

    bar['High'] = max([bar['High'], high])
    bar['Low'] = min([bar['Low'], low])
    bar['Close'] = close
    bar['Time'] = timestamp.last().time()

dest_file.close()
print('Done')
