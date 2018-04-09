import gensim
import time
import pre_process_sentence
import spacy

def max_match_score(claim_tags, claim_token, claim_ents, claim_imp_index, sta_token, sta_ents, claim_ents_index, sta_ents_index, claim_person, sta_person, claim_verb, sta_verb, model):
    verb_weight = 1.5
    noun_weight = 1
    entity_weight = 1.5
    imp_weight = 1.5
    #name-entity check
    # non_per = []
    # non_org = []
    # non_gpe = []
    # for claim_ent in claim_ents:
    #     if (claim_ent[1] == 'PERSON'):
    #         per_mark = False
    #         for sta_ent in sta_ents:
    #             if (sta_ent[1] == 'PERSON'):
    #                 if (sta_ent[0].lower() in claim_ent[0].lower() or claim_ent[0].lower() in sta_ent[0]):
    #                     per_mark = True
    #                     break
    #         if not per_mark:
    #             non_per.append(claim_ent[0])
    #             break
    #     if (claim_ent[1] == 'ORG'):
    #         org_mark = False;
    #         for sta_ent in sta_ents:
    #             if (sta_ent[1] == 'ORG'):
    #                 if (sta_ent[0].lower() in claim_ent[0].lower() or claim_ent[0].lower() in sta_ent[0]):
    #                     org_mark = True
    #                     break
    #         if not org_mark:
    #             non_org.append(claim_ent[0].lower())
    #             break
    #     if (claim_ent[1] == 'GPE'):
    #         gpe_mark = False;
    #         for sta_ent in sta_ents:
    #             if (sta_ent[1] == 'GPE'):
    #                 if (sta_ent[0].lower() in claim_ent[0].lower() or claim_ent[0].lower() in sta_ent[0]):
    #                     gpe_mark = True
    #                     break
    #         if not gpe_mark:
    #             non_gpe.append(claim_ent[0].lower())
    #
    # print non_per
    # print non_org
    # if len(non_per) > 0 or len(non_org) > 0: #if name or organization doesnt match, directly return 0.
    #     return 0
    sta_ents_words = []
    for index in sta_ents_index:
        sta_ents_words.append(sta_token[index])
    for index in claim_ents_index:
        word = claim_token[index]
        if word not in sta_ents_words:
            return 0

    #who said which situation, need further development
    if len(claim_verb) <= 1:
        if len(sta_person) == 2 and len(claim_person) == 2:
            if sta_token[sta_person[1]] != claim_token[claim_person[1]]:
                return 0
        elif len(claim_person) == 2 and len(sta_person) >=2:
            if claim_person[1] == sta_person[0] and sta_person[0] != sta_person[1]:
                return 0
        elif len(claim_person) == 1 and len(sta_person) == 2:
            if claim_token[claim_person[0]] != sta_token[sta_person[1]]:
                return 0

    w,h = len(claim_token), len(sta_token);
    matrix = [[0 for x in range(h)] for y in range(w)]

    marked_row = []
    marked_col = []
    keyError = False
    #if find similarity = 1, select the edge and proceed;
    score_sum = 0;
    for row in range(w):
        if row not in marked_row: #proceed to the next if row is already selected
            for col in range(h):
                if col not in marked_col:
                    score = 0
                    try:
                        score = model.similarity(claim_token[row], sta_token[col])
                    except KeyError:
                        keyError = True
                    if score >= 0.99 or claim_token[row] == sta_token[col]: #selec current edge since it perfectly matches
                        marked_row.append(row)
                        marked_col.append(col)
                        if row in claim_ents_index:
                            score_sum += entity_weight
                        elif row in claim_imp_index:
                            score_sum += imp_weight
                        elif verb_tag(claim_tags[row]):
                            score_sum += verb_weight
                        elif noun_tag(claim_tags[row]):
                            score_sum += noun_weight
                        else:
                            score_sum += 1
                        break
                    else:
                        matrix[row][col] = score
    #print score_sum
    max_weight = 0
    max_col = -1
    max_row = -1


    #qualify_gpe = False
    # for ent_string in non_gpe:
    #     str_list = ent_string.split(" ")
    #     for word in str_list:
    #         row = claim_token.index(word)
    #         for col in range(h):
    #             if matrix[row][col] >= 0.6:
    #                 qualify_gpe = True
    #                 break
    # if not qualify_gpe:
    #     return 0


    #stop condition: one of the sets used up
    while len(marked_row) < len(claim_token) and len(marked_col) < len(sta_token):
        #first, find the max weight of edges
        for row in range(w):
            if row not in marked_row:
                for col in range(h):
                    if col not in marked_col:
                        if matrix[row][col] > max_weight:
                            max_weight = matrix[row][col]
                            max_col = col
                            max_row = row

        if (max_weight <= 0.3):
            break
        else:
            if max_row in claim_ents_index:
                score_sum += entity_weight * max_weight
            elif max_row in claim_imp_index:
                score_sum += imp_weight * max_weight
            elif verb_tag(claim_tags[max_row]):
                score_sum += verb_weight * max_weight
            elif noun_tag(claim_tags[max_row]):
                score_sum += noun_weight * max_weight
            else:
                score_sum += max_weight
            marked_row.append(max_row)
            marked_col.append(max_col)
            max_weight = 0 #re-initialize max_weight
    #print score_sum
    return score_sum

def verb_tag(tag):
    if (tag.startswith('V')):
        return True
    return False

def noun_tag(tag):
    if (tag.startswith('N')):
        return True
    return False


#model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s

# nlp = spacy.load('en')
# claim = "Was Donald Trump right when he said that Obamacare premiums are going up?"
# sta = "Donald Trump said that On Obamacare, the premiums are going up 60, 70, 80 percent."
# (claim_token, claim_tags, claim_deps, claim_ents, claim_ents_index) = pre_process_sentence.process(claim, nlp)
# (sta_token, sta_tags, sta_deps, sta_ents, sta_ents_index) = pre_process_sentence.process(sta, nlp)
#print max_match_score(claim_tags, claim_token, claim_ents, sta_token, sta_ents, claim_ents_index, sta_ents_index, model)
