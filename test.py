import pandas
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

overdf = pandas.read_csv("/Users/rayani1203/Downloads/alloverpicks.csv")
underdf = pandas.read_csv("/Users/rayani1203/Downloads/allunderpicks.csv")

stat_headers = ['Stat Key', 'Hit Rate', '3W% vs Spread', '3W Average', 'Defense Rank']

overstats = overdf[stat_headers]
overresults = overdf['Hit?']

understats = underdf[stat_headers]
underresults = underdf['Hit?']

overstats_train, overstats_test, overresults_train, overresults_test = train_test_split(overstats, overresults, test_size=0.2)
understats_train, understats_test, underresults_train, underresults_test = train_test_split(understats, underresults, test_size=0.2)

overdtree = DecisionTreeClassifier(criterion='gini')
overdtree = overdtree.fit(overstats_train, overresults_train)
tree.plot_tree(overdtree, feature_names=stat_headers)
plt.savefig("/Users/rayani1203/Downloads/overdecisiontree.pdf")
over_predictions = overdtree.predict(overstats_test)


underdtree = DecisionTreeClassifier(criterion='gini')
underdtree = underdtree.fit(understats_train, underresults_train)
tree.plot_tree(underdtree, feature_names=stat_headers)
plt.savefig("/Users/rayani1203/Downloads/underdecisiontree.pdf")
under_predictions = underdtree.predict(understats_test)

print("Over accuracy is: ", accuracy_score(over_predictions, overresults_test)*100)
print("Under accuracy is: ", accuracy_score(under_predictions, underresults_test)*100)