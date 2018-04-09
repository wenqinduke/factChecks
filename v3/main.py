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
def check (claim, model, dataframe, nlp):
    #claim = "Have More white people been shot by police officers this past year than minorities?"
    #claim = "Is it true that Donald Trump is against same-sex marriage?"
    (claim_token, claim_tags, claim_ents, claim_ents_index, claim_imp_index, claim_person, claim_verb) = pps.process(claim, nlp)
    # print claim_token
    # print claim_tags
    # print claim_ents
    # print claim_ents_index
    # print claim_imp_index
    # print claim_person
    # print claim_verb

    #model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s
    verb_weight = 1.5
    noun_weight = 1
    entity_weight = 1.5
    imp_weight = 1.5
    claim_score = 0
    for word_index in range(len(claim_token)):
        if word_index in claim_ents_index:
            claim_score += entity_weight
        elif word_index in claim_imp_index:
            claim_score += imp_weight
        elif match.verb_tag(claim_tags[word_index]):
            claim_score += verb_weight
        elif match.noun_tag(claim_tags[word_index]):
            claim_score += noun_weight
        else:
            claim_score += 1

    # max_score = 0
    # max_index = -1
    score_list = []
    match_list = []
    index_list = []

    if claim_score <= 3.5:
        match_score = claim_score
    else:
        match_score = 0.6*claim_score#decrease match score over length
    max_statement = ""
    max_id = -1
    max_score = 0

    #don't put deps right now;
    for index in range(dataframe.shape[0]):
        (sta_token,sta_tags, sta_ents, sta_ents_index, sta_imp_index, sta_person, sta_verb) = pps.process(dataframe.speaker[index] + " said that " + dataframe.statement[index], nlp)
        cur_score = match.max_match_score(claim_tags, claim_token, claim_ents, claim_imp_index, sta_token, sta_ents, claim_ents_index, sta_ents_index, claim_person, sta_person, claim_verb, sta_verb, model) # ~0.003s
        # if (cur_score > max_score):
        #     max_score = cur_score
        #     max_index = index
        if (cur_score >= match_score):
            score_list.append(cur_score)
            match_list.append(dataframe.statement[index])
            index_list.append(dataframe.id[index])
        if (cur_score >= max_score):
            max_statement = dataframe.statement[index]
            max_id = dataframe.id[index]
            max_score = cur_score

    result = ""
    if not score_list:
        # print match_score
        # print max_score
        # print max_id
        # print max_statement
        result = "NOT FOUND"
        score_list.append(max_score)
        index_list.append(max_id)
        match_list.append(max_statement)
        #return ("Not Found", max_score, max_id, max_statement)
    else:
        result = "Matched"
    # print match_score
    # for index in range(len(match_list)):
    #     print score_list[index]
    #     print index_list[index]
    #     print match_list[index]


    return (claim_score, result, score_list, index_list, match_list)
    # result = ""
    # if (max_score >= 0.7 * claim_score and max_index > -1):
    #     result = "Matched"
    # else:
    #     result = "Not Found"
    #
    # dataframe_id = -1
    # dataframe_statement = ""
    #
    # if max_index > -1:
    #     dataframe_id = dataframe.id[max_index]
    #     dataframe_statement = dataframe.statement[max_index]

    #return (result, max_score, dataframe_id, dataframe_statement)

#future validation and declare if it is a fail/pass, by setting a threshold.
