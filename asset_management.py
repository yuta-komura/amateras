import datetime
import time
import traceback
import warnings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from lib import bitflyer, message, repository
from lib.config import AssetManagement, Bitflyer, FilePath


def close():
    while True:
        try:
            driver.get("https://lightning.bitflyer.com/trade/fxbtcjpy")

            class_name = "pnl__funds.pnl__funds--derivative._is-active._has-position"
            elements = driver.find_elements_by_class_name(class_name)
            size = None
            for e in elements:
                if "FX BTC/JPY" in e.text:
                    size = e.text
                    size = size.replace("FX BTC/JPY", "")
                    size = size.replace("ɃFX", "")
                    size = size.replace("\n", "")
                    size = float(size)
                    break

            if size is None:
                break
            else:
                if abs(size) < 0.01:
                    class_name = "button-group-item"
                    elements = driver.find_elements_by_class_name(class_name)
                    market_element = None
                    for e in elements:
                        if "成行" in e.text:
                            market_element = e
                            break
                    market_element.click()

                    class_name = "place__size"
                    oe_input = driver.find_element_by_class_name(class_name)
                    oe_input.clear()
                    oe_input.send_keys(str(0.01))
                    class_name = "button-group-item.noSelect"
                    oe_b = driver.find_elements_by_class_name(class_name)
                    for b in oe_b:
                        if size > 0:
                            if "買い" in b.text:
                                b.click()
                                break
                        if size < 0:
                            if "売り" in b.text:
                                b.click()
                                break
                    time.sleep(3)
                    continue
                else:
                    bitflyer.close()
                    time.sleep(3)
                    continue
        except Exception:
            message.error(traceback.format_exc())


def liquidate():
    message.info("liquidate start")

    while True:
        try:
            close()

            driver.get("https://lightning.bitflyer.com/funds")

            class_name = "fund__collateral"
            elements = driver.find_elements_by_class_name(class_name)
            collateral = None
            for e in elements:
                collateral = e.text
                collateral = collateral.replace(",", "")
                collateral = collateral.replace("\n", "")
                collateral = collateral.replace("円", "")
                collateral = int(collateral)
                break

            class_name = "collateral__form"
            elements = driver.find_elements_by_class_name(class_name)
            withdraw_element = None
            for e in elements:
                if "現物口座へ" in e.text:
                    withdraw_element = e

            w_input = \
                withdraw_element.find_element_by_tag_name("input")
            w_input.clear()
            w_input.send_keys(collateral)

            w_button = \
                withdraw_element.find_element_by_tag_name("button")
            w_button.click()

            driver.get("https://lightning.bitflyer.com/funds")

            class_name = "collateral__form"
            elements = driver.find_elements_by_class_name(class_name)
            deposit_element = None
            for e in elements:
                if "証拠金口座へ" in e.text:
                    deposit_element = e

            class_name = "balance__currency--jpy"
            asset_element = driver.find_element_by_class_name(class_name)
            class_name = "currency__total"
            asset_element = \
                asset_element.find_element_by_class_name(class_name)
            asset = asset_element.text
            asset = asset.replace("合計", "")
            asset = asset.replace("\n", "")
            asset = asset.replace("円", "")
            asset = asset.replace(",", "")
            asset = int(asset)

            insert_collateral = int(asset * (1 / 3))

            d_input = \
                deposit_element.find_element_by_tag_name("input")
            d_input.clear()
            d_input.send_keys(insert_collateral)

            d_button = \
                deposit_element.find_element_by_tag_name("button")
            d_button.click()

            ld = datetime.datetime.now() + datetime.timedelta(days=1)
            plan_date = str(ld).split(".")[0]
            sql = "update asset_management set plan_date='{plan_date}'"\
                .format(plan_date=plan_date)
            repository.execute(database=DATABASE, sql=sql)

            message.info("liquidate finish")
            return
        except Exception:
            message.error(traceback.format_exc())


warnings.filterwarnings('ignore')

options = Options()
path_to_chromedriver = FilePath.CHROMEDRIVER.value
driver = webdriver.Chrome(
    options=options,
    executable_path=path_to_chromedriver)

driver.get("https://lightning.bitflyer.com/trade/fxbtcjpy")
driver.maximize_window()

id = driver.find_element_by_id("LoginId")
id.send_keys(Bitflyer.User.value.LOGIN_ID.value)
password = driver.find_element_by_id("Password")
password.send_keys(Bitflyer.User.value.PASSWORD.value)

login_button = driver.find_element_by_id("login_btn")
login_button.click()

# --------------------------------------------------------------- #

k = 1

EXECUTE_TIME = AssetManagement.EXECUTE_TIME.value

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)

DATABASE = "tradingbot"

sql = "select * from asset_management"
asset_management = repository.read_sql(database=DATABASE, sql=sql)
plan_date = asset_management.at[0, "plan_date"]

latest_side = None
inserted_collaterals = []
while True:
    now = datetime.datetime.now()
    if now.day == plan_date.day and now.hour >= EXECUTE_TIME:
        while True:
            try:
                sql = "select * from position"
                position = repository.read_sql(database=DATABASE, sql=sql)
                if position.empty:
                    liquidate()
                    plan_date += datetime.timedelta(days=1)
                    break
            except Exception:
                message.error(traceback.format_exc())

    try:
        sql = "select * from entry"
        entry = repository.read_sql(database=DATABASE, sql=sql)
        if entry.empty:
            continue

        entry_side = entry.at[0, "side"]

        sql = "select * from position"
        position = repository.read_sql(database=DATABASE, sql=sql)
        if position.empty:
            continue

        position_side = position.at[0, "side"]
    except Exception:
        message.error(traceback.format_exc())
        continue

    if entry_side != position_side:
        continue

    if latest_side is None \
            or latest_side != position_side:
        inserted_collaterals = []
        latest_side = position_side

    profit = bitflyer.get_profit()
    time.sleep(3)

    insert_collateral = -profit * k - sum(inserted_collaterals)

    try:
        if insert_collateral > 0:
            driver.get("https://lightning.bitflyer.com/funds")

            class_name = "collateral__form"
            elements = driver.find_elements_by_class_name(class_name)

            deposit_element = None
            for e in elements:
                if "証拠金口座へ" in e.text:
                    deposit_element = e
                    break

            ai_input = \
                deposit_element.find_element_by_tag_name("input")
            ai_input.clear()
            ai_input.send_keys(insert_collateral)

            ai_button = \
                deposit_element.find_element_by_tag_name("button")
            ai_button.click()

            inserted_collaterals.append(insert_collateral)
            message.info("insert collateral", insert_collateral)
    except Exception:
        message.error(traceback.format_exc())
        continue
