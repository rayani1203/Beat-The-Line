# from selenium import webdriver
# from selenium.webdriver.common.by import By
import pandas

file = open("/Users/rayani1203/Downloads/allpicks.csv", "r")

df = pandas.read_csv("/Users/rayani1203/Downloads/allpicks.csv")
print(df)

# stat_dic = {
#     "points": "PTS",
#     "assists": "AST",
#     "rebounds": "REB",
#     "threes": "3PM",
#     "steals": "STL",
#     "blocks": "BLK",
#     "turnovers": "TO",
#     "p": "PTS",
#     "r": "REB",
#     "a": "AST",
#     "s": "STL",
# }

# opposition = 'Utah Jazz'
# pos = 'SG'
# stat = 'threes'

# def web_crawl(opposition, position, stat):
#     driver = webdriver.Chrome()
#     driver.get("https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php")
#     button = driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler")
#     while True:
#         try:
#             button.click()
#             break
#         except:
#             print("Closing button on driver failed...")
#     driver.execute_script("window.scrollTo(0, 0)")
#     tags = driver.find_elements(By.CSS_SELECTOR, "a")
#     for elem in tags:
#         try:
#             if elem.text == position:
#                 elem.click()
#         except:
#             continue
#     if stat in stat_dic.keys():
#         key = stat_dic[stat]
#     else:
#         key = stat_dic[stat[0]]
#     for button in driver.find_elements(By.XPATH, f"//*[text()[contains(.,'{key}')]]"):
#         if button.text == "FD PTS":
#             continue
#         try:
#             button.click()
#         except:
#             continue
#     for i, row in enumerate(driver.find_elements(By.CSS_SELECTOR, f".GC-0.{position}")):
#         cell = row.find_element(By.CSS_SELECTOR, ".left.team-cell")
#         if cell.text.split("\n")[1] == opposition:
#             return i+1
#         else:
#             print(cell.text.split("\n")[0])
#     driver.close()

# print(web_crawl(opposition, pos, stat))