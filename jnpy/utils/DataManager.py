#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/15 下午1:50
@Author   :   Fangyang
"""
from vnpy.trader.object import BarData
from vnpy.trader.utility import ArrayManager


class ArrayManagerWithDatetime(ArrayManager):
    def __init__(self, size: int = 100):
        super(ArrayManagerWithDatetime, self).__init__(size=size)
        self.datetime_list = []

    def update_bar(self, bar: BarData) -> None:
        super().update_bar(bar)
        self.datetime_list.append(str(bar.datetime))


if __name__ == "__main__":
    pass
