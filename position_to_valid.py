import traceback

from lib import bitflyer, message, repository
from lib.config import Bitflyer

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)

DATABASE = "tradingbot"
latest_side = ""
while True:
    try:
        sql = "select * from position"
        position = repository.read_sql(database=DATABASE, sql=sql)
        if position.empty:
            continue
        side = position.at[0, "side"]
        size = position.at[0, "size"]
    except Exception:
        message.error(traceback.format_exc())
        continue

    if not latest_side \
            or latest_side != side:
        bitflyer.invalidate_position_close(order_side=side, order_size=size)
        latest_side = side
