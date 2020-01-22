# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/19 下午11:45
# @Author   : Fangyang
# @Software : PyCharm


# from vnpy.trader.constant import EMPTY_STRING, EMPTY_FLOAT, OFFSET_OPEN,OFFSET_CLOSE
from vnpy.app.cta_strategy import (
    CtaTemplate,
    TickData,
    BarData,
    OrderData,
    TradeData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.constant import Interval, Direction, Offset
from typing import Any, Callable

import numpy as np
from datetime import datetime, time


########################################################################


class PercentileStrategy(CtaTemplate):
    """MACD策略Demo"""
    author = 'BillyZhang'
    fixedSize = 1
    # 策略参数
    calWindow = 150
    percentile = 95
    tickValueLimit = 5
    Multiple = 0.8

    # 策略变量
    p = 0
    tickValue = 0
    tradeSign = 0
    tickValueHigh = 0
    tickValueLow = 0

    longStop = 0  # 多头止损
    shortStop = 0  # 空头止损
    margin = 0
    lowerLimit = 0
    upperLimit = 50000

    # 时间
    initDays = 10
    DAY_START = time(9, 10)  # 日盘启动和停止时间
    DAY_END = time(14, 55)
    NIGHT_START = time(21, 10)  # 夜盘启动和停止时间
    NIGHT_END = time(10, 55)

    # 参数列表，保存了参数的名称
    parameters = ['author',
                 'initDays',
                 'fixedSize',
                 'calWindow',
                 'percentile',
                 'tickValueLimit',
                 'Multiple'
                 ]

    # 变量列表，保存了变量的名称
    variables = ['inited',
               'trading',
               'pos',
               'longStop',
               'shortStop',
               'posPrice',
               'lowerLimit',
               'p',
               'tickValue',
               'tradeSign',
               'tickValueHigh',
               'tickValueLow'
               ]

    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos',
                'posPrice',
                'longStop',
                'shortStop'
                ]

    # ----------------------------------------------------------------------
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """Constructor"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(size=self.calWindow)

        # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # 策略时方便（更多是个编程习惯的选择）

    # ----------------------------------------------------------------------
    def on_init(self):
        """初始化策略（必须由用户继承实现）"""
        self.write_log('%s策略初始化' % self.strategy_name)

        # initData = self.load_bar(self.initDays)
        # for bar in initData:
        #     self.on_bar(bar)
        # self.put_event()
        self.load_bar(self.initDays)

    # def load_bar(
    #         self,
    #         days: int,
    #         interval: Interval = Interval.MINUTE,
    #         callback: Callable = None,
    #         use_database: bool = False
    # ):
    #     """
    #     Load historical bar data for initializing strategy.
    #     """
    #     if not callback:
    #         callback = self.on_bar
    #
    #     self.cta_engine.load_bar(
    #         self.vt_symbol,
    #         days,
    #         interval,
    #         callback,
    #         use_database
    #     )

    # ----------------------------------------------------------------------
    def on_start(self):
        """启动策略（必须由用户继承实现）"""
        if self.pos == 0:
            self.write_log('%s策略启动' % self.strategy_name)

        # 当前无仓位，发送开仓委托
        # 持有多头仓位

        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop(self):
        """停止策略（必须由用户继承实现）"""
        self.write_log('%s策略停止' % self.strategy_name)
        self.put_event()

    # ----------------------------------------------------------------------
    def on_tick(self, tick: TickData):
        """收到行情TICK推送（必须由用户继承实现）"""
        if self.lowerLimit == 0 or self.upperLimit == 0:
            self.lowerLimit = tick.limit_down
            self.upperLimit = tick.limit_up
        self.bg.update_tick(tick)

    # ----------------------------------------------------------------------
    def on_bar(self, bar: BarData):
        """收到Bar推送（必须由用户继承实现）"""
        # 如果是当然最后5分钟，略过

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return
        # currentTime = datetime.now().time()
        currentTime = time(9, 20)
        # 计算p，和tickValue
        MaxHigh = am.high / am.open
        MaxLow = am.low / am.open
        MaxClose = am.close / am.open
        MaxHigh.sort()
        tt = MaxHigh[int(150*(100-self.percentile)/100)]
        lpHigh = np.percentile(MaxHigh, 100 - self.percentile)
        lpLow = np.percentile(MaxLow, self.percentile)

        self.tickValueHigh = abs(bar.open_price - bar.open_price * lpHigh)
        self.tickValueLow = abs(bar.open_price - bar.open_price * lpLow)

        if self.tickValueHigh > self.tickValueLow and self.tickValueHigh > self.tickValueLimit:
            self.tradeSign = 1
        elif self.tickValueHigh < self.tickValueLow and self.tickValueLow > self.tickValueLimit:
            self.tradeSign = -1
        else:
            self.tradeSign = 0

        # 平当日仓位, 如果当前时间是结束前日盘15点28分钟,或者夜盘10点58分钟，如果有持仓，平仓。
        if ((currentTime >= self.DAY_START and currentTime <= self.DAY_END) or
                (currentTime >= self.NIGHT_START and currentTime <= self.NIGHT_END)):
            if self.pos == 0:
                if self.tradeSign == 0:
                    pass
                elif self.tradeSign == 1 and bar.close_price > self.lowerLimit:
                    self.buy(bar.close_price + 5, self.fixedSize, False)
                elif self.tradeSign == -1 and bar.close_price < self.upperLimit:
                    self.short(bar.close_price - 5, self.fixedSize, False)
            elif self.pos > 0:
                if self.tradeSign == 1 or self.tradeSign == 0:
                    pass
                elif self.tradeSign == -1:
                    self.sell(bar.close_price - 5, abs(self.pos), False)
            elif self.pos < 0:
                if self.tradeSign == -1 or self.tradeSign == 0:
                    pass
                elif self.tradeSign == 1:
                    self.cover(bar.close_price + 5, abs(self.pos), False)

        else:
            if self.pos > 0:
                self.sell(bar.close_price - 5, abs(self.pos), False)
            elif self.pos < 0:
                self.cover(bar.close_price + 5, abs(self.pos), False)
            elif self.pos == 0:
                return

    # ----------------------------------------------------------------------
    def on_order(self, order: OrderData):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass

    # ----------------------------------------------------------------------
    def on_trade(self, trade: TradeData):
        # 发出状态更新事件
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        if trade.offset == Offset.OPEN:
            self.posPrice = trade.price
            if self.tradeSign == 1:
                self.sell(self.posPrice + self.tickValueHigh, abs(self.pos), False)
                self.sell(self.posPrice - self.Multiple * self.tickValueHigh, abs(self.pos), True)
            elif self.tradeSign == -1:
                self.cover(self.posPrice - self.tickValueLow, abs(self.pos), False)
                self.cover(self.posPrice + self.Multiple * self.tickValueLow, abs(self.pos), True)
        elif trade.offset == Offset.CLOSE:
            self.cancel_all()
            self.tradeSign = 0
            # 同步数据到数据库
        self.sync_data()

    # ----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass


if __name__ == '__main__':
    pass
