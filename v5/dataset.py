import psycopg2
import pandas as pd
import psycopg2.extras
import main
import gensim
import pre_process_sentence as ps
import match
import random
import numpy as np
import random

model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s

total_id =11724
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor()
destroyTable = "DROP TABLE IF EXISTS train_set_300"
cursor.execute(destroyTable)
command = '''CREATE TABLE train_set_300(id integer PRIMARY KEY, question VARCHAR(255), question_id integer, train_id integer, statement text, name_entity text[], name_entity_claim text[],
    name_entity_sum text[], ques_length integer, ques_score decimal, stat_length decimal, noun decimal, verb decimal, adj decimal, speaker_half_match integer, speaker_full_match integer,
    matching_score decimal, highest_noun decimal, second_noun decimal, highest_verb decimal, second_verb decimal, highest_adj decimal, second_adj decimal,
    sum_other decimal, person_entity decimal, gpe_entity decimal, person_entity_match decimal, gpe_entity_match decimal, org_entity decimal, org_entity_match decimal,
    full_other_match decimal, summary_score decimal, label integer);'''
cursor.execute(command)
conn.commit()

query = "select id, question, stat_id, potential_id from test_questions"
df = pd.read_sql_query(query, conn)
count = 1

def createDataSet(question_id, count, id_list, question, conn, cursor, classified_as):
    for stat_id in id_list:
        cursor.execute("select statement, speaker, summary from facts where id = %s", (stat_id,))
        result_row = cursor.fetchone()
        try:
            speaker = result_row[1]
        except TypeError:
            speaker = ""
        try:
            claim = result_row[0]
        except:
            claim = ""
        try:
            summary = result_row[2]
        except TypeError:
            summary = ""

        try:
            speaker_tokens = ps.process(speaker)[0]
            (ques_tokens, ques_tags, ques_ents, ques_ents_index, ques_noun, ques_verb, ques_adj) = ps.process(question)
            (claim_tokens, claim_tags, claim_ents, claim_ents_index, claim_noun, claim_verb, claim_adj) = ps.process(claim)
            (sum_tokens, sum_tags, sum_ents, sum_ents_index, sum_noun, sum_verb, sum_adj) = ps.process(summary)
        except AttributeError:
            print AttributeError
        ques_length = len(ques_tokens)
        stat_length = len(claim_tokens)
        verb_weight = 1.5
        noun_weight = 1
        entity_weight = 1.5
        ques_score = 0
        ques_length = len(ques_tokens)
        for word_index in range(ques_length):
            if word_index in ques_ents_index:
                ques_score += entity_weight
            elif match.verb_tag(ques_tags[word_index]):
                ques_score += verb_weight
            elif match.noun_tag(ques_tags[word_index]):
                ques_score += noun_weight
            else:
                ques_score += 1

        name_entity = ques_ents #{"(hillary,B-PERSON,0)","(clinton,I-PERSON,1)"}
        name_entity_claim = claim_ents
        name_entity_sum = sum_ents
        name_entity_total = name_entity_claim + name_entity_sum

        entity_match = 0
        person_entity = 0
        person_entity_match = 0
        gpe_entity = 0
        gpe_entity_match = 0
        org_entity = 0
        org_entity_match = 0
        for ent in name_entity:
            (word, tag, pos) = ent
            if tag.endswith("PERSON"):
                person_entity += 1
            elif tag.endswith("GPE"):
                gpe_entity += 1
            elif tag.endswith("ORGANIZATION"):
                org_entity += 1
            for ent_in_total in name_entity_total:
                #cur_ent_word = ent_in_total[0]
                if word == ent_in_total[0] or word.startswith(ent_in_total[0]) or ent_in_total[0].startswith(word):
                    if tag.endswith("PERSON"):
                        person_entity_match += 1
                    elif tag.endswith("GPE"):
                        gpe_entity_match += 1
                    elif tag.endswith("ORGANIZATION"):
                        org_entity_match += 1
                    entity_match += 1
                    continue

        (score, sum_others, full_entity_match, full_other_match, highest_noun, second_noun, highest_verb, second_verb, highest_adj, second_adj, speaker_half_match, speaker_full_match)= match.max_match_score(ques_tags, ques_tokens, ques_ents, ques_ents_index, claim_tags, claim_tokens, claim_ents, claim_ents_index, speaker_tokens, model)
        sum_score= match.max_match_score(ques_tags, ques_tokens, ques_ents, ques_ents_index, sum_tags, sum_tokens, sum_ents, sum_ents_index, speaker_tokens, model)[0]


        cursor.execute('''INSERT INTO train_set_300 Values (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (count, question, question_id, stat_id, claim, name_entity, name_entity_claim, name_entity_sum,
        ques_length, ques_score, stat_length, float(ques_noun)/ques_length, float(ques_verb)/ques_length, float(ques_adj)/ques_length, speaker_half_match, speaker_full_match, score/ques_score, highest_noun, second_noun, highest_verb, second_verb, highest_adj, second_adj, float(sum_others)/ques_score, float(person_entity)/ques_length, float(gpe_entity)/ques_length, float(person_entity_match)/ques_length,
        float(gpe_entity_match)/ques_length, float(org_entity)/ques_length, float(org_entity_match)/ques_length, float(full_other_match)/ques_length, float(sum_score)/ques_score, classified_as))
        conn.commit()
        count += 1

    return count


for index in range(df.shape[0]):
    question_id = df.id[index]
    # if id <= 30:
    #     continue
    print (index)
    question = df.question[index]
    stat_id_list = df.stat_id[index]
    if stat_id_list is None or len(stat_id_list) == 0:
        continue
    count = createDataSet(question_id, count, stat_id_list, question, conn, cursor, 1)

    potential_id = df.potential_id[index]
    false_id_list= [w for w in potential_id if w not in stat_id_list]
    if len(false_id_list) >=300:
        false_id_list = random.sample(false_id_list, 300)

    count = createDataSet(question_id, count, false_id_list, question, conn, cursor, 0)

conn.close()
