import logging

from sklearn.externals import joblib

from pprint import pprint

import sys
import itertools
import re

from similar import Similar
from article import Article
from searcher import Searcher

def do_voting(conclusion):
	THRESHOLD_UNKNOWN = 0.35
	if (conclusion[2] > conclusion[1]):
		if (conclusion[2] > (conclusion[1] + conclusion[3])): return 2
		else:
			if ((conclusion[1] + conclusion[3]) - conclusion[2] < THRESHOLD_UNKNOWN): return 2
		 	else: return 3
	elif (conclusion[2] <= conclusion[1]):
		if ((conclusion[3] + conclusion[2]) < conclusion[1]): return 1
		else:
			if ((conclusion[3] + conclusion[2]) - conclusion[1] < THRESHOLD_UNKNOWN): return 1
		 	else: return 3
	else: return 3


def calculate_weight(dataset):
	meta = sorted(dataset, key=lambda x: x.date, reverse=True)
	i = 0
	for a in meta:
		a.set_weight((((len(meta) - i) / float(len(meta))) * 0.5) * int(a.url_score))
		i += 1
	return dataset

def best_reference(dataset):
	meta = sorted(dataset, key=lambda x: (x.date, x.url_score), reverse=True)
	return meta[0]

def doIt(query):
	TARGET = ['unrelated', 'fact', 'hoax', 'unknown']
	DATASET = []
	TEST_SENTENCE = query
	TEST_QUERY = TEST_SENTENCE + ' hoax'

	s = Searcher(TEST_QUERY)

	print("Search for " + TEST_QUERY)
	print(s.query_hash)

	s.search_google()

	DATASET = s.get_news_google()

	sentences = []
	for article in DATASET:
		sentences.append(article.content_clean)

	DATASET = calculate_weight(DATASET)

	refer = best_reference(DATASET)

	similar = Similar(TEST_QUERY, sentences)

	dt = joblib.load('./models/model01-rev.pkl') 

	i = 0
	conclusion = [0] * 4
	for num, result in similar.rank:
	 	article = DATASET[num]
	 	article.set_similarity(result)
		idx = dt.predict([article.get_features_array()])[0]
		article.set_label(TARGET[idx])
		conclusion[idx] += 1
		if idx != 0: conclusion[idx] += article.weight
		i += 1

	do_voting(conclusion)
	print(conclusion)

	print(refer.url)

	print("*--- --- ---*")

query = ["Richard Harrison Death"]

for q in query:
	doIt(q)
