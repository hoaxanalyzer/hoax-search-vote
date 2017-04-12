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

start = time.time()

#from goose import Goose
import google

from article import Article
from database import Database

import searcher

import config

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

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
		logging.info("Start do SEARCH ALL")
		cache = self._get_cache()
		if not len(cache) > 10:
			print("No Cache")
			if len(cache) != 0:
				self.db.del_reference_by_qhash(self.query_hash)
			logging.info("Finish INIT SEARCH ALL")

			results = (searcher.search_all(self.query))
			logging.info("Finish SEARCH ALL for " + self.query)

			articles = []
			datasets = []

			for result in results:
				article = {}
				article["qhash"] = self.query_hash
				article["hash"] = uuid.uuid4().hex
				article["content"] = result[2] + '. ' + result[1]				
				article["url"] = result[0]
				article["date"] = str(result[3])
				articles.append(article)

				a = Article(self.query, article["hash"], article["url"], article["content"], article["date"])
				datasets.append(a)

			logging.info("Finish Gathering Results")
			self.db.insert_references(self.qid, articles)
			logging.info("Finish Insert to DB")

			pdatasets = datasets
			# pdatasets = self.search(searches)
			return pdatasets
		else:
			print("Cached")
			datasets = []
			for article in cache:
				a = Article(self.query, article["hash"], article["url"], article["content"], article["date"])
				datasets.append(a)
			return datasets

	def get_news(self, qhash):
		articles = self.db.get_reference_by_qhash(qhash)
		datasets = []
		for article in articles:
			a = Article(self.query, article["hash"], article["url"], article["content"], article["date"])
			datasets.append(a)
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
