#!/usr/bin/env python
from tempfile import TemporaryFile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import sys
import os
import logging
from colorlog import ColoredFormatter
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import traceback
from resuseable_modules import *

# -------------------- Logging Setup --------------------
LOG_LEVEL = logging.INFO
LOGFORMAT_COLOR = (
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s"
)
LOGFORMAT_NO_COLOR = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logger = logging.getLogger(__name__)
formatter_color = ColoredFormatter(LOGFORMAT_COLOR)
formatter_no_color = logging.Formatter(LOGFORMAT_NO_COLOR)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(LOG_LEVEL)
ch.setFormatter(formatter_color)
logger.addHandler(ch)
logger.setLevel(LOG_LEVEL)

# -------------------- Chrome Setup with Disabled Notifications --------------------
chrome_options = Options()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--disable-notifications")

# Apply options when initializing the driver
driver = webdriver.Chrome(service=Service(), options=chrome_options)
driver.maximize_window()

# -------------------- Wait Setup --------------------
wait = WebDriverWait(driver, 10)
errors = []


# This handler will sign in to Hudl. Navigation to webpage not included.
def hudl_sign_in(driver, email, password):
    try:
        # Clicking "Log in"
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/header/div/div[2]/a")))
        login_button.click()
        #Clicking "Hudl"
        hudl_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/header/div/div[2]/div/div/div/div/a[1]/span")))
        hudl_link.click()
        time.sleep(1)
        # Entering login credentials
        driver.find_element(By.ID,"username").send_keys(email)
        driver.find_element(By.XPATH,"/html/body/code/div/main/section/div/div/div/div[1]/div/form/div[2]/button").click()
        time.sleep(1)
        driver.find_element(By.ID,"password").send_keys(password)
        # Scrolling to Continue button if necessary
        try:
            driver.find_element(By.XPATH,"/html/body/code/div/main/section/div/div/div/form/div[2]/button").click()
        except:
            actions = ActionChains(driver)
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)
            driver.find_element(By.XPATH,"/html/body/code/div/main/section/div/div/div/form/div[2]/button").click()
        time.sleep(3)
        # Waiting for page to fully load
        while driver.execute_script("return document.readyState") != "complete":
            pass
        logger.info("Hudl sign in successful")
    except:
        logger.error("Unable to sign in to Hudle")

# This handler will navigate to Library. It assumes that the Hudl application is launched and signed in
def nav_to_library(driver):
    driver.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/nav[2]/div[3]/a[1]").click()
    time.sleep(3)
    expected_url = "https://app.hudl.com/watch/team/320073/analyze"        
    current_url = driver.current_url
    if current_url == expected_url:
        logger.info("Library is displayed")
    else:
        logger.error("Library is not displayed")
