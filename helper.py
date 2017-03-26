import logging
from future.standard_library import install_aliases
install_aliases()

## SIMILAR
from gensim import corpora, models, similarities
from nltk.corpus import stopwords

## SEARCHER
import os
import hashlib
import re
import time
import multiprocessing
import uuid

import requests
import urllib.parse

import gevent
from gevent import monkey
from gevent import Greenlet

from GoogleScraper import scrape_with_config, GoogleSearchError

start = time.time()

#from goose import Goose
#import google

from newspaper import Article as News
from article import Article
from database import Database

import config

class Searcher:
	basedir = "news"
	factgram = ["real", "official", "officially", "true", "truth"]

	def __init__(self, query):
		### TO-DO: QUERY?????
		self.query = re.sub(r"[^\w\s]|_+", ' ', query.lower())

		for w in Searcher.factgram:
			self.query = self.query.replace(w, ' ')

		## Only get max 100 character
		self.query = self.query[:100]

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
		cache = self._get_cache()
		if not len(cache) > 10:
			if len(cache) != 0:
				self.db.del_reference_by_qhash(self.query_hash)

			keyword = self.query + self.query_exc

			config = {
				'use_own_ip': True,
				'keyword': keyword,
				'search_engines': ['google', 'bing', 'duckduckgo'],
				'num_pages_for_keyword': 1,
				'num_results_per_page': 10,
				'scrape_method': 'selenium'
			}

			try:
				search = scrape_with_config(config)
			except GoogleSearchError as e:
				print(e)

			searches = []
			for serp in search.serps:
				se = []
				count = 0
				for link in serp.links:
					if link.link_type == "results" and count < 10:
						se.append(link.link)
						count += 1
				searches.append(se)

			manager = multiprocessing.Manager()
			datasets = manager.list()
			mps = []
			for s in searches:
				go = multiprocessing.Process(target=self.search, args=(s, datasets,))
				mps.append(go)
				go.start()
			for mp in mps:
				mp.join()
			pdatasets = [x for x in datasets]
			return pdatasets
		else:
			datasets = []
			for article in cache:
				a = Article(self.query, article["hash"], article["url"], article["content"], article["date"])
				datasets.append(a)
			return datasets

	def search(self, searches, datasets):
		mps = []
		manager = multiprocessing.Manager()
		articles = manager.list()

		for url in searches:
			mp = multiprocessing.Process(name="Process for " + str(url), target=self.article_worker, args=(url, articles,))
			mp.daemon = True
			mps.append(mp)
			mp.start()
		
		for mp in mps:
			mp.join(10)
			mp.is_alive()
			time.sleep(.1)

		self.db.insert_references(self.qid, articles)
		for article in articles:
			a = Article(self.query, article["hash"], article["url"], article["content"], article["date"])
			datasets.append(a)

		print("Finish Data Gathering")
		logging.info("Finish Data Gathering")

	def get_news(self, qhash):
		articles = self.db.get_reference_by_qhash(qhash)
		datasets = []
		for article in articles:
			a = Article(self.query, article["hash"], article["url"], article["content"], article["date"])
			datasets.append(a)
		return datasets

	def article_worker(self, url, articles):
		jobs = [Greenlet.spawn(self.__gevent_worker, url, 'en')]
		gevent.joinall(jobs)

		news = jobs[0].value
		news.download()
		news.parse()
		date = news.publish_date
		text = news.text

		if len(text) < 100:
			jobs = [Greenlet.spawn(self.__gevent_worker, url, 'id')]
			gevent.joinall(jobs)

			news = jobs[0].value
			news.download()
			news.parse()
			date = news.publish_date
			text = news.text

		if len(str(date)) < 10:
			date = None
		if len(str(date)) > 19:
			date = str(date)[:19]

		l = ''.join([x for x in text if ord(x) < 128])
		if len(l) > 0:
			article = {}
			article["qhash"] = self.query_hash
			article["hash"] = uuid.uuid4().hex
			article["content"] = l
			article["url"] = str(url)
			article["date"] = str(date)
			articles.append(article)

	def __gevent_worker(self, url, lang):
		article = News(url, language=lang)
		return article

	def __sanitize_bing_url(self, bing_url):
		parsed_url = urllib.parse.urlparse(bing_url)
		redirect_url = urllib.parse.parse_qs(parsed_url.query)['r']
		return redirect_url[0]

	def __sanitize_bing_date(self, bing_date):
		return bing_date.replace('T', ' ')

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
