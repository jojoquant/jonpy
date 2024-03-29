import time
from typing import Callable

import pandas as pd
from datetime import datetime

from jotdx.reader import Reader

from vnpy.event import EventEngine
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.object import BarData
from vnpy.trader.utility import get_folder_path
from vnpy.trader.datafeed import BaseDatafeed, get_datafeed
from vnpy.trader.database import BaseDatabase, get_database

from jnpy.datasource.jotdx import ExhqAPI, IPsSource, FutureMarketCode, KBarType

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

        self.pytdx_ip_source = IPsSource()
        self.ex_api = ExhqAPI()

        self.datafeed: BaseDatafeed = get_datafeed()
        self.database: BaseDatabase = get_database()

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
            update_qt_progress_bar: Callable,
            opt_str: str
    ):
        start_time = time.time()

        try:
            if isinstance(data[datetime_head][0], str):
                data[datetime_head] = data[datetime_head].apply(
                    lambda x: datetime.strptime(x, datetime_format) if datetime_format else datetime.fromisoformat(x))

            elif isinstance(data[datetime_head][0], pd.Timestamp):
                self.write_log("datetime 格式为 pd.Timestamp, 不用处理.")

            else:
                self.write_log("未知datetime类型, 请检查")

            self.write_log(f'df apply 处理日期时间 cost {time.time() - start_time:.2f}s')

        except Exception:
            self.write_log("通达信数据处理存在未知问题...")
            return

        if opt_str == "to_db":
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
            self.write_log(f'df apply 处理bars时间 cost {time.time() - start_time:.2f}s')

            # insert into database
            self.database.save_bar_data(bars, update_qt_progress_bar)

        elif opt_str == "high_to_db":

            start_time = time.perf_counter()

            collection_str = f"{exchange.value}_{interval.value}_{symbol}"
            self.write_log(
                f"Start write data into mongodb"
                f"->{self.database.database}"
                f"->{collection_str}"
            )

            self.database.save_bar_df(
                df=data,
                table=collection_str,
                callback=update_qt_progress_bar
            )

            self.write_log(f'df apply 处理bars时间 cost {time.time() - start_time:.2f}s')

        elif opt_str == "to_csv":

            csv_file_dir = get_folder_path("csv_files")
            data.to_csv(f'{csv_file_dir}/{exchange.value}_{symbol}.csv', index=False)

        start = data[datetime_head].iloc[0]
        end = data[datetime_head].iloc[-1]
        count = len(data)

        return start, end, count

    def load(
            self,
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
            update_qt_progress_bar: Callable,
            opt_str: str,
    ):
        """
        load by filename   %m/%d/%Y
        """

        read_local_file = True

        if read_local_file:
            reader = Reader.factory(market='ext', tdxdir='C:/new_jyplug')
            # 读取日线数据
            # df = reader.daily(symbol='600000')
            data_df = reader.minute(symbol='30#RBL8')
            print(1)
        else:
            ip, port = self.pytdx_ip_source.get_fast_exhq_ip()
            with self.ex_api.connect(ip, port):
                params_dict = {
                    "category": KBarType[interval.name].value,
                    "market": FutureMarketCode[exchange.value].value,
                    "code": symbol,
                }
                data_df = self.ex_api.get_all_KBars_df(**params_dict)

        # transform column name to vnpy format
        data_df.rename(
            columns={
                "datetime": "Datetime",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "position": "OpenInterest",
                "trade": "Volume",
            },
            inplace=True
        )

        if data_df.empty:
            return None, None, 0

        else:
            return self.load_by_handle(
                data_df,
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
                update_qt_progress_bar=update_qt_progress_bar,
                opt_str=opt_str
            )

    def write_log(self, msg: str):
        self.main_engine.write_log(msg)
        self.ex_api.info_log.write_log(msg)
