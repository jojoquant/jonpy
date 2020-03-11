# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/10/26
'''
__author__ = 'Fangyang'

from threading import Thread
from dataclasses import dataclass
from time import sleep

@dataclass
class A:
    a: int = 0
    active: bool = False

    def __post_init__(self):
        self.thread = Thread(target=self.print_a)
        self.start()

    def print_a(self):
        while self.active:
            print(f'a is {self.a}')
            sleep(1)
        print('self.active is false, stop while loop')

    def start(self):
        """"""
        self.active = True
        self.thread.start()

    def close(self):
        """"""
        if not self.active:
            return

        self.active = False
        self.thread.join()

aa = A()
sleep(3)
print('aaaaa')
aa.close()
print('aaaaa')
aa.start()  # Thread.start()只能开始一次， 在次开始需要重新实例化
sleep(2)
print('bbb')

if __name__ == '__main__':
    pass
