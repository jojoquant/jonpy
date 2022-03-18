import pandas as pd


def move_sunday_night_to_friday_night(df):
    """ 处理周五夜盘时间拼接在周日晚间的问题 """

    df['dayofweek'] = df['datetime'].dt.dayofweek
    df['datetime'] = df['datetime'].mask(
        df['dayofweek'] == 6,
        df['datetime'] - pd.Timedelta(2, unit="d")
    )
    df.drop('dayofweek', inplace=True, axis=1)
    return df


def change_df_colums(df: pd.DataFrame):
    columns_map = {
        "open": "open_price",
        "high": "high_price",
        "low": "low_price",
        "close": "close_price",
        "volume": "volume"
    }

    if 'date' in df.columns:
        columns_map['date'] = "datetime"

    if "amount" in df.columns:
        columns_map["amount"] = "open_interest"
    elif "hold" in df.columns:
        columns_map['hold'] = "open_interest"

    df.rename(
        columns=columns_map,
        inplace=True
    )
    df['turnover'] = 0

    return df[[
        "symbol", "exchange", "datetime", "interval",
        "volume", "turnover", "open_interest",
        "open_price", "high_price", "low_price", "close_price"]]
