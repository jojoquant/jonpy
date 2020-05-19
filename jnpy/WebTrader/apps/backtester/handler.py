#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午9:51
@Author   :   Fangyang
"""
import json
from typing import Union, Optional, Awaitable

from vnpy.trader.constant import Exchange, Interval

from jnpy.WebTrader.base_handler import BaseWebSocketHandler
from jnpy.WebTrader.settings import get_global_config_json_dict
from jnpy.WebTrader.apps.backtester import middleware


# symbols_dict = {}
# periods = [i.name for i in list(Interval)]
# time_format = "%Y-%m-%d %H:%M:%S"
# export_to = ["to_db", "to_csv"]


class BacktesterWssHandler(BaseWebSocketHandler):

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:

        re_data = json.dumps(
            {
                "strategy_array": middleware.getStrategyArray(),
                "exchange_array": middleware.getExchangeArray(),
                "data_nums": 0,
                "inverse_mode": ["正向", "反向"],
                "backtest_mode": ["Thread回测", "Debug回测"],
            }
        )
        self.write_message(re_data)
        print(1)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        re_data_dict = json.loads(message)

        if 'exchange' in re_data_dict:
            symbol_array = middleware.onExchangeActivated(
                current_exchange=re_data_dict['exchange']
            )
            re_data = json.dumps({"symbol_array": symbol_array})
            self.write_message(re_data)

        elif 'strategy' in re_data_dict:
            strategy_setting = middleware.onStrategyActivated(re_data_dict['strategy'])
            re_data = json.dumps({"strategy_setting": strategy_setting})
            self.write_message(re_data)

        elif 'symbol' in re_data_dict:
            recv_dict = re_data_dict['symbol']
            period_array, symbol_name = middleware.onSymbolActivated(
                current_symbol=recv_dict['symbol'],
                current_exchange=recv_dict['exchange'],
            )
            re_data = json.dumps({
                "period_array": period_array,
                "symbol_name": symbol_name
            })
            self.write_message(re_data)

        elif 'period' in re_data_dict:
            recv_dict = re_data_dict['period']
            re_data_dict = middleware.onIntervalActivated(
                current_symbol=recv_dict['symbol'],
                current_exchange=recv_dict['exchange'],
                current_interval=recv_dict['period'],
            )
            re_data = json.dumps(re_data_dict)
            self.write_message(re_data)

        elif 'run_backtest' in re_data_dict:
            recv_dict = re_data_dict['run_backtest']
            re_data_dict = middleware.onIntervalActivated(handler=self, submit_data_dict=recv_dict)

        print(re_data_dict)


if __name__ == "__main__":
    x = [i.name for i in list(Interval)]
    print(1)
