import matplotlib.pyplot as plt

from lib import repository

database = "tradingbot"

sql = """
        select
            *
        from
            backtest_entry
        order by
            date
        """
be = repository.read_sql(database=database, sql=sql)
