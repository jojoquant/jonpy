#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午9:52
@Author   :   Fangyang
"""

from tornado.web import url
from jnpy.WebTrader.apps.dataloader.handler import Wss


ws_urls_tuple = (
    url('/dataloader', Wss),
)


if __name__ == "__main__":
    pass