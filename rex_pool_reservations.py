import argparse
import configparser
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


def main():
    logging.basicConfig(level=logging.INFO)
    config = parse_config(sys.argv[1])
    web_driver = webdriver.Chrome()
    web_driver.get(config["url"])
    login(web_driver, config["username"], config["password"])


if __name__ == "__main__":
    main()
