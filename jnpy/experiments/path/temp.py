# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/12
'''
__author__ = 'Fangyang'

from collections import Counter

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
my_tuple_list = [(i['number'], i['varchar']) for i in my_list]
c = Counter(my_tuple_list)
dict_c = dict(c)

d_r = {}
for key, value in dict_c.items():
    d_r[key[1]] = []
for key, value in dict_c.items():
    d_r[key[1]].append(value)

print(c)

if __name__ == '__main__':
    pass
