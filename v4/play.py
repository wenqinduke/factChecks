import spacy
from spacy import displacy

nlp = spacy.load('en')
#sentence1 = "PolitiFact rated it Half True when Donald Trump said that Hillary Clinton wanted the wall"
#sentence2 = "Is it true that Hillary Clinton wants to raise the minimum wage?
#sentence3 = "Hillary Clinton Says Donald Trump wants to get rid of the federal minimum wage"
test = "Donald Trump Claims there's 'nothing out there' about Hillary Clinton's religion even though she's been in the public eye for years and years."
doc = nlp(unicode(test,"utf-8"))
for token in doc:
    print(token.text, token.dep_, token.head.text, token.head.pos_,
          [child for child in token.children])
displacy.serve(doc, style='dep')
