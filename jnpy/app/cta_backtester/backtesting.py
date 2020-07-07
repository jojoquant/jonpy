#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   30/06/2020 22:23
@Author   :   Fangyang
"""
import traceback
from datetime import datetime, timedelta
import time
from functools import lru_cache
from pandas.tseries.offsets import Day

from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager
from vnpy.trader.database.database import DB_TZ

from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.base import BacktestingMode, INTERVAL_DELTA_MAP


class BacktestingEngineJnpy(BacktestingEngine):

    def __init__(self, db_instance):
        super(BacktestingEngineJnpy, self).__init__()
        self.db_instance = db_instance
        self.cur_data_ix = 0
        self.load_bar_end_timestamp = ''

    def load_data(self):
        """"""
        self.output("开始加载历史数据")

        if not self.end:
            self.end = datetime.now()

        if self.start >= self.end:
            self.output("起始日期必须小于结束日期")
            return

        self.history_data = {}  # Clear previously loaded history data
        start_time = time.time()
        if self.mode == BacktestingMode.BAR:
            dbbardata_info_dict = {
                "symbol": self.symbol,
                "exchange": self.exchange.value,
                "interval": self.interval.value,
                "start": self.start,
                "end": self.end,
            }

            # data = self.db_instance.get_bar_data(**dbbardata_info_dict)
            self.history_data = self.db_instance.get_bar_data_df(**dbbardata_info_dict)
        else:
            # TODO tick load data 还没有进行加速优化
            # Load 30 days of data each time and allow for progress update
            progress_delta = timedelta(days=30)
            total_delta = self.end - self.start
            interval_delta = INTERVAL_DELTA_MAP[self.interval]

            start = self.start
            end = self.start + progress_delta
            progress = 0
            while start < self.end:
                end = min(end, self.end)  # Make sure end time stays within set range
                data = load_tick_data(
                    self.symbol,
                    self.exchange,
                    self.start,
                    self.end
                )
                self.history_data.extend(data)  # fangyang 数据库中查询出来的结果放入self.history_data中

                progress += progress_delta / total_delta
                progress = min(progress, 1)
                progress_bar = "#" * int(progress * 10)
                self.output(f"加载进度：{progress_bar} [{progress:.0%}]")

                start = end + interval_delta
                end += (progress_delta + interval_delta)

        self.output(f"backtesting load data cost:{time.time() - start_time:.2f}s")
        self.output(f"历史数据加载完成，数据量：{len(self.history_data)}")

    def run_backtesting(self):
        """"""
        if self.mode == BacktestingMode.BAR:
            func = self.new_bar
            run_backtesting_load_data = self.run_backtesting_load_data_df
            run_backtesting_for = self.run_backtesting_for_df
        else:
            func = self.new_tick
            run_backtesting_load_data = self.run_backtesting_load_data_bd
            run_backtesting_for = self.run_backtesting_for_bd

        self.strategy.on_init()

        run_backtesting_load_data()

        self.strategy.inited = True
        self.output("策略初始化完成")

        self.strategy.on_start()
        self.strategy.trading = True
        self.output("开始回放历史数据")

        run_backtesting_for(func)

        self.output("历史数据回放结束")

    def run_backtesting_load_data_df(self):
        # Use the first [days] of history data for initializing strategy
        self.load_bar_end_timestamp = self.history_data['datetime'].min() + Day(self.days)
        load_bar_df = self.history_data[self.history_data['datetime'] <= self.load_bar_end_timestamp]
        for ix in range(len(load_bar_df)):
            x = load_bar_df.iloc[ix, :]
            bar = BarData(
                symbol=x.loc['symbol'],
                exchange=Exchange(x.loc['exchange']),
                datetime=self.datetime_set_timezone(x.loc['datetime'].to_pydatetime()),
                interval=Interval(x.loc['interval']),
                volume=x.loc['volume'],
                open_price=x.loc['open_price'],
                high_price=x.loc['high_price'],
                open_interest=x.loc['open_interest'],
                low_price=x.loc['low_price'],
                close_price=x.loc['close_price'],
                gateway_name="DB",
            )

            self.datetime = bar.datetime
            # fangyang self.callback 是 strategyTemplate里面的 on_bar
            # self.callback 是在下面的 load_bar(self)函数中赋值的，去策略模板中掉的load_bar/tick
            # 这里将数据推送进我们的策略
            try:
                self.callback(bar)
            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return

    def datetime_set_timezone(self, pydatetime):
        return pydatetime.astimezone(DB_TZ)

    def run_backtesting_for_df(self, func):
        # Use the rest of history data for running backtesting
        data_df = self.history_data[self.history_data['datetime'] > self.load_bar_end_timestamp]
        progress_count = 0
        for ix in range(len(data_df)):
            x = data_df.iloc[ix, :]
            bar = BarData(
                symbol=x.loc['symbol'],
                exchange=Exchange(x.loc['exchange']),
                datetime=self.datetime_set_timezone(x.loc['datetime'].to_pydatetime()),
                interval=Interval(x.loc['interval']),
                volume=x.loc['volume'],
                open_price=x.loc['open_price'],
                high_price=x.loc['high_price'],
                open_interest=x.loc['open_interest'],
                low_price=x.loc['low_price'],
                close_price=x.loc['close_price'],
                gateway_name="DB",
            )

            try:
                func(bar)
                # fangyang 如果有设置这个属性, 那么就在这个属性打印回测进度的 log 信息
                # 进度显示适用于 在策略中计算 耗时长的回测
                if self.backtester_engine:
                    progress = (ix + 1) / len(data_df)
                    progress_interval = 10  # 设置几分区打印一次
                    if progress >= (progress_count / progress_interval):
                        self.backtester_engine.write_log(
                            f"{self.strategy.strategy_name} on_bar() progress : {progress:.2%}"
                        )
                        progress_count += 1

            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return

    def run_backtesting_load_data_bd(self):
        # Use the first [days] of history data for initializing strategy
        day_count = 1

        for ix, data in enumerate(self.history_data):
            if self.datetime and data.datetime.day != self.datetime.day:
                day_count += 1
                if day_count >= self.days:
                    break

            self.datetime = data.datetime
            # fangyang self.callback 是 strategyTemplate里面的 on_bar
            # self.callback 是在下面的 load_bar(self)函数中赋值的，去策略模板中掉的load_bar/tick
            # 这里将数据推送进我们的策略

            try:
                self.callback(data)
            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return
        self.cur_data_ix = ix

    def run_backtesting_for_bd(self, func):
        # Use the rest of history data for running backtesting
        ix = self.cur_data_ix
        history_data_length = len(self.history_data[ix:])
        for index, data in enumerate(self.history_data[ix:]):
            try:
                func(data)
                # fangyang 如果有设置这个属性, 那么就在这个属性打印回测进度的 log 信息
                # 进度显示适用于 在策略中计算 耗时长的回测
                if self.backtester_engine:
                    progress = index / history_data_length
                    if (progress * 100) % 10 == 0:
                        self.backtester_engine.write_log(
                            f"{self.strategy.strategy_name} on_bar() progress : {progress:.2%}"
                        )
            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return


@lru_cache(maxsize=999)
def load_tick_data(
        symbol: str,
        exchange: Exchange,
        start: datetime,
        end: datetime
):
    """"""
    return database_manager.load_tick_data(
        symbol, exchange, start, end
    )


if __name__ == "__main__":
    pass
