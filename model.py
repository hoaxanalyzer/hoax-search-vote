import logging

import pandas as pd

from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib
from sklearn import svm

import pickle

from similar import Similar
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
			file.write("desc,fea1,fea2,fea3,fea4,fea5,fea6,fea7,fea8,fea9,fea10,fea11,fea12,fea13,fea14,fea15,fea16,fea17,fea18,fea19,fea20,fea21,fea22,fea23,fea24,fea25,fea26,fea27,fea28,fea29,fea30,fea31,fea32,fea33,fea34,fea35,fea36,fea37,fea38,fea39,fea40,fea41,fea42,fea43,fea44,fea45,fea46,fea47,fea1,fea2,fea3,fea4,fea5,fea6,fea7,fea8,fea9,fea10,fea11,fea12,fea13,fea14,fea15,fea16,fea17,fea18,fea19,fea20,fea21,fea22,fea23,fea24,fea25,fea26,fea27,fea28,fea29,fea30,fea31,fea32,fea33,fea34,fea35,fea36,fea37,fea38,fea39,fea40,fea41,fea42,fea43,fea44,fea45,fea46,fea47,similarity,label\n")
			for qid in feedbacks:
				datasets = []
				sentences = []
				for feedback in feedbacks[qid]:
					## THE QUERY COULD RESULT IN INCONSISTENCY, PLEASE STANDARIZE: TEXT INPUT OR QUERY TO S.E.??
					article = Article(feedback["query_search"], "None", "None", feedback["article_content"], "None")
					if not feedback["is_relevant"] == "Related":
						article.set_label("unrelated")
					else:
						article.set_label(feedback["feedback_label"].lower())
					datasets.append(article)
					sentences.append(article.content_clean)

				# ATTETION HERE! CHANGE THE QUERY TO TEXT
				#similar = Similar(self._get_query_hoax(), sentences)
				similar = Similar(feedback["query_text"], sentences)

				for num, result in similar.rank:
					article = datasets[num]
					article.set_similarity(result)
					l = "model,"
					features = article.get_features_array()
					for fea in features:
						l += str(fea) + ","
					l += article.label + "\n"
					file.write(l)

		df = self._get_data(self.csvlocation)
		df2, targets = self._encode_target(df, "label")

		print(targets)
		features = list(df2.columns[:95])
		print("* features:", features)

		y = df2["target"]
		X = df2[features]

		clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(50,25), random_state=1)
		clf.fit(X, y)

		joblib.dump(clf, self.modellocation) 


model = Model()
model.create()
