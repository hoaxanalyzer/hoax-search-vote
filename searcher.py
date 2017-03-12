import articleDateExtractor
import logging
import threading
import os
import hashlib
import re
import shutil
import time

import requests
import urlparse
import urllib

from multiprocessing import cpu_count
from goose import Goose
from google import search, get_page

from pke import ProcessKillingExecutor
from article import Article

class Searcher:
	basedir = "news"

	def __init__(self, query):
		self.query = re.sub(r"[^\w\s]|_+", ' ', query.lower())
		self.query_hash = hashlib.sha256(self.query).hexdigest()
		self.articledir = Searcher.basedir + '/' + self.query_hash

	def _check_dir(self):
		start_search = not os.path.exists(self.articledir)

		if not start_search:
			start_search = len(os.listdir(self.articledir)) < 5
			if start_search:
				shutil.rmtree(self.articledir, ignore_errors=True)

		return start_search

	def check_cache(self):
		start_search = self._check_dir()

		if start_search:
		 	os.makedirs(self.articledir)
		 	return False
		return True

	def search_google(self, start=0, check=True):
		count = start
		threads = []
		data = []
		for url in search(self.query, tld='com', lang='en', stop=10):
			obj = {}
			obj["url"] = url
			obj["filename"] = str(count)
			obj["extractor"] = Goose()
			obj["date"] = None
			data.append(obj)
			count += 1
		executor = ProcessKillingExecutor(max_workers=3)
		generator = executor.map(self.__article_worker, data, timeout=35)
		for elem in generator:
			logging.info(elem)
		    print(elem)
		    #None
		print("Finish Data Gathering - Google")
		logging.info("Finish Data Gathering - Google")
		return count

	def search_bing(self, start=0, check=True):
		count = start
		threads = []
		data = []
		for url, date in self.__call_bing_api(self.query):
			obj = {}
			obj["url"] = url
			obj["filename"] = str(count)
			obj["extractor"] = Goose()
			obj["date"] = date
			data.append(obj)
			count += 1
		executor = ProcessKillingExecutor(max_workers=3)
		generator = executor.map(self.__article_worker, data, timeout=35)
		for elem in generator:
			logging.info(elem)
		    print(elem)
		    #None
		print("Finish Data Gathering - Bing")
		logging.info("Finish Data Gathering - Bing")
		return count

	def get_news(self):
		datasets = []
		for d in os.listdir(self.articledir):
			if d.endswith(".txt"):
				l, u, date = "", "", ""
				name = d.split(".")
				with open(self.articledir + '/' + d, "r") as file:
					l = ''.join([x for x in file.read() if ord(x) < 128])
				if len(l) > 0:				
					with open(self.articledir + '/' + name[0] + ".meta", "r") as f:
						i = 0
						for a in f.readlines():
							if i == 0: u = a.replace('\n','')
							elif i == 1: date = a.replace('\n','')
							i += 1			
					article = Article(d, u, l, date)
					datasets.append(article)
		return datasets

	def __article_worker(self, data, *args, **kwargs):
		extractor = data["extractor"]
		filename = data["filename"]
		url = data["url"]
		date = data["date"]

		if date == None:
			date = articleDateExtractor.extractArticlePublishedDate(url)
		if len(str(date)) < 10:
			date = None

		article = extractor.extract(raw_html=get_page(url))
		text = article.cleaned_text

		l = ''.join([x for x in text if ord(x) < 128])
		if len(l) > 0: 
			with open(self.articledir + '/' + filename + '.txt', 'w') as file:
				file.write(l)			
			with open(self.articledir + '/' + filename + '.meta', 'w') as file:
				file.write(str(url) + '\n')
				file.write(str(date) + '\n')
		return str(filename) + " OK"

	def __sanitize_bing_url(self, bing_url):
		parsed_url = urlparse.urlparse(bing_url)
		redirect_url = urlparse.parse_qs(parsed_url.query)['r']
		return redirect_url[0]

	def __sanitize_bing_date(self, bing_date):
		return bing_date.replace('T', ' ')

	def __call_bing_api(self, query):
		url_query = urllib.quote_plus(query)
		headers = {'Ocp-Apim-Subscription-Key': 'b1168966984e49eda59e502ee2b8fe94'}
		r = requests.get('https://api.cognitive.microsoft.com/bing/v5.0/news/search?q='+ url_query +'&count=10&mkt=en-us', headers=headers)
		data = []
		results = r.json()
		news = results["value"]
		for article in news:
			data.append((self.__sanitize_bing_url(article["url"]), self.__sanitize_bing_date(article["datePublished"])))
		return data
