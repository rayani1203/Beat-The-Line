from Definitions import *
from selenium import webdriver
from selenium.webdriver.common.by import By

def web_crawl(opposition, position, stat, driver):
    driver.execute_script("window.scrollTo(0, 0)")
    if stat in stat_dic.keys():
        key = stat_dic[stat]
    else:
        key = stat_dic[stat[0]]
    for button in driver.find_elements(By.XPATH, f"//*[text()[contains(.,'{key}')]]"):
        if button.text == "FD PTS" or button.text == "":
            continue
        try:
            button.click()
        except:
            continue
    try:
        driver.find_element(By.CLASS_NAME, "tablesorter-headerSortUp")
        return web_crawl(opposition, position, stat, driver)
    except:
        pass
    for i, row in enumerate(driver.find_elements(By.CSS_SELECTOR, f".GC-0.{position}")):
        cell = row.find_element(By.CSS_SELECTOR, ".left.team-cell")
        if cell.text.split("\n")[1] == opposition or (opposition == "LA Clippers" and cell.text.split("\n")[1] == "Los Angeles Clippers"):
            print(f"{opposition} defense is {i+1} against {position} {stat}")
            return i+1
    tags = driver.find_elements(By.CSS_SELECTOR, "a")
    for elem in tags:
        try:
            if elem.text == position:
                elem.click()
        except:
            continue
    return web_crawl(opposition, position, stat, driver)
