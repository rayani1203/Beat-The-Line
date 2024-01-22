from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://hashtagbasketball.com/nba-defense-vs-position")
sg_button = driver.find_element(By.ID,"ContentPlaceHolder1_RBL1_1").click()
time.sleep(5)
driver.close()