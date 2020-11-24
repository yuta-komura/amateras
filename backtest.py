import sys
import time
import traceback

import pandas as pd

from lib import repository


def get_historical_price() -> pd.DataFrame or None:
    try:
        i_from = backtest_no - 1
        i_to = i_from + CHANNEL_BAR_NUM + 1
        if i_to >= len(bitflyer_btc_ohlc):
            print("backtest finish")
            sys.exit()
        historical_price = \
            bitflyer_btc_ohlc[i_from:i_to].reset_index(drop=True)
        assert len(historical_price) == CHANNEL_BAR_NUM + 1, \
            "not len(historical_price) == CHANNEL_BAR_NUM + 1"
        return historical_price
    except Exception:
        print(traceback.format_exc())
        time.sleep(10)
        return None


def save_entry(date, side, price):
    side = str(side)
    price = int(price)
    sql = "insert into backtest_entry values('{date}','{side}',{price},0)" \
        .format(date=date, side=side, price=price)
    repository.execute(database=DATABASE, sql=sql, log=False)


TIME_FRAME = 1  # minutes
CHANNEL_WIDTH = 1
CHANNEL_BAR_NUM = TIME_FRAME * CHANNEL_WIDTH

print("TIME_FRAME", TIME_FRAME)
print("CHANNEL_WIDTH", CHANNEL_WIDTH)

DATABASE = "tradingbot"

sql = """
        select
            *
        from
            bitflyer_btc_ohlc_1S
        order by
            Date
    """
bitflyer_btc_ohlc = repository.read_sql(database=DATABASE, sql=sql)

print(bitflyer_btc_ohlc)

sql = "truncate backtest_entry"
repository.execute(database=DATABASE, sql=sql, log=False)

backtest_no = 1
has_buy_side = False
has_sell_side = False
while True:
    historical_price = get_historical_price()
    if historical_price is None:
        continue

    channel = historical_price[:-1]
    high_line = channel["High"].max()
    low_line = channel["Low"].min()

    i = len(historical_price) - 1
    latest = historical_price.iloc[i]
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
        save_entry(date=Date, side="CLOSE", price=Close)
        print("invalid trading")
    else:
        order_buy = break_high_line and not has_buy_side
        order_sell = break_low_line and not has_sell_side

        if order_buy:
            save_entry(date=Date, side="BUY", price=high_line)
            has_buy_side = True
            has_sell_side = False

        if order_sell:
            save_entry(date=Date, side="SELL", price=low_line)
            has_buy_side = False
            has_sell_side = True

    backtest_no += 1
