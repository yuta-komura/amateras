import matplotlib.pyplot as plt

from lib import math, repository

asset = 167000
lev = 4
k = 1

print(k)

surplus = asset * (2 / 3)
asset = asset * (1 / 3)
asset = asset * lev - ((asset * lev) * (1 / 10))
# --------------------------------------- #

sql = """
        select
            *
        from
            backtest_entry
        # where
            # date >= '2020-09-28 01:00:00'
        order by
            date
        """
backtest_entry = repository.read_sql(database="tradingbot", sql=sql)

start_time = backtest_entry.loc[0]["date"]
finish_time = backtest_entry.loc[len(backtest_entry) - 1]["date"]

profit_flow = []
profit_flow.append(asset)
prf = asset

downs = []
downs_list = []
daily_loses = []
daily_wins = []
loses = []
wins = []
now_date = None
init_asset = None
for i in range(len(backtest_entry)):
    if i == 0:
        continue

    past_position = backtest_entry.iloc[i - 1]

    if now_date is None:
        now_date = past_position["date"]
        init_asset = \
            (asset * 10) / (9 * lev) + surplus

    if now_date.day != past_position["date"].day:
        daily_profit = sum(daily_wins) + sum(daily_loses)
        asset = init_asset + daily_profit

        surplus = asset * (2 / 3)
        asset = asset * (1 / 3)
        asset = asset * lev - ((asset * lev) * (1 / 10))

        now_date = past_position["date"]
        init_asset = \
            (asset * 10) / (9 * lev) + surplus

        daily_wins = []
        daily_loses = []

    now_position = backtest_entry.iloc[i]

    if past_position["side"] == "BUY" and (
            now_position["side"] == "SELL" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["price"]
        profit = (amount * now_position["price"]) - asset

        if profit < 0:
            downs.append(profit)
            daily_loses.append(profit)
            loses.append(profit)
            prf += profit
            profit_flow.append(prf)

            surplus -= -profit * k

            asset -= -profit
            if surplus > 0:
                asset += -profit * k

        if profit > 0:
            downs_list.append(sum(downs))
            downs = []
            daily_wins.append(profit)
            wins.append(profit)
            prf += profit
            profit_flow.append(prf)

            asset += profit

    if past_position["side"] == "SELL" and (
            now_position["side"] == "BUY" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["price"]
        profit = asset - (amount * now_position["price"])

        if profit < 0:
            downs.append(profit)
            daily_loses.append(profit)
            loses.append(profit)
            prf += profit
            profit_flow.append(prf)

            surplus -= -profit * k

            asset -= -profit
            if surplus > 0:
                asset += -profit * k

        if profit > 0:
            downs_list.append(sum(downs))
            downs = []
            daily_wins.append(profit)
            wins.append(profit)
            prf += profit
            profit_flow.append(prf)

            asset += profit

pf = None
if sum(loses) != 0:
    pf = sum(wins) / -sum(loses)
wp = None
if len(wins) + len(loses) != 0:
    wp = len(wins) / (len(loses) + len(loses)) * 100

horizontal_line = "-------------------------------------------------"
print(horizontal_line)
print("backtest result")
print(str(start_time).split(".")[0], "〜", str(finish_time).split(".")[0])
print("profit", int(sum(wins) + sum(loses)))
if pf:
    print("pf", math.round_down(pf, -2))
if wp:
    print("wp", math.round_down(wp, 0), "%")
print("trade_cnt", len(profit_flow))
if downs_list:
    print("draw_down", int(min(downs_list)))

fig = plt.figure(figsize=(48, 24), dpi=50)
ax1 = fig.add_subplot(1, 1, 1)
ax1.plot(list(range(len(profit_flow))), profit_flow)
plt.show()
