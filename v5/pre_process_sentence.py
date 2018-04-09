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

stop_words = set(stopwords.words('english'))
lmtzr = WordNetLemmatizer()
grammar = r"""
   # Chunk NP, VP
  NP: {(<RB|CD>)*(<PR.*>)?<POS|CC|DT|JJ.*|NN.*>+}          # Chunk sequences of DT, JJ, NN
  V:{(<TO|MD>)?<VB.*>+(<IN>)?(<RB|RP>)?(<VB.*>)?(<TO|MD>)?}
  VP: {(<RB>)?<V><NP|PP|CLAUSE>*} # Chunk verbs and their arguments
  CLAUSE: {<NP|PRP><VP> | <NP|PRP><V><NP>}

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
    pos_tags = pos_tag(word_tokenize(text))
    #tree = cp.parse(pos_tags)
    #print type(tree)
    # tree.draw()
    #traverse(tree)
    # print entity_list
    #print tokens
    # print tags
    # print ents_index


    return (tokens, tags, entity_list, ents_index, noun, verb, adj)

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

def traverse(t):
    try:
        t.label()
    except AttributeError:
        print(t)
    else:
        # Now we know that t.node is defined
        print('(', t.label())
        for child in t:
            traverse(child)
        print(')')

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

# text_file = open("../test_statements.txt", "r")
# lines = text_file.readlines()
# for line in lines:
#     line = line.replace("\n", "")
#     #line = "Is it true that Trump didn't pay 16 million taxes?"
#     # process (line)
#process("Is it true that Obamacare is causing health care premiums to increase?")
