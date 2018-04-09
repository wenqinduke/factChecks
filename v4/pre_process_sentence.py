import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import state_union
import re
from num2words import num2words
import spacy
import time
# from textblob import TextBlob
# from textblob import Word
#from nltk.tokenize import PunktSentenceTokenizer

    #can also have subject/name entity recognition.
def process(example_text,nlp):
    imp_tags = ['JJS','JJR', 'PDT', 'CD'] #Important tags: may add JJ to test later
    remove_words = ['said', 'say','says', 'true', 'right', 'claim', 'do', 'be', 'want'] #words that should be removed
    example_text = example_text.decode("utf-8")
    doc = nlp(example_text.lower())
    tokens = []
    tags = []
    #deps = []
    ents = []
    ents_index = []
    imp_index = []
    person = []
    verb = []

    count = 0
    for token in doc:
        lem = token.lemma_  #lower case + stem
        tag = token.tag_ #POS tags
        #dep = token.dep_ #this  can identify subjects if dep == 'nsubj'; if dep == 'ROOT' it is important
        if not token.is_stop or tag in imp_tags:
            if lem not in remove_words and not token.is_punct :
                lem = re.sub(r'[^\w\s]','', lem) #remove punctuations
                # if lem.endswith("'s"):
                #     lem = lem[:-2]
                # elif lem.endswith("'"):
                #     lem = lem[:-1]
                if lem == '-PRON-' or lem == 'PRON' or lem == "" or lem == " " or lem == "  ": #remove pron and white space
                    continue
                tokens.append(lem)
                tags.append(tag)
                if tag.startswith('V'):
                    verb.append(count) #append the index of verbs in the tokens
                count += 1

                #deps.append(dep)

    for ent in doc.ents:
        label = ent.label_
        ent_text = ent.text
        if label == 'PERSON' or label == 'ORG':
            ents.append((ent_text, label))
            word_list = ent_text.lower().split(" ")
            if label == 'ORG':
                for word in word_list:
                    if word.endswith("'s"):
                        word = word[:-2]
                    if word in tokens:
                        ents_index.append(tokens.index(word))
            if label == 'PERSON':
                word = word_list[-1]
                if word == "":
                    word = word_list[-2]
                if word.endswith("'s"):
                    word = word[:-2]
                if word in tokens:
                    person.append(tokens.index(word))
                    ents_index.append(tokens.index(word))
        if label == 'GPE':
            word_list = ent_text.lower().split(" ")
            for word in word_list:
                if word in tokens:
                    imp_index.append(tokens.index(word))
    #also add index of name entity tags.
    return (tokens, tags, ents, ents_index, imp_index, person, verb)

    #stop_words = set(stopwords.words('english'))
    # blob = TextBlob(example_text)
    # english = False
    # try:
    #     blob = blob.correct().translate(to='en')
    # except:
    #     english = True
    #
    # tag_list = blob.tags #[('word', 'NN')]; automatically get rid of punctuations .
    # lem_text = [] #lemmatize; singular/plural;
    # tags = []
    # for index in range(len(blob.words)):
    #     lem = blob.words[index].lower()
    #     tag = tag_list[index][1]
    #     w = Word(lem)
    #     if tag.startswith("V"):
    #         lem = w.lemmatize('v')
    #     if tag.startswith("N"):
    #         lem = w.lemmatize()
    #     if lem not in stop_words or tag in imp_tags:
    #         if lem not in remove_words and lem != "":
    #             lem_text.append(lem)
    #             tags.append(tag)
    # return (lem_text, tags)
#nlp = spacy.load('en')
#print process("On Obamacare, the premiums are going up 60, 70, 80 percent.", nlp)
