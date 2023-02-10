import csv
import matplotlib.pyplot as plt
import numpy as np

f = open("/Volumes/Storage HDD/Data/LMAX EUR_USD 1 Minute.txt")
csvFile = csv.DictReader(f)
all_data = list(csvFile)

starting_bar_number = 0

for bar in all_data:
    if bar['Date'] == '12/12/2019':
        break
    starting_bar_number += 1

close = [float(bar['Close']) for bar in all_data[starting_bar_number:starting_bar_number + 100]]
time = [bar['Time'] for bar in all_data[starting_bar_number:starting_bar_number + 100]]
fig = plt.figure()
ax = fig.add_subplot()
ax.set_xticks(np.arange(0, len(time) + 1, 15))
plt.xticks(rotation=45)
plt.plot(time, close)
plt.show()