from __future__ import print_function

import os
import subprocess

import graphviz
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.datasets import load_iris
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

def visualize_tree(tree, feature_names):
    with open("dt.dot", 'w') as f:
        export_graphviz(tree, out_file=f,
                        feature_names=feature_names)
    command = ["dot", "-Tpng", "dt.dot", "-o", "dt.png"]
    try:
        subprocess.check_call(command)
    except:
        exit("Could not run dot, ie graphviz, to "
             "produce visualization")

df = get_data("../csv/dataset-03-combined-labeled.csv")
df2, targets = encode_target(df, "label")

print(targets)
features = list(df2.columns[2:97])
print("* features:", features, sep="\n")

y = df2["target"]
X = df2[features]
#dt = DecisionTreeClassifier(min_samples_split=20, random_state=99)
dt = svm.SVC(decision_function_shape='ovo')
dt.fit(X, y)

#visualize_tree(dt, features)

#iris = load_iris()
#print(iris.data[:1, :])
#print(targets[dt.predict([[0.0, 0.0758883, 0.2195]])])

#print(dt.predict_proba([[0.0, 0.0758883, 0.2195]]))

joblib.dump(dt, 'model03-combined-svm.pkl') 

