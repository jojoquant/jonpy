#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午9:51
@Author   :   Fangyang
"""
import json

import jwt

from jnpy.WebTrader.base_handler import BaseRestfulHandler
from jnpy.WebTrader.settings import get_global_config_json_dict


class LoginHandler(BaseRestfulHandler):

    async def post(self, *args, **kwargs):

        r_dict = {'token': ''}
        account_info = {
            'username': self.get_body_argument('username'),
            'password': self.get_body_argument('password')
        }

        if account_info['username'] == self.global_settings['web_trader']['username'] \
                and account_info['password'] == self.global_settings['web_trader']['password']:
            encoded_jwt = jwt.encode(account_info, 'secret', algorithm='HS256')
            encoded_jwt_str = str(encoded_jwt)

            # an = jwt.decode(encoded_jwt, 'secret', algorithms=['HS256'])

            r_dict['token'] = encoded_jwt_str
            self.log.write_log('login success.')
            self.write(r_dict)
        else:
            self.log.write_log('login username or password wrong.')
            self.write(r_dict)


if __name__ == "__main__":
    pass
