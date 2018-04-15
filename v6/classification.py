import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
import psycopg2
import psycopg2.extras
import pandas as pd

index_omit = [2,15,20,21,24,31,34,35,38,42,45,46,47,52,53,56,57,58,61,69,72,78,79,80,82,83,87,88,93,94,95,96,97,103,107,108]

conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = 'select * from test_questions'
df = pd.read_sql_query(query, conn)

clf = linear_model.LinearRegression()
clf.fit([[df.ques_length[index], df.ques_score[index], df.sum_other[index], len(df.name_entity), df.summary_score[index], df.full_match[index], df.highest_noun[index], df.second_noun[index],df.highest_verb[index], df.second_verb[index]] for index in range(df.shape[0]) if df.id[index] not in index_omit],
        [df.matching_score[index] for index in range(df.shape[0]) if df.id[index] not in index_omit ])

print clf.coef_

# [ 5.15222355e-02 -1.09505388e-01  6.66867991e-01 -1.11022302e-16
#   1.21488946e-02  2.02794812e-01  1.47036528e-01  1.38865303e-01
#   1.22032543e-01  1.23143841e-01]
