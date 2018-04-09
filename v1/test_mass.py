import main
import gensim
import time

text_file = open("../test_statements.txt", "r")
out_file = open("./test_out.txt", "w")
lines = text_file.readlines()

model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s

for line in lines:
    t0 = time.time()
    (result, max_score, max_id, max_statement) = main.check(line, model) # 20-38s
    t1 = time.time()
    print t1-t0
    out_file.write(result + " ")
    out_file.write('%s' % max_score + " ")
    out_file.write('%s' % max_id + " ")
    out_file.write(max_statement)
    out_file.write("\n")
    print "current Done"

out_file.close()
text_file.close()
