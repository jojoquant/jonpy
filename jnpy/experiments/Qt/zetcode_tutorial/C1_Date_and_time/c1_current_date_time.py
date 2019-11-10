# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/10
'''
__author__ = 'Fangyang'


from PyQt5.QtCore import QDate, QTime, QDateTime, Qt


now = QDate.currentDate()
print(now.toString(Qt.ISODate))
print(now.toString(Qt.DefaultLocaleLongDate))

datetime = QDateTime.currentDateTime()
print(datetime.toString())

time = QTime.currentTime()
print(time.toString(Qt.DefaultLocaleLongDate))

if __name__ == '__main__':
    pass


