# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/5
'''
__author__ = 'Fangyang'

import pandas as pd

if __name__ == '__main__':
    df = pd.read_csv('30#RBL8.csv', '\t', encoding='gbk', skiprows=1)
    df.dropna(inplace=True)
    df.columns = [i.strip() for i in df.columns]
    df['时间'] = df['时间'].apply(lambda x: f' {int(x):04d}')
    df['datetime'] = df['日期'] + df['时间']
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y/%m/%d %H%M')

    columns_list = ['日期', '时间', '开盘', '最高', '最低', '收盘', '成交量', '持仓量', '结算价', 'datetime']
    del_element_list = ['日期', '时间', '结算价']
    for ele in del_element_list:
        columns_list.remove(ele)

    df = df[columns_list].rename(
        columns={
            'datetime': 'Datetime',
            '开盘': 'Open',
            '最高': 'High',
            '最低': 'Low',
            '收盘': 'Close',
            '成交量': 'Volume'
        }
    )
    df.to_csv('RB99.csv', index=False)
    print(1)
