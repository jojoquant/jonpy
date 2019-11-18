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


cond = {"x": ["1~3", "4~6", "7~9"]}

for i in my_list:
    for c in cond['x']:
        c_list = c.split('~')
        if int(c_list[0]) <= i['number'] <= int(c_list[1]):
            i['number'] = c
            break

df = pd.DataFrame(my_list)
df['count'] = 1
varchar_unique_df = pd.DataFrame(df['varchar'].unique(), columns=['varchar'])

dd = pd.DataFrame()
for i in cond['x']:
    dd1 = pd.merge(df[df['number'] == i], varchar_unique_df, how='outer')
    dd1['number'] = i
    dd1.fillna(0, inplace=True)
    dd = dd.append(dd1)

ddr = dd.groupby(['number', 'varchar']).sum().reset_index()
result = {i[0]: ddr[ddr['varchar'] == i[0]]['count'].tolist()
      for i in varchar_unique_df.values}

result_list = [cond, result]
print(1)

if __name__ == '__main__':
    pass
