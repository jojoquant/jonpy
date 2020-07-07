#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/15 上午1:14
@Author   :   Fangyang
"""
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class TalibFunsEnum:
    '''
        https://github.com/FangyangJz/talib-document
    '''
    overlap_studies: Dict[str, Dict[str, Tuple[str]]]
    momentum_indicator: Dict[str, Dict[str, Tuple[str]]]
    volume_indicator: Dict[str, Dict[str, Tuple[str]]]
    volatility_indicator: Dict[str, Dict[str, Tuple[str]]]
    price_transform: Dict[str, Dict[str, Tuple[str]]]
    cycle_indicators: Dict[str, Dict[str, Tuple[str]]]
    pattern_recognition: Dict[str, Dict[str, Tuple[str]]]
    statistic_functions: Dict[str, Dict[str, Tuple[str]]]
    math_transform: Dict[str, Dict[str, Tuple[str]]]
    math_operators: Dict[str, Dict[str, Tuple[str]]]


c = ('close',)
cv = ("close", 'volume')
hl = ("high", "low")
hlc = ('high', 'low', 'close')
hlcv = ('high', 'low', 'close', 'volume')
ohlc = ('open', 'high', 'low', 'close')
real = ('real',)
integer = ('integer',)
ddh = ("dif", 'dem', 'histogram')


class TalibFuns(TalibFunsEnum):
    '''
        args: list, 一定注意名称和顺序
    '''

    def __init__(self):
        self.overlap_studies = {
            'BBANDS': {"args": c, "output": ("upperband", "middleband", "lowerband")},
            "DEMA": {"args": c, "output": real},
            "EMA": {"args": c, "output": real},
            "HT_TRENDLINE": {"args": c, "output": real},
            "KAMA": {"args": c, "output": real},
            "MA": {"args": c, "output": real},
            "MAMA": {"args": c, "output": ('mama', 'fama')},
            # periods 应该是和close一样长的数组, 可以表示动态时间均线
            # 暂时不用
            # "MAVP": {"args": ["close", "periods"], "output": real},
            "MIDPOINT": {"args": c, "output": real},
            "MIDPRICE": {"args": hl, "output": real},
            "SAR": {"args": hl, "output": real},
            "SAREXT": {"args": hl, "output": real},
            "SMA": {"args": c, "output": real},
            "T3": {"args": c, "output": real},
            "TEMA": {"args": c, "output": real},
            "TRIMA": {"args": c, "output": real},
            "WMA": {"args": c, "output": real},
        }
        self.momentum_indicator = {
            "ADX": {"args": hlc, "output": real},
            "ADXR": {"args": hlc, "output": real},
            "APO": {"args": c, "output": real},
            "AROON": {"args": hl, "output": ("aroondown", "aroonup")},
            "AROONOSC": {"args": hl, "output": real},
            "BOP": {"args": ohlc, "output": real},
            "CCI": {"args": hlc, "output": real},
            "CMO": {"args": c, "output": real},
            "DX": {"args": hlc, "output": real},
            "MACD": {"args": c, "output": ddh},
            "MACDEXT": {"args": c, "output": ddh},
            "MACDFIX": {"args": c, "output": ddh},
            "MFI": {"args": hlcv, "output": real},
            "MINUS_DI": {"args": hlc, "output": real},
            "MINUS_DM": {"args": hl, "output": real},
            "MOM": {"args": c, "output": real},
            "PLUS_DI": {"args": hlc, "output": real},
            "PLUS_DM": {"args": ["high", 'low'], "output": real},
            "PPO": {"args": c, "output": real},
            "ROC": {"args": c, "output": real},
            "ROCP": {"args": c, "output": real},
            "ROCR": {"args": c, "output": real},
            "ROCR100": {"args": c, "output": real},
            "RSI": {"args": c, "output": real},
            "STOCH": {"args": hlc, "output": ['slowk', 'slowd']},
            "STOCHF": {"args": hlc, "output": ['fastk', 'fastd']},
            "STOCHRSI": {"args": c, "output": ['fastk', 'fastd']},
            "TRIX": {"args": c, "output": real},
            "ULTOSC": {"args": hlc, "output": real},
            "WILLR": {"args": hlc, "output": real},
        }
        self.volume_indicator = {
            'AD': {"args": hlcv, "output": real},
            'ADOSC': {"args": hlcv, "output": real},
            'OBV': {"args": cv, "output": real},
        }
        self.volatility_indicator = {
            'ATR': {"args": hlc, "output": real},
            'NATR': {"args": hlc, "output": real},
            'TRANGE': {"args": hlc, "output": real},
        }
        self.price_transform = {
            'AVGPRICE': {"args": ohlc, "output": real},
            'MEDPRICE': {"args": hl, "output": real},
            'TYPPRICE': {"args": hlc, "output": real},
            'WCLPRICE': {"args": hlc, "output": real},
        }
        self.cycle_indicators = {
            'HT_DCPERIOD': {"args": c, "output": real},
            'HT_DCPHASE': {"args": c, "output": real},
            "HT_PHASOR": {"args": c, "output": ["inphase", "quadrature"]},
            'HT_SINE': {"args": c, "output": ["sine", "leadsine"]},
            'HT_TRENDMODE': {"args": c, "output": integer},
        }
        self.pattern_recognition = {
            'CDL2CROWS': {"args": ohlc, "output": integer},
            'CDL3BLACKCROWS': {"args": ohlc, "output": integer},
            'CDL3INSIDE': {"args": ohlc, "output": integer},
            'CDL3LINESTRIKE': {"args": ohlc, "output": integer},
            'CDL3OUTSIDE': {"args": ohlc, "output": integer},
            'CDL3STARSINSOUTH': {"args": ohlc, "output": integer},
            'CDL3WHITESOLDIERS': {"args": ohlc, "output": integer},
            'CDLABANDONEDBABY': {"args": ohlc, "output": integer},
            'CDLADVANCEBLOCK': {"args": ohlc, "output": integer},
            'CDLBELTHOLD': {"args": ohlc, "output": integer},
            'CDLBREAKAWAY': {"args": ohlc, "output": integer},
            'CDLCLOSINGMARUBOZU': {"args": ohlc, "output": integer},
            'CDLCONCEALBABYSWALL': {"args": ohlc, "output": integer},
            'CDLCOUNTERATTACK': {"args": ohlc, "output": integer},
            'CDLDARKCLOUDCOVER': {"args": ohlc, "output": integer},
            'CDLDOJI': {"args": ohlc, "output": integer},
            'CDLDOJISTAR': {"args": ohlc, "output": integer},
            'CDLDRAGONFLYDOJI': {"args": ohlc, "output": integer},
            'CDLENGULFING': {"args": ohlc, "output": integer},
            'CDLEVENINGDOJISTAR': {"args": ohlc, "output": integer},
            'CDLEVENINGSTAR': {"args": ohlc, "output": integer},
            'CDLGAPSIDESIDEWHITE': {"args": ohlc, "output": integer},
            'CDLGRAVESTONEDOJI': {"args": ohlc, "output": integer},
            'CDLHAMMER': {"args": ohlc, "output": integer},
            'CDLHANGINGMAN': {"args": ohlc, "output": integer},
            'CDLHARAMI': {"args": ohlc, "output": integer},
            'CDLHARAMICROSS': {"args": ohlc, "output": integer},
            'CDLHIGHWAVE': {"args": ohlc, "output": integer},
            'CDLHIKKAKE': {"args": ohlc, "output": integer},
            'CDLHIKKAKEMOD': {"args": ohlc, "output": integer},
            'CDLHOMINGPIGEON': {"args": ohlc, "output": integer},
            'CDLIDENTICAL3CROWS': {"args": ohlc, "output": integer},
            'CDLINNECK': {"args": ohlc, "output": integer},
            'CDLINVERTEDHAMMER': {"args": ohlc, "output": integer},
            'CDLKICKING': {"args": ohlc, "output": integer},
            'CDLKICKINGBYLENGTH': {"args": ohlc, "output": integer},
            'CDLLADDERBOTTOM': {"args": ohlc, "output": integer},
            'CDLLONGLEGGEDDOJI': {"args": ohlc, "output": integer},
            'CDLLONGLINE': {"args": ohlc, "output": integer},
            'CDLMARUBOZU': {"args": ohlc, "output": integer},
            'CDLMATCHINGLOW': {"args": ohlc, "output": integer},
            'CDLMATHOLD': {"args": ohlc, "output": integer},
            'CDLMORNINGDOJISTAR': {"args": ohlc, "output": integer},
            'CDLMORNINGSTAR': {"args": ohlc, "output": integer},
            'CDLONNECK': {"args": ohlc, "output": integer},
            'CDLPIERCING': {"args": ohlc, "output": integer},
            'CDLRICKSHAWMAN': {"args": ohlc, "output": integer},
            'CDLRISEFALL3METHODS': {"args": ohlc, "output": integer},
            'CDLSEPARATINGLINES': {"args": ohlc, "output": integer},
            'CDLSHOOTINGSTAR': {"args": ohlc, "output": integer},
            'CDLSHORTLINE': {"args": ohlc, "output": integer},
            'CDLSPINNINGTOP': {"args": ohlc, "output": integer},
            'CDLSTALLEDPATTERN': {"args": ohlc, "output": integer},
            'CDLSTICKSANDWICH': {"args": ohlc, "output": integer},
            'CDLTAKURI': {"args": ohlc, "output": integer},
            'CDLTASUKIGAP': {"args": ohlc, "output": integer},
            'CDLTHRUSTING': {"args": ohlc, "output": integer},
            'CDLTRISTAR': {"args": ohlc, "output": integer},
            'CDLUNIQUE3RIVER': {"args": ohlc, "output": integer},
            'CDLUPSIDEGAP2CROWS': {"args": ohlc, "output": integer},
            'CDLXSIDEGAP3METHODS': {"args": ohlc, "output": integer}
        }
        self.statistic_functions = {
            'BETA': {"args": hl, "output": real},
            'CORREL': {"args": hl, "output": real},
            'LINEARREG': {"args": c, "output": real},
            'LINEARREG_ANGLE': {"args": c, "output": real},
            'LINEARREG_INTERCEPT': {"args": c, "output": real},
            'LINEARREG_SLOPE': {"args": c, "output": real},
            'STDDEV': {"args": c, "output": real},
            'TSF': {"args": c, "output": real},
            'VAR': {"args": c, "output": real},
        }
        self.math_transform = {
            'ACOS': {"args": c, "output": real},
            'ASIN': {"args": c, "output": real},
            'ATAN': {"args": c, "output": real},
            'CEIL': {"args": c, "output": real},
            'COS': {"args": c, "output": real},
            'COSH': {"args": c, "output": real},
            'EXP': {"args": c, "output": real},
            'FLOOR': {"args": c, "output": real},
            'LN': {"args": c, "output": real},
            'LOG10': {"args": c, "output": real},
            'SIN': {"args": c, "output": real},
            'SINH': {"args": c, "output": real},
            'SQRT': {"args": c, "output": real},
            'TAN': {"args": c, "output": real},
            'TANH': {"args": c, "output": real},
        }
        self.math_operators = {
            'ADD': {"args": hl, "output": real},
            'DIV': {"args": hl, "output": real},
            "MAX": {"args": c, "output": real},
            "MAXINDEX": {"args": c, "output": integer},
            "MIN": {"args": c, "output": real},
            "MININDEX": {"args": c, "output": integer},
            "MINMAX": {"args": c, "output": ["min", "max"]},
            "MINMAXINDEX": {"args": c, "output": ["minidx", "maxidx"]},
            "MULT": {"args": hl, "output": real},
            "SUB": {"args": hl, "output": real},
            "SUM": {"args": c, "output": real},
        }


if __name__ == "__main__":
    pass
