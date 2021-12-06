#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   15/05/2020 22:19
@Author   :   Fangyang
"""
from datetime import datetime, date
from enum import Enum
import numpy as np

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.setting import get_settings
from vnpy.trader.utility import load_json, save_json

from jnpy.app.cta_backtester import BacktesterEngineJnpy
from jnpy.app.pd_db_operator.db_operation import DBOperation
from jnpy.datasource.jotdx.contracts import read_contracts_json_dict
from jnpy.datasource.pyccxt.contracts import Exchange
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
    dbbardata_groupby_df = db_instance.get_groupby_data_from_db()
    return dbbardata_groupby_df['exchange'].drop_duplicates().to_list()


def onExchangeActivated(current_exchange):
    '''
    exchange变化触发, 返回db中相应 symbol list
    '''

    dbbardata_groupby_df = db_instance.get_groupby_data_from_db()

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

    dbbardata_groupby_df = db_instance.get_groupby_data_from_db()

    period_array = dbbardata_groupby_df[
        (dbbardata_groupby_df['symbol'] == current_symbol)
        & (dbbardata_groupby_df['exchange'] == current_exchange)
        ]['interval'].to_list()

    return period_array, symbol_name


def onIntervalActivated(current_symbol, current_exchange, current_interval):
    '''
    Period 变化触发, 重置 Period
    '''

    dbbardata_groupby_df = db_instance.get_groupby_data_from_db()

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
        statistic_table_dict = get_statistic_result_dict()
        balance_curve_dict = get_balance_curve_dict()
        drawdown_curve_dict = get_drawdown_curve_dict()
        pnl_bar_dict = get_pnl_bar_dict()
        distribution_curve_dict = get_distribution_curve_dict()
        daily_table_dict = get_backtesting_record_data(record_type="daily")
        trade_table_dict = get_backtesting_record_data(record_type="trade")
        order_table_dict = get_backtesting_record_data(record_type="order")
        kline_dict = get_kline_dict()
        re_data_dict = {
            "statistics": statistic_table_dict,
            "balance": balance_curve_dict,
            "drawdown": drawdown_curve_dict,
            "pnl": pnl_bar_dict,
            "pnl_dist": distribution_curve_dict,
            "kline": kline_dict,
            "daily": daily_table_dict,
            "trade": trade_table_dict,
            "order": order_table_dict,
        }
    else:
        re_data_dict["backtest_result"] = "Backtest Error !"
    return re_data_dict


def get_statistic_result_dict():
    """获取 回测统计结果 表数据"""
    statistic_result_dict = {}
    data = backtester.get_result_statistics()

    if data:
        data = set_data_to_str(data)
        for k, v in data.items():
            if k in BACKTEST_STATISTICS_RESULT_MAP:
                statistic_result_dict[BACKTEST_STATISTICS_RESULT_MAP[k]] = v
            else:
                statistic_result_dict[k] = v
    else:
        statistic_result_dict = {value: "" for value in BACKTEST_STATISTICS_RESULT_MAP.values()}

    return statistic_result_dict


def set_data_to_str(data: dict):
    """对 统计结果表数据 做保留小数等处理"""
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


def get_balance_curve_dict():
    """获取 账户净值 图数据"""
    df = backtester.get_result_df()
    y = df["balance"].tolist()
    x = [f"{i}" for i in df.index]
    return {
        'data': {"x": x, "y": y}
    }


def get_drawdown_curve_dict():
    """获取 净值回撤 图数据"""
    df = backtester.get_result_df()
    y = df["drawdown"].tolist()
    # x = [f"{i}" for i in df.index]
    return {
        # 'data': {"x": x, "y": y}
        'data': {"y": y}
    }


def get_pnl_bar_dict():
    df = backtester.get_result_df()
    y = df["net_pnl"].tolist()
    return {
        'data': {"y": y}
    }


def get_distribution_curve_dict():
    df = backtester.get_result_df()
    hist, x = np.histogram(df["net_pnl"], bins="auto")
    return {
        'data': {"x": x[:-1].tolist(), "y": hist.tolist()}
    }


def get_kline_dict():
    BarData_list = backtester.get_history_data()
    return {
        "ohlc": [
            [int(i.datetime.timestamp()) * 1000, i.open_price, i.high_price, i.low_price, i.close_price] for i in
            BarData_list
        ],
        "volume": [[int(i.datetime.timestamp()) * 1000, i.volume] for i in BarData_list]
    }


def get_backtesting_record_data(record_type):
    """获取 成交记录表 数据"""
    if record_type == "trade":
        data_list = backtester.get_all_trades()
        headers = [
            {
                "text": "成交号",
                "align": "start",
                "value": "tradeid"
            },
            {"text": "委托号", "value": "orderid"},
            {"text": "代码", "value": "symbol"},
            {"text": "交易所", "value": "exchange"},
            {"text": "方向", "value": "direction"},
            {"text": "开平", "value": "offset"},
            {"text": "价格", "value": "price"},
            {"text": "数量", "value": "volume"},
            {"text": "时间", "value": "datetime"},
            {"text": "接口", "value": "gateway_name"},
        ]
    elif record_type == "order":
        data_list = backtester.get_all_orders()
        headers = [
            {
                "text": "委托号",
                "align": "start",
                "value": "orderid"
            },
            {"text": "代码", "value": "symbol"},
            {"text": "交易所", "value": "exchange"},
            {"text": "类型", "value": "type"},
            {"text": "方向", "value": "direction"},
            {"text": "开平", "value": "offset"},
            {"text": "价格", "value": "price"},
            {"text": "总数量", "value": "volume"},
            {"text": "已成交", "value": "status"},
            {"text": "时间", "value": "datetime"},
            {"text": "接口", "value": "gateway_name"},
        ]
    elif record_type == "daily":
        data_list = backtester.get_all_daily_results()
        headers = [
            {"text": "日期", "value": "date"},
            {"text": "成交笔数", "value": "trade_count"},
            {"text": "开盘持仓", "value": "start_pos"},
            {"text": "收盘持仓", "value": "end_pos"},
            {"text": "成交额", "value": "turnover"},
            {"text": "手续费", "value": "commission"},
            {"text": "滑点", "value": "slippage"},
            {"text": "交易盈亏", "value": "trading_pnl"},
            {"text": "持仓盈亏", "value": "holding_pnl"},
            {"text": "总盈亏", "value": "total_pnl"},
            {"text": "净盈亏", "value": "net_pnl"},
        ]

    content = []
    for elem in data_list:
        item = {}
        for header in headers:
            value = getattr(elem, header['value'])
            if isinstance(value, Enum):
                item[header['value']] = value.value
            elif isinstance(value, datetime) or isinstance(value, date):
                item[header['value']] = str(value)
            else:
                item[header['value']] = value
        content.append(item)

    return {
        "headers": headers,
        "content": content
    }


if __name__ == "__main__":
    dd = Interval["MINUTE_5"]
    print(1)
