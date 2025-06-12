from delta_rest_client import DeltaRestClient
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import pandas as pd
from zoneinfo import ZoneInfo
tz = ZoneInfo('Asia/Kolkata')

load_dotenv()

delta_client = DeltaRestClient(
  base_url='https://api.india.delta.exchange',
  api_key=os.getenv('API_KEY'),
  api_secret=os.getenv('API_SECRET')
)

headers = {
  'Accept': 'application/json'
}

# products = requests.get('https://api.india.delta.exchange/v2/products', params={

# }, headers = headers)

# print(products.json())


# indices = requests.get('https://api.india.delta.exchange/v2/indices', params={

# }, headers = headers)

# all_indices = []
# for index in indices.json()['result']:
#     if index['constituent_exchanges']:
#         exchanges = "[" + ", ".join([ex['exchange'] for ex in index['constituent_exchanges']]) + "]"
#     else:
#         exchanges = "null"
#     config = index.get('config')
#     underlying_asset = config['underlying_asset'] if config and 'underlying_asset' in config else 'null'
#     index_obj = {
#       "id": index['id'],
#       "underlying_asset_id": index['underlying_asset_id'],
#       "symbol": index['symbol'],
#       "underlying_asset": underlying_asset,
#       "exchanges": exchanges
#     }
#     all_indices.append(index_obj)
# print(all_indices)

# ticker = delta_client.get_ticker('BTCUSD')
# print(ticker)
# You are passing the parameters correctly.
# The API expects 'start' and 'end' as UNIX timestamps in seconds, which you are providing after converting from your datetime objects.
# If you pass the timestamps directly (as integers or strings), it works fine because that's what the API expects.

# Example:
# start = 1720569000
# end = 1720741799

# Your code:



def get_timestamp(datetime_str):
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    timestamp = int(dt.timestamp())
    return timestamp

def get_historical_data(symbol, resolution, start, end):
    start_ts = get_timestamp(start)
    end_ts = get_timestamp(end)
    
    params={
        'resolution': resolution,
        'symbol': symbol,
        'start': start_ts,
        'end': end_ts
    }
    response = requests.get('https://api.india.delta.exchange/v2/history/candles', params=params, headers=headers)
    return response.json()

start = '2025-06-10 00:00:00'
end = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
symbol = 'BTCUSD'
resolution = '1m'
res = get_historical_data(symbol, resolution, start, end)
df = pd.DataFrame(res['result'])
# Convert 'time' column (UNIX timestamp) to datetime in Asia/Kolkata timezone
df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)

df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
print(df)