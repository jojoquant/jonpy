#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   20/05/2020 21:13
@Author   :   Fangyang
"""

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

BACKTEST_STATISTICS_RESULT_MAP = {
    "start_date": "首个交易日",
    "end_date": "最后交易日",

    "total_days": "总交易日",
    "profit_days": "盈利交易日",
    "loss_days": "亏损交易日",

    "capital": "起始资金",
    "end_balance": "结束资金",

    "total_return": "总收益率",
    "annual_return": "年化收益",
    "max_drawdown": "最大回撤",
    "max_ddpercent": "百分比最大回撤",

    "total_net_pnl": "总盈亏",
    "total_commission": "总手续费",
    "total_slippage": "总滑点",
    "total_turnover": "总成交额",
    "total_trade_count": "总成交笔数",

    "daily_net_pnl": "日均盈亏",
    "daily_commission": "日均手续费",
    "daily_slippage": "日均滑点",
    "daily_turnover": "日均成交额",
    "daily_trade_count": "日均成交笔数",

    "daily_return": "日均收益率",
    "return_std": "收益标准差",
    "sharpe_ratio": "夏普比率",
    "return_drawdown_ratio": "收益回撤比"
}

CTP_CONNECT_MAP = {
    'account': '用户名',
    'password': '密码',
    'broker_id': '经纪商代码',
    'author_code': '授权编码',
    'td_address': '交易服务器',
    'md_address': '行情服务器',
    "appid": "产品名称",
    "auth_code": "授权编码",
    "product_info": "产品信息",
}

if __name__ == "__main__":
    pass
