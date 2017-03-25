from future.standard_library import install_aliases
install_aliases()

import logging
import pickle
import re
import urllib.parse
from datetime import datetime
from nltk.corpus import stopwords

class Article:
	factgram = ["not hoax", "accurate", "true", "proof", "scientific", "paper", \
			"study", "sources", "cited", "evidence", "official"]

	hoaxgram = ["hoax", "like a hoax", "fake", "a lie", "rumor", "false", "in fact", "fake news", \
	        "debunked", "victim", "conspiracy", "expect", "uncertain", "skeptical", \
	        "satirical", "death hoax", "fake article", "fake story", "clickbait", "fabricated", \
	        "no truth", "no evidence", "incorrect", "satire", "altered", "if this were true", "if it was true", \
	        "dont actually", "nonsense", "no credible"]

	unkngram = ["not clear", "cant conclude", "questioned", "no answer", "confusing", "dont knows"]

	sitedata = {}

	def __init__(self, query, ahash, url, content, date):
		if not Article.sitedata:
			with open("./models/sites.hash", "r") as file:
				Article.sitedata = pickle.load(file)

		self.query = query
		self.query_clean = re.sub(r"[^\w\s]|_+", ' ', self.query.lower())

		# Delete english stopword 
		# TO-DO indonesian stopword
		allstopwords = stopwords.words('english') + Article.factgram + Article.hoaxgram
		self.query_words = [word for word in self.query_clean.split() if word not in allstopwords]
		#print(self.query_words)

		self.ahash = ahash

		self.url = url
		self.url_base = url
		self.url_score = self._site_type(url)
	    
		self.content = content
		self.content_clean = re.sub(r"[^\w\s]|_+", ' ', self.content.lower())
		
		sentences = self._get_sentences(self.content)
		self.feature_fact = self._ngram_counter(Article.factgram, sentences)
		self.feature_hoax = self._ngram_counter(Article.hoaxgram, sentences)
		self.feature_unkn = self._ngram_counter(Article.unkngram, sentences)

		self.ofeature_fact = self._old_ngram_counter(Article.factgram, (self.content_clean))
		self.ofeature_hoax = self._old_ngram_counter(Article.hoaxgram, (self.content_clean))
		self.ofeature_unkn = self._old_ngram_counter(Article.unkngram, (self.content_clean))

		if date == "None": date = "1950-01-01 00:00:00+00:00"
		if len(str(date)) < 19:
			date = datetime.strptime(date[:10], '%Y-%m-%d')
		else:
			date = datetime.strptime(date[:19], '%Y-%m-%d %H:%M:%S')
		self.date = date	    

		self.similarity = 0
		self.weight = 1

		self.label = "not defined"

	def set_similarity(self, similarity):
		self.similarity = similarity

	def set_weight(self, weight):
		self.weight = weight

	def set_label(self, label):
		self.label = label

	def get_features_array(self):
	 	features = []
	 	## OLD FIRST
	 	for h in Article.hoaxgram:
	 		features.append(self.ofeature_hoax[h])
	 	for f in Article.factgram:
	 		features.append(self.ofeature_fact[f])
	 	for u in Article.unkngram:
	 		features.append(self.ofeature_unkn[u])
	 	## NEW
	 	for h in Article.hoaxgram:
	 		features.append(self.feature_hoax[h])
	 	for f in Article.factgram:
	 		features.append(self.feature_fact[f])
	 	for u in Article.unkngram:
	 		features.append(self.feature_unkn[u])
	 	features.append(self.similarity)
	 	return features

	def _old_ngram_counter(self, ngrams, text):
		counts = {}
		for ngram in ngrams:
		    words = ngram.rsplit()
		    pattern = re.compile(r'%s' % "\s+".join(words),
		        re.IGNORECASE)
		    counts[ngram] = len(pattern.findall(text))
		return counts

	def _ngram_counter(self, ngrams, sentences):
		counts = dict.fromkeys(ngrams, 0)
		sidx = 0
		for sentence in sentences:
			has_qword = False
			for qword in self.query_words:
				if not has_qword and len(qword) > 1:
					word = qword.rsplit()
					epattern = re.compile(r'%s' % "\s+".join(word), re.IGNORECASE)
					has_qword = self.__is_has_word(epattern, sentences, sidx, 3)
			if has_qword:
				for ngram in ngrams:
				    words = ngram.rsplit()
				    pattern = re.compile(r'%s' % "\s+".join(words),
				        re.IGNORECASE)
				    counts[ngram] += len(pattern.findall(sentence))
			sidx += 1
		return counts

	def __is_has_word(self, pattern, sentences, curidx, r):
		has_word = False
		if (len(pattern.findall(sentences[curidx])) >= 1):
			has_word = True
		for i in range(1, r):
			if ((curidx - i) >= 0):
				if (len(pattern.findall(sentences[curidx - i])) >= 1):
					has_word = True
			if ((curidx + i) < len(sentences)):
				if (len(pattern.findall(sentences[curidx + i])) >= 1):
					has_word = True
		return has_word

	def _get_sentences(self, text):
		ret = []
		sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s', text)
		for sentence in sentences:			
			sentence = re.sub(r"[^\w\s]|_+", ' ', sentence.lower())
			ret.append(sentence)
		return ret

	def _site_type(self, url):
		parsed_uri = urllib.parse.urlparse(url)
		domain = '{uri.netloc}'.format(uri=parsed_uri)
		ddomain = domain.split('.')

		clean_domain = ""
		if len(ddomain) > 2: 
			for d in ddomain[1:]: clean_domain += d + '.'
		else: 
			for d in ddomain[0:]: clean_domain += d + '.'

		domain = ""
		domain = clean_domain[:-1]
		self.url_base = domain

		if domain in Article.sitedata:
			if Article.sitedata[domain] == 'credible': return 2
			else: return 0
		else: return 1

