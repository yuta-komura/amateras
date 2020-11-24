import time
import traceback
from enum import Enum

import pybitflyer

from lib import math, message, repository


class API:

    def __init__(self, api_key, api_secret):
        self.api = pybitflyer.API(api_key=api_key, api_secret=api_secret)
        self.PRODUCT_CODE = "FX_BTC_JPY"
        self.LEVERAGE = 2
        self.DATABASE = "tradingbot"

    def order(self, side):
        message.info(side, "order start")
        while True:
            try:
                self.api.cancelallchildorders(
                    product_code=self.PRODUCT_CODE)

                position = self.__get_position()

                has_position = position["side"] is not None
                should_close = has_position \
                    and (side != position["side"] and position["size"] >= 0.01)
                if should_close:
                    self.close()
                    continue

                price = self.__get_order_price(side=side)

                size = self.__get_order_size(
                    price=price, position_size=position["size"])

                has_completed_order = size < 0.01 \
                    or self.__has_changed_side(side=side)
                if has_completed_order:
                    message.info(side, "order complete")
                    order_side = side
                    order_size = \
                        self.__get_order_size(price=price, position_size=0)
                    order_size = float(math.round_down(order_size, -2))
                    return order_side, order_size

                assert self.is_valid_side(side=side)
                assert self.is_valid_size(size=size)
                assert self.is_valid_price(price=price)

                self.__send_order(side=side, size=size, price=price)
                time.sleep(1)
            except Exception:
                message.error(traceback.format_exc())
                time.sleep(3)

    def close(self):
        message.info("close start")
        has_position = False
        while True:
            try:
                self.api.cancelallchildorders(
                    product_code=self.PRODUCT_CODE)

                position = self.__get_position()

                has_completed_close = \
                    position["side"] is None or position["size"] < 0.01
                if has_completed_close:
                    message.info("close complete")
                    return has_position
                else:
                    has_position = True

                side = self.__reverse_side(side=position["side"])
                size = position["size"]
                price = self.__get_order_price(side=side)

                assert self.is_valid_side(side=side)
                assert self.is_valid_size(size=size)
                assert self.is_valid_price(price=price)

                self.__send_order(side=side, size=size, price=price)
                time.sleep(1)
            except Exception:
                message.error(traceback.format_exc())
                time.sleep(3)

    def position_validation(self, order_side, order_size):
        while True:
            try:
                time.sleep(120)

                if self.__has_changed_side(side=order_side):
                    return

                position = self.__get_position()
                position_side = position["side"]
                position_size = position["size"]

                if position_side is None \
                        or order_side != position_side:
                    message.warning("invalidate position")
                    self.order(order_side)
                elif order_size * 0.5 >= position_size:
                    message.warning("not enough position size")
                    self.order(order_side)
                elif order_size * 1.5 <= position_size:
                    message.warning("close invalidate position size")
                    side = self.__reverse_side(side=order_side)
                    size = position_size - order_size
                    price = self.__get_order_price(side=side)

                    assert self.is_valid_side(side=side)
                    assert self.is_valid_size(size=size)
                    assert self.is_valid_price(price=price)

                    self.__send_order(side=side, size=size, price=price)
                else:
                    return
            except Exception:
                message.error(traceback.format_exc())
                time.sleep(3)

    def __reverse_side(self, side):
        if side == "BUY":
            return "SELL"
        if side == "SELL":
            return "BUY"

    def __has_changed_side(self, side):
        try:
            sql = "select * from entry"
            entry = \
                repository.read_sql(database=self.DATABASE, sql=sql)
            if entry.empty:
                message.warning("entry empty")
                return True
            latest_side = entry.at[0, "side"]
            if latest_side != side:
                message.warning("change side from", side, "to", latest_side)
                return True
            else:
                return False
        except Exception:
            message.error(traceback.format_exc())

    def __send_order(self, side, size, price, minute_to_expire=1):
        try:
            side, size, price = \
                self.__order_normalize(side=side, size=size, price=price)

            self.api.sendchildorder(
                product_code=self.PRODUCT_CODE,
                child_order_type="LIMIT",
                side=side,
                size=size,
                price=price,
                minute_to_expire=minute_to_expire,
                time_in_force="GTC"
            )

            sendchildorder_content = \
                "side={side}, size={size}, price={price}"\
                .format(side=side, size=size, price=price)
            message.info("sendchildorder", sendchildorder_content)
        except Exception:
            message.error(traceback.format_exc())
            time.sleep(3)

    @staticmethod
    def __order_normalize(side, size, price):
        side = str(side)
        size = float(math.round_down(size, -2))
        price = int(price)
        return side, size, price

    @staticmethod
    def is_valid_side(side):
        try:
            side = str(side)
            is_valid_side = \
                side == "BUY" or side == "SELL"
            if is_valid_side:
                return True
            else:
                return False
        except Exception:
            message.error(traceback.format_exc())
            message.error("side", side)
            return False

    @staticmethod
    def is_valid_size(size):
        try:
            size = float(size)
            is_valid_size = size > 0
            if is_valid_size:
                return True
            else:
                message.warnig("invalid size", "[", size, "]")
                return False
        except Exception:
            message.error(traceback.format_exc())
            message.error("size", size)
            return False

    @staticmethod
    def is_valid_price(price):
        try:
            price = int(price)
            is_valid_price = price > 0
            if is_valid_price:
                return True
            else:
                message.warnig("invalid price", "[", price, "]")
                return False
        except Exception:
            message.error(traceback.format_exc())
            message.error("price", price)
            return False

    def __get_order_size(self, price, position_size):
        collateral = None
        while True:
            try:
                collateral = self.api.getcollateral()

                collateral = collateral["collateral"]
                valid_size = (collateral * self.LEVERAGE) / price
                size = (valid_size - position_size) - 0.01
                return size
            except Exception:
                message.error(traceback.format_exc())
                message.error("collateral", collateral)
                time.sleep(3)

    def __get_order_price(self, side):
        while True:
            try:
                ticker = self.__ticker()
                """
                order book

                        0.03807971 1233300
                        0.13777962 1233297
                        0.10000000 1233288 ticker["best_ask"]
                ticker["best_bid"] 1233218 0.05000000
                                   1233205 0.07458008
                                   1233201 0.02000000

                sell order price -> ticker["best_ask"] - 1 : 1233287
                buy  order price -> ticker["best_bid"] + 1 : 1233219
                """

                if side == "SELL":
                    return int(ticker["best_ask"] - 1)
                if side == "BUY":
                    return int(ticker["best_bid"] + 1)
            except Exception:
                message.error(traceback.format_exc())

    def __get_position(self):
        positions = None
        while True:
            try:
                position_side = None
                position_size = 0
                position = {"side": position_side,
                            "size": position_size
                            }

                positions = \
                    self.api.getpositions(product_code=self.PRODUCT_CODE)

                for i in range(len(positions)):
                    if i == 0:
                        assert self.is_valid_side(side=positions[i]["side"])
                        position_side = positions[i]["side"]

                    assert self.is_valid_size(size=positions[i]["size"])
                    position_size += positions[i]["size"]

                if position_side is None:
                    return position

                position = {"side": position_side,
                            "size": position_size
                            }
                return position
            except Exception:
                message.error(traceback.format_exc())
                message.error("positions", positions)
                time.sleep(3)

    def can_trading(self):
        boardstate = None
        try:
            boardstate = self.api.getboardstate(
                product_code=self.PRODUCT_CODE)

            health = boardstate["health"]

            class IsHealth(Enum):
                NORMAL = "NORMAL"
                BUSY = "BUSY"
                VERY_BUSY = "VERY BUSY"
                SUPER_BUSY = "SUPER BUSY"

            is_health = False
            for i in IsHealth:
                if i.value == health:
                    is_health = True
                    break
                else:
                    is_health = False

            state = boardstate["state"]
            is_rubning = state == "RUNNING"

            if is_health and is_rubning:
                return True
            else:
                return False
        except Exception:
            message.error(traceback.format_exc())
            message.error("boardstate", boardstate)
            time.sleep(3)
            return False

    def get_historical_price(self, limit):
        sql = """
                select
                    cast(Time as datetime) as Date,
                    Open,
                    High,
                    Low,
                    Close
                from
                    (
                        select
                            date_format(
                                cast(op.date as datetime),
                                '%Y-%m-%d %H:%i:00'
                            ) as Time,
                            op.price as Open,
                            ba.High as High,
                            ba.Low as Low,
                            cl.price as Close
                        from
                            (
                                select
                                    max(price) as High,
                                    min(price) as Low,
                                    min(id) as open_id,
                                    max(id) as close_id
                                from
                                    execution_history
                                group by
                                    year(date),
                                    month(date),
                                    day(date),
                                    hour(date),
                                    minute(date)
                                order by
                                    max(date) desc
                                limit
                                    {limit}
                            ) ba
                            inner join execution_history op on op.id = ba.open_id
                            inner join execution_history cl on cl.id = ba.close_id
                    ) as ohlc
                order by
                    Time
            """.format(limit=limit)

        historical_price = repository.read_sql(database=self.DATABASE, sql=sql)
        first_Date = historical_price.loc[0]["Date"]
        sql = "delete from execution_history where date < '{first_Date}'"\
            .format(first_Date=first_Date)
        repository.execute(database=self.DATABASE, sql=sql, write=False)
        return historical_price

    def __ticker(self):
        while True:
            try:
                sql = "select * from ticker"
                ticker = repository.read_sql(database=self.DATABASE, sql=sql)
                if not ticker.empty:
                    best_ask = ticker.at[0, "best_ask"]
                    best_bid = ticker.at[0, "best_bid"]
                    return {"best_ask": best_ask, "best_bid": best_bid}
            except Exception:
                message.error(traceback.format_exc())

    def get_profit(self) -> int:
        while True:
            try:
                return int(self.api.getcollateral()["open_position_pnl"])
            except Exception:
                message.error(traceback.format_exc())
                time.sleep(3)
