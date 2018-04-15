from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import urllib2
import urllib
from bs4 import BeautifulSoup
from cookielib import CookieJar
import psycopg2
import psycopg2.extras
import pandas as pd
import time
#
# ids_needed = [1240, 386, 2253, 1379, 2249, 2063, 629, 1905, 851, 440, 940, 258, 707, 2381, 2052, 2306, 2267, 1513, 1944, 1571,2250, 2049, 981, 2269,
# 2410, 2056, 2272, 1165, 1067, 393, 2057, 456, 998, 1301, 2084, 7779, 1576, 2374, 6232, 2498, 981, 1423, 2160, 1811, 1616, 2390, 2169, 902, 2083, 529, 1855, 1681,
# 11255, 1426, 2051, 1283, 2826, 2165, 2166, 1406,3402, 1374, 3605, 3476, 3894, 1538, 530, 360, 980, 2835, 1733]
class FrequencySummarizer:
  def __init__(self, min_cut=0.1, max_cut=1):
    """
     Initilize the text summarizer.
     Words that have a frequency term lower than min_cut
     or higer than max_cut will be ignored.
    """
    self._min_cut = min_cut
    self._max_cut = max_cut
    self._stopwords = set(stopwords.words('english') + list(punctuation))

  def _compute_frequencies(self, word_sent):
    """
      Compute the frequency of each of word.
      Input:
       word_sent, a list of sentences already tokenized.
      Output:
       freq, a dictionary where freq[w] is the frequency of w.
    """
    freq = defaultdict(int)
    for s in word_sent:
      for word in s:
        if word not in self._stopwords:
          freq[word] += 1
    # frequencies normalization and fitering
    m = float(max(freq.values()))
    for w in freq.keys():
      freq[w] = freq[w]/m
      if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
        del freq[w]
    return freq

  def summarize(self, text, n):
    """
      Return a list of n sentences
      which represent the summary of text.
    """
    sents = sent_tokenize(text)
    try:
        assert n <= len(sents)
    except AssertionError:
        return [""]
    word_sent = [word_tokenize(s.lower()) for s in sents]
    self._freq = self._compute_frequencies(word_sent)
    ranking = defaultdict(int)
    for i,sent in enumerate(word_sent):
      for w in sent:
        if w in self._freq:
          ranking[i] += self._freq[w]
    sents_idx = self._rank(ranking, n)
    return [sents[j] for j in sents_idx]

  def _rank(self, ranking, n):
    """ return the first n sentences with highest ranking """
    return nlargest(n, ranking, key=ranking.get)

def get_only_text(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    cj = CookieJar()
    req = urllib2.Request(url, headers = hdr)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    try:
        page_open = opener.open(req)
        page = page_open.read().decode('utf8')
        soup = BeautifulSoup(page, 'lxml')
        text_block = soup.find("article")
        if text_block is None:
            text_block = soup.find("div", {"class": "blurb-text"})
        if text_block is None:
            text_block = soup.find("div", {"id": "tag_descr"})
        if text_block is None:
            text_block = soup.find("div", {"class": "content-fact"})
        
        for script in soup.find_all('script'):
            script.extract()
        text = ' '.join(map(lambda p: p.text, text_block.find_all('p')))
        title_text = soup.title.text
    except (Exception, AttributeError) as e:
        out_file.write(url)
        out_file.write(" : ")
        out_file.write(str(e))
        out_file.write("\n")
        text = ""
        title_text = ""

    return title_text, text

def name_entity(sentence):
    sentence = sentence.encode('ascii', 'ignore')
    ne_tree = ne_chunk(pos_tag(word_tokenize(sentence)))
    iob_tagged = tree2conlltags(ne_tree)
    entity_list = []
    for token in iob_tagged:
        (word, tag, entity) = token
        if entity != 'O':
            entity_list.append((word, entity))
    return entity_list

out_file = open("./summary_error.txt", "w")


print ('alter database..')
conn = psycopg2.connect("dbname=sharefacts user=wenqinwang")
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
drop_table_summary = '''ALTER TABLE facts DROP COLUMN IF EXISTS summary'''
drop_table_entity = '''ALTER TABLE facts DROP COLUMN IF EXISTS entity_list'''
add_table_summary = '''ALTER TABLE facts ADD COLUMN summary TEXT'''
add_table_entity = '''ALTER TABLE facts ADD COLUMN entity_list text[]'''
cursor.execute(drop_table_summary)
cursor.execute(drop_table_entity)
cursor.execute(add_table_summary)
cursor.execute(add_table_entity)
conn.commit()

print ('get dataframe...')
query = 'select id, "redirectURL", summary from facts'
dataframe = pd.read_sql_query(query, conn)

print ('summarize and extract name entity...')
fs = FrequencySummarizer()
for index in range(dataframe.shape[0]):
    #for update only: if summary and name entity already exists, continue
    # if dataframe.summary[index] != "":
    #     continue
    print (index)
    data_id = dataframe.id[index]
    data_url = dataframe.redirectURL[index]
    if data_url == "" or data_url is None:
        continue
    (title, text) = get_only_text(data_url)
    entity_list_full = set()
    for entity_tuple in name_entity(title):
        entity_list_full.add(entity_tuple)
    try:
        s = fs.summarize(text, 1)[0]
    except IndexError:
        out_file.write('%s' % index)
        out_file.write(" : ")
        out_file.write(str(IndexError))
        out_file.write("\n")
        s = ""
    for entity_tuple in name_entity(s):
        entity_list_full.add(entity_tuple)
    entity_list_full = list(entity_list_full)
    data_summary = s + title

    cursor.execute('''UPDATE facts SET summary = (%s), entity_list = (%s) where id = (%s)''', (data_summary, entity_list_full, data_id))
    conn.commit()

#article_url = 'https://www.washingtonpost.com/news/fact-checker/wp/2016/07/11/huckabees-claim-that-more-white-people-were-shot-in-2015-than-minorities/'
#article_url = 'http://www.politifact.com/texas/statements/2016/jan/06/donald-trump/donald-trump-incorrectly-says-ted-cruz-has-had-dou/'
#article_url = 'https://www.factcheck.org/2017/01/trump-pulls-quotes-aca-context/'
# article_url = 'https://www.gossipcop.com/amber-rose-growing-hair-out-photo/'
# (title, text) = get_only_text(article_url)
# print title
# entity_list_full = set()
# for entity_tuple in name_entity(title):
#     entity_list_full.add(entity_tuple)
# for s in fs.summarize(text, 1):
#     for entity_tuple in name_entity(s):
#         entity_list_full.add(entity_tuple)
#     print '*',s
#
# print entity_list_full
