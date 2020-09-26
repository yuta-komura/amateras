import datetime
import time
import traceback
import warnings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from lib import bitflyer, message, repository
from lib.config import AssetManagement, Bitflyer, FilePath


def liquidate():
    message.info("liquidate start")
    while True:
        try:
            driver.get("https://lightning.bitflyer.com/trade/fxbtcjpy")

            class_name = "pnl__period.pnl__period--daily"
            elements = driver.find_elements_by_class_name(class_name)

            daily_profit = None
            for e in elements:
                if "日次損益" in e.text:
                    daily_profit = e.text
                    daily_profit = daily_profit.replace("日次損益", "")
                    daily_profit = daily_profit.replace("\n", "")
                    daily_profit = daily_profit.replace("円", "")
                    daily_profit = daily_profit.replace(",", "")
                    daily_profit = int(daily_profit)
                    break

            sql = "select * from asset_management"
            asset_management = repository.read_sql(database=DATABASE, sql=sql)
            basis_collateral = int(asset_management.at[0, "basis_collateral"])
            basis_collateral += daily_profit

            driver.get("https://lightning.bitflyer.com/funds")

            class_name = "collateral__form"
            elements = driver.find_elements_by_class_name(class_name)
            withdraw_element = None
            deposit_element = None
            for e in elements:
                if "証拠金口座へ" in e.text:
                    deposit_element = e
                if "現物口座へ" in e.text:
                    withdraw_element = e

            class_name = "balance__currency--sub"
            elements = driver.find_elements_by_class_name(class_name)
            collateral_element = None
            for e in elements:
                if "JPY Japanese Yen" in e.text:
                    collateral_element = e
                    break

            class_name = "currency__total"
            collateral_element = \
                collateral_element.find_element_by_class_name(class_name)

            collateral = collateral_element.text
            collateral = collateral.replace("合計", "")
            collateral = collateral.replace("\n", "")
            collateral = collateral.replace("円", "")
            collateral = collateral.replace(",", "")
            collateral = int(collateral)

            amount = collateral - basis_collateral

            if amount > 0:
                w_input = \
                    withdraw_element.find_element_by_tag_name("input")
                w_input.clear()
                w_input.send_keys(amount)

                w_button = \
                    withdraw_element.find_element_by_tag_name("button")
                w_button.click()
            else:
                d_input = \
                    deposit_element.find_element_by_tag_name("input")
                d_input.clear()
                d_input.send_keys(-amount)

                d_button = \
                    deposit_element.find_element_by_tag_name("button")
                d_button.click()

            ld = datetime.datetime.now() + datetime.timedelta(days=1)
            plan_date = str(ld).split(".")[0]

            sql = "update asset_management set plan_date='{plan_date}', basis_collateral={basis_collateral}"\
                .format(plan_date=plan_date, basis_collateral=basis_collateral)
            repository.execute(database=DATABASE, sql=sql)
            break
        except Exception:
            message.error(traceback.format_exc())
    message.info("liquidate finish")


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

k = 2

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
                break

            entry_side = entry.at[0, "side"]

            sql = "select * from position"
            position = repository.read_sql(database=DATABASE, sql=sql)
            if position.empty:
                break

            position_side = position.at[0, "side"]
        except Exception:
            message.error(traceback.format_exc())
            continue

        if entry_side != position_side:
            break

        if latest_side is None \
                or latest_side != position_side:
            inserted_collaterals = []
            latest_side = position_side

        profit = bitflyer.get_profit()
        time.sleep(3)

        insert_collateral = -profit * k - sum(inserted_collaterals)

        insert_collateral = 1
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
