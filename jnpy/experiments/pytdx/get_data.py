# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/5
'''
__author__ = 'Fangyang'

from pytdx.exhq import TdxExHq_API

api = TdxExHq_API()
urls = {
    'std_hq_url':
        {'ip': '119.147.212.81',
         'port': 7709
         },
    'ex_hq_url':
        {'ip': '121.152.107.141',
         'port': 7727
         }
}

if api.connect(**urls['ex_hq_url']):
    data = api.to_df(api.get_markets())

    api.disconnect()

if __name__ == '__main__':
    pass
