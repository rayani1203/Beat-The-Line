import pandas
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

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
    best_over_depth = 5
    best_over_samples = 1
    second_over_depth = 5
    second_over_samples = 1
    retry_count = 0
    over_accuracy = 0
    while retry_count < 5 and second_over_depth == 5 or second_over_samples == 1:
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
                    second_over_samples = best_over_samples
                    best_over_samples = min_samples
                    if max_depth != best_over_depth:
                        second_over_depth = best_over_depth
                        best_over_depth = max_depth

                min_samples += 1
            max_depth += 1
        retry_count += 1

    retry_count = 0
    under_accuracy = 0
    best_under_depth = 5
    best_under_samples = 1
    second_under_depth = 5
    second_under_samples = 1
    max_under_accuracy = 0
    while retry_count < 5 and second_under_depth == 5 and second_under_samples == 1:
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
                    second_under_samples = best_under_samples
                    best_under_samples = min_samples
                    if max_depth != best_under_depth:
                        second_under_depth = best_under_depth
                        best_under_depth = max_depth

                min_samples += 1
            max_depth += 1
        retry_count += 1

    print("Over accuracy is: ", max_over_accuracy, " at depth: ", best_over_depth, " and samples: ", best_over_samples, "\nand second is: ", second_over_depth, " and: ", second_over_samples)
    print("Under accuracy is: ", max_under_accuracy, " at depth: ", best_under_depth, " and samples: ", best_under_samples, "\nand second is: ", second_under_depth, " and: ", second_under_samples)

    best_over_model = DecisionTreeClassifier(criterion='gini', min_samples_leaf=best_over_samples, max_depth=best_over_depth, random_state=0)
    best_over_model = best_over_model.fit(overstats.values, overresults)
    second_over_model = DecisionTreeClassifier(criterion='gini', min_samples_leaf=second_over_samples, max_depth=second_over_depth, random_state=0)
    second_over_model = second_over_model.fit(overstats.values, overresults)

    best_under_model = DecisionTreeClassifier(criterion='gini', min_samples_leaf=best_under_samples, max_depth=best_under_depth, random_state=0)
    best_under_model = best_under_model.fit(understats.values, underresults)
    second_under_model = DecisionTreeClassifier(criterion='gini', min_samples_leaf=second_under_samples, max_depth=second_under_depth, random_state=0)
    second_under_model = second_under_model.fit(understats.values, underresults)

    tree.plot_tree(best_over_model, feature_names=stat_headers)
    plt.savefig("/Users/rayani1203/Downloads/overdecisiontree.pdf")

    tree.plot_tree(best_under_model, feature_names=stat_headers)
    plt.savefig("/Users/rayani1203/Downloads/underdecisiontree.pdf")

    return {
        "over": best_over_model,
        "second_over": second_over_model,
        "under": best_under_model,
        "second_under": second_under_model
    }
