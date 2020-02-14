#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/15 上午1:14
@Author   :   Fangyang
"""
from dataclasses import dataclass


@dataclass
class TalibFunsEnum:
    arg_str: str
    cycle_indicators: List[str]
    math_operators: List[str]
    math_transform: List[str]
    momentum_indicator: List[str]
    overlap_studies: List[str]
    pattern_recognition: List[str]
    price_transform: List[str]
    statistic_functions: List[str]
    volatility_indicator: List[str]
    volume_indicator: List[str]


class TalibFuns1Args(TalibFunsEnum):
    arg_str = "c"

    def __init__(self):
        self.cycle_indicators = ['HT_DCPERIOD', 'HT_DCPHASE', 'HT_TRENDMODE']
        self.math_operators = ['MAX', 'MAXINDEX', 'MIN', 'MININDEX', 'SUM']
        self.math_transform = [
            'ACOS', 'ASIN', 'ATAN', 'CEIL',
            'COS', 'COSH', 'EXP', 'FLOOR',
            'LN', 'LOG10', 'SIN', 'SINH',
            'SQRT', 'TAN', 'TANH'
        ]
        self.overlap_studies = [
            'DEMA', 'EMA', 'HT_TRENDLINE', 'KAMA',
            'MA', 'MIDPOINT', 'SMA', 'T3', 'TEMA',
            'TRIMA', 'WMA'
        ]
        self.statistic_functions = [
            'LINEARREG', 'LINEARREG_ANGLE', 'LINEARREG_INTERCEPT',
            'LINEARREG_SLOPE', 'STDDEV', 'TSF', 'VAR'
        ]


class TalibFuns3Args(TalibFunsEnum):
    arg_str = "hlc"

    def __init__(self):
        self.momentum_indicator = [
            'ADX', 'ADXR', 'CCI', 'DX',
            'MINUS_DI', 'PLUS_DI', 'ULTOSC', 'WILLR'
        ]
        self.price_transform = ['TYPPRICE', 'WCLPRICE']
        self.volatility_indicator = ['ATR', 'NATR', 'TRANGE']


class TalibFuns4Args_ohlc(TalibFunsEnum):
    arg_str = "ohlc"

    def __init__(self):
        self.pattern_recognition = [
            'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3BLACKCROWS', 'CDL3LINESTRIKE'
        ]


class TalibFuns4Args_hlcv(TalibFunsEnum):
    arg_str = "hlcv"

    def __init__(self):
        self.volume_indicator = ['AD', 'ADOSC']


if __name__ == "__main__":
    pass
