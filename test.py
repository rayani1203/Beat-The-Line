from selenium import webdriver
from selenium.webdriver.common.by import By

stat_dic = {
    "points": "PTS",
    "assists": "AST",
    "rebounds": "REB",
    "threes": "3PM",
    "steals": "STL",
    "blocks": "BLK",
    "turnovers": "TO",
    "p": "PTS",
    "r": "REB",
    "a": "AST",
    "s": "STL",
}

opposition = 'DET'
pos = 'SG'
stat = 'threes'

def web_crawl(opposition, position, stat):
    driver = webdriver.Chrome()
    driver.get("https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php")
    driver.find_element(By.XPATH, f"//*[text()[contains(.,'{position}')]]").click()
    if stat in stat_dic.keys():
        key = stat_dic[stat]
    else:
        key = stat_dic[stat[0]]
    print(key)
    for button in driver.find_elements(By.XPATH, f"//*[text()[contains(.,'{key}')]]"):
        try:
            button.click()
        except:
            continue
    for i, row in enumerate(driver.find_elements(By.CSS_SELECTOR, f".GC-0.{position}")):
        cell = row.find_element(By.CSS_SELECTOR, ".left.team-cell")
        if cell.text.split("\n")[0] == opposition:
            return i+1
    driver.close()

print(web_crawl(opposition, pos, stat))