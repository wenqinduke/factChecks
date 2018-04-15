from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import state_union
from nltk.corpus import wordnet
import nltk.chunk
import nltk
import re
from num2words import num2words
import time
from sets import Set

import psycopg2
import pandas as pd
import psycopg2.extras


stop_words = set(stopwords.words('english'))
lmtzr = WordNetLemmatizer()
grammar = r"""
   # Chunk NP, VP
  NP: {(<RB|CD>)*(<PR.*>)?<POS|CC|DT|JJ.*|NN.*>+}          # Chunk sequences of DT, JJ, NN
  V:{(<TO|MD>)?<VB.*>+(<RB|RP>)?(<VB.*>)?(<TO|MD>)?}
  INP: {<IN>(<DT>)?<NN.*|NP>+}
  VP: {(<RB>)?(<TO>)?<V>+<NP|PP|CLAUSE>*(<TO>)?} # Chunk verbs and their arguments
  CLAUSE: {<NP|PRP><VP|V>+(<INP>)? | <NP|PRP><V><NP>(<INP>)? | <VP><NP>(<INP>)?}

  """
#PP: {<IN><NP>}
#VP: {<VB.*><NP|PP|CLAUSE>+$}  Chunk verbs and their arguments
#CLAUSE: {<NP><VP>} Chunk NP, VP

cp = nltk.chunk.RegexpParser(grammar)

def process(text):
    imp_tags = ['JJS','JJR', 'PDT', 'CD'] #Important tags: may add JJ to test later
    remove_words = ['said', 'says','say', 'true', 'right', 'claim', 'do', 'does', 'doe', 'be', 'want', 'might'] #words that should be removed
    #remove_verbs = ['said', 'says', 'say', 'claimed', 'claims', 'claim']
    text = text.decode('ascii', 'ignore')
    text = text.replace("-", " ")
    #text = unicode(text, 'utf-8')
    #things we want: Word tokens, word tags, entity list, entity index,
    tokens = []
    tags = []
    #ents = []
    ents_index = []
    person = []
    noun = 0
    verb = 0
    adj = 0

    #ps = PorterStemmer() - Can't use stem due to Google news model

    entity_list = [] # form: [(u'hillary', u'B-PERSON', 0), (u'clinton', u'I-PERSON', 1), (u'obama', u'B-PERSON', 6)]
    #print text
    tokenized = word_tokenize(text)
    pos_tags = pos_tag(tokenized) #form:[(u'Says', 'VBZ'), (u'Hillary', 'NNP'), (u'Clinton', 'NNP'), (u'lied', 'VBD')]

    index = 0
    for word_ent in pos_tags:
        (word, tag) = word_ent
        word = re.sub(r'[^\w\s]','',word)
        word = word.lower()
        if word not in stop_words or tag in imp_tags:
            if word not in remove_words and word != "":
                word = lem(word, tag)
                tokens.append(word)
                tags.append(tag)
                if tag.startswith("V"):
                    verb += 1
                elif tag.startswith("N"):
                    noun += 1
                elif tag.startswith("R") or tag.startswith("J"):
                    adj += 1
                index += 1

    ne_tree = ne_chunk(pos_tags)
    iob_tagged = tree2conlltags(ne_tree)
    # print iob_tagged
    remove_entity = ['did', 'does', 'do']
    for token in iob_tagged:
        (word, tag, entity) = token
        if entity != 'O' and word.lower() not in remove_entity :
            word = re.sub(r'[^\w\s]','',word)
            word = word.lower()
            word = lem(word, tag)
            if word in tokens:
                index_num = tokens.index(word)
                ents_index.append(index_num)
                entity_list.append((word, entity,index_num))
            else:
                entity_list.append((word, entity, -1))

    #text = re.sub(r'[^\w\s]','',text)
    # for rem in remove_verbs:
    #     if rem in text:
    #         text = text.replace(rem, ",")
    text = text.replace("said", ",")
    text = text.replace("says", ",")
    text = text.replace("say", ",")
    text = text.replace("that", ',')
    text = text.replace("of", "")
    text = text.replace('"', "")
    end_of_sentence = [".", "!", "?"]
    for punc in end_of_sentence:
        text = text.replace(punc, "")
    pos_tags = pos_tag(word_tokenize(text))
    # in_words = ["that", "after", "than"]
    # for node in pos_tags:
    #     (node_word, node_tag) = node
    #     if node_tag == 'IN' and node_word not in in_words:
    #         pos_tags.remove(node)

    tree = cp.parse(pos_tags)
    #print type(tree)
    tree.draw()
    all_text = []
    traverse(tree, all_text)
    print all_text
    res = process_all_text(all_text)
    print res
    print delete_duplicate(res)

    # print entity_list
    #print tokens
    # print tags
    # print ents_index


    return (tokens, tags, entity_list, ents_index, noun, verb, adj)

# TEMP: very nasty/bruteforce code;
def delete_duplicate(array_list):
    index = len(array_list)
    res = []
    array_list.pop(-1)
    res.append(array_list[-1])
    while index > 0:
        current = array_list[index]
        next_array = array_list[index - 1]
        if len(current) == len(next_array):
            diff = [w for w in current if w not in next_array]
            if len(diff) <= 1 and current[0] != next_array[0]:
                if current in res:
                    res.remove(current)
                res.append(next_array)
                index -= 1
                continue
        res.append(current)
        index -= 1
    return res

def process_all_text(all_text):
    res = []
    in_process = []
    index = 0
    while index < len(all_text):
        current = all_text[index]
        if current == '[':
            new_array = []
            if all_text[index + 2] == ']':
                index += 3
                continue
            new_array.append(all_text[index + 1])
            in_process.append(new_array)
            index += 1
        elif current == ']':
            if len(in_process[-1]) < 3:
                index += 1
                del in_process[-1]
                continue
            res.append(in_process[-1])
            del in_process[-1]
        else:
            #print current
            (word, label) = current
            if word in stop_words:
                index += 1
                continue
            word = word.lower()
            word = lem(word, label)
            for process in in_process:
                process.append(word)
        index += 1
    return res




def get_similar_words(word, model):
    bag_words = []
    try:
        bag_words = model.wv.most_similar(word, topn = 10)
    except KeyError:
        print 'key not exist'

    similar_words = Set([])

    for bag_word in bag_words:
        pos_tags = pos_tag([bag_word[0]])
        (sim_word, tag) = pos_tags[0]
        sim_word = lem(sim_word, tag)
        similar_words.add(sim_word)
    similar_words.add((word))
    similar_words = list(similar_words)
    return similar_words

    #print verbs
def lem(word, tag):
    attri = get_wordnet_pos(tag)
    if attri == '':
        word = lmtzr.lemmatize(word)
    else:
        word = lmtzr.lemmatize(word, attri)
    return word

def traverse(t, all_text):
    try:
        t.label()
    except AttributeError:
        (word, label) = t
        word = re.sub(r'[^\w\s]','',word)
        if word not in stop_words and word != "":
            all_text.append((word, label))
        #print(t)
    else:
        # Now we know that t.node is defined
        all_text.append('[')
        all_text.append( t.label())
        for child in t:
            traverse(child, all_text)
        all_text.append(']')

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''

conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
query = "select stat_id from test_questions"
df = pd.read_sql_query(query, conn)
cursor = conn.cursor()

for index in range(df.shape[0]):
    stat_ids = df.stat_id[index]
    for stat_id in stat_ids:
        cursor.execute("select statement, speaker, summary from facts where id = %s", (stat_id,))
        result_row = cursor.fetchone()
        claim = result_row[0]
        if claim.startswith('Says'):
            claim = claim.replace('Says', "")
        speaker = result_row[1]
        question = speaker + "said that" + claim
        process(question)
#process("Is it true that Obamacare is causing health care premiums to increase?")
# if tag == "IN" and word != "that"; should delete all those words. Otherwise they don't get to stick to the verb.  Maybe?? Not sure..
