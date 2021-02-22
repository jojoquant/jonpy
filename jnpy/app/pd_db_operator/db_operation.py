#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/1/24 下午8:23
@Author   :   Fangyang
"""
import importlib
from datetime import datetime
from functools import lru_cache

from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database.database import DB_TZ
from vnpy.trader.utility import get_file_path
from jnpy.utils import timeit_cls_method_wrapper


class DBOperation:
    def __init__(self, settings_dict):
        self.DBOCls_init_dict = {
            "settings_dict": settings_dict,
            "file_path_str": get_file_path(settings_dict['database'])
        }
        Pd_DB_str = f"Pd{self.DBOCls_init_dict['settings_dict']['driver'].capitalize()}"
        PdDBClsPkg = importlib.import_module(f"jnpy.app.pd_db_operator.db_classes.{Pd_DB_str}")
        self.pd_dbo = PdDBClsPkg.DBOCls(self.DBOCls_init_dict)

    def get_groupby_data(self):
        return self.pd_dbo.get_groupby_data()

    def get_end_date(self, symbol, exchange, interval):
        return self.pd_dbo.get_end_date(symbol, exchange, interval)

    def get_start_date(self, symbol, exchange, interval):
        return self.pd_dbo.get_start_date(symbol, exchange, interval)

    @lru_cache(maxsize=999)
    @timeit_cls_method_wrapper
    def get_bar_data_df(self, symbol, exchange, interval, start=None, end=None):
        return self.pd_dbo.get_bar_data_df(symbol, exchange, interval, start=start, end=end)

    @timeit_cls_method_wrapper
    def get_bar_data(self, symbol, exchange, interval, start=None, end=None):
        ''' 速度没有本来的列表推导式快 '''
        df = self.get_bar_data_df(symbol, exchange, interval, start=start, end=end)
        print(f"{self} start trans df to list")
        return df.parallel_apply(deal_func, axis=1).tolist()


def deal_func(x):
    bar = BarData(
        symbol=x.loc['symbol'],
        exchange=Exchange(x.loc['exchange']),
        datetime=datetime.strptime(x.loc['datetime'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=DB_TZ),
        interval=Interval(x.loc['interval']),
        volume=x.loc['volume'],
        open_price=x.loc['open_price'],
        high_price=x.loc['high_price'],
        open_interest=x.loc['open_interest'],
        low_price=x.loc['low_price'],
        close_price=x.loc['close_price'],
        gateway_name="DB",
    )
    return bar


if __name__ == "__main__":
    # dbbardata_info_dict = {
    #     "symbol": "RBL8",
    #     "exchange": "SHFE",
    #     "interval": "1m"
    # }
    dbbardata_info_dict = {
        "symbol": "ML8",
        "exchange": "DCE",
        "interval": "d"
    }

    from vnpy.trader.database import updated_settings
    # settings = get_settings("database.")
    dbo = DBOperation(updated_settings)
    rr1 = dbo.get_groupby_data()
    rr2 = dbo.get_end_date(**dbbardata_info_dict)
    rr3 = dbo.get_start_date(**dbbardata_info_dict)
    rr4 = dbo.get_bar_data_df(**dbbardata_info_dict)

    # data = dbo.get_bar_data(**dbbardata_info_dict)
    df = dbo.get_bar_data_df(**dbbardata_info_dict)
    for row in df.iterrows():
        print(1)
    print(1)
