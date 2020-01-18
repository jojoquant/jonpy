# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/17 22:11
# @Author   : Fangyang
# @Software : PyCharm


from enum import Enum, unique


@unique
class KBarType(Enum):
    '''
    K 线种类
    0 -  5 分钟K 线
    1 -  15 分钟K 线
    2 -  30 分钟K 线
    3 -  1 小时K 线
    4 -  日K 线
    5 -  周K 线
    6 -  月K 线
    7 -  1 分钟
    8 -  1 分钟K 线
    9 -  日K 线
    10 - 季K 线
    11 - 年K 线
    '''
    KLINE_TYPE_5MIN = 0
    KLINE_TYPE_15MIN = 1
    KLINE_TYPE_30MIN = 2
    KLINE_TYPE_1HOUR = 3
    KLINE_TYPE_DAILY = 4
    KLINE_TYPE_WEEKLY = 5
    KLINE_TYPE_MONTHLY = 6
    KLINE_TYPE_EXHQ_1MIN = 7
    KLINE_TYPE_1MIN = 8
    KLINE_TYPE_RI_K = 9
    KLINE_TYPE_3MONTH = 10
    KLINE_TYPE_YEARLY = 11


if __name__ == '__main__':
    pass
