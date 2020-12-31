import kucoin.client as kuclinet
from kucoin.asyncio import KucoinSocketManager
import asyncio
import api_creds


# client = kuclinet.Client(config.KU_API_PUBLIC, config.KU_API_SECRET, config.KU_PASSPHRASE)
TRADE_SYMBOL = 'ETH'

# currencies = client.get_currency(TRADE_SYMBOL)
# # account = client.get_account(config.ACCOUNT_ID)

# print(currencies)
async def main():
    global loop
    global TRADE_SYMBOL

    # callback function that receives messages from the socket
    async def handle_evt(msg):
        print(msg)
        if msg['topic'] == '/market/candles:ETH-USDT_1min':
            print('Got ETH_USDT candle for 1min')
            calculate_RSI(msg)

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

    client = kuclinet.Client(api_creds.KU_API_PUBLIC, api_creds.KU_API_SECRET, api_creds.KU_PASSPHRASE)

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

def calculate_RSI(msg):
    """
    params: msg = Dictionary of candlestick data 
    """
    candle_close = msg['data']['candles'][2]
    print('Candle close price is {}'.format(candle_close))


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('Check')