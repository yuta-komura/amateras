import pybitflyer

from lib import repository, stdout, message
from lib.config import Bitflyer
from lib.exception import ConfigException


def config_test():
    sql = "select * from entry limit 1"
    repository.read_sql(database=DATABASE, sql=sql)

    api = pybitflyer.API(
        api_key=Bitflyer.Api.value.KEY.value,
        api_secret=Bitflyer.Api.value.SECRET.value)
    balance = api.getbalance()
    if "error_message" in balance:
        raise ConfigException()


def truncate_table():
    sql = "truncate entry"
    repository.execute(database=DATABASE, sql=sql)

    sql = "truncate position"
    repository.execute(database=DATABASE, sql=sql)


if __name__ == "__main__":
    DATABASE = "tradingbot"

    stdout.amateras()
    print("tradingbot AMATERAS start !!")

    message.info("initialize start")

    config_test()
    truncate_table()

    message.info("initialize complete")
