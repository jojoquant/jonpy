#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午8:59
@Author   :   Fangyang
"""
from abc import ABC

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from jnpy.WebTrader.settings import get_global_config_json_dict
from jnpy.utils.logging import LogModule


class BaseRestfulHandler(RequestHandler, ABC):

    def initialize(self):
        self.global_settings = get_global_config_json_dict()
        self.log = LogModule('Tornado Restful Request', level='info')

    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "*")  # 这里要填写上请求带过来的Access-Control-Allow-Headers参数，如access_token就是我请求带过来的参数
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE")  # 请求允许的方法
        self.set_header("Access-Control-Max-Age", "3600")  # 用来指定本次预检请求的有效期，单位为秒，，在此期间不用发出另一条预检请求。

        # self.set_header('Access-Control-Allow-Origin', '*')
        # self.set_header('Access-Control-Allow-Headers', '*')
        # self.set_header('Access-Control-Max-Age', 1000)
        # self.set_header('Content-type', 'application/json')
        # self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        # self.set_header('Access-Control-Allow-Headers',
        #                 'Content-Type, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')

    def options(self):
        self.set_status(204)
        self.finish()


class BaseWebSocketHandler(WebSocketHandler, ABC):

    def initialize(self):
        self.global_settings = get_global_config_json_dict()

    def check_origin(self, origin: str) -> bool:
        """允许 Websocket 的跨域请求"""
        return True


if __name__ == "__main__":
    pass
