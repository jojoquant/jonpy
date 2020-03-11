# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/19 15:53
# @Author   : Fangyang
# @Software : PyCharm
import json
import os

from .vnpy_ctp_gateway import VnpyCtpGateway


def read_contracts_json_dict():
    """
    Load data from json file in temp path.
    """
    filepath = os.path.dirname(os.path.abspath(__file__))
    json_file_name = "market_code_info.json"
    filepath = f"{filepath}/{json_file_name}"

    if os.path.exists(filepath):
        with open(filepath, mode="r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    else:
        print(f"{filepath} 不存在!")
        return None


if __name__ == '__main__':
    pass
