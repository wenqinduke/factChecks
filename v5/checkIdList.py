import psycopg2
import psycopg2.extras
import pandas as pd

conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
query = "select id, stat_id, potential_id from test_questions"
df = pd.read_sql_query(query, conn)

for index in range(df.shape[0]):
    id = df.id[index]
    stat_id = df.stat_id[index]
    potential_id = df.potential_id[index]
    omitted_id = [i for i in stat_id if i not in potential_id ]

    if len(omitted_id) > 0:
        print id
        print omitted_id
