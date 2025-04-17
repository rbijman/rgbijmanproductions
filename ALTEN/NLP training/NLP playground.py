# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 21:08:25 2025

@author: rbijman
"""
#NLP course https://www.youtube.com/watch?v=dIUTsFT2MeQ

import spacy

nlp = spacy.load('en_core_web_sm')

with open (r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\NLP training\wiki_us.txt") as f:
    text = f.read()
    
doc = nlp(text)

print(doc)

#%% splits the text in words/punctations etc (tokens)
for token in doc[0:10]:
    print(token)
    
    
for sent in doc.sents:
    print(sent)
    
#%% grep a specific sentence. Since doc.sents are generators, we need to make them a list first    
sentence1 = list(doc.sents)[0]
print(sentence1)

#%%

text = "Mike enjoys playing football."
doc2 = nlp(text)
print(doc2)

for token in doc2:
    print (token.text, token.pos_, token.dep_)

html = spacy.displacy.render(doc2,style="dep")
from IPython.display import display, HTML
display(HTML(html))

#%% Enteties and their labels

for ent in doc.ents:
    print(ent.text, ent.label_)


#%% Word vector to use for similarity of words/docs
nlp2 = spacy.load('en_core_web_md')

doc3 = nlp2(text)
sentence1 = list(doc3.sents)[0]
print(sentence1)

doc1 = nlp2("I like salty fries and hamburgers.")
doc2 = nlp2("Fast food tastes very good.")
doc3 = nlp2("The Empire State Building is in New York")
doc4 = nlp2("I enjoy oranges.")
doc5 = nlp2("I enjoy oranges?")
print (doc4, "<->",doc5, doc4.similarity(doc5))


#%% Sample Spacy Pipeline for NER very usefull to make the functionality faster if you want specific tasks to be performed!
# but maybe less accurate

nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")
nlp2.analyze_pipes()


#%% entity ruler (rules based approach, alternatively use machine learning approach)
nlp = spacy.load("en_core_web_sm")
text = "West Chestertenfieldville was referenced in Mr. Deeds."
doc = nlp(text)
doc.text

ruler = nlp.add_pipe("entity_ruler",before="ner")

for ent in doc.ents:
    print(ent.text,ent.label_)

patterns = [{'label':'GPE','pattern':'West Chstertenfieldville'},{'label':'film','pattern':'Mr. Deeds'}]

ruler.add_patterns(patterns)

#Need to load nlp object again!!! It is not going to be updated by adding patterns or so
doc = nlp(text)
doc.text

for ent in doc.ents:
    print(ent.text,ent.label_)
    
    
#%% Matcher

matcher = spacy.matcher.Matcher(nlp.vocab)
pattern = [{"LIKE_EMAIL": True}] #Check SPACY documentation for all options for the keys, the values can either be boolean or key specific values
matcher.add("EMAIL ADDRESS",[pattern]) #label and pattern (list of lists) 
doc = nlp("This is an email adress: rik.bijman@alten.nl")
matches = matcher(doc) #output is lexeme, start token, end token
print(matches)
print(nlp.vocab[matches[0][0]].text)


#%% Example Matcher
with open (r"C:\Users\rbijman\Documents\GitHub\rgbijmanproductions\ALTEN\NLP training\wiki_mlk.txt") as f:
    text = f.read()
    
nlp = spacy.load("en_core_web_sm")

matcher = spacy.matcher.Matcher(nlp.vocab)
pattern = [{"POS":"PROPN","OP":"+"},{"POS":"VERB"}] #list of dictionairies in case you want multi pattern
matcher.add("PROPER_NOUN",[pattern],greedy="LONGEST")
doc = nlp(text)
matches=matcher(doc)
matches.sort(key=lambda x: x[1])
print(len(matches))
for match in matches[:10]:
    print(match, doc[match[1]:match[2]])



