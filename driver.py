import atexit
import chromedriver_binary
import os
import time

from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.support.ui import WebDriverWait

# Settings
BROWSER_VISIBLE = False
PROXY_LIST      = None
PAGE_TIMEOUT    = 30
USER_AGENT_LIST = None

def get_user_agent():
    try:
        with open(USER_AGENT_LIST) as fp:
            ua_list = fp.read.splitlines()
            return ua_list[randint(0, len(ua_list) - 1)]
    except:
        return "Friendly Telegram wgetBot v0.1.2"

class WebDriverResource(object):
    def __init__(self):
        capabilities = webdriver.DesiredCapabilities.CHROME

        if PROXY_LIST:
            unclean_list = open(PROXY_LIST, "r").read().split("\n")
            proxy_list = list(filter(bool, unclean_list))
            ip = proxy_list[randint(0, len(proxy_list) - 1)]

            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            proxy.http_proxy = ip
            proxy.ssl_proxy  = ip
            proxy.add_to_capabilities(capabilities)

        user_agent = get_user_agent()
        options = webdriver.ChromeOptions()
        if not BROWSER_VISIBLE:
            options.add_argument("--user-agent=" + user_agent)
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("window-size=1024,768")
            options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(desired_capabilities=capabilities, options=options)
        atexit.register(self.driver.quit)

    def get(self, url):
        self.driver.get(url)

    def wait_until(self, condition, timeout=PAGE_TIMEOUT):
        if isinstance(condition, str):
            condition = cond.presence_of_element_located((By.CSS_SELECTOR, condition))
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(condition)

    def find_element(self, selector):
        return self.driver.find_element_by_css_selector(selector)

    def click_element(self, elem):
        if isinstance(elem, str):
            elem = self.driver.find_element_by_css_selector(elem)
        elem.click()

    def send_to_element(self, keys, elem):
        if isinstance(elem, str): # css selector
            elem = self.driver.find_element_by_css_selector(elem)
        elem.send_keys(keys)
