# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/19 22:09
# @Author   : Fangyang
# @Software : PyCharm

from vnpy_ctp_gateway import VnpyCtpGateway


def main():
    '''
    主程序主要功能是从 ctp_gateway 更新 market_code_info.json 文件
    vnpy 的 main_engine 在事件监听, 所以需要手动停止程序运行
    '''
    vnpy_ctp = VnpyCtpGateway()
    vnpy_ctp.update_local_json_contracts_info_by_ctp_gateway()


if __name__ == '__main__':
    main()
