import requests

from lib.mysql import MySQL


def btcfxjpy():
    sql = "select Time-60 from bitflyer_btc_ohlc_1M order by Time desc limit 1"
    cur.execute(sql)
    rows = cur.fetchall()

    time_start = '0'
    for row in rows:
        time_start = row[0]
    print('time_start', time_start)

    url = "https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc"

    params = {"periods": 60,
              "after": time_start}
    response = requests.get(url, params=params)
    cryptowatch_json = response.json()["result"]["60"]

    for i in range(len(cryptowatch_json)):
        try:
            if i == 0:
                continue
            if i == len(cryptowatch_json) - 1:
                continue

            Time = cryptowatch_json[i - 1][0]
            Open = cryptowatch_json[i][1]
            High = cryptowatch_json[i][2]
            Low = cryptowatch_json[i][3]
            Close = cryptowatch_json[i][4]
            Volume = cryptowatch_json[i][5]
            sql = \
                "insert into bitflyer_btc_ohlc_1M values(%s,%s,%s,%s,%s,'%s')" % (
                    Time, Open, High, Low, Close, Volume)
            cur.execute(sql)
            print(sql)
        except Exception:
            pass

    conn.commit()


def ethjpy():
    sql = "select Time-60 from bitflyer_eth_ohlc_1M order by Time desc limit 1"
    cur.execute(sql)
    rows = cur.fetchall()

    time_start = '0'
    for row in rows:
        time_start = row[0]
    print('time_start', time_start)

    url = "https://api.cryptowat.ch/markets/bitflyer/ethjpy/ohlc"

    params = {"periods": 60,
              "after": time_start}
    response = requests.get(url, params=params)
    cryptowatch_json = response.json()["result"]["60"]

    for i in range(len(cryptowatch_json)):
        try:
            if i == 0:
                continue
            if i == len(cryptowatch_json) - 1:
                continue

            Time = cryptowatch_json[i - 1][0]
            Open = cryptowatch_json[i][1]
            High = cryptowatch_json[i][2]
            Low = cryptowatch_json[i][3]
            Close = cryptowatch_json[i][4]
            Volume = cryptowatch_json[i][5]
            sql = \
                "insert into bitflyer_eth_ohlc_1M values(%s,%s,%s,%s,%s,'%s')" % (
                    Time, Open, High, Low, Close, Volume)
            cur.execute(sql)
            print(sql)
        except Exception:
            pass

    conn.commit()
    print("mentainance finish")
    conn.close()


def create_historical_price():
    btcfxjpy()
    ethjpy()


if __name__ == "__main__":
    conn = MySQL(database="tradingbot").conn
    cur = conn.cursor()

    create_historical_price()
