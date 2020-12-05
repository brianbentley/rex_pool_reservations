import configparser
import datetime
import logging
import sys
import time
import keyring
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def parse_config(config_file):
    """Parses the config file"""
    logging.info(f"Parsing config file: {config_file}")
    config = configparser.ConfigParser()
    config.read(config_file)
    username = config["credentials"]["username"]
    credential_name = config["credentials"]["credential_name"]
    password = keyring.get_password(credential_name, username)
    url = config["config"]["url"]
    return {"username": username, "password": password, "url": url}


def login(web_driver, username, password):
    """Log in to the portal."""
    logging.info("logging on to portal.")
    username_field = web_driver.find_element_by_id(
        "ctl00_pageContentHolder_loginControl_UserName"
    )
    password_field = web_driver.find_element_by_id(
        "ctl00_pageContentHolder_loginControl_Password"
    )
    login_button = web_driver.find_element_by_id(
        "ctl00_pageContentHolder_loginControl_Login"
    )
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()
    WebDriverWait(web_driver, timeout=30).until(
        lambda d: d.find_element_by_id("ctl00_welcomeCnt_lbWelcome")
    )
    logging.info("login succesful.")

def schedule_pool_time(web_driver):
    """Schedules the pool time"""
    web_driver.find_element_by_id("menu_SCH").click()

    WebDriverWait(web_driver, timeout=30).until(
        lambda d: d.find_element_by_xpath("//div[@title='Aquatics']")
    )
    web_driver.find_element_by_xpath("//div[@title='Aquatics']").click()

    WebDriverWait(web_driver, timeout=30).until(
        lambda d: d.find_element_by_xpath("//div[@title='Lap Pool Reservation']")
    )
    web_driver.find_element_by_xpath("//div[@title='Lap Pool Reservation']").click()

    WebDriverWait(web_driver, timeout=30).until(
        lambda d: d.find_element_by_id("dateControlText")
    )

    target_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%m/%d/%Y")

    date_input = web_driver.find_element_by_id("dateControlText")

    #web_driver.execute_script(f"arguments[0].value = '{target_date}';", date_input)
    web_driver.execute_script(f"arguments[0].removeAttribute('disabled');", date_input)

    #web_driver.find_element_by_id("btnContinue").click()
    

def main():
    logging.basicConfig(level=logging.INFO)
    config = parse_config(sys.argv[1])
    web_driver = webdriver.Chrome()
    web_driver.get(config["url"])
    login(web_driver, config["username"], config["password"])
    schedule_pool_time(web_driver)
    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
