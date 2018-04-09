import psycopg2
import psycopg2.extras
import pre_process_sentence as ps
import gensim
import pandas as pd
import spacy
from psycopg2.extensions import AsIs
import time

t0 = time.time()

nlp = spacy.load('en')

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
conn2 = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = "select id, statement, speaker, speaker_title from facts"
dataframe = pd.read_sql_query(query, conn2)
t2 = time.time()

print t2 - t0
#model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s

words_dict = {}
for index in range(dataframe.shape[0]):
    data_id = dataframe.id[index]
    sen = dataframe.speaker[index] + " said that " + dataframe.statement[index]
    (tokens, tags, ents, ents_index, imp_index, person, verb) = ps.process(sen, nlp)
    for word_token in tokens:
        if word_token not in words_dict:
            words_dict[word_token] = [data_id]
        else:
            words_dict[word_token].append(data_id)
        # cursor.execute('''SELECT id_list FROM dataindex WHERE word = %(w)s''', {'w' : word_token})
        # row = cursor.fetchone()
        # if not row:
        #     id_list = [data_id]
        #     cursor.execute('''INSERT INTO dataindex VALUES (%s, %s)''', (word_token, id_list))
        #     conn.commit()
        # else:
        #     cursor.execute('''UPDATE dataindex SET id_list = id_list || (%s) where word = (%s)''', (data_id, word_token))
        #     conn.commit()
t3 = time.time()
print t3 - t0
for k, v in words_dict.iteritems():
    cursor.execute('''INSERT INTO data_index Values (%s, %s)''', (k, v))
    conn.commit()
t4 = time.time()
print t4 -t0

cursor.close()
cursor2.close()
conn.close()
conn2.close()
