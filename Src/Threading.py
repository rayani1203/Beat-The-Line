import time
import requests
import config
from selenium.webdriver.common.by import By

from Definitions import *
from Crawler import *

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
            with ballMutex:
                time.sleep(2)
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
            with ballMutex:
                time.sleep(2)
                response = requests.get(f"https://api.balldontlie.io/v1/stats?player_ids[]={player.id}&start_date={oldYear}-{oldMonthStr}-{oldDateStr}", headers={'Authorization': config.ball_key})
                res_json = response.json()
                success = True
        except:
            print("BDL API request failed, trying again in 10 seconds")
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
        # if len(defenses) > 0:
            # if defenses.count(defenses[0]) > 5:
            #     print("------------------ Web crawling error, restarting script... ------------------")
            #     print(defenses)
            #     driver.close()
            #     return analyze_future_odds()
