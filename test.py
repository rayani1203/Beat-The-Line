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

best_over_model = DecisionTreeClassifier()
best_under_model = DecisionTreeClassifier()

over_accuracy = 0
max_depth = 1
best_over_depth = 0
max_over_accuracy = 0
min_samples = 1
best_over_samples = 0
while max_depth < 50:
    min_samples = 1
    while min_samples < 60:
        overdtree = DecisionTreeClassifier(criterion='gini', min_samples_leaf=min_samples, max_depth=max_depth)
        overdtree = overdtree.fit(overstats_train, overresults_train)
        over_predictions = overdtree.predict(overstats_test)
        over_accuracy = accuracy_score(over_predictions, overresults_test)*100

        if over_accuracy > max_over_accuracy:
            best_over_model = overdtree
            max_over_accuracy = over_accuracy
            best_over_samples = min_samples
            if max_depth != best_over_depth:
                best_over_depth = max_depth

        min_samples += 1
    max_depth += 1

under_accuracy = 0
max_depth = 5
best_under_depth = 0
max_under_accuracy = 0
min_samples = 1
best_under_samples = 0
while max_depth < 50:
    min_samples = 1
    while min_samples < 60:
        underdtree = DecisionTreeClassifier(criterion='gini', min_samples_leaf=min_samples, max_depth=max_depth)
        underdtree = underdtree.fit(understats_train, underresults_train)
        under_predictions = underdtree.predict(understats_test)
        under_accuracy = accuracy_score(under_predictions, underresults_test)*100

        if under_accuracy > max_under_accuracy:
            best_under_model = underdtree
            max_under_accuracy = under_accuracy
            best_under_samples = min_samples
            if max_depth != best_under_depth:
                best_under_depth = max_depth
                
        min_samples += 1
    max_depth += 1

print("Over accuracy is: ", max_over_accuracy, " at depth: ", best_over_depth, " and samples: ", best_over_samples)
print("Under accuracy is: ", max_under_accuracy, " at depth: ", best_under_depth, " and samples: ", best_under_samples)

tree.plot_tree(best_over_model, feature_names=stat_headers)
plt.savefig("/Users/rayani1203/Downloads/overdecisiontree.pdf")

tree.plot_tree(best_under_model, feature_names=stat_headers)
plt.savefig("/Users/rayani1203/Downloads/overdecisiontree.pdf")