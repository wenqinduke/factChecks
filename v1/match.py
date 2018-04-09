import gensim
import nltk

def max_match_score(claim_token, sta_token, model):
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
                        # if tag_important(claim_token[row]):
                        #     score_sum += 1.5
                        # else:
                        score_sum += 1
                        break
                    else:
                        matrix[row][col] = score

    max_weight = 0
    max_col = -1
    max_row = -1
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

        if (max_weight <= 0):
            break
        else:
            # if tag_important(claim_token[max_row]):
            #     score_sum += 1.5 * max_weight
            # else:
            score_sum += max_weight
            marked_row.append(max_row)
            marked_col.append(max_col)
            max_weight = 0 #re-initialize max_weight

    return score_sum

# def tag_important(word):
#     word_tag = nltk.pos_tag([word])
#     tag = word_tag[1]
#     if (tag == 'NN' or tag == 'VB' or tag == 'JJ' or tag == 'VBD' or tag == 'JJS' or tag == 'JJR' or tag == 'NNP' or tag == 'NNS' or tag == 'RB' or tag =='RBR' or tag ==
#     'RBS' or tag == 'VB' or tag == 'VBG' or tag == 'VBN' or tag == 'VBP' or tag == 'VBZ'):
#         return True
#     return False
