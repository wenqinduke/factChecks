import gensim
import nltk

def max_match_score(claim_tags, claim_token, sta_token, model):
    #claim_tags = ['NNP', 'NNP', 'NNS', 'VBP', 'JJ', 'NN']
    #claim_token = [u'hillari', u'clinton', u'plan', u'add', u'nation', u'debt']
    #sta_token= [u'independ', u'analyst', u'donald', u'trump', u'would', u'add', u'30', u'trillion', u'nation', u'debt']
    verb_weight = 1.5
    noun_weight = 1.5
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
                        if verb_tag(claim_tags[row]):
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
            if verb_tag(claim_tags[max_row]):
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

    if (tag == 'VB' or tag == 'VBD' or tag == 'VBG' or tag == 'VBN' or tag == 'VBP' or tag == 'VBZ'):
    # if (tag == 'NN' or tag == 'VB' or tag == 'JJ' or tag == 'VBD' or tag == 'JJS' or tag == 'JJR' or tag == 'NNP' or tag == 'NNS' or tag == 'RB' or tag =='RBR' or tag ==
    # 'RBS' or tag == 'VBG' or tag == 'VBN' or tag == 'VBP' or tag == 'VBZ'):
        return True
    return False

def noun_tag(tag):
    if (tag == 'NN' or tag == 'NNS' or tag == 'NNP'):
        return True
    return False
