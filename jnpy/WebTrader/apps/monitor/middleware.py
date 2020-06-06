#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   15/05/2020 22:19
@Author   :   Fangyang
"""
import time

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Interval, Exchange

from vnpy.gateway.ctp import CtpGateway
from vnpy.app.cta_strategy import CtaEngine
from jnpy.WebTrader.constant import CTP_CONNECT_MAP

event_engine = EventEngine()
main_engine = MainEngine(event_engine)
main_engine.add_gateway(CtpGateway)

cta = CtaEngine(main_engine, event_engine)
cta2 = CtaEngine(main_engine, event_engine)


def init_strategy():
    cta.init_engine()
    xx = cta.get_all_strategy_class_names()
    # cta.init_strategy()
    print(1)
    return {"strategy_select": xx}


def get_strategy_info(class_name):
    variables = cta.get_strategy_class_parameters(class_name)
    return variables


def gateway_connect(ctp_setting):
    # TODO 给前端发送连接成功的提示信息
    cta.main_engine.connect({CTP_CONNECT_MAP[key]: value for key, value in ctp_setting.items()}, "CTP")


def gen_exchange_contract_info():
    for i in range(5):
        time.sleep(1)  # 等待在队列中的event查询交易所信息返回
        oms_engine = cta.main_engine.get_engine("oms")
        contracts_dict = oms_engine.contracts
        re_data_dict = {}
        if contracts_dict:
            cta.main_engine.write_log(f"{i + 1}/5 成功从交易所获取 {len(contracts_dict)} 条contracts信息")
            cta.main_engine.write_log(f"开始解析 contracts_dict ...")
            for key, value in contracts_dict.items():
                item = {"name": value.name, "symbol": value.symbol}
                if value.exchange.value not in re_data_dict:
                    re_data_dict[value.exchange.value] = []
                re_data_dict[value.exchange.value].append(item)
            break
    return {"exchange_contract_obj": re_data_dict}
    print(1)


if __name__ == "__main__":
    strategy_select_dict = init_strategy()
    for class_name in strategy_select_dict['strategy_select']:
        setting = get_strategy_info(class_name)

        vt_symbol = "rb2010.DCE"
        strategy_name = "aabbcc"

        cta.add_strategy(
            class_name, strategy_name, vt_symbol, setting
        )
