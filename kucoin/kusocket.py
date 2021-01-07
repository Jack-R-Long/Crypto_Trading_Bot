import kucoin.client as kuclinet
from kucoin.asyncio import KucoinSocketManager
import asyncio, numpy, talib
import api_creds


# client = kuclinet.Client(config.KU_API_PUBLIC, config.KU_API_SECRET, config.KU_PASSPHRASE)
TRADE_SYMBOL = 'ETH'
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30 
TRADE_QUANITITY = 0.01

CURRENT_CANDLE_TIME = '0'
LAST_CLOSE = '0'
CLOSE_PRICE_LIST = []
in_position = False # Not bought
order_ids = []  # List of orders placed

client = kuclinet.Client(api_creds.KU_API_PUBLIC, api_creds.KU_API_SECRET, api_creds.KU_PASSPHRASE)

# currencies = client.get_currency(TRADE_SYMBOL)
# # account = client.get_account(config.ACCOUNT_ID)

# print(currencies)
async def main(client):
    client = client
    global loop
    global TRADE_SYMBOL
    global CLOSE_PRICE_LIST

    # callback function that receives messages from the socket
    async def handle_evt(msg):
        print('Recieved message')
        if msg['topic'] == '/market/candles:ETH-USDT_1min':
            print('Got ETH_USDT candle for 1min')
            (is_new, close_price) = check_for_new_candle(msg)
            if is_new and close_price != '0':
                CLOSE_PRICE_LIST.append(float(close_price))
                (period_passed, current_rsi) = calculate_RSI(close_price)
                if period_passed:
                    trade_or_stay(current_rsi)

        if msg['topic'] == '/market/ticker:ETH-USDT':
            print(f'got ETH-USDT tick:{msg["data"]}')

        elif msg['topic'] == '/market/snapshot:BTC':
            print(f'got BTC market snapshot:{msg["data"]}')

        elif msg['topic'] == '/market/snapshot:KCS-BTC':
            print(f'got KCS-BTC symbol snapshot:{msg["data"]}')

        elif msg['topic'] == '/market/ticker:all':
            print(f'got all market snapshot:{msg["data"]}')

        elif msg['topic'] == '/account/balance':
            print(f'got account balance:{msg["data"]}')

        elif msg['topic'] == '/market/level2:KCS-BTC':
            print(f'got L2 msg:{msg["data"]}')

        elif msg['topic'] == '/market/match:BTC-USDT':
            print(f'got market match msg:{msg["data"]}')

        elif msg['topic'] == '/market/level3:BTC-USDT':
            if msg['subject'] == 'trade.l3received':
                if msg['data']['type'] == 'activated':
                    # must be logged into see these messages
                    print(f"L3 your order activated: {msg['data']}")
                else:
                    print(f"L3 order received:{msg['data']}")
            elif msg['subject'] == 'trade.l3open':
                print(f"L3 order open: {msg['data']}")
            elif msg['subject'] == 'trade.l3done':
                print(f"L3 order done: {msg['data']}")
            elif msg['subject'] == 'trade.l3match':
                print(f"L3 order matched: {msg['data']}")
            elif msg['subject'] == 'trade.l3change':
                print(f"L3 order changed: {msg['data']}")

    ksm = await KucoinSocketManager.create(loop, client, handle_evt)

    # Note: try these one at a time, if all are on you will see a lot of output

    # ETH-USDT Market Ticker
    # await ksm.subscribe('/market/ticker:ETH-USDT')
    # ETH KLINE 
    await ksm.subscribe('/market/candles:ETH-USDT_1min')
    # # BTC Symbol Snapshots
    # await ksm.subscribe('/market/snapshot:BTC')
    # # KCS-BTC Market Snapshots
    # await ksm.subscribe('/market/snapshot:KCS-BTC')
    # # All tickers
    # await ksm.subscribe('/market/ticker:all')
    # # Level 2 Market Data
    # await ksm.subscribe('/market/level2:KCS-BTC')
    # # Market Execution Data
    # await ksm.subscribe('/market/match:BTC-USDT')
    # # Level 3 market data
    # await ksm.subscribe('/market/level3:BTC-USDT')
    # Account balance - must be authenticated
    # await ksm.subscribe('/account/balance')

    while True:
        print("sleeping to keep loop open")
        await asyncio.sleep(20, loop=loop)

def check_for_new_candle(msg):
    """
    params: msg = Dictionary of candlestick data 
    """
    global CURRENT_CANDLE_TIME
    global LAST_CLOSE

    candle_time = msg['data']['candles'][0]
    current_close_price = msg['data']['candles'][2]
    print('Current close is {}'.format(current_close_price))
    if candle_time != CURRENT_CANDLE_TIME:
        print("Alert new candle!!!")
        print("Last candle close was {}".format(LAST_CLOSE))
        CURRENT_CANDLE_TIME = candle_time
        return (True, LAST_CLOSE)
    # Update global close price becuase a new candle has not been recievd
    LAST_CLOSE = current_close_price
    return (False, LAST_CLOSE)

def calculate_RSI(close_price):
    """
    params: close_price = String of current close price
    """
    global RSI_PERIOD
    global CLOSE_PRICE_LIST
    
    print(CLOSE_PRICE_LIST)
    if len(CLOSE_PRICE_LIST) > RSI_PERIOD:
        np_closes = numpy.array(CLOSE_PRICE_LIST)
        rsi = talib.RSI(np_closes, RSI_PERIOD)
        last_rsi = rsi[-1]
        print("RSI values so far \n{}".format(rsi))
        print("Current RSI is: {}".format(last_rsi))
        return (True, last_rsi)
    return (False, 0.0)


def trade_or_stay(current_rsi):
    """
    params: current_rsi = float of current rsi value
    """
    global in_position
    print('\nHIT TRADE OR STAY\n')
    if current_rsi > RSI_OVERBOUGHT:
        if in_position:
            print("Sell sell sell!")
            # put sell through KuCoin
            order_succeeded = order('sell', TRADE_QUANITITY, TRADE_SYMBOL)
            if order_succeeded :
                in_position = False
                print('SOLD POSITION')
        else:
            print("It is overbought but we don't own any")

    if current_rsi < RSI_OVERSOLD:
        if in_position:
            print("Oversold but we are already in position")
        else:
            print("Buy buy buy!")
            # Buy order through KuCoin
            order_succeeded = order('buy', TRADE_QUANITITY, TRADE_SYMBOL)
            if order_succeeded :
                in_position = True
                print('BOUGHT POSITION')


def order(side, quantity, symbol=TRADE_SYMBOL):
    try:
        print('\nSending order!')
        order = client.create_market_order(symbol, side, quantity)
        print(order)
        order_ids.append(order)
    except Exception as e:
        print('Failed to place order')
        return False
    return True

def get_accounts():
    account = client.get_accounts()
    print(account)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(client))
