from delta_rest_client import DeltaRestClient
from dotenv import load_dotenv
import os
import requests

load_dotenv()



delta_client = DeltaRestClient(
  base_url='https://api.india.delta.exchange',
  api_key=os.getenv('API_KEY'),
  api_secret=os.getenv('API_SECRET')
)

headers = {
  'Accept': 'application/json'
}

products = requests.get('https://api.india.delta.exchange/v2/products', params={

}, headers = headers)

print(products.json())


indices = requests.get('https://api.india.delta.exchange/v2/indices', params={

}, headers = headers)

all_indices = []
for index in indices.json()['result']:
    if index['constituent_exchanges']:
        exchanges = "[" + ", ".join([ex['exchange'] for ex in index['constituent_exchanges']]) + "]"
    else:
        exchanges = "null"
    config = index.get('config')
    underlying_asset = config['underlying_asset'] if config and 'underlying_asset' in config else 'null'
    index_obj = {
      "id": index['id'],
      "underlying_asset_id": index['underlying_asset_id'],
      "symbol": index['symbol'],
      "underlying_asset": underlying_asset,
      "exchanges": exchanges
    }
    all_indices.append(index_obj)
print(all_indices)

ticker = delta_client.get_ticker('BTCUSD')
print(ticker)