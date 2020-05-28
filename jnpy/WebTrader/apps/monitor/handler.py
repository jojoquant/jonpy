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

from jnpy.WebTrader.constant import DATETIME_FORMAT
from jnpy.WebTrader.apps.monitor import middleware


class MonitorWssHandler(BaseWebSocketHandler):

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        re_data = json.dumps(middleware.init_strategy())
        self.write_message(re_data)
        print(1)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        re_data_dict = json.loads(message)

        if 'strategy' in re_data_dict:
            re_data_dict = middleware.init_strategy()
            re_data = json.dumps(re_data_dict)
            self.write_message(re_data)
        print(1)


if __name__ == "__main__":
    x = [i.name for i in list(Interval)]
    print(1)
