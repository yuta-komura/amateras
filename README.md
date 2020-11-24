# amateras
bitflyer-lightning（btcfxjpy）用のビットコイン自動売買botです。  

**免責事項**：  
当botの利用により損失や被害が生じた場合、作者は一切の責任を負うことはできません。  
投資は自己責任でお願いします。　　

---
[ライセンス](https://github.com/yuta-komura/amateras/blob/master/LICENSE)

---    
### パフォーマンス
**initial parameter**：  
asset 1,000,000  

**backtest result**：  
2019-10-06 15:47:00 〜 2020-11-22 21:41:00  
profit 1,628,014  
pf 1.81  
wp 41 %  
trading cnt 75  
  
profit flow  
<a href="https://imgur.com/Otiz1s4"><img src="https://i.imgur.com/Otiz1s4.png" title="source: imgur.com" /></a>  
  
entry timing  
▲ BUY ▼ SELL  
<a href="https://imgur.com/cTq8P8H"><img src="https://i.imgur.com/cTq8P8H.png" title="source: imgur.com" /></a>

---  
### 環境  
ubuntu20.04 / mysql / python

---  
### インストール  
**mysql**：  
db.sql参照  
必要なデータベースとテーブルを作成後、  
lib/config.pyに設定してください。
```python:config.py
class DATABASE(Enum):
    class TRADINGBOT(Enum):
        HOST = 'localhost'
        USER = 'user'
        PASSWORD = 'password'
        DATABASE = 'tradingbot'
```

**pythonライブラリ**：  
venv同梱です。プログラム起動時に自動でvenvがアクティベートされます。  

**bitflyer apikey**：  
1．bitflyer-lightningのサイドバーから"API"を選択  
<a href="https://imgur.com/afZrmWf"><img src="https://i.imgur.com/afZrmWf.png" title="source: imgur.com" /></a>  
2．"新しいAPIキーを追加"を選択しapikeyを作成  
<a href="https://imgur.com/x56kiBy"><img src="https://i.imgur.com/x56kiBy.png" title="source: imgur.com" /></a>  
3．lib/config.pyに設定してください。
```python:config.py
class Bitflyer(Enum):
    class Api(Enum):
        KEY = "fcksdjcji9swefeixcJKj1"
        SECRET = "sdjkalsxc90wdwkksldfdscmcldsa"
```

**レバレッジ**：  
bitflyerでは4倍を設定してください。  
このシステムは、レバレッジ2倍分のポジションサイズをとります。  
ポジションサイズの変更は**lib/bitflyer.py**のコンストラクタで設定してください。  
```python:bitflyer.py
    def __init__(self, api_key, api_secret):
        self.api = pybitflyer.API(api_key=api_key, api_secret=api_secret)
        self.PRODUCT_CODE = "FX_BTC_JPY"
        self.LEVERAGE = 1
        self.DATABASE = "tradingbot"
```
---  
### 起動方法  
下記2点のシェルスクリプトを実行してください。（別画面で）  

**get_realtime_data.sh**：  
websocketプロトコルを利用しRealtime APIと通信。  
tickerと約定履歴（ローソク足作成用）を取得します。  
```bash
sh amateras/main/get_realtime_data.sh
```
**execute.sh**：  
メインスクリプト用  
```bash
sh amateras/main/execute.sh 
```
---  
### main process  
<a href="https://imgur.com/D9MlxAZ"><img src="https://i.imgur.com/D9MlxAZ.png" title="source: imgur.com" /></a>
