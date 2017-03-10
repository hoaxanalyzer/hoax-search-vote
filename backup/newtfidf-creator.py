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
			lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=100) # initialize an LSI transformation
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
		lsi, corpus_lsi = self.create_model(dictionary, corpus)
		self.rank = []
		if (lsi != None):
			self.rank = self.get_similarity(self.sentence, dictionary, corpus, lsi)

LANGUAGE = "english"
NEWS_DIR = "news"

factgram = ["not hoax", "accurate", "true", "proof", "scientific", "paper", \
		"study", "sources", "cited", "evidence", "official"]
hoaxgram = ["hoax", "like a hoax", "fake", "a lie", "rumor", "false", "in fact", "fake news", \
        "debunked", "victim", "conspiracy", "expect", "uncertain", "skeptical", \
        "satirical", "death hoax", "fake article", "fake story", "clickbait", "fabricated", \
        "no truth", "no evidence", "incorrect", "satire", "altered", "if this were true", "if it was true", \
        "dont actually", "nonsense", "no credible"]

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

def article_worker(extractor, directory, filename, url):
	article = extractor.extract(raw_html=get_page(url))
	text = article.cleaned_text

	l = ''.join([x for x in text if ord(x) < 128])
	if len(l) > 0: 
		with open(directory + '/' + filename, 'w') as file:
			file.write(l)


def doIt(query):
	TARGET = ['unrelated', 'fact', 'hoax', 'unknown']
	DATASET = []
	URLS = []
	THREADS_EXTRACTOR = []
	TEST_SENTENCE = query
	TEST_QUERY = TEST_SENTENCE
	DIR_NAME = hashlib.sha256(TEST_QUERY).hexdigest()

	print("Search for " + TEST_QUERY)
	print(DIR_NAME)

	DIRECTORY = NEWS_DIR + '/' + DIR_NAME

	if not os.path.exists(DIRECTORY):
	 	os.makedirs(DIRECTORY)		
		count = 0
		threads = []
		for url in search(TEST_QUERY, tld='com', lang='en', stop=10):
			print("Retreieve data")
			FILENAME = str(count) + '.txt'
			URLS.append(str(url))

			extractor = Goose()
			t = threading.Thread(target=article_worker, args=(extractor, DIRECTORY, FILENAME, url,))
			count += 1
			threads.append(t)
			t.start()
		
		for t in threads:
			t.join()

		print("Finish Data Gathering")

		with open(DIRECTORY + '/index', 'w') as file:
			count = 0
			for url in URLS:	
				file.write(str(count) + ' | ' + url + '\n')
				count += 1

	for d in os.listdir(DIRECTORY):
		if d.endswith(".txt"):
			with open(DIRECTORY + '/' + d, "r") as file:
				l = ''.join([x for x in file.read() if ord(x) < 128])
				if len(l) > 0:
					DATASET.append((d, l))

	HOAXGRAM = {}
	FACTGRAM = {}

	sentences = []
	for name, article in DATASET:
		clean_article = re.sub(r"[^\w\s]|_+", ' ', article.lower())
		sentences.append(clean_article)
		
		fn = ngram_counter(factgram, clean_article)
		FACTGRAM[name] = fn
		hn = ngram_counter(hoaxgram, clean_article)
		HOAXGRAM[name] = hn


	similar = Similar(TEST_QUERY, sentences)

	print("QUERY SIMILARITY")
	for num, result in similar.rank:
		print(DATASET[num][0] + ": " + str(result))

	print("\n")

	dt = joblib.load('./models/model01-rev.pkl') 
	i = 0
	with open(DIRECTORY + '/dataset', 'w') as file:
		for num, result in similar.rank:
		 	nsims = result
		 	filename = DATASET[num][0]

		 	hcsv = ""
		 	for h in hoaxgram:
		 		hcsv += ", " + str(HOAXGRAM[filename][h])

		 	fcsv = ""
		 	for f in factgram:
		 		fcsv += ", " + str(FACTGRAM[filename][f])

		 	featurecsv = hcsv + fcsv
		 	print(featurecsv)

		 	#print(TEST_QUERY + ', ' + DIR_NAME + ', ' + str(filename) + featurecsv + ', ' + str(nsims) + ', unlabeled\n')
			file.write(TEST_QUERY + ', ' + DIR_NAME + ', ' + str(filename) + featurecsv + ', ' + str(nsims) + ', unlabeled\n')
			i += 1

query = ["Masukin Querynya kesini"]

for q in query:
	doIt(q)
