#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午9:51
@Author   :   Fangyang
"""

from jnpy.WebTrader.base_handler import BaseRestfulHandler


class LoginHandler(BaseRestfulHandler):

    async def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')


if __name__ == "__main__":
    pass