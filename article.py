import logging
import pickle
import re
from datetime import datetime
from urlparse import urlparse

class Article:
	factgram = ["not hoax", "accurate", "true", "proof", "scientific", "paper", \
			"study", "sources", "cited", "evidence", "official"]

	hoaxgram = ["hoax", "like a hoax", "fake", "a lie", "rumor", "false", "in fact", "fake news", \
	        "debunked", "victim", "conspiracy", "expect", "uncertain", "skeptical", \
	        "satirical", "death hoax", "fake article", "fake story", "clickbait", "fabricated", \
	        "no truth", "no evidence", "incorrect", "satire", "altered", "if this were true", "if it was true", \
	        "dont actually", "nonsense", "no credible"]

	sitedata = {}

	def __init__(self, filename, url, content, date):
		self.filename = filename

		if not Article.sitedata:
			with open("./models/sites.hash", "r") as file:
				Article.sitedata = pickle.load(file)
		self.url = url
		self.url_score = self._site_type(url)
	    
		self.content = content
		self.content_clean = re.sub(r"[^\w\s]|_+", ' ', self.content.lower())
		self.feature_fact = self._ngram_counter(Article.factgram, self.content_clean)
		self.feature_hoax = self._ngram_counter(Article.hoaxgram, self.content_clean)

		if date == "None": date = "1950-01-01 00:00:00+00:00"
		date = datetime.strptime(date[:19], '%Y-%m-%d %H:%M:%S')
		self.date = date	    

		self.similarity = 0
		self.weight = 1

		self.label = "unknown"

	def set_similarity(self, similarity):
		self.similarity = similarity

	def set_weight(self, weight):
		self.weight = weight

	def set_label(self, label):
		self.label = label

	def get_features_array(self):
	 	features = []
	 	for h in Article.hoaxgram:
	 		features.append(self.feature_hoax[h])
	 	for f in Article.factgram:
	 		features.append(self.feature_fact[f])
	 	features.append(self.similarity)
	 	return features

	def _ngram_counter(self, ngrams, text):
		counts = {}
		for ngram in ngrams:
		    words = ngram.rsplit()
		    pattern = re.compile(r'%s' % "\s+".join(words),
		        re.IGNORECASE)
		    counts[ngram] = len(pattern.findall(text))
		return counts

	def _site_type(self, url):
		parsed_uri = urlparse(url)
		domain = '{uri.netloc}'.format(uri=parsed_uri)
		ddomain = domain.split('.')

		clean_domain = ""
		if len(ddomain) > 2: 
			for d in ddomain[1:]: clean_domain += d + '.'
		else: 
			for d in ddomain[0:]: clean_domain += d + '.'

		domain = ""
		domain = clean_domain[:-1]

		if domain in Article.sitedata:
			if Article.sitedata[domain] == 'credible': return 2
			else: return 0
		else: return 1

