import websocket, json, pprint, talib, numpy

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30 
TRADE_SYMBOL = "ETHUSD"
TRADE_QUANITITY = 0.1 

closes = []
in_position = False  # Not bought

def on_message(ws, message):
	global closes
	print("Message recived")
	json_message = json.loads(message)
	# pprint.pprint(json_message)
	
	candle = json_message['k']
	is_candle_closed = candle['x']
	close = candle['c']

	if is_candle_closed:
		print('Candle is closed at {}'.format(close))
		closes.append(float(close))
		print("Closes\n {}".format(closes))

		if len(closes) > RSI_PERIOD:  # Need at least 14 closes to calculate RSI 14
			np_closes = numpy.array(closes)
			rsi = talib.RSI(np_closes, RSI_PERIOD)
			last_rsi = rsi[-1]
			print("RSI values so far \n{}".format(rsi))
			print("Current RSI is: {}".format(last_rsi))

			if last_rsi > RSI_OVERBOUGHT:
				if in_position:
					print("Sell sell sell!")
					# put sell through binance
				else:
					print("It is overbought but we don't own any")
			
			if last_rsi < RSI_OVERSOLD:
				if in_position:
					print("Oversold but we are already in position")
				else:
					print("Buy buy buy!")
					# Put Binance buy here

def on_open(ws):
	print("Socket Opened")

def on_close(ws):
	print("Socket Closed")


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()