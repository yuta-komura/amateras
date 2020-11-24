import pandas as pd


def add_rsi(df: pd.DataFrame, value: int) -> pd.DataFrame:
    Price_diff_df = df["Price"].diff()

    up = Price_diff_df.copy()
    down = Price_diff_df.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    up_sum = up.rolling(value).sum()
    down_sum = down.abs().rolling(value).sum()

    df["rsi{value}".format(value=value)] = up_sum / (up_sum + down_sum) * 100
    return df


def add_sma(df: pd.DataFrame, value: int) -> pd.DataFrame:
    Price_df = df["Price"]
    df["sma{value}".format(value=value)] = Price_df.rolling(value).mean()
    return df


def add_ema(df: pd.DataFrame, value: int) -> pd.DataFrame:
    Price_df = df["Price"]
    sma = Price_df.rolling(value).mean()[:value]
    df["ema{value}".format(value=value)] = \
        pd.concat([sma, Price_df[value:]]).ewm(span=value, adjust=False).mean()
    return df
