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
LOG_PREFIX = "hudl_test_automation"
log_file = datetime.now().strftime(f"{LOG_PREFIX}_%Y-%m-%d_%H-%M.log")

logger = logging.getLogger(__name__)
formatter_color = ColoredFormatter(LOGFORMAT_COLOR)
formatter_no_color = logging.Formatter(LOGFORMAT_NO_COLOR)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(LOG_LEVEL)
ch.setFormatter(formatter_color)
logger.addHandler(ch)
logger.setLevel(LOG_LEVEL)
# Set logging output to a file
fh = logging.FileHandler(log_file)
fh.setLevel(LOG_LEVEL)
fh.setFormatter(formatter_no_color)
logger.addHandler(fh)

# -------------------- Chrome Setup with Disabled Notifications --------------------
chrome_options = Options()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--disable-notifications")

# Apply options when initializing the driver
driver = webdriver.Chrome(service=Service(), options=chrome_options)
driver.maximize_window()


# Variables
email = ""
password = ""
video = "testing purpose"

# Launching webpage
driver.get("https://www.hudl.com")
time.sleep(3)

def wait_for_element(driver, by, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def validate_video_search(driver, video_name):
    try:
        search_box = wait_for_element(driver, By.CSS_SELECTOR, "input[type='text']")
        search_box.send_keys(video_name, Keys.ENTER)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, video_name))
        )
        logger.info("Video found in search results.")
        driver.save_screenshot("video_displayed.png")
        return True
    except Exception as e:
        logger.error(f"Video not found: {e}")
        driver.save_screenshot("video_not_displayed.png")
        return False

def validate_video_playback(driver, video_name):
    try:
        driver.find_element(By.LINK_TEXT, video_name).click()
        time.sleep(3) # Waiting for video to fully load
        video_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,"/html/body/section/div/div/div[2]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[10]/div")))
        logger.info(f"Video playback time: {video_time.text}")
        if video_time.text.strip().startswith("0:00"):
            logger.error("Video is not playing.")
            driver.save_screenshot("video_not_playing.png")
        else:
            logger.info("Video is playing successfully.")
            driver.save_screenshot("video_playing_successfully.png")
    except Exception as e:
        logger.error(f"Error verifying video playback: {e}")
        driver.save_screenshot("video_playback_error.png")

# --- Main Flow ---
try:
    hudl_sign_in(driver, email, password)
    nav_to_library(driver)

    if validate_video_search(driver, video):
        validate_video_playback(driver, video)
finally:
    driver.quit()