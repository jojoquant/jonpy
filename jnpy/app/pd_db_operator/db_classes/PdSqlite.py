
import pandas as pd

from datetime import datetime
from functools import lru_cache
from sqlalchemy import create_engine

from jnpy.utils import timeit_cls_method_wrapper
from jnpy.app.pd_db_operator.db_base import PdBase
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData
from vnpy.trader.utility import get_file_path


class DBOCls(PdBase):

    def __init__(self, settings_dict):
        super(DBOCls, self).__init__(settings_dict)
        self.file_path_str = get_file_path(settings_dict['database.database'])
        self.engine = self.new_engine()


    def new_engine(self):
        return create_engine(f"{self.settings_dict['database.driver']}://{self.sqlite_os}{self.file_path_str}")

    def get_groupby_data(self):
        sql = "select exchange, symbol, interval, count(1) from dbbardata group by symbol, interval, exchange;"
        return pd.read_sql(sql, con=self.engine)

    def get_end_date(self, symbol, exchange, interval):
        sql = f'''select * from dbbardata 
         where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}' 
         order by datetime desc limit 1;
         '''
        df = pd.read_sql(sql, con=self.engine)

        if df.empty:
            return df
        return df['datetime'].values[0]

    def get_start_date(self, symbol, exchange, interval):
        sql = f'''select * from dbbardata 
         where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}' 
         order by datetime asc limit 1;
         '''
        df = pd.read_sql(sql, con=self.engine)
        # str '2013-08-19 15:00:00'
        if df.empty:
            return df
        return df['datetime'].values[0]

    def get_bar_data_df(self, symbol, exchange, interval, start=None, end=None):
        datetime_start = f" and datetime >= '{start}'" if start else ""
        datetime_end = f" and datetime <= '{end}'" if end else f" and datetime <= '{datetime.now()}'"

        sql = f'''select * from dbbardata 
         where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}'
         {datetime_start} {datetime_end}; 
         '''
        df = pd.read_sql(sql, con=self.engine).drop('id', axis=1)

        if df.empty:
            return df

        df['datetime'] = pd.to_datetime(df['datetime'])
        return df

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
    pass