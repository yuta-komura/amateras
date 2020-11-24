import datetime
import time
import traceback

import pandas as pd

from lib import bitflyer, message, repository
from lib.config import Bitflyer, HistoricalPrice


def get_historical_price() -> pd.DataFrame or None:
    try:
        limit = CHANNEL_BAR_NUM + 1
        historical_price = bitflyer.get_historical_price(limit=limit)
        if len(historical_price) != limit:
            return None
        return historical_price
    except Exception:
        message.error(traceback.format_exc())
        return None


def save_entry(side):
    message.info(side, "entry")
    sql = "update entry set side='{side}'".format(side=side)
    repository.execute(database=DATABASE, sql=sql, write=False)


TIME_FRAME = HistoricalPrice.TIME_FRAME.value
CHANNEL_WIDTH = HistoricalPrice.CHANNEL_WIDTH.value
CHANNEL_BAR_NUM = TIME_FRAME * CHANNEL_WIDTH

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)

DATABASE = "tradingbot"

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
        candlestick_Minute = Date.minute
        while True:
            minute = \
                datetime.datetime.now().minute
            if candlestick_Minute != minute:
                break
            time.sleep(1)

        message.info("invalid trading")
        save_entry(side="CLOSE")
        continue
    else:
        entry_buy = break_high_line and not has_buy
        entry_sell = break_low_line and not has_sell

        if entry_buy:
            save_entry(side="BUY")
            has_buy = True
            has_sell = False

        if entry_sell:
            save_entry(side="SELL")
            has_buy = False
            has_sell = True
