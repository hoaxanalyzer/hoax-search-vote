import logging
import json
import time

## ANALYZER
import uuid

from sklearn.externals import joblib

from helper import Similar
from helper import Searcher

from article import Article
from database import Database

class Analyzer:
	target = ['unrelated', 'fact', 'hoax', 'unknown']

	def __init__(self, text, query, client=None):
		self.text = ''.join([i if ord(i) < 128 else ' ' for i in text])
		#self.query = query
		self.query = ' '.join(self.__query_unique_list(query.split()))
	
		self.client = client
		if not type(self.client) is dict:
			self.client = {}

		self.db = Database()
	
	def _get_query_hoax(self):
		## TRying not using + Hoax query, maybe better?
		return self.query + ''

	def __query_unique_list(self, l):
	    ulist = []
	    [ulist.append(x) for x in l if x not in ulist]
	    return ulist

	def __do_voting(self, conclusion, cfact, choax):
		THRESHOLD_UNKNOWN = 0.35
		## Credible News
		if cfact > 2 and cfact > choax: return 1
		if choax > 2 and choax > cfact: return 2

		if (abs(conclusion[1] - conclusion[2]) < 0.5): return 3
		if ((conclusion[1] == 0) and (not conclusion[2] == 0)):
			if (conclusion[2] < 2.5): return 3
			if(conclusion[2] >= (conclusion[3] - (conclusion[2]/2))): return 2
		if ((conclusion[2] == 0) and (not conclusion[1] == 0)):
			if (conclusion[1] < 2.5): return 3
			if(conclusion[1] >= (conclusion[3] - (conclusion[1]/2))): return 1
		if ((conclusion[3] + 2.5) > (conclusion[1] + conclusion[2])):
			return 3
		if (conclusion[2] >= conclusion[1]):
			if (conclusion[2] < 2): return 3
			if (conclusion[2] >= conclusion[1] * 2): return 2
			if (conclusion[2] > (conclusion[1] + conclusion[3])): return 2
			else:
				if ((conclusion[1] + conclusion[3]) - conclusion[2] < THRESHOLD_UNKNOWN): return 2
				else: return 3
		elif (conclusion[2] < conclusion[1]):
			if (conclusion[1] < 2): return 3
			if (conclusion[2] > conclusion[1] * 2): return 1
			if ((conclusion[3] + conclusion[2]) < conclusion[1]): return 1
			else:
				if ((conclusion[3] + conclusion[2]) - conclusion[1] < THRESHOLD_UNKNOWN): return 1
				else: return 3
		else: return 3

	def __calculate_weight(self, dataset):
		meta = sorted(dataset, key=lambda x: x.date, reverse=True)
		i = 0
		for a in meta:
			a.set_weight((((len(meta) - i) / float(len(meta))) * 0.5) + int(a.url_score) * 0.5)
			i += 1
		return dataset

	def __get_references(self, dataset, label):
		meta = sorted(dataset, key=lambda x: (x.date, x.url_score), reverse=True)
		selected = []
		for m in meta:
			if m.label == label:
				selected.append(m)	
		for m in meta:
			if m.label != label and m.label != 'unrelated':
				selected.append(m)	
		for m in meta:
			if m.label == 'unrelated':
				selected.append(m)
		return selected

	def __cleanup_dataset(self, dataset):
		checked = {}
		clean_dataset = []
		for article in dataset:
			url = article.url.rstrip()
			if url not in checked:
				checked[url] = True
				clean_dataset.append(article)
		return clean_dataset

	def _get_conclusion(self, dataset):
		conclusion = [0] * 4
		cfact = 0
		choax = 0

		if len(dataset) > 2:
			dataset = self.__calculate_weight(dataset)

			sentences = []
			for article in dataset:
				sentences.append(article.content_clean[:550])

			# ATTETION HERE! CHANGE THE QUERY TO TEXT
			#similar = Similar(self._get_query_hoax(), sentences)
			similar = Similar(self.text, sentences)
			clf = joblib.load('./models/generated_model.pkl') 
			i = 0

			for num, result in similar.rank:
				article = dataset[num]
				article.set_similarity(result)
				article.count_query_appeared(self.text)

				counts = article.get_category_count()
				if article.similarity < 0.045:
					idx = 0
				elif article.feature_query_percentage < 0.45:
					idx = 0
				elif article.feature_query_percentage < 0.67 and article.similarity < 0.37:
					idx = 3
				elif (article.similarity < 0.35) and (article.feature_query_count < 2):
					idx = 0
				elif (article.similarity < 0.25) and (article.feature_query_count < 5):
					idx = 0
				elif len(article.content) < 400:
					idx = 3
				elif counts[1] == 0 and counts[0] == 0 and counts[3] < 20:
					idx = 1
				elif counts[1] == 0 and counts[0] == 0 and counts[3] >= 20:
					idx = 3
				elif counts[1] >= 1 and counts[0] > counts[1] * 2.5:
					idx = 2
				elif counts[0] >= 1 and counts[1] > counts[0] * 2.5:
					idx = 1
				else:
					idx = clf.predict([article.get_features_array()])[0]

				article.set_label(Analyzer.target[idx])
				conclusion[idx] += 1 + article.weight
				if article.url_score >= 2:
					if idx == 1:
						cfact += 1
					elif idx == 2:
						choax += 1

				i += 1

		return (conclusion, cfact, choax)

	def retrieve(self, loghash):
		query = self.db.get_query_by_loghash(loghash)
		if not query == None:
			self.query = query["query_search"]
			self.text = query["query_text"]

			s = Searcher(self.query)
			dataset = s.get_news(query["query_hash"])
			dataset = self.__cleanup_dataset(dataset)

			conclusion, cfact, choax = self._get_conclusion(dataset)
			ridx = self.__do_voting(conclusion, cfact, choax)
			references = self.__get_references(dataset, Analyzer.target[ridx])

			lor = []
			for r in references:
				data = {}
				data["url"] = r.url
				data["url_base"] = r.url_base
				data["label"] = r.label
				data["text"] = r.content[:900] + "... (see more at source)"
				data["id"] = r.ahash
				data["site_score"] = r.url_score
				data["date"] = str(r.date)
				data["feature"] = str(r.get_humanize_feature())
				data["counts"] = str(r.get_category_count())
				lor.append(data)

			result = {}
			result["inputText"] = query["query_text"]
			result["hash"] = query["query_hash"]
			result["query_search"] = query["query_search"]
			result["conclusion"] = Analyzer.target[ridx]
			result["scores"] = conclusion
			result["references"] = lor
			result["status"] = "Success"
			result["id"] = loghash

			self.db.insert_result_log(s.qid, conclusion[2], conclusion[1], conclusion[3], conclusion[0], result["conclusion"])
		else:
			result = {}
			result["status"] = "Failed"
			result["message"] = "Query not found"
		return result
		
	# def do_stream(self):
	# 	dataset = []

	# 	yield "{'step':0, 'total':2, 'message':'Initializing'}\n"
	# 	time.sleep(.1)
	# 	s = Searcher(self._get_query_hoax())

	# 	if not "ip" in list(self.client.keys()):
	# 		self.client["ip"] = "unknown"
	# 	if not "browser" in list(self.client.keys()):
	# 		self.client["browser"] = "unknown"

	# 	query_uuid = uuid.uuid4().hex
	# 	s.set_qid(self.db.insert_query_log(query_uuid, self.text, self.query, s.query_hash, self.client["ip"], self.client["browser"]))
		
	# 	yield "{'step':1, 'total':2, 'message':'Search for data'}\n"
	# 	time.sleep(.1)
	# 	dataset = s.search_all()

	# 	yield "{'step':2, 'total':2, 'message':'Determining conclusion'}\n"
	# 	time.sleep(.1)
	# 	conclusion = self._get_conclusion(dataset)
	# 	ridx = self.__do_voting(conclusion)
	# 	references = self.__get_references(dataset, Analyzer.target[ridx])

	# 	lor = []
	# 	for r in references:
	# 		data = {}
	# 		data["url"] = r.url
	# 		data["url_base"] = r.url_base
	# 		data["label"] = r.label
	# 		data["text"] = r.content[:900] + "... (see more at source)"
	# 		data["id"] = r.ahash
	# 		data["site_score"] = r.url_score
	# 		data["feature"] = str(r.get_humanize_feature())
	# 		data["counts"] = str(r.get_category_count())
	# 		lor.append(data)

	# 	result = {}
	# 	result["query"] = self.query
	# 	result["hash"] = s.query_hash
	# 	result["conclusion"] = Analyzer.target[ridx]
	# 	result["scores"] = conclusion
	# 	result["references"] = lor
	# 	result["status"] = "Success"
	# 	result["id"] = query_uuid

	# 	self.db.insert_result_log(s.qid, conclusion[2], conclusion[1], conclusion[3], conclusion[0], result["conclusion"])
	# 	yield json.dumps(result)

	def do(self):
		dataset = []

		s = Searcher(self._get_query_hoax())

		if not "ip" in list(self.client.keys()):
			self.client["ip"] = "unknown"
		if not "browser" in list(self.client.keys()):
			self.client["browser"] = "unknown"

		query_uuid = uuid.uuid4().hex
		s.set_qid(self.db.insert_query_log(query_uuid, self.text, self.query, s.query_hash, self.client["ip"], self.client["browser"]))
		print("Search for all")
		dataset = s.search_all()
		dataset = self.__cleanup_dataset(dataset)

		print(dataset)
		print("Going to conclusion")
		conclusion, cfact, choax = self._get_conclusion(dataset)
		ridx = self.__do_voting(conclusion, cfact, choax)
		references = self.__get_references(dataset, Analyzer.target[ridx])

		lor = []
		for r in references:
			data = {}
			data["url"] = r.url
			data["url_base"] = r.url_base
			data["label"] = r.label
			data["text"] = r.content[:900] + "... (see more at source)"
			data["id"] = r.ahash
			data["site_score"] = r.url_score
			data["date"] = str(r.date)
			data["feature"] = str(r.get_humanize_feature())
			data["counts"] = str(r.get_category_count())
			lor.append(data)

		result = {}
		result["query"] = self.query
		result["hash"] = s.query_hash
		result["conclusion"] = Analyzer.target[ridx]
		result["scores"] = conclusion
		result["references"] = lor
		result["status"] = "Success"
		result["id"] = query_uuid

		self.db.insert_result_log(s.qid, conclusion[2], conclusion[1], conclusion[3], conclusion[0], result["conclusion"])
		return result

class Feedback:
	def __init__(self, client=None):
		self.client = client
		if not type(self.client) is dict:
			self.client = {}
		self.db = Database()
	
	def result(self, is_know, label, reason, quuid):
		result = {}
		try:
			if self.db.is_query_exist(quuid):
				self.db.insert_result_feedback(quuid, is_know, reason, label, self.client["ip"], self.client["browser"])
				result["status"] = "Success"
				result["message"] = "Result feedback noted"
			else:
				result["status"] = "Failed"
				result["message"] = "Invalid quuid"				
		except Exception as e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result

	def reference(self, is_related, label, reason, auuid):
		result = {}
		try:
			if self.db.is_reference_exist(auuid):
				self.db.insert_reference_feedback(auuid, is_related, reason, label, self.client["ip"], self.client["browser"])
				result["status"] = "Success"
				result["message"] = "Reference feedback noted"
			else:
				result["status"] = "Failed"
				result["message"] = "Invalid auuid"		
		except Exception as e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result

class Management:
	def __init__(self, client=None):
		self.client = client
		if not type(self.client) is dict:
			self.client = {}
		self.db = Database()
	
	def get_references(self, qhash):
		result = {}
		try:
			result["status"] = "Success"
			result["data"] = self.db.get_reference_by_qhash(qhash)
		except Exception as e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result

	def get_query_log(self):
		result = {}
		try:
			result["status"] = "Success"
			result["data"] = self.db.get_query_log()
		except Exception as e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result
