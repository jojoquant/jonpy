#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/22 下午7:21
@Author   :   Fangyang
"""

import subprocess

p = subprocess.Popen(
    ["./main",
     "Datetime", "2019-12-18",
     "Time", "00:00:00",
     "period", "1MIN",
     "currencyPair", "BTC_CNY"
     ], shell=True
)

p.wait()

if __name__ == "__main__":
    pass
