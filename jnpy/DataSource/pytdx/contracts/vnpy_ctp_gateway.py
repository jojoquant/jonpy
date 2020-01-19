# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/19 15:44
# @Author   : Fangyang
# @Software : PyCharm

import json
import os
import time
from logging import INFO
import re

from vnpy.gateway.ctp.ctp_gateway import CtpGateway
from vnpy.trader.utility import load_json
from vnpy.trader.engine import MainEngine
from vnpy.trader.setting import SETTINGS


class VnpyCtpGateway:
    def __init__(self):
        # 和交易系统连接成功将有log信息在控制台打印
        SETTINGS["log.active"] = True
        SETTINGS["log.level"] = INFO
        SETTINGS["log.console"] = True

        setting = load_json("connect_ctp.json")

        self.main_engine = MainEngine()
        self.main_engine.add_gateway(CtpGateway)
        self.main_engine.connect(setting, "CTP")

        self.filename = "contracts"
        self.con_type_dict = {
            "主连": "L8",
            "指数": "L9"
        }

    def update_local_json_contracts_info_by_ctp_gateway(self, timeout=5):

        for i in range(timeout):
            time.sleep(1)  # 等待在队列中的event查询交易所信息返回
            oms_engine = self.main_engine.get_engine("oms")
            contracts_dict = oms_engine.contracts
            if contracts_dict:
                self.main_engine.write_log(f"{i + 1}/{timeout} 成功从交易所获取 {len(contracts_dict)} 条contracts信息")
                self.main_engine.write_log(f"开始解析 contracts_dict ...")

                contracts_dict = self.parse_contracts_continue(contracts_dict)
                self.save_json("market_code_info.json", contracts_dict)

                self.main_engine.write_log(f"成功保存 contracts_dict 为本地 json 文件... ")
                break
            else:
                self.main_engine.write_log(f"{i + 1}/{timeout} 从交易所获取contracts信息失败")
                continue

    def save_json(self, filename: str, data: dict):
        '''
        filename: "xxx.json"
        '''
        current_path = os.path.dirname(os.path.abspath(__file__))
        filepath = f"{current_path}/{filename}"
        self.main_engine.write_log(f"将 {filename} 保存到: {filepath}")
        with open(filepath, mode="w+", encoding="UTF-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    def parse_contracts_continue(self, contracts_dict):

        result_dict = {}
        for _, value in contracts_dict.items():
            # 匹配(例如fu2006)字符串开始的字母至少1个
            code_str = re.match(r"^[A-Za-z]+", value.symbol).group(0).upper()
            if code_str not in result_dict:
                result_dict[code_str] = {
                    "exchange": value.exchange.value,
                    # "name": "".join(re.findall(r'[\u4e00-\u9fa5]+', value.name)),
                    "name": value.name,
                    "main_continue_code": f"{code_str}{self.con_type_dict['主连']}",
                    "index_code": f"{code_str}{self.con_type_dict['指数']}"
                }

        return result_dict


if __name__ == '__main__':
    vnpy_ctp = VnpyCtpGateway()
    vnpy_ctp.update_local_json_contracts_info_by_ctp_gateway()
