#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午9:51
@Author   :   Fangyang
"""
import json
import time
from typing import Union, Optional, Awaitable

from vnpy.trader.constant import Exchange, Interval

from jnpy.WebTrader.base_handler import BaseWebSocketHandler
from jnpy.WebTrader.settings import get_global_config_json_dict

from jnpy.WebTrader.constant import DATETIME_FORMAT
from jnpy.WebTrader.apps.monitor import middleware


class MonitorWssHandler(BaseWebSocketHandler):

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        # in_client = ('192.168.0.108', 56986)
        in_client = self.request.server_connection.context.address
        middleware.main_engine.update_tornado_client(self)
        re_data = json.dumps(middleware.init_engine())
        self.write_message(re_data)
        print("MonitorWssHandler", in_client)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        re_data_dict = json.loads(message)
        # 业务函数名即字典的key, value为入参, 出参为反馈前端信息
        # [self.write_message(getattr(middleware, key)(**value)) for key, value in re_data_dict.items()]
        for key, value in re_data_dict.items():
            re_data = getattr(middleware, key)(**value)
            if re_data:
                self.write_message(re_data)


class MonitorSystemInfoWssHandler(BaseWebSocketHandler):

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        # in_client = ('192.168.0.108', 56986)
        in_client = self.request.server_connection.context.address
        print("MonitorSystemInfoWssHandler", in_client)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        re_data_dict = json.loads(message)

        if "gateway_connect" in re_data_dict:
            middleware.gateway_connect(re_data_dict['gateway_connect'])
            re_data = json.dumps(middleware.gen_exchange_contract_info())
            self.write_message(re_data)
        elif "" in re_data_dict:
            middleware

        print(1)


if __name__ == "__main__":
    x = [i.name for i in list(Interval)]
    print(1)
