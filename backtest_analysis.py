import matplotlib.pyplot as plt

from lib import math, repository

asset = 1000000

sql = """
        select
            *
        from
            backtest_entry
        order by
            date
        """
be = repository.read_sql(database="tradingbot", sql=sql)

start_time = be.loc[0]["date"]
finish_time = be.loc[len(be) - 1]["date"]

profits = []
for i in range(len(be)):
    if i == 0:
        continue

    entry_position = be.iloc[i - 1]
    close_position = be.iloc[i]

    if entry_position["side"] == "BUY" and (
            close_position["side"] == "SELL" or close_position["side"] == "CLOSE"):

        amount = asset / entry_position["price"]
        profit = (amount * close_position["price"]) - asset

        profits.append(profit)
        asset += profit

    if entry_position["side"] == "SELL" and (
            close_position["side"] == "BUY" or close_position["side"] == "CLOSE"):

        amount = asset / entry_position["price"]
        profit = asset - (amount * close_position["price"])

        profits.append(profit)
        asset += profit

wins = []
loses = []
for i in range(len(profits)):
    if profits[i] > 0:
        wins.append(profits[i])
    elif profits[i] < 0:
        loses.append(profits[i])

pf = None
if sum(loses) != 0:
    pf = abs(sum(wins) / sum(loses))
wp = None
if len(wins) + len(loses) != 0:
    wp = len(wins) / (len(wins) + len(loses)) * 100


horizontal_line = "-------------------------------------------------"
print(horizontal_line)
print(str(start_time).split(".")[0], "〜", str(finish_time).split(".")[0])
print("profit", int(sum(profits)))
if pf:
    print("pf", math.round_down(pf, -2))
if wp:
    print("wp", math.round_down(wp, 0), "%")
print("trading cnt", len(profits))

ps = []
p = 0
for i in range(len(profits)):
    ps.append(p)
    p += profits[i]

fig = plt.figure(figsize=(48, 24), dpi=50)
ax1 = fig.add_subplot(1, 1, 1)
ax1.plot(list(range(len(ps))), ps)
plt.show()
