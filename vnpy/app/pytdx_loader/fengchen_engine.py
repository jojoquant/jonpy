import csv
import os
import time

import pandas as pd
from datetime import datetime
from typing import TextIO

from vnpy.event import EventEngine
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.object import BarData

APP_NAME = "PytdxLoader"


class PytdxLoaderEngine(BaseEngine):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.file_path: str = ""

        self.symbol: str = ""
        self.exchange: Exchange = Exchange.SSE
        self.interval: Interval = Interval.MINUTE
        self.datetime_head: str = ""
        self.open_head: str = ""
        self.close_head: str = ""
        self.low_head: str = ""
        self.high_head: str = ""
        self.volume_head: str = ""

    def to_bar_data(self, item,
                    symbol: str,
                    exchange: Exchange,
                    interval: Interval,
                    datetime_head: str,
                    open_head: str,
                    high_head: str,
                    low_head: str,
                    close_head: str,
                    volume_head: str,
                    open_interest_head: str
                    ):
        bar = BarData(
            symbol=symbol,
            exchange=exchange,
            datetime=item[datetime_head].to_pydatetime(),
            interval=interval,
            volume=item[volume_head],
            open_interest=item[open_interest_head],
            open_price=item[open_head],
            high_price=item[high_head],
            low_price=item[low_head],
            close_price=item[close_head],
            gateway_name="DB"
        )
        return bar

    def load_by_handle(
            self,
            data,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            datetime_head: str,
            open_head: str,
            high_head: str,
            low_head: str,
            close_head: str,
            volume_head: str,
            open_interest_head: str,
            datetime_format: str,
            progress_bar_dict
    ):
        start_time = time.time()
        data[datetime_head] = data[datetime_head].apply(
            lambda x: datetime.strptime(x, datetime_format) if datetime_format else datetime.fromisoformat(x))
        print(f'df apply 处理日期时间 cost {time.time()-start_time:.2f}s')

        start_time = time.time()
        bars = data.apply(
            self.to_bar_data,
            args=(
                symbol,
                exchange,
                interval,
                datetime_head,
                open_head,
                high_head,
                low_head,
                close_head,
                volume_head,
                open_interest_head
            ),
            axis=1).tolist()
        print(f'df apply 处理bars时间 cost {time.time() - start_time:.2f}s')

        start = data[datetime_head].iloc[0]
        end = data[datetime_head].iloc[-1]
        count = len(data)
        # insert into database
        database_manager.save_bar_data(bars, progress_bar_dict)
        return start, end, count

    def load(
            self,
            file_path: str,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            datetime_head: str,
            open_head: str,
            high_head: str,
            low_head: str,
            close_head: str,
            volume_head: str,
            open_interest_head: str,
            datetime_format: str,
            progress_bar_dict

    ):
        """
        load by filename   %m/%d/%Y
        """
        data = pd.read_csv(file_path)

        return self.load_by_handle(
            data,
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            datetime_head=datetime_head,
            open_head=open_head,
            high_head=high_head,
            low_head=low_head,
            close_head=close_head,
            volume_head=volume_head,
            open_interest_head=open_interest_head,
            datetime_format=datetime_format,
            progress_bar_dict=progress_bar_dict
        )
