
import gensim
import time
import pre_process_sentence

def max_match_score(ques_tags, ques_tokens, ques_ents, ques_ents_index, claim_tags, claim_tokens, claim_ents,  claim_ents_index, speaker_token, model):
    verb_weight = 1
    noun_weight = 1
    entity_weight = 1.5
    #imp_weight = 1.5

    highest_noun = 0
    second_noun = 0
    third_noun = 0
    fourth_noun = 0
    highest_verb = 0
    second_verb = 0
    third_verb = 0
    highest_adj = 0
    second_adj = 0
    sum_others = 0
    full_entity_match = 0
    full_other_match = 0

    w,h = len(ques_tokens), len(claim_tokens);
    matrix = [[0 for x in range(h)] for y in range(w)]

    marked_row = []
    marked_col = []
    keyError = False
    speaker_half_match = 0
    speaker_full_match = 1
    score_sum = 0;
    for speaker in speaker_token:
        if speaker in ques_tokens:
            speaker_half_match = 1
            marked_row.append(ques_tokens.index(speaker))
        if speaker not in ques_tokens:
            speaker_full_match = 0

    for row in range(w):
        if row not in marked_row: #proceed to the next if row is already selected
            for col in range(h):
                if col not in marked_col:
                    score = 0
                    try:
                        score = model.similarity(ques_tokens[row], claim_tokens[col])
                    except KeyError:
                        keyError = True
                    if score >= 0.99 or ques_tokens[row] == claim_tokens[col]: #selec current edge since it perfectly matches
                        marked_row.append(row)
                        marked_col.append(col)
                        full_other_match += 1
                        if row in ques_ents_index or col in claim_ents_index:
                            score_sum += entity_weight
                            full_entity_match += 1
                        # elif row in claim_imp_index:
                        #     score_sum += imp_weight
                        elif verb_tag(ques_tags[row]):
                            if highest_verb == 0:
                                highest_verb = verb_weight
                            elif second_verb == 0:
                                second_verb= verb_weight
                            elif third_verb == 0:
                                third_verb = verb_weight
                            score_sum += verb_weight
                        elif noun_tag(ques_tags[row]):
                            if highest_noun == 0:
                                highest_noun = noun_weight
                            elif second_noun == 0:
                                second_noun = noun_weight
                            elif third_noun == 0:
                                third_noun = noun_weight
                            elif fourth_noun == 0:
                                fourth_noun = noun_weight
                            score_sum += noun_weight
                        elif adj_tag(ques_tags[row]):
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
    while len(marked_row) < len(ques_tokens) and len(marked_col) < len(claim_tokens):
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
            if max_row in ques_ents_index:
                score_sum += entity_weight * max_weight
            # elif max_row in claim_imp_index:
            #     score_sum += imp_weight * max_weight
            elif verb_tag(ques_tags[max_row]):
                if highest_verb < max_weight:
                    third_verb = second_verb
                    second_verb = highest_verb
                    highest_verb = max_weight
                elif second_verb < max_weight:
                    third_verb = second_verb
                    second_verb= max_weight
                elif third_verb < max_weight:
                    third_verb = max_weight
                score_sum += verb_weight * max_weight
            elif noun_tag(ques_tags[max_row]):
                if highest_noun < max_weight:
                    fourth_noun = third_noun
                    third_noun = second_noun
                    second_noun = highest_noun
                    highest_noun = max_weight
                elif second_noun < max_weight:
                    fourth_noun = third_noun
                    third_noun = second_noun
                    second_noun= max_weight
                elif third_noun < max_weight:
                    fourth_noun = third_noun
                    third_noun = max_weight
                elif fourth_noun < max_weight:
                    fourth_noun = max_weight
                score_sum += noun_weight * max_weight
            elif adj_tag(ques_tags[max_row]):
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
    if (sum_others < 0):
        sum_others = 0
    return (score_sum, sum_others, full_entity_match, full_other_match, highest_noun, second_noun, third_noun, fourth_noun, highest_verb, second_verb, third_verb, highest_adj, second_adj, speaker_half_match, speaker_full_match)


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
