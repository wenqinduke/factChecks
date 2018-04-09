import main
import gensim
import time
import psycopg2
import psycopg2.extras
import pandas as pd

text_file = open("../test_statements.txt", "r")
out_file = open("./test_out.txt", "w")
lines = text_file.readlines()

#0.135251045227
model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = "select id, statement, speaker, speaker_title from facts"
dataframe = pd.read_sql_query(query, conn)

for line in lines:
    t0 = time.time()
    (claim_score, result, score_list, index_list, match_list) = main.check(line, model, dataframe) # 20-38s
    t1 = time.time()
    print t1-t0
    out_file.write(result + " ")
    out_file.write('%s' % claim_score + " ")
    out_file.write("\n")
    for index in range(len(score_list)):
        out_file.write('%s' % score_list[index] + " ")
        out_file.write('%s' % index_list[index] + " ")
        out_file.write(match_list[index])
        out_file.write("\n")
    out_file.write("\n")
    print "current Done"

out_file.close()
text_file.close()
