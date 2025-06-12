import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
tz = ZoneInfo('Asia/Kolkata')
headers = {
    'Accept': 'application/json',
}


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
df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)

df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
print(df)