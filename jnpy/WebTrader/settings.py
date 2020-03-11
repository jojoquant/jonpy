#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午9:18
@Author   :   Fangyang
"""

from vnpy.trader.utility import get_folder_path, load_json
from vnpy.trader.setting import SETTINGS, SETTING_FILENAME


def get_global_config_json_dict():
    config_dict = {ele.stem: load_json(ele) for ele in get_folder_path('.').glob('*.json')}
    config_dict[SETTING_FILENAME.split('.')[0]] = SETTINGS
    return config_dict


if __name__ == "__main__":
    # global_settings_dict = {}
    # x = TRADER_DIR
    # vntrader_path = get_folder_path('.')
    # xx = [i for i in vntrader_path.iterdir() if i.is_dir()]
    # xxx = list(vntrader_path.glob('*.json'))
    # y = xxx[0].stem
    # global_settings_dict = {ele.stem: load_json(ele) for ele in vntrader_path.glob('*.json')}
    dd = get_global_config_json_dict()
    print(1)
