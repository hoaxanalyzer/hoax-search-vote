import time
import json
import hashlib
from lxml import html
import multiprocessing
from multiprocessing.pool import ThreadPool

from urllib.request import urlopen 
import urllib

import gevent
from gevent import monkey
monkey.patch_all()

from newspaper import Article
from newspaper.configuration import Configuration

import searcher.duckduckgo
import searcher.bing

def search(search_engine, query):
	if search_engine == "bing":
		return bing.search(query, max_results=10)
	if search_engine == "duckduckgo":
		return duckduckgo.search(query, max_results=10)
	return None

def search_all(query):
	results = {}
	engine = ["bing", "duckduckgo"]

	def worker(search_engine, query):
		return (search(search_engine, query))

	pool = ThreadPool(processes=2)
	multiple_results = [pool.apply_async(worker, (s, query)) for s in engine]
	temp_result = ([res.get(timeout=10) for res in multiple_results])
	for s in temp_result:
		for se in s:
			se["title"] = ''.join([x for x in se["title"] if ord(x) < 128])
			url = se["url"]
			if not url[:4] == "http":
				se["url"] = "http://" + url
			results[hashlib.sha1(se["url"].encode()).hexdigest()] = se

	def request_worker(result):
		req = urllib.request.Request(result["url"], headers={'User-Agent' : "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.0.1) Gecko/20020919"}) 
		con = urllib.request.urlopen(req)
		html = con.read().decode('utf-8')
		return (result["title"], html, result["url"])

	jobs = [gevent.spawn(request_worker, results[key]) for key in results]
	gevent.wait(jobs)

	def worker(html, title, url):
		config = Configuration()
		config.fetch_images = False

		article = Article(url='', config=config)
		article.set_html(html)
		article.parse()

		if len(article.text) < 300:
			article = Article(url='', config=config, language="id")
			article.set_html(html)
			article.parse()

		content = article.text.replace('\n', ' ')
		content = content.replace('\'', ' ')
		content = content.replace('\"', '"')
		content = ''.join([x for x in content if ord(x) < 128])
		return (url, title, content, article.publish_date)

	max_process = 20
	process = multiprocessing.cpu_count()
	if process > max_process:
		process = max_process

	pool = ThreadPool(processes=process)
	multiple_results = [pool.apply_async(worker, (job.value[1], job.value[0], job.value[2],)) for job in jobs]

	return ([res.get(timeout=30) for res in multiple_results])