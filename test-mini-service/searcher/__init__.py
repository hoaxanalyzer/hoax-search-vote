import requests
import time
import json
import hashlib
import searcher
from lxml import html
from multiprocessing.pool import ThreadPool

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
		return (searcher.search(search_engine, query))

	pool = ThreadPool(processes=2)
	multiple_results = [pool.apply_async(worker, (s, query)) for s in engine]
	for s in ([res.get(timeout=1) for res in multiple_results]):
		for se in s:
			url = se["url"]
			if not url[:4] == "http":
				se["url"] = "http://" + url
			results[hashlib.sha1(se["url"].encode()).hexdigest()] = se
	return results