import datetime
import time
import traceback

import pandas as pd

from lib import bitflyer, message, repository
from lib.config import AssetManagement, Bitflyer, Virtual


def get_historical_price() -> pd.DataFrame or None:
    try:
        limit = CHANNEL_BAR_NUM + 1
        historical_price = bitflyer.get_historical_price(limit=limit)
        first_Time = int(historical_price.loc[0]["Time"])
        first_date = datetime.datetime.fromtimestamp(first_Time)
        sql = "delete from execution_history where date < '{first_date}'"\
            .format(first_date=first_date)
        repository.execute(database=DATABASE, sql=sql, write=False)
        return historical_price
    except Exception:
        message.error(traceback.format_exc())
        return None


def save_entry(side, price):
    message.info(side, "entry")
    sql = "delete from entry"
    repository.execute(database=DATABASE, sql=sql, write=False)
    sql = "insert into entry values(null,now(6),'{side}',{price})" \
        .format(side=side, price=price)
    repository.execute(database=DATABASE, sql=sql, write=False)


TIME_FRAME = Virtual.Trade.value.TIME_FRAME.value
CHANNEL_WIDTH = Virtual.Trade.value.CHANNEL_WIDTH.value
CHANNEL_BAR_NUM = TIME_FRAME * CHANNEL_WIDTH

EXECUTE_TIME = AssetManagement.EXECUTE_TIME.value

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)

DATABASE = "tradingbot"

sql = "select * from asset_management"
asset_management = repository.read_sql(database=DATABASE, sql=sql)
plan_date = asset_management.at[0, "plan_date"]

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

    latest_High = latest["High"]
    latest_Low = latest["Low"]
    latest_Close = latest["Close"]

    now = datetime.datetime.now()
    if now.day == plan_date.day and now.hour >= EXECUTE_TIME:
        message.info("enty pause")
        save_entry(side="CLOSE", price=latest_Close)
        tomorrow = now + datetime.timedelta(days=1)
        while True:
            sql = "select * from asset_management"
            asset_management = repository.read_sql(database=DATABASE, sql=sql)
            plan_date = asset_management.at[0, "plan_date"]
            if plan_date.day == tomorrow.day:
                break
            else:
                time.sleep(1)
        message.info("enty start")
        continue

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
        l_minute = datetime.datetime.fromtimestamp(latest_Time).minute
        while True:
            minute = \
                datetime.datetime.now().minute
            if l_minute != minute:
                break
            time.sleep(1)

        save_entry(side="CLOSE", price=latest_Close)
        message.info("invalid trading")
        continue

    order_buy = break_high_line and not has_buy_side
    order_sell = break_low_line and has_buy_side

    if order_buy:
        save_entry(side="BUY", price=high_line)
        has_buy_side = True

    if order_sell:
        save_entry(side="SELL", price=low_line)
        has_buy_side = False
