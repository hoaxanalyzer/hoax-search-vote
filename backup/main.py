from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import linear_kernel
from nltk.corpus import stopwords

import numpy as np
import numpy.linalg as LA

from goose import Goose

import os
import sys
import hashlib

from google import search, get_page

LANGUAGE = "english"
NEWS_DIR = "news"
NEWS_CONTENT = []

if __name__ == "__main__":
	TEST_SENTENCE = sys.argv[1]
	TEST_QUERY = TEST_SENTENCE
	DIR_NAME = hashlib.sha256(TEST_QUERY).hexdigest()

	URLS = []
	DATASET = []
	DATASET.append(TEST_QUERY)

	print("Search for " + TEST_QUERY)

	for url in search(TEST_QUERY, tld='com', lang='en', stop=10):
		print("dafuq")
		URLS.append(str(url))
		#try:
		extractor = Goose()
		article = extractor.extract(raw_html=get_page(url))
		text = article.cleaned_text

		NEWS_CONTENT.append(text.encode('utf-8'))
		DATASET.append(text)
		#except:
		#	print('Error', sys.exc_info()[0])

	stopWords = stopwords.words(LANGUAGE)

	trainVectorizer = TfidfVectorizer().fit_transform(DATASET)
	cosine_similarities = linear_kernel(trainVectorizer[0:1], trainVectorizer).flatten()

	if not os.path.exists(NEWS_DIR + '/' + DIR_NAME):
	 	os.makedirs(NEWS_DIR + '/' + DIR_NAME)

	count = 0
	for content in NEWS_CONTENT:
		with open(NEWS_DIR + '/' + DIR_NAME + '/' + str(count) + '.txt', 'w') as file:
			file.write(content)
		count += 1

	print(URLS)

	print(cosine_similarities)