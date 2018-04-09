import main
import gensim
import time
import psycopg2
import psycopg2.extras
import pandas as pd
import spacy

nlp = spacy.load('en')

text_file = open("../test_statements.txt", "r")
out_file = open("./test_out.txt", "w")
lines = text_file.readlines()

model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = "select id, statement, speaker, speaker_title from facts"
dataframe = pd.read_sql_query(query, conn)
count = 1
for line in lines:

    line = line.replace("\n", "")
    #line = "Is it true that Donna Brazile gave Clinton debate questions in advance?"
    #line = "Was Donald Trump right when he said Hillary Clinton gave uranium to Russia?"
    #line =  "Will Hillary Clinton's plans add to the national debt?"
    #print line
    t0 = time.time()
    (claim_score, claim_ents_index, result, score_list, index_list, match_list) = main.check(line, model, dataframe, conn, nlp) # 20-38s
    t1 = time.time()
    print t1-t0
    out_file.write('%s' % count + " ")
    out_file.write(result + " ")
    out_file.write('%s' % claim_score + " ")
    out_file.write('%s' % len(claim_ents_index) + " ")
    out_file.write("\n")
    for index in range(len(score_list)):
        out_file.write('%s' % score_list[index] + " ")
        out_file.write('%s' % index_list[index] + " ")
        out_file.write(match_list[index])
        out_file.write("\n")
    out_file.write("\n")
    count += 1

conn.close()
out_file.close()
text_file.close()
