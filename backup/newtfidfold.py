import logging
import os

from sklearn.externals import joblib

from gensim import corpora, models, similarities
from pprint import pprint

from nltk.corpus import stopwords
from nltk.corpus import wordnet
import nltk.data

from goose import Goose

import os
import sys
import hashlib
import itertools
import threading
import re
import pickle

import articleDateExtractor

from urlparse import urlparse
from datetime import datetime

from google import search, get_page

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

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

LANGUAGE = "english"
NEWS_DIR = "news"

factgram = ["not hoax", "accurate", "true", "proof", "scientific", "paper", \
		"study", "sources", "cited", "evidence", "official"]
hoaxgram = ["hoax", "like a hoax", "fake", "a lie", "rumor", "false", "in fact", "fake news", \
        "debunked", "victim", "conspiracy", "expect", "uncertain", "skeptical", \
        "satirical", "death hoax", "fake article", "fake story", "clickbait", "fabricated", \
        "no truth", "no evidence", "incorrect", "satire", "altered", "if this were true", "if it was true", \
        "dont actually", "nonsense", "no credible"]

DATASET = []
URLS = []
f = open('./models/sites.hash', 'r')
SITES = pickle.load(f)
f.close()  

def get_site_type(url, sitedata):
	parsed_uri = urlparse(url)
	domain = '{uri.netloc}'.format(uri=parsed_uri)
	ddomain = domain.split('.')

	clean_domain = ""
	if len(ddomain) > 2:
		for d in ddomain[1:]:
			clean_domain += d + '.'
	else:
		for d in ddomain[0:]:
			clean_domain += d + '.'

	domain = ""
	domain = clean_domain[:-1]

	if domain in sitedata:
		if sitedata[domain] == 'credible': return 2
		else: return 0
	else: return 1

def ngram_counter(ngrams, text):
	counts = {}
	for ngram in ngrams:
	    words = ngram.rsplit()
	    pattern = re.compile(r'%s' % "\s+".join(words),
	        re.IGNORECASE)
	    counts[ngram] = len(pattern.findall(text))
	return counts

def article_worker(extractor, directory, filename, url):
	date = articleDateExtractor.extractArticlePublishedDate(url)

	article = extractor.extract(raw_html=get_page(url))
	text = article.cleaned_text

	l = ''.join([x for x in text if ord(x) < 128])
	if len(l) > 0: 
		with open(directory + '/' + filename + '.txt', 'w') as file:
			file.write(l)			
		with open(directory + '/' + filename + '.meta', 'w') as file:
			file.write(str(url) + '\n')
			file.write(str(date) + '\n')
			file.write(str(get_site_type(url, SITES)))

def get_news_file(directory):
	datasets = []
	for d in os.listdir(directory):
		if d.endswith(".txt"):
			l = ""
			u = ""
			date = ""
			valid = ""
			name = d.split(".")
			with open(directory + '/' + d, "r") as file:
				l = ''.join([x for x in file.read() if ord(x) < 128])
			if len(l) > 0:				
				with open(directory + '/' + name[0] + ".meta", "r") as f:
					i = 0
					for a in f.readlines():
						if i == 0:
							u = a.replace('\n','')
						elif i == 1:
							a = a.replace('\n','')
							if a == "None":
								a = "1950-01-01 00:00:00+00:00"
							date = datetime.strptime(a[:19], '%Y-%m-%d %H:%M:%S')
						elif i == 2:
							valid = a.replace('\n','')
						i += 1			
				datasets.append((d, l, u, date, valid))
	return datasets

def calculate_weight(meta):
	modifier = {}
	meta = sorted(meta, key=lambda x: x[2], reverse=True)
	i = 0
	for a in meta:
		modifier[a[0]] = (((len(meta) - i) / float(len(meta))) * 0.5) + (int(a[3]) * 0.25)
		i += 1
	return modifier

def best_reference(meta):
	meta = sorted(meta, key=lambda x: (x[2], x[3]), reverse=True)
	return meta[0]

def doIt(query):
	TARGET = ['unrelated', 'fact', 'hoax', 'unknown']
	DATASET = []
	URLS = []
	THREADS_EXTRACTOR = []
	TEST_SENTENCE = query
	TEST_QUERY = TEST_SENTENCE + ' hoax'
	DIR_NAME = hashlib.sha256(TEST_QUERY).hexdigest()

	print("Search for " + TEST_QUERY)
	print(DIR_NAME)

	DIRECTORY = NEWS_DIR + '/' + DIR_NAME

	if not os.path.exists(DIRECTORY):
	 	os.makedirs(DIRECTORY)		
		count = 0
		threads = []
		for url in search(TEST_QUERY, tld='com', lang='en', stop=10):
			FILENAME = str(count)
			URLS.append(str(url))

			extractor = Goose()
			t = threading.Thread(target=article_worker, args=(extractor, DIRECTORY, FILENAME, url,))
			count += 1
			threads.append(t)
			t.start()
		
		for t in threads:
			t.join()

		print("Finish Data Gathering")

		with open(DIRECTORY + '/index', 'w') as file:
			count = 0
			for url in URLS:	
				file.write(str(count) + ' | ' + url + '\n')
				count += 1

	DATASET = get_news_file(DIRECTORY)

	HOAXGRAM = {}
	FACTGRAM = {}

	sentences = []
	meta = []
	for name, article, url, date, valid in DATASET:
		clean_article = re.sub(r"[^\w\s]|_+", ' ', article.lower())
		sentences.append(clean_article)		
		fn = ngram_counter(factgram, clean_article)
		FACTGRAM[name] = fn
		hn = ngram_counter(hoaxgram, clean_article)
		HOAXGRAM[name] = hn
		meta.append((name, url, date, valid))

	MODIFIER = calculate_weight(meta)

	similar = Similar(TEST_QUERY, sentences)

	dt = joblib.load('./models/model01-rev.pkl') 
	i = 0
	conclusion = [0] * 4

	for num, result in similar.rank:
	 	nsims = result
	 	filename = DATASET[num][0]

	 	check = []
	 	for h in hoaxgram:
	 		check.append(HOAXGRAM[filename][h])
	 	for f in factgram:
	 		check.append(FACTGRAM[filename][f])
	 	check.append(nsims)

		idx = dt.predict([check])[0]
		print(filename + "::")
		print(check)
		
		conclusion[idx] += 1
		if idx != 0:
			conclusion[idx] += MODIFIER[filename]

		i += 1

	THRESHOLD_UNKNOWN = 0.35
	if (conclusion[2] > conclusion[1]):
		if (conclusion[2] > (conclusion[1] + conclusion[3])):
		 	print(TEST_QUERY + " is HOAX")
		else:
			if ((conclusion[1] + conclusion[3]) - conclusion[2] < THRESHOLD_UNKNOWN):
		 		print(TEST_QUERY + " is HOAX")
		 	else:
		 		print(TEST_QUERY + " is UNKNOWN")
	elif (conclusion[2] <= conclusion[1]):
		if ((conclusion[3] + conclusion[2]) < conclusion[1]):
		 	print(TEST_QUERY + " is FACT")
		else:
			if ((conclusion[3] + conclusion[2]) - conclusion[1] < THRESHOLD_UNKNOWN):
		 		print(TEST_QUERY + " is FACT")
		 	else:
		 		print(TEST_QUERY + " is UNKNOWN")
	else:
		print(TEST_QUERY + " is UNKNOWN")

	print(conclusion)


	
	
	print("*--- --- ---*")

query = ["Richard Harrison Death"]

for q in query:
	doIt(q)
