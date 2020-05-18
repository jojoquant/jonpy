#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   15/05/2020 22:19
@Author   :   Fangyang
"""
from datetime import datetime

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.setting import get_settings

from jnpy.app.cta_backtester import BacktesterEngineJnpy
from jnpy.app.cta_backtester.db_operation import DBOperation
from jnpy.DataSource.pytdx.contracts import read_contracts_json_dict
from jnpy.DataSource.pyccxt.contracts import Exchange

#############################################################
# BacktesterEngine
#############################################################
event_engine = EventEngine()
main_engine = MainEngine(event_engine)
backtester = BacktesterEngineJnpy(main_engine, event_engine)
backtester.init_engine()

strategy_array = backtester.get_strategy_class_names()
strategy_setting_dict = {
    strategy_class_name: backtester.get_default_setting(strategy_class_name)
    for strategy_class_name in strategy_array
}

#############################################################
# DBOperation
#############################################################
db_instance = DBOperation(get_settings("database."))
dbbardata_groupby_df = db_instance.get_groupby_data_from_sql_db()
exchange_array = dbbardata_groupby_df['exchange'].drop_duplicates().to_list()
pytdx_contracts_dict = read_contracts_json_dict()
pyccxt_exchange = Exchange()


def onExchangeActivated(current_exchange):
    '''
    exchange变化触发, 返回db中相应 symbol list
    '''
    return dbbardata_groupby_df[
        dbbardata_groupby_df['exchange'] == current_exchange
        ]['symbol'].drop_duplicates().to_list()


def onSymbolActivated(current_symbol, current_exchange):
    '''
    symbol变化触发, 重置interval QCombox
    '''

    symbol_de_L8_str = current_symbol[:-2]
    if symbol_de_L8_str in pytdx_contracts_dict:
        symbol_name = f"{pytdx_contracts_dict[symbol_de_L8_str]['name']}"
    elif current_exchange.lower() in pyccxt_exchange.exchange_list:
        symbol_name = current_symbol

    period_array = dbbardata_groupby_df[
        (dbbardata_groupby_df['symbol'] == current_symbol)
        & (dbbardata_groupby_df['exchange'] == current_exchange)
        ]['interval'].to_list()

    return period_array, symbol_name


def onIntervalActivated(current_symbol, current_exchange, current_interval):
    '''
    Period 变化触发, 重置 Period
    '''
    count_series = dbbardata_groupby_df[
        (dbbardata_groupby_df['symbol'] == current_symbol)
        & (dbbardata_groupby_df['exchange'] == current_exchange)
        & (dbbardata_groupby_df['interval'] == current_interval)
        ]['count(1)']

    if count_series.empty:
        data_nums = 0
    else:
        data_nums = int(count_series.values[0])

    if current_exchange and current_symbol and current_interval:
        symbol_de_L8_str = current_symbol[:-2]
        if symbol_de_L8_str in pytdx_contracts_dict:
            size = pytdx_contracts_dict[symbol_de_L8_str]['size']
            pricetick = pytdx_contracts_dict[symbol_de_L8_str]['pricetick']
        elif current_exchange.lower() in pyccxt_exchange.exchange_list:
            cur_exchange_market_info_dict = pyccxt_exchange.read_local_market_info_json_file(
                current_exchange.lower()
            )
            if cur_exchange_market_info_dict \
                    and (current_symbol.replace("_", "/").upper() in cur_exchange_market_info_dict):
                market_info = cur_exchange_market_info_dict[current_symbol.replace("_", "/").upper()]
                pricetick = market_info['limits']['price']['min']
            else:
                pricetick = 999
            size = 1

        # TODO 增加重置日期后统计数据数目
        # 重置日期
        db_end_dt = db_instance.get_end_date_from_db(
            symbol=current_symbol,
            exchange=current_exchange,
            interval=current_interval
        )
        # db_end_dt = datetime.strptime(db_end_dt, '%Y-%m-%d %H:%M:%S')
        db_start_dt = db_instance.get_start_date_from_db(
            symbol=current_symbol,
            exchange=current_exchange,
            interval=current_interval
        )
        # db_start_dt = datetime.strptime(db_start_dt, '%Y-%m-%d %H:%M:%S')

    return {
        'data_nums': data_nums,
        'submit_data': {
            'size': size,
            'pricetick': pricetick,
            'start_datetime': db_start_dt,
            'end_datetime': db_end_dt,
        }
    }


print(1)


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

    # for symbol_code in symbol_code_list:
    #     for interval in interval_list:
    #         symbol = symbol_code + symbol_type
    #         start, end, count = datalaoder.load(
    #             symbol,
    #             Exchange[exchange],
    #             Interval[interval],
    #             datetime_head,
    #             open_head,
    #             high_head,
    #             low_head,
    #             close_head,
    #             volume_head,
    #             open_interest_head,
    #             datetime_format,
    #             progress_bar_dict=progress_bar_dict,
    #             opt_str=click_button_text
    #         )
    #
    #         msg = f"\
    #                 执行成功\n\
    #                 代码：{symbol}\n\
    #                 交易所：{Exchange[exchange].value}\n\
    #                 周期：{Interval[interval].value}\n\
    #                 起始：{start}\n\
    #                 结束：{end}\n\
    #                 总数量：{count}\n\
    #                 "
    #         handler.write_message({"save_result": msg})
    # QtWidgets.QMessageBox.information(self, "载入成功！", msg)


if __name__ == "__main__":
    dd = Interval["MINUTE_5"]
    print(1)
