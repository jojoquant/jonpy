#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   15/05/2020 22:19
@Author   :   Fangyang
"""

import time

from vnpy.event import EventEngine
from vnpy.gateway.ctp import CtpGateway
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG

from jnpy.WebTrader.constant import CTP_CONNECT_MAP
from jnpy.WebTrader.apps.monitor.engine import MonitorMainEngine, MonitorCtaEngine

event_engine = EventEngine()
main_engine = MonitorMainEngine(event_engine)
main_engine.write_log("主引擎创建成功")

main_engine.add_gateway(CtpGateway)
cta = main_engine.add_engine(MonitorCtaEngine)
log_engine = main_engine.get_engine("log")
event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
main_engine.write_log("注册日志事件监听")


def init_engine():
    cta.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    engines_dict = {}
    for strategy_name, strategy_class in cta.strategies.items():
        if strategy_class.vt_symbol not in engines_dict:
            engines_dict[strategy_class.vt_symbol] = {"strategy_arr": []}

        strategy_variables_dict = cta.get_strategy_parameters(strategy_name)
        strategy_parameters_dict = cta.strategy_data[strategy_name] if (strategy_name in cta.strategy_data) else {}
        engines_dict[strategy_class.vt_symbol]["strategy_arr"].append(
            {
                "strategy_name": strategy_name,
                "strategy_class": strategy_class.__class__.__name__,
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


def get_strategy_info(class_name: str):
    variables = cta.get_strategy_class_parameters(class_name)
    return variables


def gateway_connect(ctp_setting):
    main_engine.connect({CTP_CONNECT_MAP[key]: value for key, value in ctp_setting.items()}, "CTP")
    main_engine.write_log("连接CTP接口")

    return gen_exchange_contract_info()


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


def init_strategy(strategy_name: str):
    """"""
    try:
        print("init_strategy")
        cta.init_strategy(strategy_name)
        return None
    except:
        return dialog_dict(type_str="error", msg=f"策略({strategy_name})初始化遇到问题")


def start_strategy(strategy_name: str):
    """"""
    try:
        cta.start_strategy(strategy_name)
        return None
    except:
        return dialog_dict(type_str="error", msg=f"策略({strategy_name})启动遇到问题")


def edit_strategy(strategy_name: str, strategy_variables: dict):
    setting = {item['name']: item['value'] for item in strategy_variables}
    try:
        cta.edit_strategy(strategy_name, setting)
        return dialog_dict(type_str="success", msg=f"策略({strategy_name})编辑成功")
    except:
        return dialog_dict(type_str="error", msg=f"策略({strategy_name})编辑失败")


def dialog_dict(type_str: str, msg: str):
    return {"dialog": {"type": type_str, "msg": msg}}


if __name__ == "__main__":
    pass
