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
from jnpy.datasource.jotdx.contracts import read_contracts_json_dict
from jnpy.WebTrader.constant import DATETIME_FORMAT
from jnpy.WebTrader.apps.dataloader.middleware import load_data

symbols_dict = {}
periods = [i.name for i in list(Interval)]
time_format = DATETIME_FORMAT
export_to = ["to_db", "to_csv"]


class DataloaderWssHandler(BaseWebSocketHandler):

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        contracts_dict = read_contracts_json_dict()

        # 提取 contracts_dict 中信息变为 symbols_dict
        for key, value in contracts_dict.items():
            if value["exchange"] in symbols_dict:
                symbols_dict[value["exchange"]].append(f"{key}.{value['name']}")
            else:
                symbols_dict[value["exchange"]] = [f"{key}.{value['name']}"]

        re_data = json.dumps(
            {
                "exchanges": list(symbols_dict.keys()),
                "periods": periods,
                "time_format": time_format,
                "export_to": export_to,
            }
        )
        self.write_message(re_data)
        print(1)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        re_data_dict = json.loads(message)

        if 'exchanges' in re_data_dict:
            symbols_list = symbols_dict[re_data_dict['exchanges']]
            re_data = json.dumps({"symbols": symbols_list})
            self.write_message(re_data)

        elif 'load_data' in re_data_dict:
            load_data(self, re_data_dict['load_data'])
            print('load_data')

        print(1)


if __name__ == "__main__":
    x = [i.name for i in list(Interval)]
    print(1)
