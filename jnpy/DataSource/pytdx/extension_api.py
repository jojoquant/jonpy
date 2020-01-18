# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/15 0:25
# @Author   : Fangyang
# @Software : PyCharm


import time
import pandas as pd
from logging import INFO

from pytdx.exhq import TdxExHq_API
from ips import IPsSource
from log import LogModule
from constant import KBarType

from vnpy.gateway.ctp.ctp_gateway import CtpGateway
from vnpy.trader.utility import load_json
from vnpy.trader.engine import MainEngine
from vnpy.trader.setting import SETTINGS


class ExhqAPI(TdxExHq_API):

    def __init__(self):
        super(ExhqAPI, self).__init__()
        self.info_log = LogModule(name="ExhqAPI_info", level="info")
        self.err_log = LogModule(name="ExhqAPI_error", level="error")

    def update_contracts_info_by_ctp_gateway(self, timeout=5):

        # 和交易系统连接成功将有log信息在控制台打印
        SETTINGS["log.active"] = True
        SETTINGS["log.level"] = INFO
        SETTINGS["log.console"] = True

        setting = load_json("connect_ctp.json")
        main_engine = MainEngine()
        main_engine.add_gateway(CtpGateway)
        main_engine.connect(setting, "CTP")

        for i in range(timeout):
            time.sleep(1)  # 等待在队列中的event查询交易所信息返回
            oms_engine = main_engine.get_engine("oms")
            contracts_dict = oms_engine.contracts
            if contracts_dict:
                #TODO parse contracts
                self.info_log.write_log(f"{i + 1}/{timeout} 成功从交易所获取 {len(contracts_dict)} 条contracts信息")
                break
            else:
                # main_engine.write_log(msg=f"{i+1}/{timeout} 从交易所获取contracts信息失败")
                # print(f"{i+1}/{timeout} 从交易所获取contracts信息失败")
                self.err_log.write_log(f"{i+1}/{timeout} 从交易所获取contracts信息失败")
                continue
        print(1)


    def get_all_KBars_df(self,
                         category=KBarType.KLINE_TYPE_DAILY.value,
                         market=30, code="FU2006") -> pd.DataFrame:  # 29 LL8  FUL8 主链
        '''
        category=KBarType.KLINE_TYPE_DAILY.value

        market 信息可以通过 data_df = ex_api.to_df(ex_api.get_markets()) 获得

        '''
        result_df = pd.DataFrame()
        start = 0

        while True:
            df = ex_api.to_df(
                ex_api.get_instrument_bars(
                    category=category,
                    market=market, code=code, start=start, count=500
                )
            )
            if df.shape[0] == 0:
                break
            result_df = result_df.append(df)
            start += 500

        if result_df.shape[0] == 0:
            self.info_log(f"{code} 数据条数为 0 !")
            return result_df

        select_columns_list = ["open", "high", "low", "close", "position", "trade", "datetime"]
        result_df = result_df[select_columns_list]

        result_df['datetime'] = pd.to_datetime(result_df['datetime'])
        result_df.sort_values(by='datetime', inplace=True)
        result_df.reset_index(drop=True, inplace=True)
        return result_df


if __name__ == '__main__':
    ip, port = IPsSource().get_fast_exhq_ip()
    # ex_api = TdxExHq_API()
    ex_api = ExhqAPI()
    with ex_api.connect(ip, port):
        data_df = ex_api.to_df(ex_api.get_markets())

        # total_data_df = pd.DataFrame()
        # instrument_count = ex_api.get_instrument_count()
        # for i in range(0, instrument_count, 500):
        #     print(f"{i}/{instrument_count}")
        #     data_df_slice = ex_api.to_df(ex_api.get_instrument_info(0, i+500))
        #     total_data_df = total_data_df.append(data_df_slice)
        # total_data_df.reset_index(inplace=True, drop=True)

        # data_df.to_csv("markets_info.csv", index=False)
        # total_data_df.to_csv("instrument_info.csv", index=False)
        # dd = ex_api.to_df(ex_api.get_history_minute_time_data(29, "LL8", 20200110))

        # start=0 代表现在, 700 代表距现在700个k bar前为start, 然后count
        # count最大700
        # dc = ex_api.to_df(ex_api.get_instrument_bars(TDXParams.KLINE_TYPE_DAILY, 29, "LL8", start=100, count=1000))
        # dc1 = ex_api.to_df(
        #     ex_api.get_instrument_bars(KBarType.KLINE_TYPE_DAILY.value, 29, "LL8", start=100, count=1000))

        ex_api.update_contracts_info_by_ctp_gateway()
        df = ex_api.get_all_KBars_df(category=KBarType.KLINE_TYPE_1HOUR.value)
        print(1)
