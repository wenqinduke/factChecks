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

#test_id_region = random.sample(list(range(1,112,1)), 22)

test_id_region = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
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
        # if question_id not in test_id_region:
        #     X_train.append(data_array)
        #     y_train.append(df_train.label[index])
        if question_id in test_id_region:
            X_train.append(data_array)
            y_train.append(df_train.label[index])

    #classifiers = SVC(kernel="linear", C=0.025)
    classifiers = AdaBoostClassifier()
    classifiers.fit(X_train, y_train)
    score = classifiers.score(X_train, y_train)
    print score
    return classifiers

model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = "select id, statement, speaker, speaker_title from facts"
df_facts = pd.read_sql_query(query, conn)
query2 = "select stat_id, id, question, potential_id from test_questions"
df_ques = pd.read_sql_query(query2, conn)

query_train = "select * from train_set"
df_train = pd.read_sql_query(query_train, conn)
clf = get_classifier(df_train)

# drop_table_result = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS match_id_adaboost, DROP COLUMN IF EXISTS match_list_adaboost'''
# add_table_result = ''' ALTER TABLE test_questions ADD COLUMN match_id_adaboost integer[], ADD COLUMN match_list_adaboost text[] '''
# cursor.execute(drop_table_result)
# cursor.execute(add_table_result)


for index in range(df_ques.shape[0]):
    id = df_ques.id[index]
    print (id)
    if id not in test_id_region:
        continue
    question = df_ques.question[index]
    potential_id = df_ques.potential_id[index]
    if potential_id is None:
        continue
    t0 = time.time()
    (index_list, match_list) = main.check(question, model, potential_id, df_facts, conn, clf)

    #cursor.execute('''UPDATE test_questions SET match_id = (%s), match_list = (%s) where id = (%s)''',  (index_list, match_list, id))
    cursor.execute('''UPDATE test_questions SET match_id_adaboost = (%s), match_list_adaboost = (%s) where id = (%s)''',  (index_list, match_list, id))
    conn.commit()

    t1 = time.time()
    print t1 - t0


conn.close()
