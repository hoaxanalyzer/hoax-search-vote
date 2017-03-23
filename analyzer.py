import logging
import uuid

from sklearn.externals import joblib

from similar import Similar
from article import Article
from searcher import Searcher
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

	def do(self):
		dataset = []
		query = self.query + ' hoax'

		s = Searcher(query)

		if not "ip" in self.client.keys():
			self.client["ip"] = "unknown"
		if not "browser" in self.client.keys():
			self.client["browser"] = "unknown"

		s.set_qid(self.db.insert_query_log(uuid.uuid4().hex, self.text, query, s.query_hash, self.client["ip"], self.client["browser"]))
		dataset = s.search_all()
		dataset = self.__calculate_weight(dataset)

		sentences = []
		for article in dataset:
			sentences.append(article.content_clean)

		similar = Similar(query, sentences)

		clf = joblib.load('./models/model03-combined-mlp.pkl') 

		i = 0
		conclusion = [0] * 4
		print(conclusion)
		for num, result in similar.rank:
		 	article = dataset[num]
		 	article.set_similarity(result)
			idx = clf.predict([article.get_features_array()])[0]
			article.set_label(Analyzer.target[idx])
			print("label: " + article.label)
			print("idx label: " + str(idx))
			conclusion[idx] += 1
			if idx != 0: conclusion[idx] += article.weight
			print(conclusion)
			i += 1
		print("Final")
		print(conclusion)

		ridx = self.__do_voting(conclusion)

		references = self.__get_references(dataset, Analyzer.target[ridx])
		lor = []
		for r in references:
			data = {}
			data["url"] = r.url
			data["url_base"] = r.url_base
			data["label"] = r.label
			lor.append(data)

		result = {}
		result["query"] = query
		result["hash"] = s.query_hash

		result["conclusion"] = Analyzer.target[ridx]
		result["scores"] = conclusion

		result["references"] = lor

		self.db.insert_result_log(s.qid, conclusion[2], conclusion[1], conclusion[3], conclusion[0], result["conclusion"])
		return result


