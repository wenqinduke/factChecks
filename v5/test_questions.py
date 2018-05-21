# from nltk.tokenize import sent_tokenize,word_tokenize
# from nltk.chunk import conlltags2tree, tree2conlltags
# from nltk import word_tokenize, pos_tag, ne_chunk
# from nltk.corpus import stopwords
# from collections import defaultdict
# from string import punctuation
# from heapq import nlargest
# import urllib2
# import urllib
import psycopg2
import psycopg2.extras
import pandas as pd
import time
import main
import gensim
import pre_process_sentence as pps
import match
import nltk
from sets import Set
import random

conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# def initialize_table(conn, cursor):
    # destroyTable = "DROP TABLE IF EXISTS test_questions"
    # cursor.execute(destroyTable)
    # command = '''CREATE TABLE test_questions(id integer, question VARCHAR(255) PRIMARY KEY, stat_id integer[], potential_id integer[], match_id_adaboost integer[], match_id_adaboost_all integer[], match_id_adaboost_30 integer[]);'''
    # cursor.execute(command)
    # conn.commit()
    # text_file = open("../test_statements.txt", "r")
    # lines = text_file.readlines()
    # count = 1
    # for line in lines:
    #     line = line.replace("\n", "")
    #     cursor.execute('''INSERT INTO test_questions(id, question) Values (%s, %s)''',(count, line))
    #     conn.commit()
    #     count += 1

def alter_table(cursor, conn):
    return

def select_mod_potential_id(conn, cursor):
    count = 22
    for index in range(count):
        cursor.execute("select stat_id, match_id_adaboost_30, mod_potential_id from test_questions where id = %s", (index + 1,))
        row = cursor.fetchone()
        stat_id = row[0]
        id_list_1 = row[1]
        mod_potential_id = row[2]
        id_needed = []
        id_needed += stat_id
        length_needed = 20 - len(stat_id)
        mod_no_stat = [w for w in mod_potential_id if w not in stat_id]
        rand = []
        if len(mod_no_stat) >= length_needed:
            rand = random.sample(mod_no_stat, length_needed)
        else:
            rand += mod_no_stat
            rand += random.sample(list(range(1, 11725)), length_needed - len(mod_no_stat))
        id_needed += rand

        cursor.execute('''UPDATE test_questions SET final_mod_potential_id = (%s) where id = (%s)''', (id_needed, index + 1))
        conn.commit()


def select_potential_id(conn, cursor):
    model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s
    count = 111
    for index in range(count):
        cursor.execute("select id, question from test_questions where id = %s " , (index + 1,))
        row = cursor.fetchone()
        question = row[1]
        print question
        (ques_token, ques_tags, ques_ents, ques_ents_index, ques_noun, ques_verb, ques_adj) = pps.process(question)

        appear = Set([])
        second = Set([])
        index_all = Set([])

        name_ent = 0
        cursor = conn.cursor()
        persons = ['I-PERSON', 'B-PERSON']
        for ent in ques_ents:
            if ent[0] in ques_token and ent[1] in persons :
                ques_token.remove(ent[0])
                if name_ent < 1 or ent[1] == 'I-PERSON':
                    cursor.execute('''SELECT id_list FROM data_index WHERE word = %(w)s''', {'w' : ent[0]})
                    id_list = cursor.fetchone()
                    if id_list:
                        for num in id_list[0]:
                            if num in second:
                                index_all.add(num)
                            elif num in appear:
                                second.add(num)
                            else:
                                appear.add(num)
                name_ent += 1
        for i in range(len(ques_token)):
            word = ques_token[i]
            similar_words = pps.get_similar_words(word, model)
            for similar_word in similar_words:
                cursor.execute('''SELECT id_list FROM data_index WHERE word = %(w)s''', {'w' : similar_word})
                id_list = cursor.fetchone()
                if id_list:
                    for num in id_list[0]:
                        if num in second:
                            index_all.add(num)
                        elif num in appear:
                            second.add(num)
                        else:
                            appear.add(num)
        if len(ques_token) <= 4:
            index_all = second

        cursor.execute('''UPDATE test_questions SET potential_id = (%s) where id = (%s)''', (list(index_all), index + 1))
        conn.commit()

#alter_table(cursor, conn)
#select_mod_potential_id(conn, cursor)
select_potential_id(conn, cursor)
