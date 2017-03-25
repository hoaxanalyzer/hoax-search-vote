import logging
from future.standard_library import install_aliases
install_aliases()

## SIMILAR
from gensim import corpora, models, similarities
from nltk.corpus import stopwords

## SEARCHER
import articleDateExtractor
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

start = time.time()

from goose import Goose
import google

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

		self.query_hash = hashlib.sha256(self.query).hexdigest()
		self.articledir = Searcher.basedir + '/' + self.query_hash
		self.db = Database()
		self.qid = -1

	def set_qid(self, qid):
		self.qid = qid

	def _get_cache(self):
		return self.db.get_reference_by_qhash(self.query_hash)

	def search_all(self):
		cache = self._get_cache()
		if not len(cache) > 5:
			manager = multiprocessing.Manager()
			datasets = manager.list()
			searches = [self.google(), self.bing()]
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
		
		for data in searches:
			mp = multiprocessing.Process(name="Process for " + str(data["url"]), target=self.article_worker, args=(data, articles,))
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

	def article_worker(self, data, articles):
		filename = data["filename"]
		url = data["url"]
		date = data["date"]

		jobs = [Greenlet.spawn(google.get_page, url)]
		gevent.joinall(jobs)

		html = jobs[0].value
		
		extractor =  Goose({'browser_user_agent': 'Mozilla', 'enable_image_fetching': False, 'http_timeout': 10})
		if date == None:
			date = articleDateExtractor.extractArticlePublishedDate(url, html)
		if len(str(date)) < 10:
			date = None
		if len(str(date)) > 19:
			date = str(date)[:19]

		article = extractor.extract(raw_html=html)
		text = article.cleaned_text

		l = ''.join([x for x in text if ord(x) < 128])
		if len(l) > 0:
			article = {}
			article["qhash"] = self.query_hash
			article["hash"] = uuid.uuid4().hex
			article["content"] = l
			article["url"] = str(url)
			article["date"] = str(date)
			articles.append(article)

	def __sanitize_bing_url(self, bing_url):
		parsed_url = urllib.parse.urlparse(bing_url)
		redirect_url = urllib.parse.parse_qs(parsed_url.query)['r']
		return redirect_url[0]

	def __sanitize_bing_date(self, bing_date):
		return bing_date.replace('T', ' ')

	def bing(self):
		count = 0
		url_query = urllib.quote_plus(self.query)
		headers = {'Ocp-Apim-Subscription-Key': config.bing_api_credential}
		r = requests.get('https://api.cognitive.microsoft.com/bing/v5.0/news/search?q='+ url_query +'&count=10&mkt=en-us', headers=headers)
		data = []
		results = r.json()
		for article in results["value"]:
			date = "1950-01-01 00:00:00+00:00"
			if "datePublished" in article.keys():
				date = article["datePublished"]
			obj = {}
			obj["url"] = self.__sanitize_bing_url(article["url"])
			obj["filename"] = 'b' + str(count)
			obj["date"] = self.__sanitize_bing_date(date)
			data.append(obj)
			count += 1
			if (count > 10): break
		return data

	def google(self):
		count = 0
		data = []
		query_exclusion = " -site:twitter.com -site:youtube.com -site:pinterest.com -site:amazon.com"
		for url in google.search(self.query + query_exclusion, tld='com', lang='en', stop=10):
			obj = {}
			obj["url"] = url
			obj["filename"] = 'g' + str(count)
			obj["date"] = None
			data.append(obj)
			count += 1
			if (count > 10): break
		return data

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
