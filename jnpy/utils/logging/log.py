# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/19 0:48
# @Author   : Fangyang
# @Software : PyCharm


import logging


class LogModule:

    def __init__(self, name: str, level: str):
        '''
        name, 需要打印信息的模块名称
        level, "info"/"warning"/ "debug"
        '''

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        set_display_level = logging.DEBUG

        self.console = logging.StreamHandler()
        self.console.setLevel(level=set_display_level)
        self.console.setFormatter(formatter)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level=set_display_level)
        self.logger.addHandler(self.console)
        self.level = level

        self.levelname_dict = {
            "debug": self.logger.debug,
            "info": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error,
            "critical": self.logger.critical,
        }

    def write_log(self, msg: str):
        self.levelname_dict[self.level](msg)
        # self.logger.removeHandler(self.console)


if __name__ == '__main__':
    # LogModule(name="tttt", level="info").write_log("haha")
    ll = LogModule(name="ttttee", level="debug")
    ll.write_log("sadfdasfds")
