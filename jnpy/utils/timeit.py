#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   30/06/2020 22:44
@Author   :   Fangyang
"""

import time
from functools import wraps


def timeit_cls_method_wrapper(func):
    @wraps(func)  # --> 4
    def clocked(self, *args, **kwargs):  # -- 1
        """this is inner clocked function"""
        start_time = time.time()
        result = func(self, *args, **kwargs)  # --> 2
        print(func.__name__ + " func time_cost -> {:.2f}s".format(time.time() - start_time))
        return result
    return clocked  # --> 3

def timeit_function_wrapper(func):
    @wraps(func)  # --> 4
    def clocked(*args, **kwargs):  # -- 1
        """this is inner clocked function"""
        start_time = time.time()
        result = func(*args, **kwargs)  # --> 2
        print(func.__name__ + " func time_cost -> {:.2f}s".format(time.time() - start_time))
        return result
    return clocked  # --> 3

if __name__ == "__main__":
    pass