import pybitflyer

from lib import repository, stdout
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


def execute():
    config_test()
    stdout.amateras()
    print("tradingbot AMATERAS start !!")

    truncate_table()


if __name__ == "__main__":
    DATABASE = "tradingbot"
    execute()
