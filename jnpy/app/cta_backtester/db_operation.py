#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/1/24 下午8:23
@Author   :   Fangyang
"""
from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import platform

from vnpy.trader.object import BarData

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database.database import DB_TZ

from vnpy.trader.setting import get_settings
from vnpy.trader.utility import get_file_path

from jnpy.utils import timeit_cls_method_wrapper
from pandarallel import pandarallel

pandarallel.initialize()


class DBOperation:
    def __init__(self, settings_dict):
        self.settings_dict = settings_dict
        self.file_path_str = get_file_path(settings_dict['database'])

        os_str = platform.system()
        if os_str == "Windows":
            sqlite_os = "/"
        elif os_str == "Linux":
            sqlite_os = "//"
        else:
            print(f"OS is {os_str}. DBoperation may meet problem.")

        self.engine = create_engine(f"{self.settings_dict['driver']}://{sqlite_os}{self.file_path_str}")

    def get_groupby_data_from_sql_db(self):
        sql = "select exchange, symbol, interval, count(1) from dbbardata group by symbol, interval, exchange;"
        return pd.read_sql(sql, con=self.engine)

    def get_end_date_from_db(self, symbol, exchange, interval):
        sql = f'''select * from dbbardata 
        where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}' 
        order by datetime desc limit 1;
        '''
        df = pd.read_sql(sql, con=self.engine)
        return df['datetime'].values[0]

    def get_start_date_from_db(self, symbol, exchange, interval):
        sql = f'''select * from dbbardata 
        where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}' 
        order by datetime asc limit 1;
        '''
        df = pd.read_sql(sql, con=self.engine)
        # str '2013-08-19 15:00:00'
        return df['datetime'].values[0]

    @lru_cache(maxsize=999)
    @timeit_cls_method_wrapper
    def get_bar_data_df(self, symbol, exchange, interval, start=None, end=None):
        datetime_start = f" and datetime >= '{start}'" if start else ""
        datetime_end = f" and datetime <= '{end}'" if end else f" and datetime <= '{datetime.now()}'"

        sql = f'''select * from dbbardata 
        where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}'
        {datetime_start} {datetime_end}; 
        '''
        df = pd.read_sql(sql, con=self.engine).drop('id', axis=1)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df

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
    settings = get_settings("database.")
    dbo = DBOperation(settings)
    # dbo.get_start_date_from_db()

    dbbardata_info_dict = {
        "symbol": "RBL8",
        "exchange": "SHFE",
        "interval": "1m",
        "end": "2015-11-24 23:58:02"
    }

    # data = dbo.get_bar_data(**dbbardata_info_dict)
    df = dbo.get_bar_data_df(**dbbardata_info_dict)
    for row in df.iterrows():
        print(1)
    print(1)
