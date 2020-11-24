import datetime as dt
import hmac
import json
import os
import signal
import time
from datetime import datetime as dtdt
from hashlib import sha256
from secrets import token_hex
from threading import Thread

import websocket

from lib import message, repository
from lib.config import Bitflyer

# -------------------------------------
key = Bitflyer.Api.value.KEY.value
secret = Bitflyer.Api.value.SECRET.value

end_point = 'wss://ws.lightstream.bitflyer.com/json-rpc'

public_channels = ['lightning_executions_FX_BTC_JPY',
                   'lightning_ticker_FX_BTC_JPY']
private_channels = []
database = "tradingbot"
# -------------------------------------


def quit_loop(signal, frame):
    os._exit(0)


class bFwebsocket(object):
    def __init__(
            self,
            end_point,
            public_channels,
            private_channels,
            key,
            secret):
        self._end_point = end_point
        self._public_channels = public_channels
        self._private_channels = private_channels
        self._key = key
        self._secret = secret
        self._JSONRPC_ID_AUTH = 1

    def startWebsocket(self):
        def on_open(ws):
            print("Websocket connected")

            if len(self._private_channels) > 0:
                auth(ws)

            if len(self._public_channels) > 0:
                params = [{'method': 'subscribe', 'params': {'channel': c}}
                          for c in self._public_channels]
                ws.send(json.dumps(params))

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("Websocket closed")

        def run(ws):
            while True:
                ws.run_forever()
                time.sleep(3)

        def on_message(ws, message):
            messages = json.loads(message)

            # auth レスポンスの処理
            if 'id' in messages and messages['id'] == self._JSONRPC_ID_AUTH:
                if 'error' in messages:
                    print('auth error: {}'.format(messages["error"]))
                elif 'result' in messages and messages['result']:
                    params = [{'method': 'subscribe', 'params': {'channel': c}}
                              for c in self._private_channels]
                    ws.send(json.dumps(params))

            if 'method' not in messages or messages['method'] != 'channelMessage':
                return

            params = messages["params"]
            channel = params["channel"]
            recept_data = params["message"]

            if channel == "lightning_executions_FX_BTC_JPY":
                for r in recept_data:
                    date = r["exec_date"][:26]
                    date = date.replace("T", " ").replace("Z", "")
                    date = \
                        dtdt.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
                    date = date + dt.timedelta(hours=9)
                    side = r["side"]
                    price = r["price"]
                    size = str(r["size"])
                    sql = "insert into execution_history values (null,'{date}','{side}',{price},'{size}')"\
                        .format(date=date, side=side, price=price, size=size)
                    repository.execute(database=database, sql=sql, log=False)

            if channel == "lightning_ticker_FX_BTC_JPY":
                date = recept_data["timestamp"][:26]
                date = date.replace("T", " ").replace("Z", "")
                date = \
                    dtdt.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
                date = date + dt.timedelta(hours=9)
                best_bid = recept_data["best_bid"]
                best_ask = recept_data["best_ask"]

                sql = "update ticker set date='{date}',best_bid={best_bid},best_ask={best_ask}"\
                    .format(date=date, best_bid=best_bid, best_ask=best_ask)
                repository.execute(database=database, sql=sql, log=False)

        def auth(ws):
            now = int(time.time())
            nonce = token_hex(16)
            sign = hmac.new(self._secret.encode(
                'utf-8'), ''.join([str(now), nonce]).encode('utf-8'), sha256).hexdigest()
            params = {
                'method': 'auth',
                'params': {
                    'api_key': self._key,
                    'timestamp': now,
                    'nonce': nonce,
                    'signature': sign},
                'id': self._JSONRPC_ID_AUTH}
            ws.send(json.dumps(params))

        ws = websocket.WebSocketApp(
            self._end_point,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close)
        websocketThread = Thread(target=run, args=(ws, ))
        websocketThread.start()


def initialize():
    sql = "select * from ticker"
    ticker = repository.read_sql(database=database, sql=sql)
    if ticker.empty:
        message.info("initialize ticker")
        sql = "insert into ticker values (now(),0,0)"
        repository.execute(database=database, sql=sql, write=False)


if __name__ == '__main__':
    initialize()
    signal.signal(signal.SIGINT, quit_loop)
    ws = bFwebsocket(end_point, public_channels, private_channels, key, secret)
    ws.startWebsocket()
