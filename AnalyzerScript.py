import requests
from datetime import datetime
import time
from operator import attrgetter
import csv
import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Thread, Lock
import os
import pandas
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

class Matchup:
    def __init__(self, home, home_id, home_brief, away, away_id, away_brief, id):
        self.home = home
        self.home_id = home_id
        self.home_brief = home_brief
        self.away = away
        self.away_id = away_id
        self.away_brief = away_brief
        self.id = id

class Stat:
    def __init__(self, line, over, under, stat, player):
        self.stat = stat
        self.player = player
        self.line = line
        self.over = over
        self.under = under
        self.hit = 0.0
        self.spread_diff = 0.0
        self.defense = 0

class Player:
    def __init__(self, name, id, home, away, points, rebounds, assists, threes, turnovers, steals, blocks, p_r, p_a, r_a, p_r_a, s_b):
        self.name = name
        self.sr_id = id
        self.home = home
        self.away = away
        self.opposition = ""
        self.position = ""
        self.points = points
        self.rebounds = rebounds
        self.assists = assists
        self.threes = threes
        self.turnovers = turnovers
        self.steals = steals
        self.blocks = blocks
        self.p_r = p_r
        self.p_a = p_a
        self.r_a = r_a
        self.p_r_a = p_r_a
        self.s_b = s_b
        self.id = 0,
        self.team = "",
        self.game_count = 0
        self.stats = {
            "points": 0.0,
            "assists": 0.0,
            "rebounds": 0.0,
            "threes": 0.0,
            "steals": 0.0,
            "blocks": 0.0,
            "turnovers": 0.0,
            "p_r": 0.0,
            "p_a": 0.0,
            "r_a": 0.0,
            "p_r_a": 0.0,
            "s_b": 0.0,
        }

if datetime.now().hour >= 17:
    currDate = datetime.now().day + 2
else:
    currDate = datetime.now().day + 1
currMonth = datetime.now().month
currYear = datetime.now().year
if currDate > 31:
    currMonth += 1
    currDate -= 31

currDateStr = str(currDate)
currMonthStr = str(currMonth)
if currDate - 1 < 1:
    prevDateStr = str(currDate + 30)
else:
    prevDateStr = str(currDate - 1)
if currDate < 10:
    currDateStr = '0' + currDateStr
    if currDate - 1 >= 1:
        prevDateStr = '0' + prevDateStr
if currMonth < 10:
    currMonthStr = '0' + currMonthStr


props = {
    "points": "sr:market:921",
    "assists": "sr:market:922",
    "rebounds": "sr:market:923",
    "threes": "sr:market:924",
    "steals": "sr:market:8000",
    "blocks": "sr:market:8001",
    "turnovers": "sr:market:8002",
    "p_r": "sr:market:8003",
    "p_a": "sr:market:8004",
    "r_a": "sr:market:8005",
    "p_r_a": "sr:market:8006",
    "s_b": "sr:market:8007",
}
altprops = dict((v,k) for k,v in props.items())

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

stat_num = {
    "points": 1,
    "assists": 2,
    "rebounds": 3,
    "threes": 4,
    "steals": 5,
    "blocks": 6,
    "turnovers": 7,
    "P/R": 8,
    "P/A": 9,
    "R/A": 10,
    "P/R/A": 11,
    "S/B": 12
}


apiMutex = Lock()
countLock = Lock()
global counter
counter = 0
global done
done = False
balance = 0.0

def find_best_ML_models():
    overdf = pandas.read_csv("/Users/rayani1203/Downloads/alloverpicks.csv")
    underdf = pandas.read_csv("/Users/rayani1203/Downloads/allunderpicks.csv")

    stat_headers = ['Stat Key', 'Hit Rate', '3W% vs Spread', '3W Average', 'Defense Rank']

    overstats = overdf[stat_headers]
    overresults = overdf['Hit?']

    understats = underdf[stat_headers]
    underresults = underdf['Hit?']

    overstats_train, overstats_test, overresults_train, overresults_test = train_test_split(overstats, overresults, test_size=0.2)
    understats_train, understats_test, underresults_train, underresults_test = train_test_split(understats, underresults, test_size=0.2)

    max_over_accuracy = 0
    best_over_depth = 0
    best_over_samples = 0
    retry_count = 0
    over_accuracy = 0
    while retry_count < 10:
        overstats_train, overstats_test, overresults_train, overresults_test = train_test_split(overstats, overresults, test_size=0.2)
        max_depth = 5
        min_samples = 1
        while max_depth < 40:
            min_samples = 1
            while min_samples < 40:
                overdtree = DecisionTreeClassifier(criterion='gini', min_samples_leaf=min_samples, max_depth=max_depth, random_state=0)
                overdtree = overdtree.fit(overstats_train, overresults_train)
                over_predictions = overdtree.predict(overstats_test)
                over_accuracy = accuracy_score(over_predictions, overresults_test)*100

                if over_accuracy > max_over_accuracy:
                    max_over_accuracy = over_accuracy
                    best_over_samples = min_samples
                    if max_depth != best_over_depth:
                        best_over_depth = max_depth

                min_samples += 1
            max_depth += 1
        retry_count += 1

    retry_count = 0
    under_accuracy = 0
    best_under_depth = 0
    best_under_samples = 0
    max_under_accuracy = 0
    while retry_count < 10:
        understats_train, understats_test, underresults_train, underresults_test = train_test_split(understats, underresults, test_size=0.2)
        max_depth = 5
        min_samples = 1
        while max_depth < 40:
            min_samples = 1
            while min_samples < 40:
                underdtree = DecisionTreeClassifier(criterion='gini', min_samples_leaf=min_samples, max_depth=max_depth, random_state=0)
                underdtree = underdtree.fit(understats_train, underresults_train)
                under_predictions = underdtree.predict(understats_test)
                under_accuracy = accuracy_score(under_predictions, underresults_test)*100

                if under_accuracy > max_under_accuracy:
                    max_under_accuracy = under_accuracy
                    best_under_samples = min_samples
                    if max_depth != best_under_depth:
                        best_under_depth = max_depth

                min_samples += 1
            max_depth += 1
        retry_count += 1

    print("Over accuracy is: ", max_over_accuracy, " at depth: ", best_over_depth, " and samples: ", best_over_samples)
    print("Under accuracy is: ", max_under_accuracy, " at depth: ", best_under_depth, " and samples: ", best_under_samples)

    best_over_model = DecisionTreeClassifier(criterion='gini', min_samples_leaf=best_over_samples, max_depth=best_over_depth, random_state=0)
    best_over_model = best_over_model.fit(overstats.values, overresults)

    best_under_model = DecisionTreeClassifier(criterion='gini', min_samples_leaf=best_under_samples, max_depth=best_under_depth, random_state=0)
    best_under_model = best_under_model.fit(understats.values, underresults)

    tree.plot_tree(best_over_model, feature_names=stat_headers)
    plt.savefig("/Users/rayani1203/Downloads/overdecisiontree.pdf")

    tree.plot_tree(best_under_model, feature_names=stat_headers)
    plt.savefig("/Users/rayani1203/Downloads/underdecisiontree.pdf")

    return {
        "over": best_over_model,
        "under": best_under_model
    }

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
    
def player_thread(player, oldYear, oldMonth, oldDate, playerResults):
    success = False
    while not success:
        try:
            with apiMutex:
                time.sleep(1)
                response = requests.get(f"http://api.sportradar.us/nba/trial/v8/en/players/{player.sr_id}/profile.json?api_key={config.player_key}", headers={'Accept': 'application/json'})
                res_json = response.json()
                success = True
                break
        except:
            print("API request failed, trying again in 7 seconds")
            time.sleep(7)
    player.position = res_json['primary_position']

    success = False
    name_list = player.name.split()
    if len(name_list) < 2:
        return
    while not success:
        try:
            response = requests.get(f"https://api.balldontlie.io/v1/players/?first_name={name_list[0]}&last_name={name_list[1]}", headers={'Accept': 'application/json', 'Authorization': config.ball_key})
            res_json = response.json()
            success = True
        except:
            print("balldontlie API request failed, trying again in 10 seconds")
            time.sleep(10)
    all_data = res_json['data']
    if len(all_data) == 0:
        return
    data = all_data[0]
    player.id = data['id']
    player.team = data['team']['full_name']
    if player.home == data['team']['full_name']:
        player.opposition = player.away
    else:
        player.opposition = player.home
    print(f'Analyzing stats for {player.name} of the {player.team}...')

    oldMonthStr = str(oldMonth)
    oldDateStr = str(oldDate)

    if len(oldMonthStr) < 2:
        oldMonthStr = '0' + oldMonthStr
    if len(oldDateStr) < 2:
        oldDateStr = '0' + oldDateStr

    success = False
    while not success:
        try:
            response = requests.get(f"https://api.balldontlie.io/v1/stats?player_ids[]={player.id}&start_date={oldYear}-{oldMonthStr}-{oldDateStr}", headers={'Authorization': config.ball_key})
            res_json = response.json()
            success = True
        except:
            print("API request failed, trying again in 10 seconds")
            time.sleep(10)
    data = res_json['data']
    game_count = 0
    for game in data:
        if float(game['min']) < 10:
            continue
        game_count += 1
        player.stats['points'] += game['pts']
        player.stats['assists'] += game['ast']
        player.stats['rebounds'] += game['reb']
        player.stats['threes'] += game['fg3m']
        player.stats['steals'] += game['stl']
        player.stats['blocks'] += game['blk']
        player.stats['turnovers'] += game['turnover']
        player.stats['p_r'] += game['pts'] + game['reb']
        player.stats['p_a'] += game['pts'] + game['ast']
        player.stats['r_a'] += game['ast'] + game['reb']
        player.stats['p_r_a'] += game['pts'] + game['reb'] + game['ast']
        player.stats['s_b'] += game['stl'] + game['blk']

        if game['pts'] > player.points.line:
            player.points.hit += 1
        if game['ast'] > player.assists.line:
            player.assists.hit += 1
        if game['reb'] > player.rebounds.line:
            player.rebounds.hit += 1
        if game['fg3m'] > player.threes.line:
            player.threes.hit += 1
        if game['stl'] > player.steals.line:
            player.steals.hit += 1
        if game['blk'] > player.blocks.line:
            player.blocks.hit += 1
        if game['turnover'] > player.turnovers.line:
            player.turnovers.hit += 1
        if game['pts'] + game['reb'] > player.p_r.line:
            player.p_r.hit += 1
        if game['pts'] + game['ast'] > player.p_a.line:
            player.p_a.hit += 1
        if game['reb'] + game['ast'] > player.r_a.line:
            player.r_a.hit += 1
        if game['pts'] + game['ast'] + game['reb'] > player.p_r_a.line:
            player.p_r_a.hit += 1
        if game['stl'] + game['blk'] > player.s_b.line:
            player.s_b.hit += 1

    player.game_count = game_count
    with countLock:    
        global counter
        playerResults.append(player)
        counter += 1

def worker_thread(playerResults, driver, overs, unders):
    global done
    global counter
    while not done or counter > 0:
        while counter < 1 and not done:
            continue
        with countLock:
            player = playerResults.pop(0)
            counter -= 1
        if player.game_count <= 5:
            continue
        print(f'Web crawling for defensive stats for {player.name} of the {player.team}...')
        driver.execute_script("window.scrollTo(0, 0)")
        tags = driver.find_elements(By.CSS_SELECTOR, "a")
        for elem in tags:
            try:
                if elem.text == player.position:
                    elem.click()
            except:
                continue
        defenses = []
        for stat in player.stats:
            player_stat = getattr(player, stat)
            player.stats[stat] /= player.game_count
            player_stat.hit /= player.game_count
            if player_stat.line == 0.0:
                continue
            if player_stat.hit >= 0.7:
                player_stat.spread_diff = player.stats[stat]
                if player_stat.hit >= 0.875:
                        player_stat.defense = web_crawl(player.opposition, player.position, stat, driver)
                        defenses.append(player_stat.defense)
                        overs.append(player_stat)
                elif player_stat.over >= 1.7:
                    player_stat.defense = web_crawl(player.opposition, player.position, stat, driver)
                    defenses.append(player_stat.defense)
                    if player_stat.defense > 10 and player_stat.hit >= 0.8:
                        overs.append(player_stat)
                    elif player_stat.defense >15 and player_stat.hit >= 0.7:
                        overs.append(player_stat)
            elif player_stat.hit <= 0.3:
                player_stat.spread_diff = player.stats[stat]
                if player_stat.hit <= 0.125:
                    player_stat.defense = web_crawl(player.opposition, player.position, stat, driver)
                    defenses.append(player_stat.defense)
                    unders.append(player_stat)
                elif player_stat.under >= 1.7:
                    player_stat.defense = web_crawl(player.opposition, player.position, stat, driver)
                    defenses.append(player_stat.defense)
                    if player_stat.defense <=20 and player_stat.hit <= 0.2:
                        unders.append(player_stat)
                    elif player_stat.defense <= 15 and player_stat.hit <= 0.3:
                        unders.append(player_stat)
        if len(defenses) > 0:
                if defenses.count(defenses[0]) > 5:
                    print("------------------ Web crawling error, restarting script... ------------------")
                    print(defenses)
                    return analyze_future_odds()

def analyze_future_odds():
    games = []
    players = []
    overs = []
    unders = []
    response = requests.get(f"https://api.sportradar.us/oddscomparison-player-props/trial/v2/en/competitions/sr:competition:132/schedules.json?api_key={config.nba_key}", headers={'Accept': 'application/json'})
    res_json = response.json()
    print('\nToday\'s games are:')
    for game in res_json['schedules']:
        if ((game['sport_event']['start_time'][8:10] == currDateStr) and (int(game['sport_event']['start_time'][11]) == 0)) or ((game['sport_event']['start_time'][8:10] == prevDateStr) and (int(game['sport_event']['start_time'][11]) > 0)):
            print(game['sport_event']['competitors'][0]['name'], "vs", game['sport_event']['competitors'][1]['name'])
            games.append(Matchup(game['sport_event']['competitors'][0]['name'], game['sport_event']['competitors'][0]['id'], game['sport_event']['competitors'][0]['abbreviation'], game['sport_event']['competitors'][1]['name'], game['sport_event']['competitors'][1]['id'], game['sport_event']['competitors'][1]['abbreviation'], game['sport_event']['id']))
    print('\n')
    time.sleep(2)
    for game in games:
        success = False
        while not success:
            try:
                response = requests.get(f"https://api.sportradar.us/oddscomparison-player-props/trial/v2/en/sport_events/{game.id}/players_props.json?api_key={config.nba_key}", headers={'Accept': 'application/json'})
                res_json = response.json()
                success = True
            except:
                print("API request failed, trying again in 10 seconds")
                time.sleep(10)
        print()
        print(f"-------------- Props for {game.home} vs {game.away} --------------")
        print("Getting lines for:")
        for prop in res_json['sport_event_players_props']['players_props']:
            name = " ".join(prop['player']['name'].split(", ")[::-1])
            print(name)
            lines = {
                "points": Stat(0.0, 0.0, 0.0, "points", name),
                "assists": Stat(0.0, 0.0, 0.0, "assists", name),
                "rebounds": Stat(0.0, 0.0, 0.0, "rebounds", name),
                "threes": Stat(0.0, 0.0, 0.0, "threes", name),
                "steals": Stat(0.0, 0.0, 0.0, "steals", name),
                "blocks": Stat(0.0, 0.0, 0.0, "blocks", name),
                "turnovers": Stat(0.0, 0.0, 0.0, "turnovers", name),
                "p_r": Stat(0.0, 0.0, 0.0, "P/R", name),
                "p_a": Stat(0.0, 0.0, 0.0, "P/A", name),
                "r_a": Stat(0.0, 0.0, 0.0, "R/A", name),
                "p_r_a": Stat(0.0, 0.0, 0.0, "P/R/A", name),
                "s_b": Stat(0.0, 0.0, 0.0, "S/B", name)
            }
            i = 0
            for market in prop['markets']:
                if market['id'] in altprops.keys():
                    while True and i < 10:
                        try:
                            lines[altprops[market['id']]].line = float(market['books'][i]['outcomes'][0]['total'])
                            lines[altprops[market['id']]].over = float(market['books'][i]['outcomes'][0]['odds_decimal'])
                            lines[altprops[market['id']]].under = float(market['books'][i]['outcomes'][1]['odds_decimal'])
                            break
                        except:
                            i += 1
                            continue;
            if i < 10:
                players.append(Player(name, prop['player']['id'], game.home, game.away, lines['points'], lines['rebounds'], lines['assists'], lines['threes'],lines['turnovers'], lines['steals'], lines['blocks'], lines['p_r'], lines['p_a'], lines['r_a'], lines['p_r_a'], lines['s_b']))
    print('\n')
    time.sleep(2.5)

    oldDate = currDate - 21
    if oldDate < 1:
        oldMonth = currMonth - 1
        oldDate += 30
        if oldMonth < 1:
            oldYear = currYear - 1
            oldMonth += 12
        else:
            oldYear = currYear
    else:
        oldMonth = currMonth
        oldYear = currYear


    print('-------------- Statistical Analysis of Recent Games --------------')
    driver = webdriver.Chrome()
    driver.get("https://www.fantasypros.com/daily-fantasy/nba/fanduel-defense-vs-position.php")
    button = driver.find_element(By.CLASS_NAME, "onetrust-close-btn-handler")
    while True:
        try:
            button.click()
            break
        except:
            print("Closing button on driver failed...")
    threads = []
    playerResults = []
    for player in players:
        thread = Thread(target=player_thread, args=(player, oldYear, oldMonth, oldDate, playerResults))
        threads.append(thread)
        thread.start()

    consumer = Thread(target=worker_thread, args=(playerResults, driver, overs, unders))
    consumer.start()
    
    for thread in threads:
        thread.join()
    global done
    done = True
    consumer.join()
    driver.close()
    print()

    overs = sorted(overs, key=attrgetter('hit', 'spread_diff'), reverse=True)
    unders = sorted(unders, key=attrgetter('hit', 'spread_diff'))

    print("************** Please wait, building the optimal ML model ***************")
    ML_dic = find_best_ML_models()
    over_model = ML_dic['over']
    under_model = ML_dic['under']

    file = open(f'/Users/rayani1203/Downloads/{currYear}-{currMonth}-{currDate-1}-picks.csv', 'w', encoding='UTF-8')
    writer  = csv.writer(file)
    header = ['Best Over Picks']
    header1 = ['Player', 'Stat', 'Line', 'Odds', 'Last 3W Hit Rate%', 'Last 3W% Above Line', 'Last 3W Avg', 'Opp. Defense vs Position in Stat', 'ML prediction %', 'Expected return', 'Bet (Y)?']
    writer.writerows([header, header1])

    print("--------------- Best Over Picks ---------------")
    print("Pick                    | Last 3W Hit Rate  | Last 3W % Above Line | Last 3W Avg  |  Opp. Defense vs Pos")
    print()
    for stat in overs:
        prediction_val = round(over_model.predict_proba([[stat_num[stat.stat], round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense]])[0][1]*100, 1)
        print(f"{stat.player} over {stat.line} {stat.stat} at {stat.over}        |    {round(stat.hit * 100, 1)}%     |    {round(((stat.spread_diff/ stat.line)-1)*100, 1)}%   |    {round(stat.spread_diff, 1)}     |     {stat.defense}")
        writer.writerow([stat.player, stat.stat, stat.line, stat.over, round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense, prediction_val, round(prediction_val/100*stat.over, 2)])

    writer.writerow([])
    header = ['Best Under Picks']
    header1 = ['Player', 'Stat', 'Line', 'Odds', 'Last 3W Hit Rate%', 'Last 3W% Above Line', 'Last 3W Avg', 'Opp. Defense vs Position in Stat', 'ML prediction %', 'Expected Return', 'Bet (Y)?']
    writer.writerows([header, header1])

    print()
    print("--------------- Best Under Picks ---------------")
    print("Pick                     | Last 3W Hit Rate  | Last 3W % Above Line | Last 3W Avg  |  Opp. Defense vs Pos")
    print()
    for stat in unders:
        prediction_val = round(under_model.predict_proba([[stat_num[stat.stat], round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense]])[0][1]*100, 1)
        print(f"{stat.player} under {stat.line} {stat.stat} at {stat.under}        |     {round(stat.hit * 100, 1)}%    |    {round(((stat.spread_diff/ stat.line)-1)*100, 1)}%  |    {round(stat.spread_diff, 1)}     |     {stat.defense}")
        writer.writerow([stat.player, stat.stat, stat.line, stat.under, round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense, prediction_val, round(prediction_val/100*stat.under, 2)])
    print()
    print("--------------- Downloaded your picks as picks.csv in Downloads! ----------------")
    print()
    file.close()

def analyze_row(row, won, lost, date):
    time.sleep(1)
    global balance
    success = False
    count = 0
    name_list = row[0].split()
    if len(name_list) < 2:
        return
    while not success and count < 3:
        try:            
            response = requests.get(f"https://api.balldontlie.io/v1/players/?first_name={name_list[0]}&last_name={name_list[1]}", headers={'Accept': 'application/json', 'Authorization': config.ball_key})
            res_json = response.json()
            success = True
        except:
            count += 1
            print("API request failed, trying again in 10 seconds")
            time.sleep(10)
    if count == 3:
        return
    all_data = res_json['data']
    if len(all_data) == 0:
        return
    data = all_data[0]
    player_id = data['id']
    success = False

    dateStr = str(date)
    if len(dateStr) < 2:
        dateStr = '0' + dateStr

    while not success:
        try:
            response = requests.get(f"https://api.balldontlie.io/v1/stats?player_ids[]={player_id}&start_date={currYear}-{currMonthStr}-{dateStr}&end_date={currYear}-{currMonthStr}-{dateStr}", headers={'Authorization': config.ball_key})
            res_json = response.json()
            success = True
        except:
            print("API request failed, trying again in 10 seconds")
            time.sleep(10)
    try:
        data = res_json['data'][0]
    except:
        print(f"Failed to retrieve data for {row[0]}, continuing...")
        return
    match row[1]:
        case 'points':
            row.append(data['pts'])
            if float(row[4]) >= 70:
                if data['pts'] > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if data['pts'] > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'assists':
            row.append(data['ast'])
            if float(row[4]) >= 70:
                if data['ast'] > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if data['ast'] > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'rebounds':
            row.append(data['reb'])
            if float(row[4]) >= 70:
                if data['reb'] > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if data['reb'] > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'threes':
            row.append(data['fg3m'])
            if float(row[4]) >= 70:
                if data['fg3m'] > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if data['fg3m'] > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'steals':
            row.append(data['stl'])
            if float(row[4]) >= 70:
                if data['stl'] > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if data['stl'] > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'blocks':
            row.append(data['blk'])
            if float(row[4]) >= 70:
                if data['blk'] > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if data['blk'] > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'turnovers':
            row.append(data['turnover'])
            if float(row[4]) >= 70:
                if data['turnover'] > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if data['turnover'] > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'S/B':
            row.append(data['stl'] + data['blk'])
            if float(row[4]) >= 70:
                if (data['stl'] + data['blk']) > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if (data['stl'] + data['blk']) > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'P/R':
            row.append(data['pts'] + data['reb'])
            if float(row[4]) >= 70:
                if (data['pts'] + data['reb']) > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if (data['pts'] + data['reb']) > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'P/A':
            row.append(data['pts'] + data['ast'])
            if float(row[4]) >= 70:
                if (data['pts'] + data['ast']) > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if (data['pts'] + data['ast']) > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'R/A':
            row.append(data['ast'] + data['reb'])
            if float(row[4]) >= 70:
                if (data['reb'] + data['ast']) > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if (data['reb'] + data['ast']) > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)
        case 'P/R/A':
            row.append(data['pts'] + data['reb'] + data['ast'])
            if float(row[4]) >= 70:
                if (data['pts'] + data['reb'] + data['ast']) > float(row[2]):
                    won.append(row)
                    balance += (float(row[3]) - 1)
                else:
                    lost.append(row)
            else:
                if (data['pts'] + data['reb'] + data['ast']) > float(row[2]):
                    lost.append(row)
                else:
                    won.append(row)
                    balance += (float(row[3]) - 1)

def analyze_past_picks():
    global balance
    won = []
    lost = []
    file = open(f'/Users/rayani1203/Downloads/{currYear}-{currMonth}-{currDate-2}-picks.csv', encoding='UTF-8')
    reader  = csv.reader(file)
    for row in reader:
        print(row)
        if row[0] == 'Pick Results:':
            break
        if len(row) < 8:
            continue
        if row[10].capitalize() == 'Y':
            analyze_row(row, won, lost, currDate-2)
    file.close()
    file = open(f'/Users/rayani1203/Downloads/{currYear}-{currMonth}-{currDate-2}-picks.csv', 'a')
    
    writer = csv.writer(file)
    writer.writerow([])
    balance -= len(lost)
    writer.writerow(['Pick Results:', f'Net: {round(balance, 2)} units'])
    writer.writerow(['Winning Bets:'])
    for row in won:
        if float(row[4]) >= 70:
            row.insert(1, 'over')
        else:
            row.insert(1, 'under')
        writer.writerow(row)
    writer.writerow([])
    writer.writerow(['Losing Bets:'])
    for row in lost:
        if float(row[4]) >= 70:
            row.insert(1, 'over')
        else:
            row.insert(1, 'under')
        writer.writerow(row)

    file.close()

def add_dataset():
    date = input("Enter the date of the sheet (this month) you'd like to add to the allpicks database\n")
    while not date.isdigit() or int(date) > 31 or int(date) < 1:
        date = input("Please enter a valid numerical value for the date to be analyzed\n")
    while not os.path.isfile(f"/Users/rayani1203/Downloads/{currYear}-{currMonth}-{date}-picks.csv"):
        date = input("The specified date does not exist as a sheet, please enter another\n")

    file = open(f"/Users/rayani1203/Downloads/{currYear}-{currMonth}-{date}-picks.csv", 'r')
    reader  = csv.reader(file)
    oversfile = open("/Users/rayani1203/Downloads/alloverpicks.csv", "a", )
    overswriter = csv.writer(oversfile)
    undersfile = open("/Users/rayani1203/Downloads/allunderpicks.csv", "a", )
    underswriter = csv.writer(undersfile)

    won = []
    lost = []

    for row in reader:
        if len(row) < 1:
            continue
        if row[0] == 'Pick Results:':
            break
        if len(row) < 8:
            continue
        print(row)
        analyze_row(row, won, lost, date)
    
    overswriter.writerow([])
    underswriter.writerow([])
    
    for row in won:
        del row[3]
        del row[0]
        del row[1]
        row.pop()
        row.pop()
        row.pop()
        row[0] = stat_num[row[0]]
        row.append('1')
        if float(row[1]) >= 70:
            overswriter.writerow(row)
        else:
            underswriter.writerow(row)
    for row in lost:
        del row[3]
        del row[0]
        del row[1]
        row.pop()
        row.pop()
        row.pop()
        row[0] = stat_num[row[0]]
        row.append('0')
        if float(row[1]) >= 70:
            overswriter.writerow(row)
        else:
            underswriter.writerow(row)


input("Hello and welcome to Rayan's Odds Analyzer, your friendly neighborhood script designed to help you beat the odds every day!\nTo continue, press Enter.\n")
res = input("Select whether you'd like to analyze future odds(f), analyze returns on past picks(p), or add a previous dataset to the learning database(a)\n")
match res:
    case 'f':
        analyze_future_odds()
    case 'p':
        analyze_past_picks()
    case 'a':
        add_dataset()