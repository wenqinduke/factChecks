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
#
# destroyTable = "DROP TABLE IF EXISTS test_questions"
# cursor.execute(destroyTable)
# command = '''CREATE TABLE test_questions(id integer, question VARCHAR(255) PRIMARY KEY, stat_id integer[], ques_length integer, ques_score integer, matching_score integer,
#             full_match integer, name_entity VARCHAR(255)[], highest_noun integer, second_noun integer, highest_verb integer, second_verb integer, sum_other integer, summary_score integer);'''
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
#
# id_file = open("./match_id.txt", "r")
# lines = id_file.readlines()
# count = 1
# for line in lines:
#     line = line.replace("\n", "")
#     line = line.replace("{", "")
#     line = line.replace("}", "")
#     ids = line.split(",")
#     id_list = []
#     for id in ids:
#         id = id.strip()
#         if id == "":
#             continue
#         id_list.append(int(id))
#     cursor.execute('''UPDATE test_questions SET stat_id = (%s) where id = (%s)''',(id_list, count))
#     conn.commit()
#     count += 1

def alter_table(cursor, conn):
    # alter_table = "ALTER TABLE test_questions ALTER COLUMN ques_score type numeric(10,0) using cast(ques_score as numeric), ALTER COLUMN matching_score type numeric(10,0) using cast(matching_score as numeric), ALTER COLUMN highest_noun type numeric(10,0) using cast(highest_noun as numeric), ALTER COLUMN second_noun type numeric(10,0) using cast(second_noun as numeric), ALTER COLUMN highest_verb type numeric(10,0) using cast(highest_verb as numeric), ALTER COLUMN second_verb type numeric(10,0) using cast(second_verb as numeric), ALTER COLUMN sum_other type numeric(10,0) using cast(sum_other as numeric), ALTER COLUMN summary_score type numeric(10,0) using cast(summary_score as numeric);"
    # alter_table = "ALTER TABLE test_questions ALTER COLUMN ques_score type decimal, ALTER COLUMN matching_score type decimal, ALTER COLUMN highest_noun type decimal, ALTER COLUMN second_noun type decimal, ALTER COLUMN highest_verb type decimal, ALTER COLUMN second_verb type decimal, ALTER COLUMN sum_other type decimal, ALTER COLUMN summary_score type decimal;"
    # cursor.execute(alter_table)
    # conn.commit
    # drop_table_id = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS false_id'''
    # add_table_id = '''ALTER TABLE test_questions ADD COLUMN false_id integer[]'''
    # drop_table_mc = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS matching_score, DROP COLUMN IF EXISTS ques_score, DROP COLUMN IF EXISTS sum_other, DROP COLUMN IF EXISTS summary_score, DROP COLUMN IF EXISTS full_match'''
    # add_table_mc = '''ALTER TABLE test_questions ADD COLUMN matching_score decimal, ADD COLUMN ques_score decimal, ADD COLUMN sum_other decimal, ADD COLUMN summary_score decimal, ADD COLUMN full_match decimal'''
    # add_table_mc = '''ALTER TABLE test_questions ADD COLUMN matching_score decimal, ADD COLUMN ques_score decimal, ADD COLUMN sum_other decimal, ADD COLUMN summary_score decimal, ADD COLUMN full_match decimal'''
    # drop_table_noun = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS highest_noun, DROP COLUMN IF EXISTS second_noun'''
    # add_table_noun = '''ALTER TABLE test_questions ADD COLUMN highest_noun decimal, ADD COLUMN second_noun decimal'''
    # drop_table_verb = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS highest_verb, DROP COLUMN IF EXISTS second_verb'''
    # add_table_verb = '''ALTER TABLE test_questions ADD COLUMN highest_verb decimal, ADD COLUMN second_verb decimal'''
    # drop_table = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS ques_length, DROP COLUMN IF EXISTS name_entity'''
    #
    drop_table_pid = '''ALTER TABLE test_questions DROP COLUMN IF EXISTS final_mod_potential_id'''
    add_table_pid = '''ALTER TABLE test_questions ADD COLUMN final_mod_potential_id integer[]'''

    # cursor.execute(drop_table_id)
    # # cursor.execute(add_table_id)
    # cursor.execute(drop_table_mc)
    # # cursor.execute(add_table_mc)
    # cursor.execute(drop_table_noun)
    # # cursor.execute(add_table_noun)
    # cursor.execute(drop_table_verb)
    # # cursor.execute(add_table_verb)
    # cursor.execute(drop_table)
    cursor.execute(drop_table_pid)
    cursor.execute(add_table_pid)

    conn.commit()
def select_mod_potential_id(conn, cursor):
    count = 22
    for index in range(count):
        cursor.execute("select stat_id, match_id_adaboost_self, match_id_adaboost_30, mod_potential_id from test_questions where id = %s", (index + 1,))
        row = cursor.fetchone()
        stat_id = row[0]
        id_list_1 = row[1]
        id_list_2 = row[2]
        mod_potential_id = row[3]
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
    #todo: If question has less than 3 keywords, do it as 2 time match.
    count = 111
    for index in range(count):
        cursor.execute("select id, question, stat_id from test_questions where id = %s " , (index + 1,))
        row = cursor.fetchone()
        question = row[1]
        print question
        stat_id_list = row[2]
        # question ='Did Clinton abuse her power as secretary of state for the Clinton Foundation?'
        # if stat_id_list is None or len(stat_id_list) == 0:
        #     continue
        (ques_token, ques_tags, ques_ents, ques_ents_index, ques_noun, ques_verb, ques_adj) = pps.process(question)
        # print ques_token
        # print ques_ents
        # print ques_ents_index

        appear = Set([])
        second = Set([])
        index_all = Set([])
        # person = 0

        name_ent = 0
        cursor = conn.cursor()
        persons = ['I-PERSON', 'B-PERSON']
        for ent in ques_ents:
            # if ent[0] in ques_token and ent[1] == 'I-PERSON':
        #         # print "I-PERSON"
        #         # print ent[0]
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
            #print similar_words
            # print similar_words
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

alter_table(cursor, conn)
select_mod_potential_id(conn, cursor)
