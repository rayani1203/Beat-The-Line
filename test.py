# from selenium import webdriver
# from selenium.webdriver.common.by import By
import pandas
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt

overdf = pandas.read_csv("/Users/rayani1203/Downloads/alloverpicks.csv")
underdf = pandas.read_csv("/Users/rayani1203/Downloads/allunderpicks.csv")

stat_headers = ['Stat Key', 'Hit Rate', '3W% vs Spread', '3W Average', 'Defense Rank']

overstats = overdf[stat_headers]
overresults = overdf['Hit?']

understats = underdf[stat_headers]
underresults = underdf['Hit?']

overdtree = DecisionTreeClassifier()
overdtree = overdtree.fit(overstats, overresults)
tree.plot_tree(overdtree, feature_names=stat_headers)
plt.savefig("/Users/rayani1203/Downloads/overdecisiontree.pdf")

underdtree = DecisionTreeClassifier()
underdtree = underdtree.fit(understats, underresults)
tree.plot_tree(underdtree, feature_names=stat_headers)
plt.savefig("/Users/rayani1203/Downloads/underdecisiontree.pdf")

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