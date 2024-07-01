import requests
import time
from threading import Lock
from datetime import datetime
from calendar import monthrange

import config

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
ballMutex = Lock()
countLock = Lock()
global counter
counter = 0
global done
done = False
balance = 0.0

if datetime.now().hour >= 17:
    currDate = datetime.now().day + 2
else:
    currDate = datetime.now().day + 1
currMonth = datetime.now().month
currYear = datetime.now().year

monthLength = monthrange(currYear, currMonth)[1]
if currDate > monthLength:
    currMonth += 1
    currDate -= monthLength

currDateStr = str(currDate)
currMonthStr = str(currMonth)
if currDate - 1 < 1:
    prevDateStr = str(currDate + 29)
else:
    prevDateStr = str(currDate - 1)
if currDate < 10:
    currDateStr = '0' + currDateStr
    if currDate - 1 >= 1:
        prevDateStr = '0' + prevDateStr
if currMonth < 10:
    currMonthStr = '0' + currMonthStr

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
            with ballMutex:
                response = requests.get(f"https://api.balldontlie.io/v1/players/?first_name={name_list[0]}&last_name={name_list[1]}", headers={'Accept': 'application/json', 'Authorization': config.ball_key})
                res_json = response.json()
                success = True
        except:
            count += 1
            print("BDL API request failed, trying again in 10 seconds")
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
            with ballMutex:
                response = requests.get(f"https://api.balldontlie.io/v1/stats?player_ids[]={player_id}&start_date={currYear}-{currMonthStr}-{dateStr}&end_date={currYear}-{currMonthStr}-{dateStr}", headers={'Authorization': config.ball_key})
                res_json = response.json()
                success = True
        except:
            print("BDL API request failed, trying again in 10 seconds")
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
