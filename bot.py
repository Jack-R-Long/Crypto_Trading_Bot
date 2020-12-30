import websocket, json, pprint

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"


def on_message(ws, message):
	print("Message recived")
	json_message = json.loads(message)
	# pprint.pprint(json_message)
	
	candle = message['k']
	is_candle_closed = candle['x']
	close = candle['c']

	if is_candle_closed:
		print('Candle is closed at {}'.format(close))




def on_open(ws):
	print("Socket Opened")

def on_close(ws):
	print("Socket Closed")


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()