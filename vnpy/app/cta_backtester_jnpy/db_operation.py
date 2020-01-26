#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/1/24 下午8:23
@Author   :   Fangyang
"""

import pandas as pd
from sqlalchemy import create_engine
from vnpy.trader.setting import get_settings
from vnpy.trader.utility import get_file_path


class DBOperation:
    def __init__(self, settings_dict):
        self.settings_dict = settings_dict
        self.file_path_str = get_file_path(settings_dict['database'])
        self.engine = create_engine(f"{self.settings_dict['driver']}:////{self.file_path_str}")

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


if __name__ == "__main__":
    settings = get_settings("database.")
    dbo = DBOperation(settings)
    dbo.get_start_date_from_db()
    print(1)
