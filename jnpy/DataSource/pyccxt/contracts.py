#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/13 下午6:22
@Author   :   Fangyang
"""
import json
import os

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
        self.cur_exchange_str = ''

        self.cur_market_info_json_path = f"{os.path.dirname(os.path.abspath(__file__))}/exchange_market_info"

        self.log = LogModule("Pyccxt", level="info")
        # self.init_exchange(exchange_str)

    def init_exchange(self, exchange_str):
        self.cur_exchange_str = exchange_str.lower()
        if self.cur_exchange_str in self.exchange_list:
            self.exchange = eval(f"ccxt.{self.cur_exchange_str}()")
            self.exchange.proxies = PROXIES
            self.exchange.load_markets()
        else:
            self.log.write_log(f"{self.cur_exchange_str} 不在ccxt交易所列表中, 请查询")

    def get_market_symbol_info(self, symbol: str) -> dict:
        """ symbol : 'BTC/USDT' """
        return self.exchange.market(symbol)

    def get_currency_symbol_info(self, symbol: str) -> dict:
        return self.exchange.currency(symbol)

    def get_currencies(self):
        return self.exchange.currencies

    def update_local_market_info_json_file(self):
        if self.cur_exchange_str:
            self.save_json(f"{self.cur_exchange_str}_market_code_info.json", self.exchange.markets)
        else:
            self.log.write_log(f"{self.cur_exchange_str} 为空, 未进行正确初始化")

    def save_json(self, filename: str, data: dict):
        '''
        filename: "xxx.json"
        '''
        filepath = f"{self.cur_market_info_json_path}/{filename}"
        self.log.write_log(f"将 {filename} 保存到: {filepath}")
        with open(filepath, mode="w+", encoding="UTF-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    def read_local_market_info_json_file(self, exchange_str):
        """
        Load data from json file in temp path.
        """
        filepath = f"{self.cur_market_info_json_path}/{exchange_str}_market_code_info.json"

        if os.path.exists(filepath):
            with open(filepath, mode="r", encoding="UTF-8") as f:
                data = json.load(f)
            return data
        else:
            print(f"{filepath} 不存在!")
            return None



if __name__ == "__main__":
    exchange_list = ccxt.exchanges

    p = Exchange()
    used_exchange_list = ["BINANCE", "OKEX3", "BITMEX", "HUOBIPRO"]
    for exchange_str in used_exchange_list:

        p.init_exchange(exchange_str)
        p.update_local_market_info_json_file()

    # ee = p.get_currencies()
    # ss = p.get_currency_symbol_info("BTC")

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
