import pandas as pd
import numpy as np
import talib

from jnpy.utils.logging import LogModule
from lnpy.objects import TalibFuns


class PreProcessor(object):

    def __init__(
            self, df: pd.DataFrame, not_used_func_lst: list = [],
            alpha: float = 0.01, beta: float = 0.4,
            method: str = 'pearson'
    ):
        self.talib_funcs = TalibFuns()
        self.df = df.dropna()
        self.cols = self.df.columns.tolist()
        self.not_used_func_lst = not_used_func_lst
        self.alpha = alpha  # 方差滤波阈值，方差低于阈值的列会被删除
        self.beta = beta  # 相关性滤波阈值，相关性系数高于阈值的列会被删除
        self.method = method  # 相关性系数，还可以选择'spearman'和'kendall'

        self.close = self.df['close_price'].values
        self.open = self.df['open_price'].values
        self.high = self.df['high_price'].values
        self.low = self.df['low_price'].values
        self.volume = self.df['volume'].values

        self.logmodule = LogModule(name="Ta-lib相关性", level="info")

    def extend_df_tech_cols(self) -> pd.DataFrame:
        for tech_attr, param_dict in self.talib_funcs.__dict__.items():
            if tech_attr not in self.not_used_func_lst:
                for TaIndicatorClassStr, args_output_dict in param_dict.items():
                    args = {
                        'close': self.close,
                        'open': self.open,
                        'high': self.high,
                        'low': self.low,
                        'volume': self.volume,
                    }
                    args_list = [args[key] for key in args_output_dict['args']]
                    col_list = []
                    for out in args_output_dict['output']:
                        col_str = f"{TaIndicatorClassStr}_{out}"
                        self.df[col_str] = pd.Series()
                        col_list.append(col_str)
                    ta_result_tuple = getattr(talib, TaIndicatorClassStr)(*args_list)

                    # Debugger
                    # if TaIndicatorClassStr == "DEMA":
                    #     rrr = talib.EMA(self.close)
                    #     print(1)

                    if not isinstance(ta_result_tuple, tuple):
                        ta_result_tuple = (ta_result_tuple,)
                    for col, array in zip(col_list, ta_result_tuple):
                        self.df[col] = array

        self.df = self.df.fillna(method='bfill')
        self.df = self.df.replace([np.inf, -np.inf], np.nan).dropna(axis=1)
        return self.df

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
    df = pd.read_csv('/home/fangyang/桌面/python_project/vnpy/vnpy/app/cta_strategy/strategies/rbl8_1m.csv')
    not_used_func_lst = ['pattern_recognition']
    # a = PreProcessor(df, not_used_func_lst=not_used_func_lst)
    a = PreProcessor(df)
    df = a.get_filtered_cols_df()
    print(1)
