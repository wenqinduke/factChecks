import psycopg2
import psycopg2.extras
import pandas as pd

conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = "select id, question, stat_id, match_id_adaboost_30 from test_questions"
dataframe = pd.read_sql_query(query, conn)

out_file = open("./wrong_match_adaboost.txt", "w")

false_positive = []
false_negative = []
true_positive = []

for index in range(dataframe.shape[0]):
    if dataframe.match_id_adaboost_30[index] is None:
        continue
    stat_id = dataframe.stat_id[index]
    match_id = dataframe.match_id_adaboost_30[index]

    false_pos = [w for w in match_id if w not in stat_id]
    false_neg = [w for w in stat_id if w not in match_id]
    true_pos = [w for w in stat_id if w in match_id]

    false_positive += false_pos
    false_negative += false_neg
    true_positive += true_pos


    out_file.write("===== Question:")

    out_file.write('%s' %dataframe.id[index] + " ")
    out_file.write(dataframe.question[index])
    out_file.write("\n")

    out_file.write("false positive: ")
    out_file.write("\n")

    for w in false_pos:
        cursor.execute("select id, statement, speaker from facts where id = %s", (w,))
        result_row = cursor.fetchone()
        out_file.write('%s' %result_row[0])
        out_file.write("   ")
        out_file.write(result_row[1])
        out_file.write("   ")
        out_file.write(result_row[2])
        out_file.write("\n")

    out_file.write("false negative: ")
    out_file.write("\n")
    for w in false_neg:
        cursor.execute("select id, statement, speaker from facts where id = %s", (w,))
        result_row = cursor.fetchone()
        out_file.write('%s' %result_row[0])
        out_file.write("   ")
        out_file.write(result_row[1])
        out_file.write("   ")
        out_file.write(result_row[2])
        out_file.write("\n")

    out_file.write("\n")

precision = float(len(true_positive)) / (len(true_positive) + len(false_positive))
recall = float(len(true_positive)) / (len(true_positive) + len(false_negative))
out_file.write("Precision: ")
out_file.write('%s' %precision)
out_file.write("Recall: ")
out_file.write('%s' %recall)
