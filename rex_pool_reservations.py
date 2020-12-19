import calendar
import datetime
import json
import logging
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


class PoolReservationError(Exception):
    pass


def parse_config(config_file):
    """Parses the config file"""
    logging.info("Parsing config file: %s", config_file)
    with open(config_file, "r") as json_file:
        config = json.load(json_file)
    return config


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


def pick_date(calender_element, target_date):
    """Picks the date using the JQuery calendar UI"""
    logging.info("Picking date: %s", target_date)
    today = datetime.date.today()

    if today.day > target_date.day:
        calender_element.find_element_by_xpath("//a[@title='Next']").click()

    calender_element.find_element_by_link_text(str(target_date.day)).click()


def navigate_to_reservation_page(web_driver):
    """navigates to the reservation page"""
    logging.info("Navigating to the reservation page.")
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

    web_driver.find_elements_by_class_name("ui-datepicker-trigger")[0].click()

    WebDriverWait(web_driver, timeout=30).until(
        lambda d: d.find_element_by_id("ui-datepicker-div")
    )
    calender_element = web_driver.find_element_by_id("ui-datepicker-div")

    target_date = datetime.date.today() + datetime.timedelta(days=7)
    pick_date(calender_element, target_date)

    web_driver.find_element_by_id("btnContinue").click()


def schedule_pool_time(web_driver, config):
    """Schedules the pool time"""
    navigate_to_reservation_page(web_driver)

    WebDriverWait(web_driver, timeout=30).until(
        lambda d: d.find_element_by_id("spnWeekDate")
    )
    # TODO: This should probably be changed to an element wait
    time.sleep(5)
    web_driver.find_element_by_id("ancSchListView").click()

    WebDriverWait(web_driver, timeout=30).until(
        lambda d: d.find_element_by_class_name("tblSchslots")
    )

    schedule_table = web_driver.find_element_by_class_name("tblSchslots")

    current_weekday = datetime.datetime.today().weekday()

    for weekday, hour in config["schedule"].items():
        if getattr(calendar, weekday.upper()) == current_weekday:
            schedule_table.find_element_by_xpath(
                f"//td[starts-with(text(),'{hour:02d}:')]"
            ).find_element_by_xpath("..").find_element_by_class_name(
                "schTblButton"
            ).click()
            WebDriverWait(web_driver, timeout=30).until(
                lambda d: d.find_element_by_id("btnContinue")
            )
            web_driver.find_element_by_id("btnContinue").click()
            break

    try:
        WebDriverWait(web_driver, timeout=30).until(
            lambda d: d.find_element_by_id("ctl00_pageContentHolder_btnContinueCart")
        )
        web_driver.find_element_by_id("ctl00_pageContentHolder_btnContinueCart").click()
    except:
        raise PoolReservationError("Unable to find matching pool time.")
    try:
        WebDriverWait(web_driver, timeout=30).until(
            lambda d: d.find_element_by_id("ctl00_pageContentHolder_ScheduleDetails")
        )
        logging.info(
            web_driver.find_element_by_id(
                "ctl00_pageContentHolder_ScheduleDetails"
            ).text
        )
    except:
        raise PoolReservationError("Confirmation screen was not found.")


def main():
    logging.basicConfig(level=logging.INFO)
    config = parse_config(sys.argv[1])
    chrome_options = Options()
    if config["headless"]:
        chrome_options.add_argument("--headless")
    web_driver = webdriver.Chrome(options=chrome_options)
    try:
        web_driver.get(config["url"])
        login(web_driver, config["username"], config["password"])
        schedule_pool_time(web_driver, config)
        input("Press Enter to continue...")
        web_driver.quit()
    except Exception as e:
        logging.error("An error has occured.")
        logging.error(e, exc_info=True)
        input("Press Enter to continue...")
        web_driver.quit()
        raise


if __name__ == "__main__":
    main()
