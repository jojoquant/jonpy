'''
1. 增加了缺失值的向前填充
2. 增加了方差过滤模块
3. 增加了一个logging模块(待完善)
4. 增加了一些注释
'''

import pandas as pd
import talib

from log import LogModule


class PreProcessor(object):

    def __init__(self, df, func_lst, alpha=0.01, beta=0.4, method='pearson'):
        self.df = df.dropna()
        self.cols = self.df.columns.tolist()
        self.func_lst = func_lst
        self.alpha = alpha  # 方差滤波阈值，方差低于阈值的列会被删除
        self.beta = beta  # 相关性滤波阈值，相关性系数高于阈值的列会被删除
        self.method = method  # 相关性系数，还可以选择'spearman'和'kendall'

        self.close = self.df['close_price'].values
        self.open = self.df['open_price'].values
        self.high = self.df['high_price'].values
        self.low = self.df['low_price'].values
        self.volume = self.df['volume'].values

        self.logmodule = LogModule(name="get_filtered_cols", level="debug")

    def cycle_indicators(self):
        func_lst = ['HT_DCPERIOD', 'HT_DCPHASE', 'HT_TRENDMODE']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.close)
        return self.df

    def math_operators(self):
        func_lst = ['MAX', 'MAXINDEX', 'MIN', 'MININDEX', 'SUM']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.close)
        return self.df

    def math_transform(self):
        func_lst = ['ACOS', 'ASIN', 'ATAN', 'CEIL', 'COS', 'COSH', 'EXP', 'FLOOR', 'LN', 'LOG10', 'SIN', 'SINH', 'SQRT',
                    'TAN', 'TANH']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.close)
        return self.df

    def momentum_indicator(self):
        func_lst = ['ADX', 'ADXR', 'CCI', 'DX', 'MINUS_DI', 'PLUS_DI', 'ULTOSC', 'WILLR']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.high, self.low, self.close)
        return self.df

    def overlap_studies(self):
        func_lst = ['DEMA', 'EMA', 'HT_TRENDLINE', 'KAMA', 'MA', 'MIDPOINT', 'SMA', 'T3', 'TEMA',
                    'TRIMA', 'WMA']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.close)
        return self.df

    def pattern_recognition(self):
        func_lst = ['CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3BLACKCROWS', 'CDL3LINESTRIKE']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.open, self.high, self.low, self.close)
        return self.df

    def price_transform(self):
        func_lst = ['TYPPRICE', 'WCLPRICE']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.high, self.low, self.close)
        return self.df

    def statistic_functions(self):
        func_lst = ['LINEARREG', 'LINEARREG_ANGLE', 'LINEARREG_INTERCEPT', 'LINEARREG_SLOPE', 'STDDEV', 'TSF',
                    'VAR']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.close)
        return self.df

    def volatility_indicator(self):
        func_lst = ['ATR', 'NATR', 'TRANGE']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.high, self.low, self.close)
        return self.df

    def volume_indicator(self):
        func_lst = ['AD', 'ADOSC']
        for func in func_lst:
            self.df[func] = getattr(talib, func)(self.high, self.low, self.close, self.volume)
        return self.df

    def add_cols(self):
        for func in self.func_lst:
            self.df = eval('self.{}()'.format(func))
        self.df = self.df.fillna(method='bfill')
        return self.df

    def high_correlation_filter(self):
        # 删除原始dataframe的列，防止这些列被删掉
        features = self.add_cols().drop(self.cols, axis=1)
        corr = features.corr(method=self.method).replace(1, 0)

        drop_cols = []
        for col in features.columns.tolist():
            if corr[col].any() <= self.beta:
                drop_cols.append(col)
        return drop_cols

    def low_variance_filter(self):
        # 删除原始dataframe的列，防止这些列被删掉
        # 进行归一化， 消除数据范围对方差的影响
        features = self.add_cols().drop(self.cols, axis=1).apply(lambda x: x / x.max())
        variance = features.var()
        drop_cols = variance[variance < self.alpha].index.tolist()
        return drop_cols

    def get_filtered_cols(self):
        corr_cols = self.high_correlation_filter()
        var_cols = self.low_variance_filter()
        drop_cols = list(set(corr_cols + var_cols))

        added_cols = self.add_cols().columns.tolist()
        kept_cols = self.add_cols().drop(drop_cols, axis=1).columns.tolist()
        self.logmodule.write_log('过滤前的列：{}， 过滤的列：{}， 保留的列：{}'.format(added_cols, drop_cols, kept_cols))
        return self.add_cols().drop(drop_cols, axis=1)


df = pd.read_csv('RBL8.csv')

func_lst = ['cycle_indicators', 'math_operators',
            'math_transform', 'momentum_indicator',
            'overlap_studies', 'price_transform',
            'statistic_functions', 'volatility_indicator',
            'volume_indicator']

A = PreProcessor(df, func_lst=func_lst)
print(A.get_filtered_cols().shape)
