import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn import tree
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import (ExtraTreesClassifier, RandomForestClassifier,
                              AdaBoostClassifier, GradientBoostingClassifier)
import pandas as pd
import psycopg2
import psycopg2.extras
import random
from sklearn.grid_search import GridSearchCV
from sklearn.model_selection import train_test_split

def get_data_array(df, index):
    question_id = df.id[index]
    # data_array = [df.ques_length[index], df.ques_score[index], df.stat_length[index], df.noun[index], df.verb[index], df.adj[index], df.speaker_half_match[index], df.speaker_full_match[index],
    # df.matching_score[index], df.highest_noun[index], df.second_noun[index], df.highest_verb[index], df.second_verb[index], df.highest_adj[index], df.second_adj[index],
    # df.sum_other[index], df.person_entity[index], df.gpe_entity[index], df.person_entity_match[index], df.gpe_entity_match[index], df.org_entity[index], df.org_entity_match[index],
    # df.full_other_match[index], df.summary_score[index]]
    data_array = [df.ques_length[index], df.stat_length[index], df.noun[index], df.verb[index], df.adj[index], df.speaker_half_match[index],
    df.matching_score[index], df.highest_noun[index], df.second_noun[index], df.third_noun[index], df.fourth_noun[index], df.highest_verb[index],
    df.second_verb[index], df.third_verb[index], df.highest_adj[index], df.second_adj[index], df.person_entity_match[index], df.gpe_entity_match[index], df.org_entity_match[index],
    df.full_other_match[index]]
    return (question_id, data_array)

def main():
    # def classify(X_train, y_train):
    classifiers = [
        # SVC(kernel="linear", C=0.02),
        # SVC(kernel="linear", C=0.05),
        # SVC(kernel="linear", C=0.03),
        SVC(kernel="linear", C=0.025),
        # SVC(kernel="linear", C=0.02),
        # SVC(kernel="linear", C=0.015),
        # svm.SVC(gamma=0.001, C=100.),
        # KNeighborsClassifier(3),
        #
        # DecisionTreeClassifier(max_depth=5),
        # # RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
        # # MLPClassifier(alpha=1),
        AdaBoostClassifier(),
        # # GaussianNB(),
        tree.DecisionTreeClassifier(),
        # # QuadraticDiscriminantAnalysis(),
        MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1),
        # #GaussianProcessClassifier(1.0 * RBF(1.0)),
        # MultinomialNB()
        #SGDClassifier(loss="hinge", penalty="l2")
    ]
    #classifiers = svm.SVC(gamma=0.001, C=100.)
    #classifiers = SVC(kernel="linear", C=0.03)
    # models1 = {
    #     'ExtraTreesClassifier': ExtraTreesClassifier(),
    #     'RandomForestClassifier': RandomForestClassifier(),
    #     'AdaBoostClassifier': AdaBoostClassifier(),
    #     'GradientBoostingClassifier': GradientBoostingClassifier(),
    #     'SVC': SVC()
    # }
    # params1 = {
    #     'ExtraTreesClassifier': { 'n_estimators': [16, 32] },
    #     'RandomForestClassifier': { 'n_estimators': [16, 32] },
    #     'AdaBoostClassifier':  { 'n_estimators': [16, 32] },
    #     'GradientBoostingClassifier': { 'n_estimators': [16, 32], 'learning_rate': [0.8, 1.0] },
    #     'SVC': [
    #         {'kernel': ['linear'], 'C': [1, 10]},
    #         {'kernel': ['rbf'], 'C': [1, 10], 'gamma': [0.001, 0.0001]},
    #     ]
    # }
    conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "select * from train_set"
    df = pd.read_sql_query(query, conn)
    # total_X = []
    # total_y = []
    # for index in range(df.shape[0]):
    #     label = df.label[index]
    #     data_array = [df.ques_length[index], df.ques_score[index], df.stat_length[index], df.noun[index], df.verb[index], df.adj[index], df.speaker_half_match[index], df.speaker_full_match[index],
    #     df.matching_score[index], df.highest_noun[index], df.second_noun[index], df.highest_verb[index], df.second_verb[index], df.highest_adj[index], df.second_adj[index],
    #     df.sum_other[index], df.person_entity[index], df.gpe_entity[index], df.person_entity_match[index], df.gpe_entity_match[index], df.org_entity[index], df.org_entity_match[index],
    #     df.full_other_match[index], df.summary_score[index]]
    #     total_X.append(data_array)
    #     total_y.append(label)
    #
    # X_train, X_test, y_train, y_test= train_test_split(total_X, total_y, test_size=0.2)

    X_test = []
    y_test = []
    X_train = []
    y_train = []
    X_id = []
    for index in range(df.shape[0]):
        id = df.id[index]
        data_array = [df.ques_length[index], df.ques_score[index], df.stat_length[index], df.noun[index], df.verb[index], df.adj[index], df.speaker_half_match[index], df.speaker_full_match[index],
        df.matching_score[index], df.highest_noun[index], df.second_noun[index], df.highest_verb[index], df.second_verb[index], df.highest_adj[index], df.second_adj[index],
        df.sum_other[index], df.person_entity[index], df.gpe_entity[index], df.person_entity_match[index], df.gpe_entity_match[index], df.org_entity[index], df.org_entity_match[index],
        df.full_other_match[index], df.summary_score[index]]

        if id >=2018 and id <= 2850:
            X_id.append(id)
            X_test.append(data_array)
            y_test.append(df.label[index])
        else:
            X_train.append(data_array)
            y_train.append(df.label[index])

    for  clf in classifiers:
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)
        result = clf.predict(X_test)
        # score = clf.score(X_train, y_train)
        # result = clf.predict(X_train)

        true_positive = 0
        false_positive = 0
        true_negative = 0
        false_negative = 0

        for i in range(len(result)):
            if result[i] == y_test[i]:
            # if result[i] == y_test[i]:
                if result[i] == 1:
                    true_positive += 1
                else:
                    true_negative += 1
            else:
                if result[i] == 1:
                    # print ("false pos")
                    # print (X_train[i])
                    # print (i + 576)
                    false_positive += 1

                else:
                    # print ("false neg")
                    # print (X_train[i])
                    # print (i + 572)
                    false_negative += 1
        try:
            precision = float(true_positive) / (true_positive + false_positive)
            recall = float(true_positive) / (true_positive + false_negative)
            # precision is reported, correct positive / overall true positive
            # recall is reported, correct positive / overall reported positive.
        except ZeroDivisionError:
            print "zero"
        # print (clf)
        # print precision
        # print recall
        # print score
        # print " ===== "
    # helper1 = EstimatorSelectionHelper(models1, params1)
    # helper1.fit(X_train, y_train, scoring='f1', n_jobs=-1)
    #
    # count = 0
    # classifiers.fit(X_train, y_train)
    # score = classifiers.score(X_test, y_test)
    # result = classifiers.predict(X_test)
    #
    # true_positive = 0
    # false_positive = 0
    # true_negative = 0
    # false_negative = 0
    #
    # for i in range(len(result)):
    #     if result[i] == y_test[i]:
    #         if result[i] == 1:
    #             true_positive += 1
    #         else:
    #             true_negative += 1
    #     else:
    #         if result[i] == 1:
    #             false_positive += 1
    #             print ("false positive")
    #             print i + 1
    #         else:
    #             false_negative += 1
    #             print ("false negative")
    #             print i + 1
    # precision = float(true_positive) / (true_positive + false_positive)
    # recall = float(true_positive) / (true_positive + false_negative)
    # print precision
    # print recall
    # print score


# print helper1.score_summary(sort_by='min_score')
