from urllib.request import urlopen 
import urllib

import gevent
from gevent import monkey
monkey.patch_all()

from newspaper import Article
import collector.searcher

import multiprocessing
from multiprocessing.pool import ThreadPool

def do(query):
	results = (searcher.search_all(query))

	def request_worker(result):
		req = urllib.request.Request(result["url"], headers={'User-Agent' : "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.0.1) Gecko/20020919"}) 
		con = urllib.request.urlopen( req )
		return (result["title"], str(con.read()))

	jobs = [gevent.spawn(request_worker, results[key]) for key in results]
	gevent.wait(jobs)

	def worker(html, title):
		article = Article(url='')
		article.set_html(html)

		article.parse()
		return (title, article.text, article.publish_date)

	max_process = 20
	process = multiprocessing.cpu_count()
	if process > max_process:
		process = max_process

	pool = ThreadPool(processes=process)
	multiple_results = [pool.apply_async(worker, (job.value[1], job.value[0],)) for job in jobs]

	return ([res.get(timeout=10) for res in multiple_results])