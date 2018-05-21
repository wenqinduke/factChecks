import main
import gensim
import time
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import ml
import random
from sklearn.ensemble import (ExtraTreesClassifier, RandomForestClassifier,
                              AdaBoostClassifier, GradientBoostingClassifier)
import matplotlib.pyplot as plt
from itertools import cycle
from sklearn.metrics import roc_curve, auc
from scipy import interp
from sklearn.preprocessing import label_binarize
from sklearn import metrics
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score

# test_id_region = random.sample(list(range(1,112,1)), 22)
#print test_id_region
test_id_region = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

def get_classifier(df_train):
    y_train = []
    X_train = []
    X_test = []
    y_test = []
    for index in range(df_train.shape[0]):
        (question_id, data_array) = ml.get_data_array(df_train, index)

        if question_id not in test_id_region:
            X_train.append(data_array)
            y_train.append(df_train.label[index])
    classifiers = AdaBoostClassifier()
    #classifiers = SVC(kernel="linear", C=0.02)
    classifiers = classifiers.fit(X_train, y_train)
    score = classifiers.score(X_train, y_train)
    print score
    return classifiers

#initialization; get data from database.
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query_fact = "select id, statement, speaker, speaker_title from facts"
query_questions = "select stat_id, id, question, potential_id, final_mod_potential_id from test_questions"
query_train = "select * from train_set_all"
#query_train = "select * from train_set_30"
#query_train = "select * from train_set_300"
df_facts = pd.read_sql_query(query_fact, conn)
df_ques = pd.read_sql_query(query_questions, conn)
df_train = pd.read_sql_query(query_train, conn)
clf = get_classifier(df_train)
model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s


y_score = []
y_test = []

#Iterate through test questions
n = 0
for index in range(df_ques.shape[0]):
    id = df_ques.id[index]
    if id not in test_id_region:
        continue
    #print (id)
    question = df_ques.question[index]
    stat_id = df_ques.stat_id[index]
    potential_id = df_ques.potential_id[index]
    #final_mod_potential_id: To balance the positive/negative dataset, I chose some negative examples that are easy to be confused with positive cases, along with all positive cases.
    #final_mod_potential_id = df_ques.final_mod_potential_id[index]
    if potential_id is None:
        continue
    (index_list, match_list, y_score, y_test) = main.check(question, model, potential_id, df_facts, conn, clf, y_score, y_test, stat_id)
    #print index_list
    n += 1

    # cursor.execute('''UPDATE test_questions SET match_id_adaboost_30= (%s) where id = (%s)''',  (index_list, id))
    # cursor.execute('''UPDATE test_questions SET match_id_adaboost= (%s) where id = (%s)''',  (index_list, id))
    cursor.execute('''UPDATE test_questions SET match_id_adaboost_all= (%s) where id = (%s)''',  (index_list, id))
    conn.commit()


def plot_graph(y_score, y_test):

    average_precision = average_precision_score(y_test, y_score)
    print('Average precision-recall score: {0:0.2f}'.format(average_precision))
    precision, recall, _ = precision_recall_curve(y_test, y_score)
    plt.figure()
    plt.step(recall, precision, color='b', alpha=0.2,
         where='post')
    plt.fill_between(recall, precision, step='post', alpha=0.2,
                 color='b')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('2-class Precision-Recall curve: AP={0:0.2f}'.format(
          average_precision))
    plt.show()

plot_graph(y_score, y_test)
conn.close()
