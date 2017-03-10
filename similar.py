import logging

from gensim import corpora, models, similarities
from nltk.corpus import stopwords

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
