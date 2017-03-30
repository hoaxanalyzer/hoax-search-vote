import time
from urllib.request import urlopen 
import urllib

import gevent
from gevent import monkey
monkey.patch_all()

from newspaper import Article
import searcher
from multiprocessing.pool import ThreadPool

start = time.time()

results = (searcher.search_all("flat earth"))

stop = time.time()
print("Time elapsed: " + str(stop-start))

def request_worker(result):
	print('Starting %s' % result["url"])

	req = urllib.request.Request(result["url"], headers={'User-Agent' : "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.0.1) Gecko/20020919"}) 
	con = urllib.request.urlopen( req )

	return str(con.read())

jobs = [gevent.spawn(request_worker, results[key]) for key in results]
gevent.wait(jobs)

def worker(html):
	article = Article(url='')
	article.set_html(html)

	article.parse()
	return (article.text)

pool = ThreadPool(processes=10)
multiple_results = [pool.apply_async(worker, (job.value,)) for job in jobs]
print([res.get(timeout=10) for res in multiple_results])

stop = time.time()
print("Time elapsed: " + str(stop-start))