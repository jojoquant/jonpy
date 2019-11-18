from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd
from dataclasses import fields

from vnpy.trader.object import BarData

from .base import to_int


class BarManager:
    """"""

    def __init__(self):
        """"""
        self._bars: Dict[datetime, BarData] = {}
        self._datetime_index_map: Dict[datetime, int] = {}
        self._index_datetime_map: Dict[int, datetime] = {}

        self._price_ranges: Dict[Tuple[int, int], Tuple[float, float]] = {}
        self._volume_ranges: Dict[Tuple[int, int], Tuple[float, float]] = {}

        self.df: pd.DataFrame = None
        self.gen_df_flag: bool = False

    def update_history(self, history: List[BarData]) -> None:
        """
        Update a list of bar data.
        """
        # Put all new bars into dict
        for bar in history:
            self._bars[bar.datetime] = bar

        # Sort bars dict according to bar.datetime
        self._bars = dict(sorted(self._bars.items(), key=lambda tp: tp[0]))

        # Update map relationiship
        ix_list = range(len(self._bars))
        dt_list = self._bars.keys()

        self._datetime_index_map = dict(zip(dt_list, ix_list))
        self._index_datetime_map = dict(zip(ix_list, dt_list))

        # Clear data range cache
        self._clear_cache()

    def update_bar(self, bar: BarData) -> None:
        """
        Update one single bar data.
        """
        dt = bar.datetime

        if dt not in self._datetime_index_map:
            ix = len(self._bars)
            self._datetime_index_map[dt] = ix
            self._index_datetime_map[ix] = dt

        self._bars[dt] = bar

        self._clear_cache()

    def get_count(self) -> int:
        """
        Get total number of bars.
        """
        return len(self._bars)

    def get_index(self, dt: datetime) -> int:
        """
        Get index with datetime.
        """
        return self._datetime_index_map.get(dt, None)

    def get_datetime(self, ix: float) -> datetime:
        """
        Get datetime with index.
        """
        ix = to_int(ix)
        return self._index_datetime_map.get(ix, None)

    def get_bar(self, ix: float) -> BarData:
        """
        Get bar data with index.
        """
        ix = to_int(ix)
        dt = self._index_datetime_map.get(ix, None)
        if not dt:
            return None

        return self._bars[dt]

    def get_all_bars(self) -> List[BarData]:
        """
        Get all bar data.
        """
        return list(self._bars.values())

    def get_price_range(self, min_ix: float = None, max_ix: float = None) -> Tuple[float, float]:
        """
        Get price range to show within given index range.
        """
        if not self._bars:
            return 0, 1

        if not min_ix:
            min_ix = 0
            max_ix = len(self._bars) - 1
        else:
            min_ix = to_int(min_ix)
            max_ix = to_int(max_ix)
            max_ix = min(max_ix, self.get_count())

        buf = self._price_ranges.get((min_ix, max_ix), None)
        if buf:
            return buf

        bar_list = list(self._bars.values())[min_ix:max_ix + 1]
        first_bar = bar_list[0]
        max_price = first_bar.high_price
        min_price = first_bar.low_price

        for bar in bar_list[1:]:
            max_price = max(max_price, bar.high_price)
            min_price = min(min_price, bar.low_price)

        self._price_ranges[(min_ix, max_ix)] = (min_price, max_price)
        return min_price, max_price

    def get_volume_range(self, min_ix: float = None, max_ix: float = None) -> Tuple[float, float]:
        """
        Get volume range to show within given index range.
        """
        if not self._bars:
            return 0, 1

        if not min_ix:
            min_ix = 0
            max_ix = len(self._bars) - 1
        else:
            min_ix = to_int(min_ix)
            max_ix = to_int(max_ix)
            max_ix = min(max_ix, self.get_count())

        buf = self._volume_ranges.get((min_ix, max_ix), None)
        if buf:
            return buf

        bar_list = list(self._bars.values())[min_ix:max_ix + 1]

        first_bar = bar_list[0]
        max_volume = first_bar.volume
        min_volume = 0

        for bar in bar_list[1:]:
            max_volume = max(max_volume, bar.volume)

        self._volume_ranges[(min_ix, max_ix)] = (min_volume, max_volume)
        return min_volume, max_volume

    def _clear_cache(self) -> None:
        """
        Clear cached range data.
        """
        self._price_ranges.clear()
        self._volume_ranges.clear()
        self.df = None
        self.gen_df_flag = False

    def clear_all(self) -> None:
        """
        Clear all data in manager.
        """
        self._bars.clear()
        self._datetime_index_map.clear()
        self._index_datetime_map.clear()

        self._clear_cache()

    def _gen_df(self):
        '''
        generate BarManager pd.DataFrame
        '''

        all_bars = self.get_all_bars()
        self.gen_df_flag = True

        if all_bars:
            self.df = pd.DataFrame(all_bars, columns=['all_bars'])
            for field in fields(all_bars[0]):
                attr = field.name
                self.df[attr] = self.df['all_bars'].apply(lambda x: getattr(x, attr))
            self.df.drop(labels=['all_bars'], axis=1, inplace=True)
        else:
            self.df = None

    def get_df(self):
        '''
        get generated BarManager pd.DataFrame
        '''
        #############################################################
        # all_bars = self._manager.get_all_bars()
        ########################################################################
        ### ArrayManager 读入23000条数据, 耗时 0.9s
        # start_time = time.time()
        # am = ArrayManager(size=len(all_bars))
        # for bar in all_bars:
        #     am.update_bar(bar)
        #     if not am.inited:
        #         continue
        # print(f'ArrayManager load all bars cost: {time.time()-start_time:.2f}s')
        ########################################################################

        ##################################################
        ### Pandas 读入23000条数据并进行处理, 耗时 0.28s
        # start_time = time.time()
        # df = pd.DataFrame(all_bars, columns=['all_bars'])
        # for field in fields(all_bars[0]):
        #     attr = field.name
        #     df[attr] = df['all_bars'].apply(lambda x: getattr(x, attr))
        # df.drop(labels=['all_bars'], axis=1, inplace=True)
        # print(f'Pandas load all bars cost: {time.time() - start_time:.2f}s')
        ######################################################
        if self.gen_df_flag:
            return self.df
        else:
            self._gen_df()
            return self.df
