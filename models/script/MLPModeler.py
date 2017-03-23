from __future__ import print_function

import os
import subprocess

import graphviz
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib
from sklearn import svm

import pickle

def get_data(path):
    print("Found the csv file")
    df = pd.read_csv(path, index_col=0)
    return df

def encode_target(df, target_column):
    df_mod = df.copy()
    targets = df_mod[target_column].unique()
    map_to_int = {name: n for n, name in enumerate(targets)}
    df_mod["target"] = df_mod[target_column].replace(map_to_int)
    return (df_mod, targets)

df = get_data("../csv/dataset-03-combined-labeled.csv")
#df = get_data("../csv/dataset-02-labeled.csv")
df2, targets = encode_target(df, "label")

print(targets)
features = list(df2.columns[2:97])
print("* features:", features, sep="\n")

y = df2["target"]
X = df2[features]

clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(50,25), random_state=1)
clf.fit(X, y)

joblib.dump(clf, 'model03-combined-mlp.pkl') 

