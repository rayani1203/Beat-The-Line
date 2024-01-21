import csv

file = open('/Users/rayani1203/Downloads/picks.csv', 'w', encoding='UTF-8')
writer  = csv.writer(file)
header = ['Best Over Picks']
header1 = ['Player', 'Stat', 'Line', 'Odds', 'Last 3W Hit Rate', 'Last 3W% Above Line', 'Last 3W% Avg']
writer.writerows([header, header1])