import logging
import os

from sklearn.externals import joblib

from gensim import corpora, models, similarities
from pprint import pprint

from nltk.corpus import stopwords
from nltk.corpus import wordnet
import nltk.data

from goose import Goose

import os
import sys
import hashlib
import itertools
import threading
import re

from google import search, get_page

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Similar:
	def __init__(self, sentence, paragraph):
	    self.sentence = sentence
	    self.paragraph = paragraph
	    self.similarity_of(sentence, paragraph)

	def create_dic(self, documents):	
		texts = [[word for word in document.lower().split() if word not in stopwords.words('english')]
		         for document in documents]

		from collections import defaultdict
		frequency = defaultdict(int)
		for text in texts:
		    for token in text:
		        frequency[token] += 1
		texts = [[token for token in text if frequency[token] > 1]
		         for text in texts]

		dictionary = corpora.Dictionary(texts)
		corpus = [dictionary.doc2bow(text) for text in texts]
		return [dictionary, corpus]

	def create_model(self, dictionary, corpus):
		tfidf = models.TfidfModel(corpus)
		corpus_tfidf = tfidf[corpus]
		if len(dictionary) > 0:
			lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=500) # initialize an LSI transformation
			corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
			return lsi, corpus_lsi
		return None

	def get_similarity(self, doc, dictionary, corpus, lsi):
		vec_bow = dictionary.doc2bow(doc.lower().split())
		vec_lsi = lsi[vec_bow] # convert the query to LSI space
		index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
		sims = index[vec_lsi] # perform a similarity query against the corpus
		sims = list(enumerate(sims))
		return sims # return sorted (document number, similarity score) 2-tuples

	def similarity_of(self, sentence, paragraph):
		dictionary, corpus = self.create_dic(self.paragraph)
		# for d in dictionary:
		# 	print(dictionary[d])
		lsi, corpus_lsi = self.create_model(dictionary, corpus)
		self.rank = []
		if (lsi != None):
			self.rank = self.get_similarity(self.sentence, dictionary, corpus, lsi)

LANGUAGE = "english"
NEWS_DIR = "news"

DATASET = []
URLS = []

def ngram_counter(ngrams, text):
	counts = {}
	for ngram in ngrams:
	    words = ngram.rsplit()
	    pattern = re.compile(r'%s' % "\s+".join(words),
	        re.IGNORECASE)
	    counts[ngram] = len(pattern.findall(text))
	return counts

def doIt(query):
	DATASET = []
	URLS = []
	DIR_NAME = query

	print(DIR_NAME)

	DIRECTORY = NEWS_DIR + '/' + DIR_NAME

	with open(DIRECTORY, "r") as file:
		l = ''.join([x for x in file.read() if ord(x) < 128])
		if len(l) > 0:
			DATASET.append((DIRECTORY, l))

	sentences = []
	for name, article in DATASET:
		clean_article = re.sub(r"[^\w\s.]|_+", ' ', article.lower())
		clean_article = re.sub(r"[\n]", ' ', clean_article)
		sentences = clean_article.split('.')

	print(clean_article)

	fact = ["not hoax", "accurate", "true", "proof", "scientific", "paper", \
			"study", "sources", "cited", "evidence", "official"]
	hoax = ["hoax", "like a hoax", "fake", "lie", "rumor", "false", "in fact", "fake news", \
	        "debunked", "victim", "conspiracy", "expect", "uncertain", "skeptical", \
	        "satirical", "death hoax", "fake article", "fake story", "clickbait", "fabricated", \
	        "no truth", "no evidence", "incorrect", "satire", "altered", "if this were true", "if it was true", \
	        "dont actually", "nonsense", "no credible"]

	print(ngram_counter(hoax, clean_article))
	print(ngram_counter(fact, clean_article))

	print("\n")


query = ["3672bb6bd1719b5ea441940c4ca41832a52d28d9718953627de74d4da3a804f0/9.txt"]

for q in query:
	doIt(q)
