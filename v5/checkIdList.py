import psycopg2
import psycopg2.extras
import pandas as pd


# TEMP: This file is to check for each question, whether all the matching-ids are in the potential-matching-id lists.
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def check_potential_id_contains_all_correct_case(conn, cursor):
    query = "select id, stat_id, potential_id from test_questions"
    df = pd.read_sql_query(query, conn)
    id_number = 0
    for index in range(df.shape[0]):
        id = df.id[index]
        stat_id = df.stat_id[index]
        potential_id = df.potential_id[index]
        print len(potential_id)
        id_number += len(potential_id)
        omitted_id = [i for i in stat_id if i not in potential_id ]

        if len(omitted_id) > 0:
            print id
            print omitted_id

#ignore this
def check_final_mod_id_length(conn,cursor):
    query = "select id, stat_id, final_mod_potential_id from test_questions"
    df = pd.read_sql_query(query, conn)
    for index in range(df.shape[0]):
        id = df.id[index]
        if id >=23:
            continue
        stat_id = df.stat_id[index]
        potential_id = df.final_mod_potential_id[index]

        omitted_id = [i for i in stat_id if i not in potential_id ]
        if len(omitted_id) > 0:
            print id
            print omitted_id
        if len(potential_id) != 30:
            print id

check_final_mod_id_length(conn, cursor)
