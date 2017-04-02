"""
WEKA CLASSIFIER

Weka Classifier
Usage: -
Example: - 

TW (2017)

"""

from query_builder.ms_text_analytics import LANG_ID, LANG_EN
from weka.classifiers import Classifier, Evaluation
from weka.core.dataset import Attribute
from weka.core.dataset import Instance
from weka.core.dataset import Instances
from weka.filters import Filter
from weka.core.classes import Random
import json
import weka.core.converters as converters
import weka.core.jvm as jvm
import weka.core.serialization as serialization

ID_ARFF_NNP = "../output/id-notoken-nnp-full.arff"
ID_ARFF_NN = "../output/id-notoken-nn-full.arff"
ID_ARFF_CDP = "../output/id-notoken-cdp-full.arff"

ID_MODEL_NNP = "../model/id-randf.nnp.model"
ID_MODEL_NN = "../model/id-randf.nn.model"
ID_MODEL_CDP ="../model/id-randf.cdp.model"

ID_TAG = ['nnp', 'nn', 'cdp']
ID_TAG_FEATURE = ['prob', 'wcount', 'wpos', 'spos']
ID_N_FEATURE = 8

EN_ARFF_NNP = "../output/en-notoken-nnp-full.arff"
EN_ARFF_JJ = "../output/en-notoken-jj-full.arff"
EN_ARFF_NN = "../output/en-notoken-nn-full.arff"
EN_ARFF_VBP = "../output/en-notoken-vbp-full.arff"
EN_ARFF_CD = "../output/en-notoken-cd-full.arff"
EN_ARFF_VB = "../output/en-notoken-vb-full.arff"

EN_MODEL_NNP = "../model/en-randf.nnp.model"
EN_MODEL_JJ = "../model/en-randf.jj.model"
EN_MODEL_NN ="../model/en-randf.nn.model"
EN_MODEL_VBP = "../model/en-randf.vbp.model"
EN_MODEL_CD = "../model/en-randf.cd.model"
EN_MODEL_VB ="../model/en-randf.vb.model"

EN_TAG = ['nnp', 'jj', 'nn', 'vbp', 'cd', 'vb']
EN_TAG_FEATURE = ['prob', 'wcount', 'kpcount', 'wseq', 'sseq']
EN_N_FEATURE = 5

def print_title(title):
    print("\n" + title)
    print("=" * len(title))

def create_model(input_file, output_file):
    # Load data
    data = converters.load_any_file(input_file)
    data.class_is_last()   # set class attribute
    
    # filter data 
    print_title("Filtering Data")
    discretize = Filter(classname="weka.filters.unsupervised.attribute.Discretize", options=["-B", "10", "-M", "-1.0", "-R", "first-last"])
    discretize.inputformat(data)    # let the filter know about the type of data to filter
    filtered_data = discretize.filter(data)
    print("Done! (believe it or not)")


    print_title("Build Classifier")
    classifier = Classifier(classname="weka.classifiers.trees.RandomForest", options=["-I", "100", "-K", "0", "-S", "1"])
    classifier.build_classifier(filtered_data)
    print("Done! (believe it or not)")
    serialization.write_all(output_file, [classifier, discretize])
    print("Model and filter saved to ", output_file)

    evaluation = Evaluation(data)   # initialize with priors
    evaluation.crossvalidate_model(classifier, filtered_data, 10, Random(42))   # 10-fold CV
    print(evaluation.summary())
    print("pctCorrect: " + str(evaluation.percent_correct))
    print("incorrect: " + str(evaluation.incorrect))


def classify_new_instance(model, dataset):
    pred = "?"
    try:
        filtered_dataset = model['filter'].filter(dataset)
        pred = model['classifier'].classify_instance(filtered_dataset.get_instance(0))
        pred = (filtered_dataset.class_attribute.value(int(pred)))
    except KeyError:
        i
    return pred

def load_classifier(lang, tag):
    classifier = {}

    if lang == LANG_ID and tag == "nnp":
        objects = serialization.read_all(ID_MODEL_NNP)
    elif lang == LANG_ID and tag == "nn":
        objects = serialization.read_all(ID_MODEL_NN)
    elif lang == LANG_ID and tag == "cdp":
        objects = serialization.read_all(ID_MODEL_CDP)

    elif lang == LANG_EN and tag == "nnp":
        objects = serialization.read_all(EN_MODEL_NNP)
    elif lang == LANG_EN and tag == "jj":
        objects = serialization.read_all(EN_MODEL_JJ)
    elif lang == LANG_EN and tag == "nn":
        objects = serialization.read_all(EN_MODEL_NN)
    elif lang == LANG_EN and tag == "vbp":
        objects = serialization.read_all(EN_MODEL_VBP)
    elif lang == LANG_EN and tag == "cd":
        objects = serialization.read_all(EN_MODEL_CD)
    elif lang == LANG_EN and tag == "vb":
        objects = serialization.read_all(EN_MODEL_VB)

    classifier['classifier'] = Classifier(jobject=objects[0])
    classifier['filter'] = Filter(jobject=objects[1])
    return classifier

def create_attributes(lang, tag):
    attr = []
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
    for i in range(0,n_feature):
        for tag in tag_list:
            for ftr in tag_feature:
                attr.append(Attribute.create_numeric(tag + str(i+1) + "_" + ftr))
    attr.append(Attribute.create_nominal(tag + "_class", []))
    return attr

def classify_json_object(lang, tag, json_data):
    model = load_classifier(lang, tag)

    # create dataset
    attr = create_attributes(lang, tag)
    dataset = Instances.create_instances(lang + "_dataset", attr, 0)

    # create an instance
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

    # print (attr)
    val = []
    for tag in tag_list:
        for i in range(0,n_feature):
            for ftr in tag_feature:
                cur_key = tag + str(i + 1)
                val.append(json_data[cur_key][cur_key + "_" + ftr])
                # print(cur_key + "_" + ftr, json_data[cur_key][cur_key + "_token"], json_data[cur_key][cur_key + "_" + ftr])
    val.append(0)
    inst = Instance.create_instance(val)
    dataset.add_instance(inst)
    dataset.class_is_last()
    
    pred = classify_new_instance(model, dataset)
    
    return pred


def main():
    # Create Model
    print_title("ID_MODEL_NNP")
    create_model(ID_ARFF_NNP, ID_MODEL_NNP)
    print_title("ID_MODEL_NN")
    create_model(ID_ARFF_NN, ID_MODEL_NN)
    print_title("ID_MODEL_CDP")
    create_model(ID_ARFF_CDP, ID_MODEL_CDP)

    print_title("EN_MODEL_NNP")
    create_model(EN_ARFF_NNP, EN_MODEL_NNP)
    print_title("EN_MODEL_JJ")
    create_model(EN_ARFF_JJ, EN_MODEL_JJ)
    print_title("EN_MODEL_NN")
    create_model(EN_ARFF_NN, EN_MODEL_NN)
    print_title("EN_MODEL_VBP")
    create_model(EN_ARFF_VBP, EN_MODEL_VBP)
    print_title("EN_MODEL_CD")
    create_model(EN_ARFF_CD, EN_MODEL_CD)
    print_title("EN_MODEL_VB")
    create_model(EN_ARFF_VB, EN_MODEL_VB)
    

if __name__ == "__main__":
    try:
        jvm.start()
        main()
    except Exception as e:
        print(traceback.format_exc())
    finally:
        jvm.stop()