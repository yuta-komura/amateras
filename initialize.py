import pybitflyer

from lib import message, repository, stdout
from lib.config import Bitflyer
from lib.exception import ConfigException


def config_test():
    sql = "select * from entry"
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


def insert_data():
    message.info("initial entry")
    sql = "insert into entry values('CLOSE')"
    repository.execute(database=DATABASE, sql=sql, write=False)


if __name__ == "__main__":
    DATABASE = "tradingbot"

    stdout.AA()
    print("tradingbot amateras start !!")

    message.info("initialize start")

    config_test()
    truncate_table()
    insert_data()

    message.info("initialize complete")
