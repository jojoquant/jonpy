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
from vnpy.trader.utility import load_json, save_json

from jnpy.app.cta_backtester import BacktesterEngineJnpy
from jnpy.app.cta_backtester.db_operation import DBOperation
from jnpy.DataSource.pytdx.contracts import read_contracts_json_dict
from jnpy.DataSource.pyccxt.contracts import Exchange
from jnpy.WebTrader.constant import DATE_FORMAT, BACKTEST_STATISTICS_RESULT_MAP

#############################################################
# BacktesterEngine
#############################################################
event_engine = EventEngine()
main_engine = MainEngine(event_engine)
backtester = BacktesterEngineJnpy(main_engine, event_engine)


# backtester.init_engine()
# strategy_array = backtester.get_strategy_class_names()
# strategy_setting_dict = {
#     strategy_class_name: backtester.get_default_setting(strategy_class_name)
#     for strategy_class_name in strategy_array
# }

def getStrategySettingDict():
    return {
        strategy_class_name: backtester.get_default_setting(strategy_class_name)
        for strategy_class_name in getStrategyArray()
    }


def getStrategyArray():
    backtester.init_engine()
    return backtester.get_strategy_class_names()


# def onStrategyActivated(current_strategy: str):
#     strategy_setting_dict = getStrategySettingDict()
#     return strategy_setting_dict[current_strategy]


#############################################################
# DBOperation
#############################################################
db_instance = DBOperation(get_settings("database."))
# dbbardata_groupby_df = db_instance.get_groupby_data_from_sql_db()
# exchange_array = dbbardata_groupby_df['exchange'].drop_duplicates().to_list()
pytdx_contracts_dict = read_contracts_json_dict()
pyccxt_exchange = Exchange()


def getExchangeArray():
    dbbardata_groupby_df = db_instance.get_groupby_data_from_sql_db()
    return dbbardata_groupby_df['exchange'].drop_duplicates().to_list()


def onExchangeActivated(current_exchange):
    '''
    exchange变化触发, 返回db中相应 symbol list
    '''

    dbbardata_groupby_df = db_instance.get_groupby_data_from_sql_db()

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
    else:
        symbol_name = current_symbol

    dbbardata_groupby_df = db_instance.get_groupby_data_from_sql_db()

    period_array = dbbardata_groupby_df[
        (dbbardata_groupby_df['symbol'] == current_symbol)
        & (dbbardata_groupby_df['exchange'] == current_exchange)
        ]['interval'].to_list()

    return period_array, symbol_name


def onIntervalActivated(current_symbol, current_exchange, current_interval):
    '''
    Period 变化触发, 重置 Period
    '''

    dbbardata_groupby_df = db_instance.get_groupby_data_from_sql_db()

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
            'start_datetime': db_start_dt.split()[0],
            'end_datetime': db_end_dt.split()[0],
        }
    }


def run_backtest(handler, submit_data_dict, strategy_setting_dict):
    """"""
    setting_filename = "cta_backtester_setting.json"

    class_name = submit_data_dict['strategy']
    vt_symbol = f"{submit_data_dict['symbol']}.{submit_data_dict['exchange']}"
    interval = submit_data_dict['period']
    start = datetime.strptime(
        submit_data_dict['start_datetime'],
        DATE_FORMAT
    ).date()
    end = datetime.strptime(
        submit_data_dict['end_datetime'],
        DATE_FORMAT
    ).date()
    rate = float(submit_data_dict['rate'])
    slippage = float(submit_data_dict['slippage'])
    size = float(submit_data_dict['size'])
    pricetick = float(submit_data_dict['pricetick'])
    capital = float(submit_data_dict['capital'])

    if submit_data_dict['inverse_mode_selected'] == "正向":
        inverse = False
    else:
        inverse = True

    # fangyang add
    if submit_data_dict['backtest_mode_selected'] == "Thread 运行回测":  # "Debug 运行回测"
        backtesting_debug_mode = False
    else:
        backtesting_debug_mode = True
    #######################

    # Save backtesting parameters
    backtesting_setting = {
        "class_name": class_name,
        "vt_symbol": vt_symbol,
        "interval": interval,
        "rate": rate,
        "slippage": slippage,
        "size": size,
        "pricetick": pricetick,
        "capital": capital,
        "inverse": inverse,
    }
    save_json(setting_filename, backtesting_setting)

    # Get strategy setting
    # old_setting = strategy_setting_dict[class_name]
    # old_setting = getStrategySettingDict()[class_name]
    # dialog = BacktestingSettingEditor(class_name, old_setting)
    # i = dialog.exec()
    # if i != dialog.Accepted:
    #     return
    # new_setting = dialog.get_setting()

    handler.multi_strategy_settings[class_name] = strategy_setting_dict

    result = backtester.start_backtesting(
        class_name,
        vt_symbol,
        interval,
        start,
        end,
        rate,
        slippage,
        size,
        pricetick,
        capital,
        inverse,
        backtesting_debug_mode,  # fangyang add
        strategy_setting_dict
    )

    re_data_dict = {}
    if result:
        statistic_result_dict = set_data_to_str(backtester.get_result_statistics())
        for k, v in statistic_result_dict.items():
            if k in BACKTEST_STATISTICS_RESULT_MAP:
                re_data_dict[BACKTEST_STATISTICS_RESULT_MAP[k]] = v
            else:
                re_data_dict[k] = v
    else:
        re_data_dict["backtest_result"] = "Backtest Error !"
    return re_data_dict
    # if result:
    #     self.statistics_monitor.clear_data()
    #     self.chart.clear_data()
    #
    #     self.trade_button.setEnabled(False)
    #     self.order_button.setEnabled(False)
    #     self.daily_button.setEnabled(False)
    #     self.candle_button.setEnabled(False)
    #
    #     self.trade_dialog.clear_data()
    #     self.order_dialog.clear_data()
    #     self.daily_dialog.clear_data()
    #     self.candle_dialog.clear_data()


def set_data_to_str(data: dict):
    """"""
    keep_2_decimal_list = [
        "capital", "end_balance", 'max_drawdown', 'total_net_pnl', 'total_commission',
        'total_slippage', 'total_turnover', 'daily_net_pnl', 'daily_commission',
        'daily_slippage', 'daily_turnover', 'sharpe_ratio', 'return_drawdown_ratio',
        'daily_trade_count'
    ]
    keep_2_percent_list = ["total_return", 'annual_return', 'max_ddpercent', 'daily_return', 'return_std']

    for k, v in data.items():
        if k in keep_2_decimal_list:
            data[k] = f"{v:,.2f}"
        elif k in keep_2_percent_list:
            data[k] = f"{v:,.2f}%"
        else:
            data[k] = f"{v}"

    return data


if __name__ == "__main__":
    dd = Interval["MINUTE_5"]
    print(1)
