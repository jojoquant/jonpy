import pandas as pd
from jotdx.reader import Reader
from vnpy_jomongodb import Database
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import DB_TZ

Exchange_Map = {
    "28": Exchange.CZCE,
    "29": Exchange.DCE,
    "30": Exchange.SHFE,
    "47": Exchange.CFFEX,
}

TDXDIR = 'C:/new_jyplug'


def read_ext_data(file_name, interval):
    # market 参数 std 为标准市场(就是股票), ext 为扩展市场(期货，黄金等)
    # tdxdir 是通达信的数据目录, 根据自己的情况修改
    # 读取日线数据
    # df = reader.daily(symbol='600000')
    # df = reader.fzline(symbol='30#RBL8')  # 获取5分钟数据
    # df = reader.minute(symbol='30#RBL8')  # 获取1分钟数据

    reader = Reader.factory(market="ext", tdxdir=TDXDIR)

    if interval == Interval.MINUTE:
        df = reader.minute(symbol=file_name)
        df['interval'] = Interval.MINUTE.value
    elif interval == Interval.MINUTE_5:
        df = reader.fzline(symbol=file_name)
        df['interval'] = Interval.MINUTE_5.value
    elif interval == Interval.DAILY:
        df = reader.daily(symbol=file_name)
        df['interval'] = Interval.DAILY.value

    exchange_code, symbol = file_name.split("#")
    df['symbol'] = symbol
    df['exchange'] = Exchange_Map[exchange_code].value

    return change_df_colums(df)


def read_std_data(file_name, interval):
    # market 参数 std 为标准市场(就是股票), ext 为扩展市场(期货，黄金等)
    # tdxdir 是通达信的数据目录, 根据自己的情况修改
    # 读取日线数据
    # df = reader.daily(symbol='600000')
    # df = reader.fzline(symbol='30#RBL8')  # 获取5分钟数据
    # df = reader.minute(symbol='30#RBL8')  # 获取1分钟数据
    if len(file_name) != 6:
        print("股票 可转债 输入6位代码即可, 无需市场信息")
        return

    # TODO 可转债 股票 根据代码区分 exchange SSE SZSE

    reader = Reader.factory(market="std", tdxdir=TDXDIR)

    if interval == Interval.MINUTE:
        df = reader.minute(symbol=file_name)
        df['interval'] = Interval.MINUTE.value
    elif interval == Interval.MINUTE_5:
        df = reader.fzline(symbol=file_name)
        df['interval'] = Interval.MINUTE_5.value
    elif interval == Interval.DAILY:
        df = reader.daily(symbol=file_name)
        df['interval'] = Interval.DAILY.value

    df['symbol'] = file_name
    df['exchange'] = "SZSE"

    print(1)
    return change_df_colums(df)


def change_df_colums(df: pd.DataFrame):
    df = df.tz_localize(DB_TZ)  # 设置 datetime 的 tzinfo 为 DBTZ, 通过 df.tz_convert("UTC") 转为UTC时区
    df.reset_index(inplace=True)
    df.rename(
        columns={
            "date": "datetime",
            "open": "open_price",
            "high": "high_price",
            "low": "low_price",
            "close": "close_price",
            "volume": "volume",
            "amount": "open_interest"
        },
        inplace=True
    )
    df['turnover'] = 0
    return df[[
        "symbol", "exchange", "datetime", "interval",
        "volume", "turnover", "open_interest",
        "open_price", "high_price", "low_price", "close_price"]]


class Stock:
    def __init__(self):
        self.value = "stock"


if __name__ == '__main__':
    db = Database()
    interval = Interval.MINUTE_5
    symbol = "30#CUL8"
    df = read_ext_data(symbol, interval)
    # df = read_std_data(symbol, interval)
    db.delete_bar_data(symbol.split("#")[1], Exchange_Map[symbol.split("#")[0]], interval)
    # db.delete_bar_data("123028", Stock(), interval)
    db.save_bar_df(df)
