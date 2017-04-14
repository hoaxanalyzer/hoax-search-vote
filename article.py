from future.standard_library import install_aliases
install_aliases()

import logging
import pickle
import re
import regex
import urllib.parse
from datetime import datetime
from nltk.corpus import stopwords

class WordGram:
	def __init__(self, words):
		self.words = words
		self.value = words[0]

	def pattern(self):
		regex = r""
		first = True
		for ngram in self.words:
			if first:
				first = False
			else:
				regex += r'%s' % "|"
			words = ngram.rsplit()
			regex += r'%s' % "\s+".join(words)
		return regex

class Article:
	factgram = [WordGram(["not hoax", "bukan hoax", "(?<!not\s)accurate", "(?<!tidak\s)akurat",\
		"(?<!tidak\sditemukan\s)(?<!tidak\smenemukan\s)(?<!tidak\sber)hubungan", "fakta",\
		"(?<!tidak\sada\s)referensi", "(?<!tidak\sada\s)kesaksian", "(?<!tidak\sada\s)saksi",\
		"(?<!not\s)official(?!s)", "(?<!lembaga\s)(?<!tidak\s)resmi"])]

	hoaxgram = [WordGram(["(?<!not\s)hoax", "berita bohong", "kabar burung", "hoak", "hoaks", "editan",\
		"mitos", "like a hoax", "seperti hoax", "mirip hoax", "(?<!not\s)fake", "penipuan", "tipuan",\
		"palsu", "memperdaya", "a lie", "bohong", "kebohongan", "pemalsuan", "penipuan", "rumor", "rumor",\
		"\bisu\b", "false", "tidak benar", "ditepis", "menyatakan sebaliknya", "in fact", "faktanya", "sebenarnya",\
		"sesungguhnya", "sebetulnya", "fake news", "berita palsu", "berita yang tidak benar", "debunked",\
		"tidak terbukti", "terbukti salah", "dipatahkan", "conspiracy", "konspirasi", "kontroversi", "menyangka",\
		"mengharapkan", "uncertain", "tidak pasti", "samar", "skeptical", "skeptis", "curiga", "ragu", "satirical",\
		"menyidir", "satir", "death hoax", "hoax kematian", "fake article", "artikel palsu", "fake story", "cerita palsu",\
		"clickbait", "fabricated", "no truth", "tidak benar", "no evidence", "tidak terbukti", "tidak ada bukti",\
		"terbukti tidak", "belum ada bukti", "incorrect", "tidak tepat", "membantah", "satire", "menyindir", "satir",\
		"altered", "diubah", "if this were true", "jika benar", "jika hal ini benar", "if it was true", "jika benar",\
		"jika ini benar", "dont actually", "tidak benar-benar", "nonsense", "omong kosong", "tidak masuk akal", "no credible",\
		"tidak kredibel", "tidak ada sumber", "terbukti tidak", "tidak terbukti", "tidak ada bukti", "belum ada bukti",\
		"tidak menemukan bukti", "tidak ditemukan bukti", "bukan berdasarkan bukti", "tidak membuktikan", "tidak ada penelitian",\
		"tidak berhubungan", "tidak menemukan hubungan", "tidak ditemukan hubungan", "untrue", "no other scientists",\
		"dishonestly", "irresponsibly", "still believe", "retracted", "falsified", "no link", "validity", "fan fiction",\
		"no direct correlation", "no correlation", "disreputable", "to tarnish", "no such thing", "fan-fiction", "absurdity of the claim",\
		"absurd claim", "lacks truth", "urban legends", "urban legend", "no law against", "answer is no",\
		"not been able to replicate", "implausible", "sempat dikabarkan", "error", "april fools", "april mop", "denies", "bogus"])]

	unkngram = [WordGram(["not clear", "tidak jelas", "cant conclude", "tidak ada kesimpulan", "tidak bisa disimpulkan",\
		"questioned", "mempertanyakan", "dipertanyakan", "menyangsikan", "meragukan", "no answer", "tidak ada jawaban",\
		"tidak menjawab", "tidak terjawab", "confusing", "membingungkan", "dont know", "tidak tau", "tidak mengerti", "orang dekat", "ayah dari", "ibu dari", "istri dari", "adik dari", "saudara dari"])]
	
	asmpgram = [WordGram(["if", "might", "consider", "when will", "what if"])]

	sitedata = {}

	def __init__(self, query, ahash, url, content, date):
		if not Article.sitedata:
			with open("./models/sites.hash", "rb") as file:
				Article.sitedata = pickle.load(file)

		self.query = query
		self.query_clean = re.sub(r"[^\w\s]|_+", ' ', self.query.lower())

		# Delete english stopword 
		# TO-DO indonesian stopword
		allstopwords = stopwords.words('english')
		self.query_words = [word for word in self.query_clean.split() if word not in allstopwords]
		#print(self.query_words)

		self.ahash = ahash

		self.url = url
		self.url_base = url
		self.url_score = self._site_type(url)
		
		self.content = content
		self.content = re.sub(r"\t", '', self.content)
		self.content_clean = re.sub(r"[^\w\s]|_+", ' ', self.content.lower())
		
		self.sentences = self._get_sentences(self.content)
		self.feature_fact = self._ngram_counter(Article.factgram, self.sentences, 1)
		self.feature_hoax = self._ngram_counter(Article.hoaxgram, self.sentences, 2)
		self.feature_unkn = self._ngram_counter(Article.unkngram, self.sentences, 1)
		self.feature_asmp = self._ngram_counter(Article.asmpgram, self.sentences, 0)

		self.ofeature_fact = self._old_ngram_counter(Article.factgram, (self.content_clean))
		self.ofeature_hoax = self._old_ngram_counter(Article.hoaxgram, (self.content_clean))
		self.ofeature_unkn = self._old_ngram_counter(Article.unkngram, (self.content_clean))
		self.ofeature_asmp = self._old_ngram_counter(Article.asmpgram, (self.content_clean))

		self.feature_query_count = 0
		self.feature_query_percentage = 0
		self.feature_query_onesen = 0

		self.reason = "None"

		if date == "None": date = "1950-01-01 00:00:00+00:00"
		if date == '': date = "1950-01-01 00:00:00+00:00"
		try:
			if len(str(date)) < 19:
				date = datetime.strptime(date[:10], '%Y-%m-%d')
			else:
				date = datetime.strptime(date[:19], '%Y-%m-%d %H:%M:%S')
		except:
			date = "1950-01-01 00:00:00+00:00"

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
			features.append(self.ofeature_hoax[h.value] * 0.25)
		for f in Article.factgram:
			features.append(self.ofeature_fact[f.value])
		for u in Article.unkngram:
			features.append(self.ofeature_unkn[u.value])
		for a in Article.asmpgram:
			features.append(self.ofeature_asmp[a.value])
		## NEW
		for h in Article.hoaxgram:
			features.append(self.feature_hoax[h.value])
		for f in Article.factgram:
			features.append(self.feature_fact[f.value])
		for u in Article.unkngram:
			features.append(self.feature_unkn[u.value])
		for a in Article.asmpgram:
			features.append(self.feature_asmp[a.value])
		features.append(self.similarity)
		features.append(self.feature_query_count)
		features.append(self.feature_query_percentage)
		features.append(self.feature_query_onesen)
		return features

	def get_category_count(self):
		category = []
		hoax = 0
		for h in Article.hoaxgram:
			hoax += (self.ofeature_hoax[h.value]) * 0.25
		for h in Article.hoaxgram:
			hoax += (self.feature_hoax[h.value])
		category.append(hoax)

		fact = 0
		for f in Article.factgram:
			fact += (self.ofeature_fact[f.value])
		for f in Article.factgram:
			fact += (self.feature_fact[f.value])
		category.append(fact)

		unkn = 0
		for u in Article.unkngram:
			unkn += (self.ofeature_unkn[u.value])
		for u in Article.unkngram:
			unkn += (self.feature_unkn[u.value])
		category.append(unkn)

		asmp = 0
		for a in Article.asmpgram:
			asmp += (self.feature_asmp[a.value])
		category.append(asmp)

		return category

	def get_humanize_feature(self):
		features = {}
		## OLD FIRST
		for h in Article.hoaxgram:
			features['1' + h.value] = self.ofeature_hoax[h.value]
		for f in Article.factgram:
			features['1' + f.value] = self.ofeature_fact[f.value]
		for u in Article.unkngram:
			features['1' + u.value] = self.ofeature_unkn[u.value]
		for a in Article.asmpgram:
			features['1' + a.value] = self.ofeature_asmp[a.value]
		## NEW
		for h in Article.hoaxgram:
			features['2' + h.value] = self.feature_hoax[h.value]
		for f in Article.factgram:
			features['2' + f.value] = self.feature_fact[f.value]
		for u in Article.unkngram:
			features['2' + u.value] = self.feature_unkn[u.value]
		for a in Article.asmpgram:
			features['2' + a.value] = self.feature_asmp[a.value]
		features["similarity"] = self.similarity
		features["query_count"] = self.feature_query_count
		features["query_percentage"] = self.feature_query_percentage
		features["query_onesen"] = self.feature_query_onesen
		return features		

	def count_query_appeared(self, querypure):
		allstopwords = stopwords.words('english')
		## This is counting that the query apeared near each other
		text = self.content_clean
		queryclean = re.sub(r"[^\w\s]|_+", ' ', querypure.lower())
		querywords = queryclean.split()
		querywords = [word for word in querywords if word not in allstopwords]

		total = 0
		appeared = 0
		counts = {}
		for word in querywords:
			counts[word] = 0
			words = word.rsplit()
			regexpat = r'%s' % "\s+".join(words)
			pattern = regex.findall(regexpat, text.lower())
			ln = len(pattern)
			counts[word] = ln
			total += ln
			if ln > 0:
				appeared += 1

		self.feature_query_count = total / len(querywords)
		self.feature_query_percentage = appeared / len(querywords)
		self.feature_query_onesen = 0

		for sentence in self.sentences:
			counter = 0
			for word in querywords:
				if word in sentence:
					counter += 1
			if len(querywords) <= 3:
				if counter == len(querywords):
					self.feature_query_onesen += 1
			elif (counter/len(querywords)) > 0.55:
				self.feature_query_onesen += 1

	def _old_ngram_counter(self, ngrams, text):
		counts = {}
		for ngram in ngrams:
			counts[ngram.value] = 0
		for ngram in ngrams:
			#print(ngram.pattern())
			pattern = regex.findall(ngram.pattern(), text.lower())
			counts[ngram.value] += len(pattern)
		return counts

	def _ngram_counter(self, ngrams, sentences, r):
		counts = {}
		for ngram in ngrams:
			counts[ngram.value] = 0
		sidx = 0
		for sentence in sentences:
			sentence = re.sub(r"[^\w\s]|_+", ' ', sentence.lower())
			has_qword = False
			for qword in self.query_words:
				if not has_qword and len(qword) > 1:
					word = qword.rsplit()
					epattern = re.compile(r'%s' % "\s+".join(word), re.IGNORECASE)
					has_qword = self.__is_has_word(epattern, sentences, sidx, r)
			epattern = re.compile(r'\bnot\b')
			has_nword = self.__is_has_word(epattern, sentences, sidx, 0)
			if has_qword:
				for ngram in ngrams:
					#print(ngram.pattern())
					pattern = regex.findall(ngram.pattern(), sentence.lower())
					counts[ngram.value] += len(pattern)
					if has_nword:
						counts[ngram.value] -= len(pattern)
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
		for d in ddomain[0:]: clean_domain += d + '.'

		domain = ""
		domain = clean_domain[:-1]

		onesub = '.'.join(domain.split(".")[1:])

		self.url_base = domain

		score = 0
		## Make more punishing for non-credible sites
		if domain in Article.sitedata:
			if Article.sitedata[domain] == 'credible': score = 2
			else: score = -2
		elif onesub in Article.sitedata: 
			if Article.sitedata[onesub] == 'credible': score = 2
			else: score = -2			
		else: score = -1

		return score

	def _ngrams(self, text, n):
		text = text.split(' ')
		output = {}
		for i in range(len(text)-n+1):
			g = ' '.join(text[i:i+n])
			output.setdefault(g, 0)
			output[g] += 1
		return output
 
