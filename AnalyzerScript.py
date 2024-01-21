import requests
from datetime import date, datetime
import time
from operator import attrgetter
import csv
import config

class Matchup:
    def __init__(self, home, home_id, away, away_id, id):
        self.home = home
        self.home_id = home_id
        self.away = away
        self.away_id = away_id
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

class Player:
    def __init__(self, name, id, points, rebounds, assists, threes, turnovers, steals, blocks, p_r, p_a, r_a, p_r_a, s_b):
        self.name = name
        self.id = id
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

games = []
players = []
overs = []
unders = []

if datetime.now().hour >= 17:
    currDate = datetime.now().day + 2
else:
    currDate = datetime.now().day + 1
currMonth = datetime.now().month
currYear = datetime.now().year

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

def analyze_future_odds():
    response = requests.get(f"https://api.sportradar.us/oddscomparison-player-props/trial/v2/en/competitions/sr:competition:132/schedules.json?api_key={config.nba_key}", headers={'Accept': 'application/json'})
    res_json = response.json()
    print('Today\'s games are:')
    for game in res_json['schedules']:
        if game['sport_event']['start_time'][8:10] == str(currDate):
            print(game['sport_event']['competitors'][0]['name'], "vs", game['sport_event']['competitors'][1]['name'])
            games.append(Matchup(game['sport_event']['competitors'][0]['name'], game['sport_event']['competitors'][0]['id'], game['sport_event']['competitors'][1]['name'], game['sport_event']['competitors'][1]['id'], game['sport_event']['id']))
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
            for market in prop['markets']:
                if market['id'] in altprops.keys():
                    lines[altprops[market['id']]].line = float(market['books'][0]['outcomes'][0]['total'])
                    lines[altprops[market['id']]].over = float(market['books'][0]['outcomes'][0]['odds_decimal'])
                    lines[altprops[market['id']]].under = float(market['books'][0]['outcomes'][1]['odds_decimal'])
            players.append(Player(name, prop['player']['id'], lines['points'], lines['rebounds'], lines['assists'], lines['threes'],lines['turnovers'], lines['steals'], lines['blocks'], lines['p_r'], lines['p_a'], lines['r_a'], lines['p_r_a'], lines['s_b']))
    print('\n')
    time.sleep(5)

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
    for player in players:
        success = False
        while not success:
            try:
                response = requests.get(f"https://www.balldontlie.io/api/v1/players/?search={player.name}", headers={'Accept': 'application/json'})
                res_json = response.json()
                success = True
            except:
                print("API request failed, trying again in 10 seconds")
                time.sleep(10)
        all_data = res_json['data']
        if len(all_data) == 0:
            continue
        data = all_data[0]
        player.id = data['id']
        player.team = data['team']['full_name']
        print(f'Analyzing stats for {player.name} of the {player.team}...')

        success = False
        while not success:
            try:
                response = requests.get(f"https://www.balldontlie.io/api/v1/stats?player_ids[]={player.id}&start_date={oldYear}-{oldMonth}-{oldDate}")
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

        if game_count < 5:
            continue

        for stat in player.stats:
            player.stats[stat] /= game_count
            getattr(player, stat).hit /= game_count
            if getattr(player, stat).line == 0.0:
                continue
            if getattr(player, stat).hit >= 0.7:
                getattr(player, stat).spread_diff = player.stats[stat] 
                overs.append(getattr(player, stat))
            if getattr(player, stat).hit <= 0.3:
                getattr(player, stat).spread_diff = player.stats[stat]
                unders.append(getattr(player, stat))
    time.sleep(5)  
    print()  

    overs = sorted(overs, key=attrgetter('hit', 'spread_diff'), reverse=True)
    unders = sorted(unders, key=attrgetter('hit', 'spread_diff'))

    file = open(f'/Users/rayani1203/Downloads/{currYear}-{currMonth}-{currDate-1}-picks.csv', 'w', encoding='UTF-8')
    writer  = csv.writer(file)
    header = ['Best Over Picks']
    header1 = ['Player', 'Stat', 'Line', 'Odds', 'Last 3W Hit Rate%', 'Last 3W% Above Line', 'Last 3W Avg', 'Bet (Y)?']
    writer.writerows([header, header1])

    print("--------------- Best Over Picks ---------------")
    print("Pick                    | Last 3W Hit Rate  | Last 3W % Above Line | Last 3W Avg")
    print()
    for stat in overs:
        print(f"{stat.player} over {stat.line} {stat.stat} at {stat.over}        |    {round(stat.hit * 100, 1)}%     |    {round(((stat.spread_diff/ stat.line)-1)*100, 1)}%   |    {round(stat.spread_diff, 1)}")
        writer.writerow([stat.player, stat.stat, stat.line, stat.over, round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1)])

    writer.writerow([])
    header = ['Best Under Picks']
    header1 = ['Player', 'Stat', 'Line', 'Odds', 'Last 3W Hit Rate%', 'Last 3W% Above Line', 'Last 3W Avg', 'Bet (Y)?']
    writer.writerows([header, header1])

    print()
    print("--------------- Best Under Picks ---------------")
    print("Pick                     | Last 3W Hit Rate  | Last 3W % Above Line | Last 3W Avg")
    print()
    for stat in unders:
        print(f"{stat.player} under {stat.line} {stat.stat} at {stat.under}        |     {round(stat.hit * 100, 1)}%    |    {round(((stat.spread_diff/ stat.line)-1)*100, 1)}%  |    {round(stat.spread_diff, 1)}")
        writer.writerow([stat.player, stat.stat, stat.line, stat.under, round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1)])

    print()
    print("--------------- Downloaded your picks as picks.csv in Downloads! ----------------")
    print()

    file.close()

def analyze_past_picks():
    picked_balance = 0.0
    total_balance = 0.0
    file = open(f'/Users/rayani1203/Downloads/{currYear}-{currMonth}-{currDate-2}-picks.csv', encoding='UTF-8')
    reader  = csv.reader(file)
    for row in reader:
        success = False
        while not success:
            try:
                response = requests.get(f"https://www.balldontlie.io/api/v1/players/?search={row[0]}", headers={'Accept': 'application/json'})
                res_json = response.json()
                success = True
            except:
                print("API request failed, trying again in 10 seconds")
                time.sleep(10)
        all_data = res_json['data']
        if len(all_data) == 0:
            continue
        data = all_data[0]
        player_id = data['id']
        success = False
        while not success:
            try:
                response = requests.get(f"https://www.balldontlie.io/api/v1/stats?player_ids[]={player_id}&start_date={currYear}-{currMonth}-{currDate-2}")
                res_json = response.json()
                success = True
            except:
                print("API request failed, trying again in 10 seconds")
                time.sleep(10)
        data = res_json['data'][0]
        # if row[4] >= 70:
        #     if row[1] == 'points':
                
        # elif row[4] <= 30:

        # if row[7].capitalize() == 'Y':



input("Hello and welcome to Rayan's Odds Analyzer, your friendly neighborhood script designed to help you beat the odds every day!\nTo continue, press Enter.\n")
res = input("Select whether you'd like to analyze future odds(f), or analyze returns on past picks(p)\n")
match res:
    case 'f':
        analyze_future_odds()
    case 'p':
        analyze_past_picks()