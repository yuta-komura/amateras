import time
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from lib import message, repository
from lib.config import Bitflyer, FilePath

options = Options()
path_to_chromedriver = FilePath.CHROMEDRIVER.value
driver = webdriver.Chrome(
    options=options,
    executable_path=path_to_chromedriver)

driver.get("https://lightning.bitflyer.com/")
driver.maximize_window()

id = driver.find_element_by_id("LoginId")
id.send_keys(Bitflyer.User.value.LOGIN_ID.value)
password = driver.find_element_by_id("Password")
password.send_keys(Bitflyer.User.value.PASSWORD.value)

login_button = driver.find_element_by_id("login_btn")
login_button.click()

# --------------------------------------------------------------- #

DATABASE = "tradingbot"

asset = None
latest_side = None
insert_assets = []
while True:
    while True:
        driver.get("https://lightning.bitflyer.com/funds")
        time.sleep(3)

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
            insert_assets = []
            latest_side = position_side

        try:
            xpath = """//*[@id="funds__summary"]/div[1]/ul/li[7]/span[4]"""
            asset = driver.find_element_by_xpath(xpath).text\
                .replace("円", "").replace(",", "").replace("合計", "")
            asset = int(asset)

            xpath = """//*[@id="funds__summary"]/div[2]/div/ul/li[1]/span[2]"""
            trading_asset = driver.find_element_by_xpath(xpath).text\
                .replace("円", "").replace(",", "").replace("合計", "")
            trading_asset = int(trading_asset)

            insert_asset = asset - trading_asset
            insert_asset = insert_asset - sum(insert_assets)

            if insert_asset > 0:
                xpath = """
                            //*[@id="collateralForm"]/div[2]/div/ul[1]/li[5]/aside/table/tbody/tr/td[2]/input
                            """
                collateral_form = driver.find_element_by_xpath(xpath)
                collateral_form.send_keys(insert_asset)

                xpath = """
                            //*[@id="collateralForm"]/div[2]/div/ul[1]/li[5]/aside/table/tbody/tr/td[3]/button
                            """
                collateralBtn = driver.find_element_by_xpath(xpath)
                collateralBtn.click()

                insert_assets.append(insert_asset)
                message.info("insert asset", insert_asset)
        except Exception:
            message.error(traceback.format_exc())
