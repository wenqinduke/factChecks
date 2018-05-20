from nltk.parse.stanford import StanfordDependencyParser
stanford_parser_dir = '../stanford-parser/'
eng_model_path = stanford_parser_dir  + "stanford-parser-models/edu/stanford/nlp/models/lexparser/englishRNN.ser.gz"
my_path_to_models_jar = stanford_parser_dir  + "stanford-parser-3.5.2-models.jar"
my_path_to_jar = stanford_parser_dir  + "stanford-parser.jar"
# nlp = StanfordCoreNLP(r'/Users/wenqinwang/Desktop/Fact-Checking/stanford-corenlp-python/stanford-corenlp-full-2018-02-27')

sentence = 'Guangdong University of Foreign Studies is located in Guangzhou.'
# print 'Tokenize:', nlp.word_tokenize(sentence)
# print 'Part of Speech:', nlp.pos_tag(sentence)
# print 'Named Entities:', nlp.ner(sentence)
print 'Constituency Parsing:', nlp.parse(sentence)
# print 'Dependency Parsing:', nlp.dependency_parse(sentence)

nlp.close()
