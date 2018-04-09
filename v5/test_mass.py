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

test_id_region = random.sample(list(range(1,112,1)), 22)
def get_classifier(df_train):
    y_train = []
    X_train = []
    X_test = []
    y_test = []
    for index in range(df_train.shape[0]):
        (question_id, data_array) = ml.get_data_array(df_train, index)

        # if question_id <= 20:
        #     X_test.append(data_array)
        #     y_test.append(df_train.label[index])
        #else:
        if question_id not in test_id_region:
            X_train.append(data_array)
            y_train.append(df_train.label[index])

    classifiers = SVC(kernel="linear", C=0.025)
    classifiers.fit(X_train, y_train)
    score = classifiers.score(X_train, y_train)
    print score
    return classifiers

model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = "select id, statement, speaker, speaker_title from facts"
dataframe = pd.read_sql_query(query, conn)
query2 = "select stat_id, id, question, potential_id from test_questions"
df = pd.read_sql_query(query2, conn)

query_train = "select * from train_set"
df_train = pd.read_sql_query(query_train, conn)
clf = get_classifier(df_train)

# drop_table_result = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS match_id_adaboost, DROP COLUMN IF EXISTS match_list_adaboost'''
# add_table_result = ''' ALTER TABLE test_questions ADD COLUMN match_id_adaboost integer[], ADD COLUMN match_list_adaboost text[] '''
# cursor.execute(drop_table_result)
# cursor.execute(add_table_result)

false_positive = []
false_negative = []
true_positive = []

for index in range(df.shape[0]):
    id = df.id[index]
    print (id)
    if id not in test_id_region:
        continue
    question = df.question[index]
    potential_id = df.potential_id[index]
    if potential_id is None:
        continue
    t0 = time.time()
    (index_list, match_list) = main.check(question, model, potential_id, dataframe, conn, clf)

    #cursor.execute('''UPDATE test_questions SET match_id = (%s), match_list = (%s) where id = (%s)''',  (index_list, match_list, id))
    cursor.execute('''UPDATE test_questions SET match_id = (%s), match_list = (%s) where id = (%s)''',  (index_list, match_list, id))
    conn.commit()

    stat_id = df.stat_id[index]
    false_pos = [i for i in index_list if i not in stat_id]
    false_neg = [i for i in stat_id if i not in index_list]
    true_pos = [i for i in index_list if i in stat_id]

    false_positive += false_pos
    false_negative += false_neg
    true_positive += true_pos

    t1 = time.time()
    print t1 - t0

precision = float(len(true_positive)) / (len(true_positive) + len(false_positive))
recall = float(len(true_positive)) / (len(true_positive) + len(false_negative))
print precision
print recall


conn.close()
