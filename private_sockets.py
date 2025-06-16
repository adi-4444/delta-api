import websocket
import hashlib
import hmac
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

WEBSOCKET_URL = "wss://socket.india.delta.exchange"
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

def on_error(ws, error):
    print(f"Socket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Socket closed with status: {close_status_code} and message: {close_msg}")

def on_open(ws):
    print(f"Socket opened")
    send_authentication(ws)
    subscribe(ws, "v2/ticker", ["BTCUSD"])
    # subscribe(ws, "candlestick_1m", ["MARK:BTCUSD", "ETHUSD", "C-BTC-95200-200225", "P-BTC-95200-200225"])

def send_authentication(ws):
    method = 'GET'
    timestamp = str(int(time.time()))
    path = '/live'
    signature_data = method + timestamp + path
    signature = generate_signature(API_SECRET, signature_data)
    ws.send(json.dumps({
        "type": "auth",
        "payload": {
            "api-key": API_KEY,
            "signature": signature,
            "timestamp": timestamp
        }
    }))

def generate_signature(secret, message):
    message = bytes(message, 'utf-8')
    secret = bytes(secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    return hash.hexdigest()

def on_message(ws, message):
    message_json = json.loads(message)
    # subscribe private channels after successful authentication
    if message_json['type'] == 'success' and message_json['message'] == 'Authenticated':
         # subscribe orders channel for order updates for all contracts
        subscribe(ws, "orders", ["all"])
        # subscribe positions channel for position updates for all contracts
        subscribe(ws, "positions", ["all"])
    else:
      print(message_json)


# subscribe payload
# {
#     "type": "subscribe",
#     "payload": {
#         "channels": [
#             {
#                 "name": "v2/ticker",
#                 "symbols": [
#                     "BTCUSD",
#                     "ETHUSD"
#                 ]
#             },
#             {
#                 "name": "l2_orderbook",
#                 "symbols": [
#                     "BTCUSD"
#                 ]
#             },
#             {
#                 "name": "funding_rate",
#                 "symbols": [
#                     "all"
#                 ]
#             }
#         ]
#     }
# }


def subscribe(ws, channel, symbols):
    payload = {
        "type": "subscribe",
        "payload": {
            "channels": [
                {
                    "name": channel,
                    "symbols": symbols
                }
            ]
        }
    }
    ws.send(json.dumps(payload))

if __name__ == "__main__":
  ws = websocket.WebSocketApp(WEBSOCKET_URL, on_message=on_message, on_error=on_error, on_close=on_close)
  ws.on_open = on_open
  ws.run_forever()


