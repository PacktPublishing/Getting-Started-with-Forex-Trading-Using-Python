import mplfinance as mpf
import pandas

file_name = "/Volumes/Storage HDD/Data/LMAX EUR_USD 1 Minute.txt"
source_data = pandas.read_csv(file_name)

source_data['Timestamp'] = pandas.to_datetime(source_data['Date']) + pandas.to_timedelta(source_data['Time'])
source_data.set_index(source_data['Timestamp'], inplace=True)

sample_date = '23-03-2020'
start_time = '00:01:00'
day_close_time = '23:00:00'

all_day_sample = source_data.loc[sample_date + " " + start_time: sample_date + " " + day_close_time]
OHLC_data = all_day_sample[['Open', 'High', 'Low', 'Close']]
print(OHLC_data)
mpf.plot(OHLC_data, type = 'candle', mav = (20, 50, 200))

