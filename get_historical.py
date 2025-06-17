import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from stock_indicators import indicators, Quote, CandlePart

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

start = '2025-06-15 00:00:00'
end = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
symbol = 'BTCUSD'
resolution = '1m'
res = get_historical_data(symbol, resolution, start, end)
df = pd.DataFrame(res['result'])
df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)

df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]


qdf = pd.to_datetime(df['datetime'])

candle_quotes = [
    Quote(dt, open_, high, low, close, volume)
    for dt, open_, high, low, close, volume in zip(
        qdf, df['open'], df['high'], df['low'], df['close'], df['volume']
    )
]
macd = indicators.get_macd(candle_quotes, 12, 26, 9, CandlePart.CLOSE)

macddf = pd.DataFrame(
    [{
            'macd_fast_blue': round(float(0 if macd_result.macd is None else macd_result.macd), 2),
            'macd_slow_red':  round(float(0 if macd_result.signal is None else macd_result.signal), 2),
            'macd_signal_hist': round(float(0 if macd_result.histogram is None else macd_result.histogram), 2)
    }
        for macd_result in macd
    ]
)
df["macd_fast_blue"] = macddf['macd_fast_blue']
df['macd_slow_red'] = macddf['macd_slow_red']
df["macd_signal_hist"] = macddf['macd_signal_hist']


vwap = indicators.get_vwap(candle_quotes)
vwapdf = pd.DataFrame(
    [{
        'vwap': round(float(vwap_result.vwap), 2)
    } for vwap_result in vwap]
)
df['vwap'] = vwapdf['vwap']

sma = indicators.get_sma(candle_quotes, 20, CandlePart.CLOSE)
sma_df = pd.DataFrame(
    [{
        'sma': sma_result.sma if sma_result.sma is not None else 0
    } for sma_result in sma]
)
df['sma'] = sma_df['sma']

supertrend = indicators.get_super_trend(candle_quotes, 10, 3)
supertrend_df = pd.DataFrame(
    [{
        'supertrend': supertrend_result.super_trend if supertrend_result.super_trend is not None else 0,
    } for supertrend_result in supertrend]
)
df['supertrend'] = supertrend_df['supertrend']


df.to_csv('data.csv', index=False)