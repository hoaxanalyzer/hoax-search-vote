import logging

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
		self.text = text
		self.query = query
		
		self.client = client
		if not type(self.client) is dict:
			self.client = {}

		self.db = Database()
	
	def _get_query_hoax(self):
		return self.query + ' hoax'

	def __do_voting(self, conclusion):
		THRESHOLD_UNKNOWN = 0.35
		if (conclusion[2] >= conclusion[1]):
			if (conclusion[2] > (conclusion[1] + conclusion[3])): return 2
			else:
				if ((conclusion[1] + conclusion[3]) - conclusion[2] < THRESHOLD_UNKNOWN): return 2
				else: return 3
		elif (conclusion[2] < conclusion[1]):
			if ((conclusion[3] + conclusion[2]) < conclusion[1]): return 1
			else:
				if ((conclusion[3] + conclusion[2]) - conclusion[1] < THRESHOLD_UNKNOWN): return 1
				else: return 3
		else: return 3

	def __calculate_weight(self, dataset):
		meta = sorted(dataset, key=lambda x: x.date, reverse=True)
		i = 0
		for a in meta:
			a.set_weight((((len(meta) - i) / float(len(meta))) * 0.5) * int(a.url_score))
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
		return selected

	def _get_conclusion(self, dataset):
		dataset = self.__calculate_weight(dataset)

		sentences = []
		for article in dataset:
			sentences.append(article.content_clean)

		# ATTETION HERE! CHANGE THE QUERY TO TEXT
		#similar = Similar(self._get_query_hoax(), sentences)
		similar = Similar(self.text, sentences)
		clf = joblib.load('./models/generated_model.pkl') 
		i = 0
		conclusion = [0] * 4

		for num, result in similar.rank:
			article = dataset[num]
			article.set_similarity(result)
			idx = clf.predict([article.get_features_array()])[0]
			article.set_label(Analyzer.target[idx])
			conclusion[idx] += 1
			if idx != 0: conclusion[idx] += article.weight
			i += 1
		return conclusion

	def retrieve(self, loghash):
		query = self.db.get_query_by_loghash(loghash)
		if not query == None:
			self.query = query[3]

			s = Searcher("this is not query")
			dataset = s.get_news(query[4])

			conclusion = self._get_conclusion(dataset)
			ridx = self.__do_voting(conclusion)
			references = self.__get_references(dataset, Analyzer.target[ridx])

			lor = []
			for r in references:
				data = {}
				data["url"] = r.url
				data["url_base"] = r.url_base
				data["label"] = r.label
				data["text"] = r.content
				data["id"] = r.ahash
				lor.append(data)

			result = {}
			result["inputText"] = query[2]
			result["hash"] = query[4]
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
		

	def do(self):
		dataset = []

		s = Searcher(self._get_query_hoax())

		if not "ip" in self.client.keys():
			self.client["ip"] = "unknown"
		if not "browser" in self.client.keys():
			self.client["browser"] = "unknown"

		query_uuid = uuid.uuid4().hex
		s.set_qid(self.db.insert_query_log(query_uuid, self.text, self.query, s.query_hash, self.client["ip"], self.client["browser"]))
		dataset = s.search_all()

		conclusion = self._get_conclusion(dataset)
		ridx = self.__do_voting(conclusion)
		references = self.__get_references(dataset, Analyzer.target[ridx])

		lor = []
		for r in references:
			data = {}
			data["url"] = r.url
			data["url_base"] = r.url_base
			data["label"] = r.label
			data["text"] = r.content
			data["id"] = r.ahash
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
		except Exception, e:
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
		except Exception, e:
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
		except Exception, e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result

	def get_query_log(self):
		result = {}
		try:
			result["status"] = "Success"
			result["data"] = self.db.get_query_log()
		except Exception, e:
			result["status"] = "Failed"
			result["message"] = "Database error"
			result["detail"] = str(e)
		return result
