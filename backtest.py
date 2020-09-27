import datetime
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
    date = datetime.datetime.fromtimestamp(int(date))
    side = str(side)
    price = int(price)
    sql = "insert into backtest_entry values('{date}','{side}',{price})" \
        .format(date=date, side=side, price=price)
    repository.execute(database=DATABASE, sql=sql, log=False)


def entry(date, side, price):
    save_entry(date=date, side=side, price=price)


def to_entry_data(date, side, price):
    return {"date": date, "side": side, "price": price}


TIME_FRAME = 1  # minutes
CHANNEL_WIDTH = 10
CHANNEL_BAR_NUM = TIME_FRAME * CHANNEL_WIDTH

DATABASE = "tradingbot"

now = datetime.datetime.now()
after = int(
    datetime.datetime(
        2020,
        6,
        1,
        0,
        0,
        00,
        0000).timestamp())

sql = """
        select
            *
        from
            bitflyer_btc_ohlc_1M
        where
            Time >= {after}
        order by
            Time
    """.format(after=after)
bitflyer_btc_ohlc = repository.read_sql(database=DATABASE, sql=sql)

sql = "delete from backtest_entry"
repository.execute(database=DATABASE, sql=sql, log=False)

backtest_no = 1

entry_data = None

before_latest_Time = 0
change_candlestick = True
is_first_entry = True
has_buy_side = False
while True:
    historical_price = get_historical_price()
    if historical_price is None:
        continue

    channel = historical_price[:-1]
    high_line = channel["High"].max()
    low_line = channel["Low"].min()

    i = len(historical_price) - 1
    latest = historical_price.iloc[i]
    latest_Time = int(latest["Time"])

    if before_latest_Time != latest_Time:
        change_candlestick = True

    latest_High = latest["High"]
    latest_Low = latest["Low"]
    latest_Close = latest["Close"]

    break_high_line = high_line < latest_High
    break_low_line = low_line > latest_Low

    """
        invalid_trading
                             |  <- break
        high_line --------- |¯|
        low_line  --------- |_|
                             |  <- break
        天井や底で出る可能性が高い：手仕舞
    """
    invalid_trading = break_high_line and break_low_line
    if invalid_trading:
        if change_candlestick:
            entry(date=latest_Time, side="CLOSE", price=latest_Close)
            entry_data = to_entry_data(
                date=latest_Time, side="CLOSE", price=latest_Close)
            print("invalid trading")
            change_candlestick = False
    else:
        order_buy = break_high_line and not has_buy_side
        order_sell = break_low_line and has_buy_side

        if order_buy:
            if is_first_entry:
                is_first_entry = False
            else:
                entry(date=latest_Time, side="BUY", price=high_line)
                entry_data = to_entry_data(
                    date=latest_Time, side="BUY", price=high_line)
            has_buy_side = True

        if order_sell:
            if is_first_entry:
                is_first_entry = False
            else:
                entry(date=latest_Time, side="SELL", price=low_line)
                entry_data = to_entry_data(
                    date=latest_Time, side="SELL", price=low_line)
            has_buy_side = False

    before_latest_Time = latest_Time
    backtest_no += 1
