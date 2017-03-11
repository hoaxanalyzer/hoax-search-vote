import articleDateExtractor
import logging
import threading
import os
import hashlib
import re
import shutil

from goose import Goose
from google import search, get_page

from article import Article

class Searcher:
	basedir = "news"

	def __init__(self, query):
		self.query = re.sub(r"[^\w\s]|_+", ' ', query.lower())
		self.query_hash = hashlib.sha256(self.query).hexdigest()
		self.articledir = Searcher.basedir + '/' + self.query_hash

	def search_google(self):
		start_search = not os.path.exists(self.articledir)

		if not start_search:
			start_search = len([name for name in os.listdir(self.articledir) if os.path.isfile(name)]) < 5
			if start_search:
				shutil.rmtree(self.articledir, ignore_errors=True)

		if start_search:
		 	os.makedirs(self.articledir)		
			count = 0
			threads = []
			for url in search(self.query, tld='com', lang='en', stop=10):
				filename = str(count)
				extractor = Goose()
				t = threading.Thread(target=self.__article_worker, args=(extractor, filename, url,))
				count += 1
				threads.append(t)
				t.start()
			for t in threads:
				t.join()
			print("Finish Data Gathering")

	def get_news_google(self):
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

	def __article_worker(self, extractor, filename, url):
		date = articleDateExtractor.extractArticlePublishedDate(url)

		article = extractor.extract(raw_html=get_page(url))
		text = article.cleaned_text

		l = ''.join([x for x in text if ord(x) < 128])
		if len(l) > 0: 
			with open(self.articledir + '/' + filename + '.txt', 'w') as file:
				file.write(l)			
			with open(self.articledir + '/' + filename + '.meta', 'w') as file:
				file.write(str(url) + '\n')
				file.write(str(date) + '\n')
