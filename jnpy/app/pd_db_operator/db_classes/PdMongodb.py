import pandas as pd

from datetime import datetime
from pymongo import MongoClient

from jnpy.app.pd_db_operator.db_base import PdBase
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData


class DBOCls(PdBase):

    def __init__(self, settings_dict):
        super(DBOCls, self).__init__(settings_dict)
        self.client = self.new_engine()

    def new_engine(self):
        return MongoClient(
            host=self.settings_dict['database.host'],
            port=self.settings_dict['database.port'],
            # username=self.settings_dict['database.user'],
            # password=self.settings_dict['database.password']
        )

    def get_groupby_data(self):
        db = self.client[self.settings_dict["database.database"]]
        collection = db["db_bar_data"]
        query = [
            {
                "$group": {
                    "_id": {"exchange": "$exchange", "interval": "$interval", "symbol": "$symbol"},
                    "count": {"$sum": 1}
                }
            }
        ]

        return pd.json_normalize(
            list(collection.aggregate(query))
        ).rename(
            columns={
                "_id.exchange": "exchange",
                "_id.interval": "interval",
                "_id.symbol": "symbol",
                "count": "count(1)",
            }
        )

    def get_end_date(self, symbol, exchange, interval):
        # sql = f'''select * from dbbardata
        #  where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}'
        #  order by datetime desc limit 1;
        #  '''

        db = self.client[self.settings_dict["database.database"]]
        collection = db["db_bar_data"]
        query = (
            {"symbol": symbol, "exchange": exchange, "interval": interval},
            {'_id': 0}
        )
        df = pd.json_normalize(
            list(
                collection.find(*query).sort([("datetime", -1)]).limit(1)
            )
        )

        return df['datetime'].astype(str).values[0]

    def get_start_date(self, symbol, exchange, interval):
        sql = f'''select * from dbbardata 
         where symbol='{symbol}' and exchange='{exchange}' and interval='{interval}' 
         order by datetime asc limit 1;
         '''

        db = self.client[self.settings_dict["database.database"]]
        collection = db["db_bar_data"]
        query = (
            {"symbol": symbol, "exchange": exchange, "interval": interval},
            {'_id': 0}
        )
        df = pd.json_normalize(
            list(
                collection.find(*query).sort([("datetime", 1)]).limit(1)
            )
        )
        return df['datetime'].astype(str).values[0]

    def get_bar_data_df(
            self, symbol: str, exchange: str, interval: str,
            start: datetime.date = None, end: datetime.date = None) -> pd.DataFrame:
        datetime_start = {"$gte": datetime(start.year, start.month, start.day)} if start else {}
        datetime_end = {"$lte": datetime(end.year, end.month, end.day)} if end else {"$lte": datetime.now()}

        db = self.client[self.settings_dict["database.database"]]
        collection = db["db_bar_data"]
        query = (
            {
                "symbol": symbol, "exchange": exchange, "interval": interval,
                "datetime": {**datetime_start, **datetime_end}
            },
            {'_id': 0}
        )

        df = pd.json_normalize(list(collection.find(*query)))

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
