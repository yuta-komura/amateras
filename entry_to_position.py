import traceback

from lib import bitflyer, message, repository
from lib.config import Bitflyer

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)

DATABASE = "tradingbot"
latest_side = ""
while True:
    try:
        sql = "select * from entry order by date desc limit 1"
        entry = repository.read_sql(database=DATABASE, sql=sql)
        if entry.empty:
            continue
        side = entry.at[0, "side"]
    except Exception:
        message.error(traceback.format_exc())
        continue

    if not latest_side \
            or latest_side != side:
        bitflyer.close()
        if side != "CLOSE":
            bitflyer.order(side=side)
        latest_side = side
