import kucoin.client as kuclinet
import json, pprint
import config


client = kuclinet.Client(config.KU_API_PUBLIC, config.KU_API_SECRET, config.KU_PASSPHRASE)
TRADE_SYMBOL = 'BTC'

currencies = client.get_currency(TRADE_SYMBOL)
# account = client.get_account(config.ACCOUNT_ID)

print(currencies)