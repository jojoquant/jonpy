#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/15 下午1:50
@Author   :   Fangyang
"""
from typing import List

import pandas as pd

from vnpy.trader.object import BarData
from vnpy.trader.utility import ArrayManager


class ArrayManagerWithDatetime(ArrayManager):
    def __init__(self, size: int = 100):
        super(ArrayManagerWithDatetime, self).__init__(size=size)

        # numpy 不支持 datetime 类型
        self.datetime_list: List = []
        self.df = pd.DataFrame(
            [],
            columns=[
                "datetime", "open", "high", "low", "close",
                "volume", "turnover", "open_interest"]
        )

    @property
    def datetime(self) -> List:
        """
        Get trading datetime time series list.
        """
        return self.datetime_list

    def update_bar(self, bar: BarData) -> None:
        super().update_bar(bar)
        self.datetime.append(bar.datetime)

        if len(self.datetime) > self.size:
            self.datetime.pop(0)

        if len(self.datetime) == self.size:
            self.df = pd.DataFrame(
                {
                    "datetime": self.datetime,
                    "open": self.open, "high": self.high, "low": self.low, "close": self.close,
                    "volume": self.volume, "turnover": self.turnover,
                    "open_interest": self.open_interest,
                }
            )


if __name__ == "__main__":
    pass
