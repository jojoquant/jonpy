#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/19 下午4:24
@Author   :   Fangyang
"""
from datetime import datetime
import pandas as pd

from vnpy_ctastrategy.strategies.double_ma_strategy import DoubleMaStrategy
from vnpy_ctastrategy.strategies.boll_channel_strategy import BollChannelStrategy
from vnpy_ctastrategy.strategies.atr_rsi_strategy import AtrRsiStrategy
from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_ctastrategy.strategies.turtle_signal_strategy import TurtleSignalStrategy

from jnpy.DataSource.jotdx.contracts import read_contracts_json_dict
from jnpy.app.cta_backtester.backtesting import BacktestingEngineJnpy
from vnpy.trader.constant import Interval
from vnpy.trader.database import get_database

class PortfolioBacktesting:

    def __init__(self):
        self.database = get_database()
        self.backtesting_engine = BacktestingEngineJnpy(self.database)
        self.contracts_dict = read_contracts_json_dict()
        self.last_vt_symbol = ''

    def run_backtesting(self, strategy_class, setting, vt_symbol, bk_param_dict):
        bk_param_dict['vt_symbol'] = vt_symbol
        symbol_key = vt_symbol.split("L8")[0]
        bk_param_dict['size'] = self.contracts_dict[symbol_key]['size']
        bk_param_dict['pricetick'] = self.contracts_dict[symbol_key]['pricetick']

        self.backtesting_engine.set_parameters(**bk_param_dict)
        self.backtesting_engine.add_strategy(strategy_class, setting)

        if vt_symbol != self.last_vt_symbol:
            self.backtesting_engine.load_data()
            self.last_vt_symbol = vt_symbol

        self.backtesting_engine.run_backtesting()
        df = self.backtesting_engine.calculate_result()
        self.backtesting_engine.clear_data()
        return df

    def show_portafolio(self, df):
        # engine = BacktestingEngine()

        self.backtesting_engine.calculate_statistics(df)
        self.backtesting_engine.show_chart(df)


if __name__ == "__main__":

    pb = PortfolioBacktesting()

    for symbol_idx, vt_symbol in enumerate(["RBL8.SHFE"]):
        # vt_symbol = "RBL8.SHFE"  # 遍历得到各种低相关性合约
        bk_param_dict = {
            "interval": Interval.MINUTE_5,
            "start": datetime(2019, 1, 1),
            "end": datetime(2021, 10, 30),
            "rate": 0.3 / 10000,  # 未来从人工统计表中获取
            "slippage": 1,
            "size": 10,
            "pricetick": 1,
            "capital": 1_000_000,  # 资金分配需要动态调整
        }

        strategy_cls_list = [DoubleMaStrategy, AtrRsiStrategy,  BollChannelStrategy]
        for strategy_idx, strategy_cls in enumerate(strategy_cls_list):
            df = pb.run_backtesting(
                strategy_class=strategy_cls,
                setting={},
                vt_symbol=vt_symbol,
                bk_param_dict=bk_param_dict
            )
            pb.show_portafolio(df)

            # setting = OptimizationSetting()
            # setting.set_target("sharpe_ratio")
            # op_params_list = pb.backtesting_engine.strategy.parameters

            # setting.set_target("sharpe_ratio")
            # setting.add_parameter(op_params_list[0], 3, 100, 10)
            # setting.add_parameter(op_params_list[1], 3, 100, 10)
            # op_params_result_list = pb.backtesting_engine.run_ga_optimization(setting)
            # show op result
            # op_df = pb.run_backtesting(
            #     strategy_class=strategy_cls,
            #     setting=op_params_result_list[0][0],
            #     vt_symbol=vt_symbol,
            #     bk_param_dict=bk_param_dict
            # )
            # pb.show_portafolio(op_df)

            # if strategy_idx == 0:
            #     single_symbol_multi_strategy_df = df
            #     continue
            # single_symbol_multi_strategy_df += df

        # single_symbol_multi_strategy_df = single_symbol_multi_strategy_df.dropna()
        # single_symbol_multi_strategy_df = single_symbol_multi_strategy_df.fillna(0)
        # pb.show_portafolio(single_symbol_multi_strategy_df)
        #
        # if symbol_idx == 0:
        #     multi_symbol_multi_strategy_df = single_symbol_multi_strategy_df
        #     continue
        # multi_symbol_multi_strategy_df += single_symbol_multi_strategy_df

    # multi_symbol_multi_strategy_df = multi_symbol_multi_strategy_df.dropna()
    # multi_symbol_multi_strategy_df = multi_symbol_multi_strategy_df.fillna(0)
    # pb.show_portafolio(multi_symbol_multi_strategy_df)
    # print(1)
