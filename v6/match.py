import gensim
import time
import pre_process_sentence

def max_match_score(claim_tags, claim_token, claim_ents, claim_ents_index, sta_tags, sta_token, sta_ents,  sta_ents_index, speaker_token, model):
    verb_weight = 1.5
    noun_weight = 1
    entity_weight = 1.5
    imp_weight = 1.5

    highest_noun = 0
    second_noun = 0
    highest_verb = 0
    second_verb = 0
    highest_adj = 0
    second_adj = 0
    sum_others = 0
    full_entity_match = 0
    full_other_match = 0

    # if name or place doesn't appear in statements, return 0
    # sta_ents_words = []
    # for index in sta_ents_index:
    #     sta_ents_words.append(sta_token[index])
    # count = 0
    # for index in claim_ents_index:
    #     word = claim_token[index]
    #     if word not in sta_ents_words:
    #         count += 1
    #     if count == len(claim_ents_index):
    #         return (0,0,0,0,0,0,0)

    #who said which situation, need further development
    # if len(claim_verb) <= 1:
    #     if len(sta_person) == 2 and len(claim_person) == 2:
    #         if sta_token[sta_person[1]] != claim_token[claim_person[1]]:
    #             return (0,0,0,0,0,0,0)
    #     elif len(claim_person) == 2 and len(sta_person) >=2:
    #         if claim_person[1] == sta_person[0] and sta_person[0] != sta_person[1]:
    #             return (0,0,0,0,0,0,0)
    #     elif len(claim_person) == 1 and len(sta_person) == 2:
    #         if claim_token[claim_person[0]] != sta_token[sta_person[1]]:
    #             return (0,0,0,0,0,0,0)


    w,h = len(claim_token), len(sta_token);
    matrix = [[0 for x in range(h)] for y in range(w)]

    marked_row = []
    marked_col = []
    keyError = False
    #if find similarity = 1, select the edge and proceed;
    speaker_half_match = 0
    speaker_full_match = 1
    score_sum = 0;
    for speaker in speaker_token:
        if speaker in claim_token:
            speaker_half_match = 1
            marked_row.append(claim_token.index(speaker))
        if speaker not in claim_token:
            speaker_full_match = 0

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
                        full_other_match += 1
                        if row in claim_ents_index:
                            score_sum += entity_weight
                            full_entity_match += 1
                        # elif row in claim_imp_index:
                        #     score_sum += imp_weight
                        elif verb_tag(claim_tags[row]):
                            if highest_verb == 0:
                                highest_verb = verb_weight
                            elif second_verb == 0:
                                second_verb= verb_weight
                            score_sum += verb_weight
                        elif noun_tag(claim_tags[row]):
                            if highest_noun == 0:
                                highest_noun = noun_weight
                            elif second_noun == 0:
                                second_noun = noun_weight
                            score_sum += noun_weight
                        elif adj_tag(claim_tags[row]):
                            if highest_adj == 0:
                                highest_adj = 1
                            elif second_noun == 0:
                                second_noun = 1
                            score_sum += 1
                        else:
                            score_sum += 1
                        break
                    else:
                        matrix[row][col] = score
    #print score_sum
    max_weight = 0
    max_col = -1
    max_row = -1

    full_other_match = full_other_match - full_entity_match
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
            # elif max_row in claim_imp_index:
            #     score_sum += imp_weight * max_weight
            elif verb_tag(claim_tags[max_row]):
                if highest_verb < max_weight:
                    second_verb = highest_verb
                    highest_verb = max_weight
                elif second_verb < max_weight:
                    second_verb= max_weight
                score_sum += verb_weight * max_weight
            elif noun_tag(claim_tags[max_row]):
                if highest_noun < max_weight:
                    second_noun = highest_noun
                    highest_noun = max_weight
                elif second_noun < max_weight:
                    second_noun= max_weight
                score_sum += noun_weight * max_weight
            elif adj_tag(claim_tags[max_row]):
                if highest_adj < max_weight:
                    second_adj= highest_adj
                    highest_adj = max_weight
                elif second_adj < max_weight:
                    second_adj= max_weight
                score_sum +=  max_weight
            else:
                score_sum += max_weight
            marked_row.append(max_row)
            marked_col.append(max_col)
            max_weight = 0 #re-initialize max_weight
    #print score_sum
    sum_others = score_sum - highest_noun - second_noun - highest_verb - second_verb - highest_adj - second_adj
    return (score_sum, sum_others, full_entity_match, full_other_match, highest_noun, second_noun, highest_verb, second_verb, highest_adj, second_adj, speaker_half_match, speaker_full_match)


def verb_tag(tag):
    if (tag.startswith('V')):
        return True
    return False

def noun_tag(tag):
    if (tag.startswith('N')):
        return True
    return False

def adj_tag(tag):
    if (tag.startswith('J')):
        return True
    return False

#model = gensim.models.KeyedVectors.load_word2vec_format('../Model/GoogleNews-vectors-negative300.bin', binary=True) #time usage: 71.88s
