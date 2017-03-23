import articleDateExtractor
import logging
import threading
import os
import hashlib
import re
import shutil
import time
import multiprocessing
import uuid

import requests
import urlparse
import urllib

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

	def get_news(self, loghash):
		articles = self.db.get_references_by_loghash(loghash)
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
		parsed_url = urlparse.urlparse(bing_url)
		redirect_url = urlparse.parse_qs(parsed_url.query)['r']
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
		query_exclusion = " -site:twitter.com -site:reddit.com -site:facebook.com -site:youtube.com -site:pinterest.com -site:amazon.com -site:wordpress.com -site:blogspot.com"
		for url in google.search(self.query + query_exclusion, tld='com', lang='en', stop=10):
			obj = {}
			obj["url"] = url
			obj["filename"] = 'g' + str(count)
			obj["date"] = None
			data.append(obj)
			count += 1
			if (count > 10): break
		return data