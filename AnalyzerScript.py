import requests
import time
from operator import attrgetter
import csv
import config
import os
from threading import Thread

from Src.Definitions import *
from Src.MLModel import *
from Src.Crawler import *
from Src.Threading import *

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

    if len(players) == 0:
        print('---------------------- No games today, come back again tomorrow! -----------------------')
        return

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
    second_over_model = ML_dic['second_over']
    second_under_model = ML_dic['second_under']

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
        second_prediction = round(second_over_model.predict_proba([[stat_num[stat.stat], round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense]])[0][1]*100, 1)
        average_prediction = round((prediction_val+second_prediction)/2.0, 2)
        print(f"{stat.player} over {stat.line} {stat.stat} at {stat.over}        |    {round(stat.hit * 100, 1)}%     |    {round(((stat.spread_diff/ stat.line)-1)*100, 1)}%   |    {round(stat.spread_diff, 1)}     |     {stat.defense}")
        row = [stat.player, stat.stat, stat.line, stat.over, round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense, average_prediction, round(average_prediction/100*stat.over, 2)]
        if round(average_prediction/100*stat.over, 2) >= 1:
            row.append('y')
        writer.writerow(row)

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
        second_prediction = round(second_under_model.predict_proba([[stat_num[stat.stat], round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense]])[0][1]*100, 1)
        average_prediction = round((prediction_val + second_prediction)/2.0, 2)
        print(f"{stat.player} under {stat.line} {stat.stat} at {stat.under}        |     {round(stat.hit * 100, 1)}%    |    {round(((stat.spread_diff/ stat.line)-1)*100, 1)}%  |    {round(stat.spread_diff, 1)}     |     {stat.defense}")
        row = [stat.player, stat.stat, stat.line, stat.under, round(stat.hit * 100, 1), round(((stat.spread_diff/ stat.line)-1)*100, 1), round(stat.spread_diff, 1), stat.defense, average_prediction, round(average_prediction/100*stat.under, 2)]
        if round(average_prediction/100*stat.under, 2) >= 1:
            row.append('y')
        writer.writerow(row)
    print()
    print("--------------- Downloaded your picks as picks.csv in Downloads! ----------------")
    print()
    file.close()


def analyze_past_picks():
    global balance
    balance = 0.0
    won = []
    lost = []
    file = open(f'/Users/rayani1203/Downloads/{currYear}-{currMonth}-{currDate-2}-picks.csv', encoding='UTF-8')
    reader  = csv.reader(file)
    for row in reader:
        print(row)
        if len(row) < 1:
            continue
        if row[0] == 'Pick Results:':
            break
        if len(row) < 11:
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
    global balance
    balance = 0.0

    for row in reader:
        if len(row) < 1:
            continue
        if row[0] == 'Pick Results:':
            break
        if len(row) < 8:
            continue
        while len(row) > 11:
            row.pop()
        print(row)
        analyze_row(row, won, lost, date)

    file.close()
    file = open(f"/Users/rayani1203/Downloads/{currYear}-{currMonth}-{date}-picks.csv", 'a')
    writer = csv.writer(file)
    overswriter.writerow([])
    underswriter.writerow([])

    for row in won:
        del row[3]
        del row[0]
        del row[1]
        row.pop()
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
        balance -= 1
        del row[3]
        del row[0]
        del row[1]
        row.pop()
        row.pop()
        row.pop()
        row.pop()
        row[0] = stat_num[row[0]]
        row.append('0')
        if float(row[1]) >= 70:
            overswriter.writerow(row)
        else:
            underswriter.writerow(row)
    
    writer.writerows([[], ["Net results of all picks:", balance]])
    file.close()
    undersfile.close()
    oversfile.close()


input("Hello and welcome to Rayan's Odds Analyzer, your friendly neighborhood script designed to help you beat the odds every day!\nTo continue, press Enter.\n")
res = input("Select whether you'd like to analyze future odds(f), analyze returns on past picks(p), or add a previous dataset to the learning database(a)\n")
match res:
    case 'f':
        analyze_future_odds()
    case 'p':
        analyze_past_picks()
    case 'a':
        add_dataset()
    case 'm':
        find_best_ML_models()