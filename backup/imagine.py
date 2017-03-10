import logging
import os

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
		# We are using TF-IDF here
		tfidf = models.TfidfModel(corpus)
		corpus_tfidf = tfidf[corpus]

		if len(dictionary) > 0:
			lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2) # initialize an LSI transformation
			corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
			return lsi
		return None

	def get_similarity(self, doc, dictionary, corpus, lsi):
		vec_bow = dictionary.doc2bow(doc.lower().split())
		vec_lsi = lsi[vec_bow] # convert the query to LSI space

		index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it

		# vec_lsi is the new data queried
		sims = index[vec_lsi] # perform a similarity query against the corpus
		#print(list(enumerate(sims))) # print (document_number, document_similarity) 2-tuples

		sims = sorted(enumerate(sims), key=lambda item: -item[1])
		return sims # return sorted (document number, similarity score) 2-tuples

	def similarity_of(self, sentence, paragraph):
		dictionary, corpus = self.create_dic(self.paragraph)
		lsi = self.create_model(dictionary, corpus)
		self.rank = []
		if (lsi != None):
			self.rank = self.get_similarity(self.sentence, dictionary, corpus, lsi)

LANGUAGE = "english"
NEWS_DIR = "news"

if __name__ == "__main__":
	TEST_SENTENCE = sys.argv[1]
	TEST_QUERY = TEST_SENTENCE
	DIR_NAME = hashlib.sha256(TEST_QUERY).hexdigest()

	URLS = []
	DATASET = []

	ANTONYM_QUERY = []
	# for w in TEST_QUERY.split():
	# 	synonyms = []
	# 	antonyms = []	
	# 	#antonyms.append(w)
	# 	for syn in wordnet.synsets(w):
	# 	    for l in syn.lemmas():
	# 	        synonyms.append(l.name())
	# 	        if l.antonyms():
	# 	            antonyms.append(l.antonyms()[0].name())
	# 	if len(antonyms) > 0: ANTONYM_QUERY.append(antonyms) 
	print("Search for " + TEST_QUERY)

	DIRECTORY = NEWS_DIR + '/' + DIR_NAME

	if not os.path.exists(DIRECTORY):
	 	os.makedirs(DIRECTORY)		
		count = 0
		for url in search(TEST_QUERY, tld='com', lang='en', stop=10):
			print("Got data")
			FILENAME = str(count) + '.txt'
			URLS.append(str(url))

			extractor = Goose()
			article = extractor.extract(raw_html=get_page(url))
			text = article.cleaned_text

			l = ''.join([x for x in text if ord(x) < 128])
			if len(l) > 0: 
				DATASET.append((FILENAME, text))

				with open(DIRECTORY + '/' + FILENAME, 'w') as file:
					file.write(l)
				count += 1

			with open(DIRECTORY + '/index', 'w') as file:
				count = 0
				for url in URLS:	
					file.write(str(count) + ' | ' + url + '\n')
					count += 1
	else:
		for d in os.listdir(DIRECTORY):
			with open(DIRECTORY + '/' + d, "r") as file:
				l = ''.join([x for x in file.read() if ord(x) < 128])
				if len(l) > 0:
					DATASET.append((d, l))

	i = 0
	for name, article in DATASET:
		tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		sentences = tokenizer.tokenize(article)
		print(name)

		#similar = Similar(TEST_QUERY, sentences)
		#pprint(sentences)
		#print(similar.rank)

		# print('Antonym Query: ' + str(ANTONYM_QUERY))

		# for t in itertools.product(*ANTONYM_QUERY):
		# 	q = ' '.join(t)
		# 	similar = Similar(q, sentences)
		# 	count = 1
		# 	score = 0
		# 	for rank in similar.rank:
		# 		count += 1
		# 		score += rank[1]
		# 	print("Q Similar (" + q + "): " + str(score/count))

		pprint(sentences)
		negativity = ["false",
					  "a lie",
					  "a rumor", 
					  "hoax", 
					  "debunked hoax",
					  "conspiracy theory", 
					  "confirmed false"
					  "confirmed complete hoax", 
					  "contrary to rumors", 
					  "fake report",
					  "victim of hoax"]
		for neg in negativity:
		 	negsim = Similar(neg, sentences)
			print("Overall Negative (" + neg + "): ")
			print(negsim.rank)

		# for neg in negativity:
		# 	negsim = Similar(neg, sentences)
		# 	count = 1
		# 	score = 0
		# 	for rank in negsim.rank:
		# 		count += 1
		# 		score += rank[1]
		# 	print("Overall Negative (" + neg + "): " + str(score/count))

		positivity = ["still developing", "details uncertain", "blurry images", "no evidence", "skeptical", "believe"]
		for pos in positivity:
			possim = Similar(pos, sentences)
			count = 1
			score = 0
			for rank in possim.rank:
				count += 1
				score += rank[1]
			print("Overall Positive (" + pos + "): " + str(score/count))


		print("\n=======\n")
		i += 1
