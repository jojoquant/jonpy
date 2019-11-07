# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/10/29
'''
__author__ = 'Fangyang'

import sys

sys.path.insert(0, '/home/fangyang/Desktop/python_project/fushare')
import fushare as fs

# df = fs.get_future_daily(
#     start='20190107', end='20190110', market='SHFE', indexBar=True)
df2 = fs.get_future_daily_sp(bar_type='5m', symbol='RB')
df2.rename(columns={'date': 'Datetime',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'vol': 'Volume',
                    'exchange': 'Exchange',
                    'symbol': 'Symbol'},
           inplace=True)
df2.to_csv('RB_5m_dailyBar.csv', index=False)

if __name__ == '__main__':
    pass
