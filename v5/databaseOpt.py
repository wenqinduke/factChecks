import psycopg2
import psycopg2.extras
import pre_process_sentence as ps
import gensim
import pandas as pd
import spacy
from psycopg2.extensions import AsIs
import time
from sets import Set

#TEMP: This file is to help speed up the application. By pre-processing each statement, we would get a database in which every word has a list of statement ids, in which the word appears (either in summary, speaker or statement)
t0 = time.time()

print ('create database..')
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor()
destroyTable = "DROP TABLE IF EXISTS data_index"
cursor.execute(destroyTable)
command = '''CREATE TABLE data_index(word VARCHAR(255) PRIMARY KEY,id_list integer[]);'''
cursor.execute(command)
conn.commit()

t1 = time.time()
print t1 - t0

print ('get dataframe...')
query = "select id, statement, speaker, speaker_title, summary from facts"
dataframe = pd.read_sql_query(query, conn)
t2 = time.time()

print t2 - t0
#model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s

words_dict = {}
for index in range(dataframe.shape[0]):
    data_id = dataframe.id[index]
    summary = dataframe.summary[index]
    if summary is  None:
        summary = ""
    sen = dataframe.speaker[index] + " " + dataframe.statement[index] + " " + summary
    (tokens, tags, ents, ents_index, noun, verb, adj) = ps.process(sen)
    for word_token in tokens:
        if word_token not in words_dict:
            words_dict[word_token] = Set([data_id])
        else:
            words_dict[word_token].add(data_id)

t3 = time.time()
print t3 - t0
for k, v in words_dict.iteritems():
    cursor.execute('''INSERT INTO data_index Values (%s, %s)''', (k, list(v)))
    conn.commit()
t4 = time.time()
print t4 -t0

cursor.close()
conn.close()
