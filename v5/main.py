import gensim
import match
import pandas as pd
import psycopg2
import psycopg2.extras
import pre_process_sentence as ps
import os
import sys
import collections
import time #testing performance
from sets import Set
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

def is_two_name_person(i, ques_tags):
    if ques_tags[i] == "I-PERSON":
        return True
    return False

def create_data_array(cursor, model, question, stat_id):
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
        return []
    ques_length = len(ques_tokens)
    claim_length = len(claim_tokens)
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
    selected = []
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
                if word not in selected:
                    if tag.endswith("PERSON"):
                        person_entity_match += 1
                    elif tag.endswith("GPE"):
                        gpe_entity_match += 1
                    elif tag.endswith("ORGANIZATION"):
                        org_entity_match += 1
                    entity_match += 1
                    selected.append(word)
                    continue

    (score, sum_others, full_entity_match, full_other_match, highest_noun, second_noun, third_noun, fourth_noun, highest_verb, second_verb, third_verb, highest_adj, second_adj, speaker_half_match, speaker_full_match)= match.max_match_score(ques_tags, ques_tokens, ques_ents, ques_ents_index, claim_tags, claim_tokens, claim_ents, claim_ents_index, speaker_tokens, model)
    sum_score= match.max_match_score(ques_tags, ques_tokens, ques_ents, ques_ents_index, sum_tags, sum_tokens, sum_ents, sum_ents_index, speaker_tokens, model)[0]

    # data = [ques_length, ques_score, claim_length, float(ques_noun)/ques_length, float(ques_verb)/ques_length, float(ques_adj)/ques_length, speaker_half_match, speaker_full_match, score/ques_score, highest_noun, second_noun, third_noun, fourth_noun, highest_verb, second_verb, third_verb, highest_adj, second_adj, float(sum_others)/ques_score, float(person_entity)/ques_length, float(gpe_entity)/ques_length, float(person_entity_match)/ques_length,
    # float(gpe_entity_match)/ques_length, float(org_entity)/ques_length, float(org_entity_match)/ques_length, float(full_other_match)/ques_length, float(sum_score)/ques_score]

    if person_entity == 0:
        person_entity_match = -1
    else:
        person_entity_match = float(person_entity_match) / person_entity

    if org_entity == 0:
        org_entity_match = -1
    else:
        org_entity_match = float(org_entity_match) / org_entity

    if gpe_entity == 0:
        gpe_entity_match = -1
    else:
        gpe_entity_match = float(gpe_entity_match) / gpe_entity

    data = [ques_length, claim_length, float(ques_noun)/ques_length, float(ques_verb)/ques_length, float(ques_adj)/ques_length, speaker_half_match, float(score)/ques_length, highest_noun, second_noun, third_noun, fourth_noun, highest_verb, second_verb, third_verb, highest_adj, second_adj, person_entity_match,
    gpe_entity_match, org_entity_match, float(full_other_match)/ques_length]


    return data

def check (ques, model, potential_id, dataframe, conn, clf, y_score, y_test, stat_id):
    (ques_token, ques_tags, ques_ents, ques_ents_index, ques_noun, ques_verb, ques_adj) = ps.process(ques)
    #print ques_token

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #TODO: make code more efficient by only computing question's length, entity once and pass in as a parameter.
    match_list = []
    index_list = []

    ques_length = len(ques_token)

    data_array = []

    for n in potential_id:
        data = create_data_array(cursor, model, ques, n)
        #data_array.append(data)
        if len(data) < 1:
            continue
        result = clf.predict([data])
        if result[0] == 1:
            index_list.append(n)
        decision_score = clf.decision_function([data])
        y_score.append(decision_score[0])
        if n in stat_id:
            y_test.append(1)
        else:
            y_test.append(0)
    return (index_list, match_list, y_score, y_test)
