"""
SKLEARN CLASSIFIER

Sklearn Classifier
Usage: -
Example: - 

TW (2017)

"""

import csv
import numpy as np
from itertools import islice
from query_builder.ms_text_analytics import LANG_ID, LANG_EN
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier


ID_CSV_NNP = "output/id-notoken-nnp-full.csv"
ID_CSV_NN = "output/id-notoken-nn-full.csv"
ID_CSV_CDP = "output/id-notoken-cdp-full.csv"

ID_MODEL_NNP = "models/id-mlp.nnp.pkl"
ID_MODEL_NN = "models/id-mlp.nn.pkl"
ID_MODEL_CDP ="models/id-mlp.cdp.pkl"

ID_TAG = ['nnp', 'nn', 'cdp']
ID_TAG_FEATURE = ['prob', 'wcount', 'wpos', 'spos']
ID_N_FEATURE = 8

EN_CSV_NNP = "output/en-notoken-nnp-full.csv"
EN_CSV_JJ = "output/en-notoken-jj-full.csv"
EN_CSV_NN = "output/en-notoken-nn-full.csv"
EN_CSV_VBP = "output/en-notoken-vbp-full.csv"
EN_CSV_CD = "output/en-notoken-cd-full.csv"
EN_CSV_VB = "output/en-notoken-vb-full.csv"

EN_MODEL_NNP = "models/en-mlp.nnp.pkl"
EN_MODEL_JJ = "models/en-mlp.jj.pkl"
EN_MODEL_NN ="models/en-mlp.nn.pkl"
EN_MODEL_VBP = "models/en-mlp.vbp.pkl"
EN_MODEL_CD = "models/en-mlp.cd.pkl"
EN_MODEL_VB ="models/en-mlp.vb.pkl"

EN_TAG = ['nnp', 'jj', 'nn', 'vbp', 'cd', 'vb']
EN_TAG_FEATURE = ['prob', 'wcount', 'kpcount', 'wseq', 'sseq']
EN_N_FEATURE = 5

def print_title(title):
    print("\n" + title)
    print("=" * len(title))

def create_model(input_file, output_file):
    # Load data
    X = []
    y = []
    with open(input_file, 'r') as csvfile:
        dataset = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        for row in islice(dataset, 1, None):
            data = []
            label = ""
            for cell in row:
                try:
                    data.append(float(cell))
                except ValueError:
                    label = cell
            X.append(data)
            y.append(label)

    # Create and Save Model
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
    clf.fit(X,y)
    print("Done! (believe it or not)")
    joblib.dump(clf, output_file) 
    print("Model and filter saved to ", output_file)

def load_classifier(lang, tag):
    classifier = {}

    if lang == LANG_ID and tag == "nnp":
        clf = joblib.load(ID_MODEL_NNP)
    elif lang == LANG_ID and tag == "nn":
        clf = joblib.load(ID_MODEL_NN)
    elif lang == LANG_ID and tag == "cdp":
        clf = joblib.load(ID_MODEL_CDP)

    elif lang == LANG_EN and tag == "nnp":
        clf = joblib.load(EN_MODEL_NNP)
    elif lang == LANG_EN and tag == "jj":
        clf = joblib.load(EN_MODEL_JJ)
    elif lang == LANG_EN and tag == "nn":
        clf = joblib.load(EN_MODEL_NN)
    elif lang == LANG_EN and tag == "vbp":
        clf = joblib.load(EN_MODEL_VBP)
    elif lang == LANG_EN and tag == "cd":
        clf = joblib.load(EN_MODEL_CD)
    elif lang == LANG_EN and tag == "vb":
        clf = joblib.load(EN_MODEL_VB)
    return clf

def classify_json_object(lang, tag, json_data):
    clf = load_classifier(lang, tag)

    # Create an instance
    n_feature = 0
    tag_list = ""
    tag_feature = ""

    if lang == LANG_ID:
        n_feature = ID_N_FEATURE
        tag_list = ID_TAG
        tag_feature = ID_TAG_FEATURE
    elif lang == LANG_EN:
        n_feature = EN_N_FEATURE
        tag_list = EN_TAG
        tag_feature = EN_TAG_FEATURE

    val = []
    for tag in tag_list:
        for i in range(0,n_feature):
            for ftr in tag_feature:
                cur_key = tag + str(i + 1)
                val.append(float(json_data[cur_key][cur_key + "_" + ftr]))
    
    x_pred = np.array(val).reshape((1, -1))
    pred = clf.predict(x_pred)
    return pred[0]

def main():
    # Create Model
    print_title("ID_MODEL_NNP")
    create_model(ID_CSV_NNP, ID_MODEL_NNP)
    print_title("ID_MODEL_NN")
    create_model(ID_CSV_NN, ID_MODEL_NN)
    print_title("ID_MODEL_CDP")
    create_model(ID_CSV_CDP, ID_MODEL_CDP)

    print_title("EN_MODEL_NNP")
    create_model(EN_CSV_NNP, EN_MODEL_NNP)
    print_title("EN_MODEL_JJ")
    create_model(EN_CSV_JJ, EN_MODEL_JJ)
    print_title("EN_MODEL_NN")
    create_model(EN_CSV_NN, EN_MODEL_NN)
    print_title("EN_MODEL_VBP")
    create_model(EN_CSV_VBP, EN_MODEL_VBP)
    print_title("EN_MODEL_CD")
    create_model(EN_CSV_CD, EN_MODEL_CD)
    print_title("EN_MODEL_VB")
    create_model(EN_CSV_VB, EN_MODEL_VB)
    

if __name__ == "__main__":
    main()