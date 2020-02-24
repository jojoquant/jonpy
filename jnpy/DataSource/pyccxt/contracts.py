#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/13 下午6:22
@Author   :   Fangyang
"""

import ccxt
from jnpy.utils.logging.log import LogModule

PROXIES = {
    'http': 'socks5://localhost:1080',
    'https': 'socks5h://localhost:1080',
}


class Exchange:

    def __init__(self):
        self.exchange_list = ccxt.exchanges
        self.exchange = ''
        self.log = LogModule("Pyccxt", level="info")
        # self.init_exchange(exchange_str)

    def init_exchange(self, exchange_str):
        if exchange_str.lower() in self.exchange_list:
            self.exchange = eval(f"ccxt.{exchange_str.lower()}()")
            self.exchange.proxies = PROXIES
            self.exchange.load_markets()
        else:
            self.log.write_log(f"{exchange_str} 不在ccxt交易所列表中, 请查询")

    def get_market_symbol_info(self, symbol: str) -> dict:
        """ symbol : 'BTC/USDT' """
        return self.exchange.market(symbol)

    def get_currency_symbol_info(self, symbol: str) -> dict:
        return self.exchange.currency(symbol)

    def get_currencies(self):
        return self.exchange.currencies


if __name__ == "__main__":
    # exchange_list = ccxt.exchanges
    # huobipro = ccxt.huobipro()
    # okex = ccxt.okex3()
    # bitmex = ccxt.bitmex()

    # binance = ccxt.binance()
    # binance.currencies

    p = Exchange()
    p.init_exchange("BINANCE")
    xx = p.get_market_symbol_info("BTC/USDT")
    ee = p.get_currencies()
    ss = p.get_currency_symbol_info("BTC")

    # huobipro_ticker = huobipro.fetch_ticker('BTCUSD')
    # okex_ticker = okex.fetch_ticker('BTC/USD')
    # binance_ticker = binance.fetch_ticker('BTC/USD')

    # okex_ticker = okex.fetch_ticker('BTC/USD')
    # okex_ohlcv = okex.fetch_ohlcv('BTC/USD')

    # bitmex_ticker = bitmex.fetch_ticker('BTC/USD')
    # bitmex_ohlcv = bitmex.fetch_ohlcv('BTC/USD')

    # huobipro = ccxt.huobipro(
    #     {'urls': {
    #         'logo': 'https://user-images.githubusercontent.com/1294454/27766569-15aa7b9a-5edd-11e7-9e7f-44791f4ee49c.jpg',
    #         'api': {
    #             'market': 'https://api.huobi.br.com',
    #             'public': 'https://api.huobi.br.com',
    #             'private': 'https://api.huobi.br.com',
    #             'zendesk': 'https://huobiglobal.zendesk.com/hc/en-us/articles',
    #         },
    #         'www': 'https://www.huobi.pro',
    #         'referral': 'https://www.huobi.br.com/en-us/topic/invited/?invite_code=rwrd3',
    #         'doc': 'https://github.com/huobiapi/API_Docs/wiki/REST_api_reference',
    #         'fees': 'https://www.huobi.pro/about/fee/',
    #     }
    #     }
    # )
    # interval = huobipro.timeframes
    #
    # markets = huobipro.load_markets()
    # symbols = huobipro.symbols
    print(1)
