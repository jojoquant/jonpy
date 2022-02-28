import time

import akshare as ak
import pandas as pd

from jnpy.datasource.utils import change_df_colums
from vnpy.trader.database import get_database
from vnpy.trader.constant import Exchange, Interval

period_map = {
    Interval.MINUTE: "1",
    Interval.MINUTE_5: "5",
    Interval.MINUTE_15: "15",
    Interval.MINUTE_30: "30",
    Interval.HOUR: "60"
}


def get_main_contract_data(exchange_list):
    pass


if __name__ == '__main__':
    db = get_database()

    exchange_list = [Exchange.SHFE, Exchange.DCE, Exchange.CZCE]
    exchange_symbol_list = [e.value.lower() for e in exchange_list]

    interval_list = [Interval.MINUTE, Interval.MINUTE_5, Interval.MINUTE_15]
    counter = 0

    for exchange_symbol in exchange_symbol_list:
        main_contract_list = ak.match_main_contract(symbol=exchange_symbol).split(",")

        for symbol in main_contract_list:

            for interval in interval_list:
                print("#" * 50)
                print(f"Start download [{exchange_symbol}] - [{symbol}] - [{interval.value}]")
                futures_zh_minute_sina_df = ak.futures_zh_minute_sina(symbol=symbol, period=period_map[interval])
                futures_zh_minute_sina_df['datetime'] = pd.to_datetime(futures_zh_minute_sina_df['datetime'])
                futures_zh_minute_sina_df['symbol'] = symbol
                futures_zh_minute_sina_df['exchange'] = exchange_symbol.upper()
                futures_zh_minute_sina_df['interval'] = interval.value

                futures_zh_minute_sina_df = change_df_colums(futures_zh_minute_sina_df)

                counter += 1
                if counter % 20:
                    time.sleep(60)

                # db.save_bar_df(futures_zh_minute_sina_df)
                # print(1)
