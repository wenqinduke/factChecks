import gensim
import match
import pandas as pd
import psycopg2
import psycopg2.extras
import pre_process_sentence as pps
import os
import sys
import collections
import time #testing performance

# reload(sys)
# sys.setdefaultencoding('latin-1')
def check (claim, model):
    #claim = "Have More white people been shot by police officers this past year than minorities?"
    claim_token = pps.process(claim) #time usage: ~0.055s
    #print claim_token
    model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s

    claim_score = len(claim_token)
    # for word in claim_token:
    #     if match.tag_important(word):
    #         claim_score += 1.5
    #     else:
    #         claim_score += 1

    #0.135251045227
    conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "select id, statement, speaker, speaker_title from facts"
    dataframe = pd.read_sql_query(query, conn)

    max_score = 0
    max_index = -1

    for index in range(dataframe.shape[0]):
        sta_token = pps.process(dataframe.statement[index] + " " + dataframe.speaker[index] + " "+ dataframe.speaker_title[index])
        cur_score = match.max_match_score(claim_token, sta_token, model) # ~0.003s

        if (cur_score > max_score):
            max_score = cur_score
            max_index = index

    result = ""
    if (max_score >= 0.7 * claim_score and max_index > -1):
        result = "Matched"
    else:
        result = "Not Found"

    dataframe_id = -1
    dataframe_statement = ""

    if max_index > -1:
        dataframe_id = dataframe.id[max_index]
        dataframe_statement = dataframe.statement[max_index]

    return (result, max_score, dataframe_id, dataframe_statement)

#future validation and declare if it is a fail/pass, by setting a threshold.
