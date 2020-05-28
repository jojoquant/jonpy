#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   15/05/2020 22:19
@Author   :   Fangyang
"""

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Interval, Exchange
from vnpy.app.cta_strategy import CtaEngine

event_engine = EventEngine()
main_engine = MainEngine(event_engine)
cta = CtaEngine(main_engine, event_engine)


def init_strategy():
    cta.init_engine()
    xx = cta.get_all_strategy_class_names()
    # cta.init_strategy()
    print(1)
    return {"strategy_array": xx}


if __name__ == "__main__":
    init_strategy()
