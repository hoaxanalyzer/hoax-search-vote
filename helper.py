import logging
#from future.standard_library import install_aliases
#install_aliases()

## SIMILAR
from gensim import corpora, models, similarities
from nltk.corpus import stopwords

## SEARCHER
import hashlib
import re
import time
import uuid
import sys
import multiprocessing

start = time.time()

#from goose import Goose
import google

from article import Article
from database import Database

import searcher

import config

def create_article(data):
	url, title, text, date, qhash, query = data
	a = None
	if text != None:
		article = {}
		article["qhash"] = qhash
		article["hash"] = uuid.uuid4().hex
		article["content"] = title + '. ' + text
		article["url"] = url
		article["date"] = str(date)
		a = Article(query, article["hash"], article["url"], article["content"], article["date"])
	return a

def create_article_db(data):
	a = Article(data["query"], data["hash"], data["url"], data["content"], data["date"])
	return a

class Searcher:
	basedir = "news"
	factgram = ["real", "official", "officially", "true", "truth"]

	def __init__(self, query):
		### TO-DO: QUERY?????
		self.query = re.sub(r"[^\w\s]|_+", ' ', query.lower())

		for w in Searcher.factgram:
			self.query = self.query.replace(w, ' ')

		self.query = self.query[:100]
		self.query = self.query.strip()
		self.query_exc = ' -youtube -wikipedia -amazon -wordpress -blogspot -facebook -twitter -pinterest -google'

		self.query_hash = hashlib.sha256((self.query).encode('utf-8')).hexdigest()
		self.articledir = Searcher.basedir + '/' + self.query_hash
		self.db = Database()
		self.qid = -1

	def set_qid(self, qid):
		self.qid = qid

	def _get_cache(self):
		return self.db.get_reference_by_qhash(self.query_hash)

	def search_all(self):
		print("Start search for query: " + self.query)
		cache = self._get_cache()
		if not len(cache) > 10:
			print("No Cache")

			results = (searcher.search_all(self.query))

			articles = []
			datasets = []

			results = [o + (self.query_hash, self.query,) for o in results]

			with multiprocessing.Pool(processes=16) as pool:
				ret = pool.map(create_article, results)

			datasets = [x for x in ret if x is not None]

			self.db.insert_references(self.qid, self.query_hash, datasets)

			return datasets
		else:
			print("Cached")
			datasets = []
			for a in cache:
				a.update({"query": self.query})
			with multiprocessing.Pool(processes=len(cache)) as pool: 
				datasets = pool.map(create_article_db, cache)
			return datasets

	def get_news(self, qhash):
		articles = self.db.get_reference_by_qhash(qhash)
		datasets = []
		for a in articles:
			a.update({"query": self.query})
		if len(articles) != 0:
			with multiprocessing.Pool(processes=len(articles)) as pool: 
				datasets = pool.map(create_article_db, articles)
		return datasets

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
			lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50) # initialize an LSI transformation
			corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
			return lsi, corpus_lsi
		return None

	def get_similarity(self, doc, dictionary, corpus, lsi):
		vec_bow = dictionary.doc2bow(doc.lower().split())
		vec_lsi = lsi[vec_bow] # convert the query to LSI space
		index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
		sims = index[vec_lsi] # perform a similarity query against the corpus
		sims = list(enumerate(sims))
		print(sims)
		return sims # return sorted (document number, similarity score) 2-tuples

	def similarity_of(self, sentence, paragraph):
		dictionary, corpus = self.create_dic(self.paragraph)
		lsi, corpus_lsi = self.create_model(dictionary, corpus)
		self.rank = []
		if (lsi != None):
			self.rank = self.get_similarity(self.sentence, dictionary, corpus, lsi)
