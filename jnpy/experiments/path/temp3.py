# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/12
'''
__author__ = 'Fangyang'

import pandas as pd

my_list = [
    {"number": 1, "varchar": "a1"},
    {"number": 2, "varchar": "a1"},
    {"number": 3, "varchar": "b1"},
    {"number": 4, "varchar": "b1"},
    {"number": 5, "varchar": "a1"},
    {"number": 6, "varchar": "a1"},
    {"number": 7, "varchar": "c1"},
    {"number": 8, "varchar": "b1"},
    {"number": 9, "varchar": "a1"},
]

# [{"x": "1~3", "4~6", "7~9"}, {"a1": [2, 2, 1], "b1": [1, 1, 1], "c1": [0, 0, 1]}]

bins_num = 5  # 设置均分为几个区域

df = pd.DataFrame(my_list)
df['number_cut'] = pd.cut(df['number'], bins_num).apply(lambda x: f'{x.left}~{x.right}')

df['count'] = 1
varchar_unique_df = pd.DataFrame(df['varchar'].unique(), columns=['varchar'])

number_cut_unique_index = df['number_cut'].unique().categories
dd = pd.DataFrame()
for i in number_cut_unique_index:
    dd1 = pd.merge(df[df['number_cut'] == i], varchar_unique_df, how='outer')
    dd1['number_cut'] = i
    dd1['count'].fillna(0, inplace=True)
    dd = dd.append(dd1)

ddr = dd.groupby(['number_cut', 'varchar']).sum().reset_index()

result2 = {i[0]: ddr[ddr['varchar'] == i[0]]['count'].tolist()
           for i in varchar_unique_df.values}

result1 = number_cut_unique_index.tolist()

result = [{'x': result1}, result2]
print(1)

if __name__ == '__main__':
    pass
