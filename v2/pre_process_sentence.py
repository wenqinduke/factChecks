import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import state_union
import re
from num2words import num2words
#from nltk.tokenize import PunktSentenceTokenizer

def process(example_text):

    ps = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    imp_tags = ['JJS','JJR', 'PDT', 'CD'] #may add JJ to test later;
    remove_words = ['said', 'say','says', 'true', 'right']
    tagged_sentence = nltk.pos_tag(word_tokenize(example_text.decode('utf-8')))

    tokens=[]
    tags=[]

    for word_tag in tagged_sentence:
        word = re.sub(r'[^\w\s]','',word_tag[0])
        tag = word_tag[1]
        if word.lower() not in stop_words or tag in imp_tags:
            if word.lower() not in remove_words and word != '':
                tokens.append(ps.stem(word.lower()))
                tags.append(tag)

    return (tokens, tags)
    #convert number into string
    # num_converted_sentence =[]
    # for word in filtered_sentence:
    #     if not re.search('\d+', word):
    #         num_converted_sentence.append(word)
    #     else:
    #         #can detect 'th', 's' which doesn't affect numbers
    #         word = word.replace("th", "")
    #         word = word.replace("s", "")
    #         try:
    #             num_converted_sentence += word_tokenize(num2words(int(word)).replace("-", " "))
    #         except ValueError:
    #             #add to results for those cannot converted; like 1billion
    #             num_converted_sentence.append(word)


    #namedEnt = nltk.ne_chunk(tagged)

    #return num_converted_sentence


#the abstract class for the default sentence tokenizer
#custom_sent_tokenizer = PunktSentenceTokenizer(example_text)
#tokenized = custom_sent_tokenizer.tokenize(example_text)
