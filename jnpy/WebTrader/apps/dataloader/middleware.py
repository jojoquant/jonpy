#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   15/05/2020 22:19
@Author   :   Fangyang
"""

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Interval, Exchange
from vnpy.app.pytdx_loader.engine import PytdxLoaderEngine

event_engine = EventEngine()
main_engine = MainEngine(event_engine)
datalaoder = PytdxLoaderEngine(main_engine, event_engine)


def load_data(handler, data_dict):
    symbol_code_list = [symbol.split(".")[0] for symbol in data_dict['symbols_selected']]
    symbol_type = data_dict['type']
    exchange = data_dict['exchange_selected']
    interval_list = [period for period in data_dict['periods_selected']]
    datetime_head = "Datetime"
    open_head = "Open"
    low_head = "Low"
    high_head = "High"
    close_head = "Close"
    volume_head = "Volume"
    open_interest_head = "OpenInterest"
    datetime_format = data_dict['time_format']

    # to_db / to_csv
    click_button_text = data_dict['export_to_selected']

    progress_bar_dict = {"web_progress": handler}

    for symbol_code in symbol_code_list:
        for interval in interval_list:
            symbol = symbol_code + symbol_type
            start, end, count = datalaoder.load(
                symbol,
                Exchange[exchange],
                Interval[interval],
                datetime_head,
                open_head,
                high_head,
                low_head,
                close_head,
                volume_head,
                open_interest_head,
                datetime_format,
                progress_bar_dict=progress_bar_dict,
                opt_str=click_button_text
            )

            msg = f"\
                    执行成功\n\
                    代码：{symbol}\n\
                    交易所：{Exchange[exchange].value}\n\
                    周期：{Interval[interval].value}\n\
                    起始：{start}\n\
                    结束：{end}\n\
                    总数量：{count}\n\
                    "
            handler.write_message({"save_result": msg})
    # QtWidgets.QMessageBox.information(self, "载入成功！", msg)


if __name__ == "__main__":
    dd = Interval["MINUTE_5"]
    print(1)