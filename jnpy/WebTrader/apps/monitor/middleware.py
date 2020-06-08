#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   15/05/2020 22:19
@Author   :   Fangyang
"""

import time

from vnpy.event import EventEngine

from vnpy.gateway.ctp import CtpGateway
from vnpy.app.cta_strategy import CtaEngine

from vnpy.trader.engine import MainEngine
from jnpy.WebTrader.constant import CTP_CONNECT_MAP

event_engine = EventEngine()
main_engine = MainEngine(event_engine)
main_engine.add_gateway(CtpGateway)

cta = main_engine.add_engine(CtaEngine)
cta.init_engine()


def init_strategy():
    engines_dict = {}
    for strategy_name, strategy_class in cta.strategies.items():
        if strategy_class.vt_symbol not in engines_dict:
            engines_dict[strategy_class.vt_symbol] = {"strategy_arr": []}

        expension_name = f"{strategy_name}_{strategy_class.__class__.__name__}"
        strategy_variables_dict = cta.get_strategy_parameters(strategy_name)
        strategy_parameters_dict = cta.strategy_data[strategy_name] if (strategy_name in cta.strategy_data) else {}
        engines_dict[strategy_class.vt_symbol]["strategy_arr"].append(
            {
                "expension_name": expension_name,
                "strategy_variables": transform_expansion_table_format(strategy_variables_dict),
                "strategy_parameters": transform_expansion_table_format(strategy_parameters_dict)
            }
        )

    return {
        "strategy_select": cta.get_all_strategy_class_names(),
        "engines": engines_dict
    }


def transform_expansion_table_format(data_dict):
    return [{"name": key, "value": value} for key, value in data_dict.items()]


def get_strategy_info(class_name):
    variables = cta.get_strategy_class_parameters(class_name)
    return variables


def gateway_connect(ctp_setting):
    # TODO 给前端发送连接成功的提示信息
    main_engine.connect({CTP_CONNECT_MAP[key]: value for key, value in ctp_setting.items()}, "CTP")


def gen_exchange_contract_info():
    for i in range(5):
        time.sleep(1)  # 等待在队列中的event查询交易所信息返回
        oms_engine = main_engine.get_engine("oms")
        contracts_dict = oms_engine.contracts
        re_data_dict = {}
        if contracts_dict:
            main_engine.write_log(f"{i + 1}/5 成功从交易所获取 {len(contracts_dict)} 条contracts信息")
            main_engine.write_log(f"开始解析 contracts_dict ...")
            for key, value in contracts_dict.items():
                item = f"{value.symbol}_{value.name}"
                if value.exchange.value not in re_data_dict:
                    re_data_dict[value.exchange.value] = []
                re_data_dict[value.exchange.value].append(item)

            re_data_dict[value.exchange.value].sort()
            break

    return {"exchange_contract_obj": re_data_dict}


if __name__ == "__main__":
    pass
