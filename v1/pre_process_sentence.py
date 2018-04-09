import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import state_union
import re
from num2words import num2words
#from nltk.tokenize import PunktSentenceTokenizer

def process(example_text):

    #get rid of punctuations and tokenize them.
    example_text = example_text.lower();
    word_tokens = word_tokenize(re.sub(r'[^\w\s]','',example_text))
    #extract stop_words
    stop_words = set(stopwords.words('english'))
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    #filtered_sentence = [w for w in tokenized if not w in stop_words]
    #ps = PorterStemmer()
    #stems = [ps.stem(w) for w in word_tokens]

    #convert number into string
    num_converted_sentence =[]
    for word in filtered_sentence:
        if not re.search('\d+', word):
            num_converted_sentence.append(word)
        else:
            #can detect 'th', 's' which doesn't affect numbers
            word = word.replace("th", "")
            word = word.replace("s", "")
            try:
                num_converted_sentence += word_tokenize(num2words(int(word)).replace("-", " "))
            except ValueError:
                #add to results for those cannot converted; like 1billion
                num_converted_sentence.append(word)


    #tagged = nltk.pos_tag(filtered_sentence)
    #namedEnt = nltk.ne_chunk(tagged)

    #todo: need to convert number into string
    return num_converted_sentence

#this is a sentence wise tokenization
#sentence_tokens = sent_tokenize(example_text)
#this is a word-wise tokenization
#word_tokens = word_tokenize(example_text)

#the abstract class for the default sentence tokenizer
#custom_sent_tokenizer = PunktSentenceTokenizer(example_text)
#tokenized = custom_sent_tokenizer.tokenize(example_text)
