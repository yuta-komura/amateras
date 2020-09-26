import matplotlib.pyplot as plt

from lib import math, repository

asset = 300000

# k = 0.01 許容値
k = 0.06
# --------------------------------------- #

fee = k / 100


sql = """
        select
            *
        from
            backtest_entry
        order by
            date
        """
backtest_entry = repository.read_sql(database="tradingbot", sql=sql)

start_time = backtest_entry.loc[0]["date"]
finish_time = backtest_entry.loc[len(backtest_entry) - 1]["date"]

profits = []
asset_flow = []
downs = []
downs_list = []
wait_cnt_down = -1
for i in range(len(backtest_entry)):
    past_position = backtest_entry.iloc[i - 1]

    now_position = backtest_entry.iloc[i]

    if past_position["side"] == "BUY" and (
            now_position["side"] == "SELL" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["price"]
        profit = ((amount * now_position["price"]) - asset)
        profit -= (asset * fee)

        if profit <= 0:
            downs.append(profit)
        else:
            downs_list.append(sum(downs))
            downs = []
        profits.append(profit)
        asset += profit
        asset_flow.append(asset)

    if past_position["side"] == "SELL" and (
            now_position["side"] == "BUY" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["price"]
        profit = (asset - (amount * now_position["price"]))
        profit -= (asset * fee)

        if profit <= 0:
            downs.append(profit)
        else:
            downs_list.append(sum(downs))
            downs = []
        profits.append(profit)
        asset += profit
        asset_flow.append(asset)

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
print("backtest result")
print(str(start_time).split(".")[0], "〜", str(finish_time).split(".")[0])
print("asset", math.round_down(asset, 0))
print("profit", int(sum(profits)))
if pf:
    print("pf", math.round_down(pf, -2))
if wp:
    print("wp", math.round_down(wp, 0), "%")
print("trade_cnt", len(profits))
if downs_list:
    print("draw_down", int(min(downs_list)))

fig = plt.figure(figsize=(48, 24), dpi=50)
ax1 = fig.add_subplot(1, 1, 1)
ax1.plot(list(range(len(asset_flow))), asset_flow)
plt.show()
