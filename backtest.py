import sys

import pandas as pd

from lib import repository
from lib.config import HistoricalPrice


def get_historical_price() -> pd.DataFrame or None:
    i_from = backtest_no - 1
    i_to = i_from + CHANNEL_BAR_NUM + 1

    if i_to > len(bo):
        print("complete")
        sys.exit()

    historical_price = \
        bo[i_from:i_to].reset_index(drop=True)
    return historical_price


def save_entry(date, side, price):
    sql = "insert into backtest_entry values('{date}','{side}',{price},0)" \
        .format(date=date, side=side, price=price)
    repository.execute(database=DATABASE, sql=sql, log=False)


TIME_FRAME = HistoricalPrice.TIME_FRAME.value
CHANNEL_WIDTH = HistoricalPrice.CHANNEL_WIDTH.value
CHANNEL_BAR_NUM = TIME_FRAME * CHANNEL_WIDTH

print("TIME_FRAME", TIME_FRAME)
print("CHANNEL_WIDTH", CHANNEL_WIDTH)

DATABASE = "tradingbot"

sql = """
        select
            *
        from
            bitflyer_btc_ohlc_1M
        order by
            Date
    """
bo = repository.read_sql(database=DATABASE, sql=sql)

sql = "truncate backtest_entry"
repository.execute(database=DATABASE, sql=sql, log=False)

backtest_no = 1
has_buy = False
has_sell = False
while True:
    hp = get_historical_price()
    if hp is None:
        continue

    channel = hp[:-1]
    high_line = channel["High"].max()
    low_line = channel["Low"].min()

    i = len(hp) - 1
    latest = hp.iloc[i]
    Date = latest["Date"]

    High = latest["High"]
    Low = latest["Low"]
    Close = latest["Close"]

    break_high_line = high_line < High
    break_low_line = low_line > Low

    """
        invalid_trading
                             |  <- break
        high_line --------- |¯|
        low_line  --------- |_|
                             |  <- break
    """
    invalid_trading = break_high_line and break_low_line

    if invalid_trading:
        print("invalid trading")
        save_entry(date=Date, side="CLOSE", price=Close)
        backtest_no += 1
        continue
    else:
        entry_buy = break_high_line and not has_buy
        entry_sell = break_low_line and not has_sell

        if entry_buy:
            save_entry(date=Date, side="BUY", price=high_line)
            has_buy = True
            has_sell = False

        if entry_sell:
            save_entry(date=Date, side="SELL", price=low_line)
            has_buy = False
            has_sell = True

    backtest_no += 1
