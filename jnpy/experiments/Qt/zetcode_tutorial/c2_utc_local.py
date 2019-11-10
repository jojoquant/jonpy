# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/10
'''
__author__ = 'Fangyang'

from PyQt5.QtCore import QDateTime, Qt, QDate

now = QDateTime.currentDateTime()

print(f"Local datetime : {now.toString(Qt.ISODate)}")
print(f"Universal datetime : {now.toUTC().toString(Qt.ISODate)}")

print(f"The offset from UTC is : {now.offsetFromUtc()} seconds -> {now.offsetFromUtc() / 3600} hours")

d = QDate(1945, 5, 7)
print(f"Days in month : {d.daysInMonth()}")
print(f"Days in year: {d.daysInYear()}")

xmas1 = QDate(2016, 12, 24)
xmas2 = QDate(2019, 12, 24)
now = QDate.currentDate()
days_passed = xmas1.daysTo(now)
print(f"{days_passed} days have passed since last XMas")
days_future = xmas2.daysTo(now)
print(f"{days_future} days have passed since last XMas")

if __name__ == '__main__':
    pass
