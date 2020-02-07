#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/7 下午7:19
@Author   :   Fangyang
"""

import pandas as pd
from dataclasses import fields

def accept_bars_data_list(all_bar_list:list):

    if all_bar_list:
        df = pd.DataFrame(all_bar_list, columns=['all_bars'])
        for field in fields(all_bar_list[0]):
            attr = field.name
            df[attr] = df['all_bars'].apply(lambda x: getattr(x, attr))
        df.drop(labels=['all_bars'], axis=1, inplace=True)
    else:
        df = None

    df.to_csv("/home/fangyang/桌面/python_project/vnpy/vnpy/app/cta_backtester_jnpy/DRL/data/RBL8.csv", index=False)
    print(1)


if __name__ == "__main__":
    pass