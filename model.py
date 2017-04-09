import logging

import pandas as pd

from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib
from sklearn import svm

import pickle

from core import Similar
from article import Article
from database import Database

class Model:
	def __init__(self):
		self.csvlocation = 'models/csv/generated_dataset.csv'
		self.modellocation = 'models/generated_model.pkl'
		self.db = Database()
	
	def _get_data(self, path):
	    print("Found the csv file")
	    df = pd.read_csv(path, index_col=0)
	    return df

	def _encode_target(self, df, target_column):
	    df_mod = df.copy()
	    targets = df_mod[target_column].unique()
	    map_to_int = {name: n for n, name in enumerate(targets)}
	    df_mod["target"] = df_mod[target_column].replace(map_to_int)
	    return (df_mod, targets)

	def create(self):
		feedbacks = self.db.get_reference_feedback()

		with open(self.csvlocation, 'w') as file:
			file.write("desc,fea1,fea2,fea3,fea4,fea21,fea22,fea23,fea24,similarity,qcount,qperct,label\n")
			length = len(feedbacks)
			for qid in feedbacks:
				datasets = []
				sentences = []

				print(str(qid) + "/" + str(length))

				if not qid == None:
					all_references = self.db.get_reference_by_qid(qid)
					already_hash = []

					for feedback in feedbacks[qid]:
						## THE QUERY COULD RESULT IN INCONSISTENCY, PLEASE STANDARIZE: TEXT INPUT OR QUERY TO S.E.??
						article = Article(feedback["query_search"], "None", "None", feedback["article_content"], "None")
						if not (feedback["is_relevant"] == "Related" or feedback["is_relevant"] == "Relevant"):
							article.set_label("unrelated")
						else:
							article.set_label(feedback["feedback_label"].lower())
						datasets.append(article)
						sentences.append(article.content_clean)
						already_hash.append(article.ahash)

					## For similarity
					for ref in all_references:
						if ref["hash"] not in already_hash:
							article = Article(feedback["query_search"], "None", "None", ref["content"], "None")
							article.set_label("similarity")
							datasets.append(article)
							sentences.append(article.content_clean)

					# ATTETION HERE! CHANGE THE QUERY TO TEXT
					#similar = Similar(self._get_query_hoax(), sentences)
					similar = Similar(feedback["query_text"], sentences)

					for num, result in similar.rank:
						if not datasets[num].label == "similarity":
							article = datasets[num]
							article.set_similarity(result)
							article.count_query_appeared(feedback["query_text"])
							l = "model,"
							features = article.get_features_array()
							for fea in features:
								l += str(fea) + ","
							l += article.label + "\n"
							file.write(l)

		df = self._get_data(self.csvlocation)
		df2, targets = self._encode_target(df, "label")

		print(targets)
		features = list(df2.columns[:11])
		print("* features:", features)

		y = df2["target"]
		X = df2[features]

		clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(12,6), random_state=1)
		clf.fit(X, y)

		joblib.dump(clf, self.modellocation) 


model = Model()
model.create()
