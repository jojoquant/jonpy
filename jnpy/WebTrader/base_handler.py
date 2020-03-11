#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午8:59
@Author   :   Fangyang
"""
from abc import ABC

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler


class BaseRestfulHandler(RequestHandler, ABC):

    def set_default_headers(self) -> None:
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "x-requested-with,access_token")  # 这里要填写上请求带过来的Access-Control-Allow-Headers参数，如access_token就是我请求带过来的参数
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE")  # 请求允许的方法
        self.set_header("Access-Control-Max-Age", "3600")  # 用来指定本次预检请求的有效期，单位为秒，，在此期间不用发出另一条预检请求。


class BaseWebSocketHandler(WebSocketHandler, ABC):

    def check_origin(self, origin: str) -> bool:
        """允许 Websocket 的跨域请求"""
        return True


if __name__ == "__main__":
    pass
