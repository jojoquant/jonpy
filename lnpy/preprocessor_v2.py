

import pandas as pd
import talib

from jnpy.utils.logging import LogModule
from lnpy.objects import TalibFuns1Args, TalibFuns3Args, TalibFuns4Args_ohlc, TalibFuns4Args_hlcv


class PreProcessor(object):

    def __init__(
            self, df: pd.DataFrame, not_used_func_lst: list,
            alpha: float = 0.01, beta: float = 0.4,
            method: str = 'pearson'
    ):
        self.talib_funcs_list = [
            TalibFuns1Args(), TalibFuns3Args(),
            TalibFuns4Args_ohlc(), TalibFuns4Args_hlcv()
        ]
        self.df = df.dropna()
        self.cols = self.df.columns.tolist()
        self.not_used_func_lst = not_used_func_lst
        self.func_lst = [1, 23, 4]
        self.alpha = alpha  # 方差滤波阈值，方差低于阈值的列会被删除
        self.beta = beta  # 相关性滤波阈值，相关性系数高于阈值的列会被删除
        self.method = method  # 相关性系数，还可以选择'spearman'和'kendall'

        self.close = self.df['close_price'].values
        self.open = self.df['open_price'].values
        self.high = self.df['high_price'].values
        self.low = self.df['low_price'].values
        self.volume = self.df['volume'].values

        self.logmodule = LogModule(name="Ta-lib相关性", level="info")

    def extend_df_tech_cols(self):
        for talib_funs_instance in self.talib_funcs_list:
            for tech_attr, funcs_list in talib_funs_instance.__dict__.items():
                if tech_attr not in self.not_used_func_lst:
                    for func in funcs_list:
                        if talib_funs_instance.arg_str == "c":
                            self.df[func] = getattr(talib, func)(self.close)
                        elif talib_funs_instance.arg_str == "hlc":
                            self.df[func] = getattr(talib, func)(self.high, self.low, self.close)
                        elif talib_funs_instance.arg_str == "hlcv":
                            self.df[func] = getattr(talib, func)(self.high, self.low, self.close, self.volume)
                        elif talib_funs_instance.arg_str == "ohlc":
                            self.df[func] = getattr(talib, func)(self.open, self.high, self.low, self.close)
        self.df = self.df.fillna(method='bfill')

    def high_correlation_filter(self, tech_features_df: pd.DataFrame) -> list:
        # 删除原始dataframe的列，防止这些列被删掉
        corr = tech_features_df.corr(method=self.method).replace(1, 0)

        drop_cols = []
        for col in tech_features_df.columns.tolist():
            if corr[col].any() <= self.beta:
                drop_cols.append(col)
        return drop_cols

    def low_variance_filter(self, tech_features_df) -> list:
        # 删除原始dataframe的列，防止这些列被删掉
        # 进行归一化， 消除数据范围对方差的影响
        features = tech_features_df.apply(lambda x: x / x.max())
        variance = features.var()
        drop_cols = variance[variance < self.alpha].index.tolist()
        return drop_cols

    def get_filtered_cols_df(self) -> pd.DataFrame:
        self.extend_df_tech_cols()
        tech_features_df = self.df.drop(self.cols, axis=1)
        corr_cols_list = self.high_correlation_filter(tech_features_df)
        var_cols_list = self.low_variance_filter(tech_features_df)
        drop_cols = list(set(corr_cols_list + var_cols_list))

        added_cols = tech_features_df.columns.tolist()
        kept_cols = tech_features_df.drop(drop_cols, axis=1).columns.tolist()
        self.logmodule.write_log(f'过滤前的列：{added_cols}')
        self.logmodule.write_log(f'过滤的列：{drop_cols}')
        self.logmodule.write_log(f'保留的列：{kept_cols}')
        return tech_features_df.drop(drop_cols, axis=1)


if __name__ == "__main__":
    df = pd.read_csv('/home/fangyang/桌面/python_project/vnpy/vnpy/app/cta_backtester_jnpy/DRL/data/RBL8.csv')
    not_used_func_lst = ['pattern_recognition']
    a = PreProcessor(df, not_used_func_lst=not_used_func_lst)
    df = a.get_filtered_cols_df()
    print(1)
