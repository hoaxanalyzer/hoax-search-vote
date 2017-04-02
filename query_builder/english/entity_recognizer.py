"""
ENTITY RECOGNIZER

Module for recognizing entities within text
Usage: python entity_recognizer.py [file]
Example: python entity_recognizer.py jackie.txt

entity_recognizer.py
TW (2017)

"""

from multiprocessing.pool import ThreadPool
from nltk.tag.stanford import StanfordNERTagger
from nltk.tree import Tree
from query_builder.english.preprocessor import *
import csv
import nltk
import os
import sys
import time

st = StanfordNERTagger('lib/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', 'lib/stanford-ner/stanford-ner.jar')

def entity_recognition_stanford(text):
    for sent in nltk.sent_tokenize(text):
        tokens = nltk.tokenize.word_tokenize(sent)
        tags = st.tag(tokens)
        res = []
        for tag in tags:
            if tag[1].isupper() and len(tag[1]) > 1:
                if tag not in res:
                    res.append(tag)

    return res

def entity_recognition(chunked):
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
            if type(i) == Tree:
                    current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:
                    named_entity = " ".join(current_chunk)
                    if named_entity not in continuous_chunk:
                            continuous_chunk.append(named_entity)
                            current_chunk = []
            else:
                    continue
    return continuous_chunk

def main():
    if (len(sys.argv) >= 3):
        directory = sys.argv[1]
        file_output = sys.argv[2]

        csvfile = open(file_output, 'wb')
        for subdir, dirs, files in os.walk(directory):
            for filename in files:
                with open(directory + "/" + filename, 'r') as myfile:
                    text = myfile.read().replace('\n', '')
                    myfile.close()

                result = [filename, text]
                text = preprocess(text)
                # tokens = tokenize(text)
                # ne_chunk = chunk_words(tokens)
                # ent = entity_recognition_stanford(ne_chunk)
                # ent_res = "[" + ", ".join(ent) + "]"
                firsttime = time.time()
                ent = entity_recognition_stanford(text)
                lasttime = time.time()
                res_time = str(lasttime-firsttime) + " s"
                result.append(ent)
                result.append(res_time)
                print ent
                print res_time

                wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                wr.writerow(result)
                print filename, "done!"
    else:
        filename = sys.argv[1]
        with open(filename, 'r') as myfile:
            text = myfile.read().replace('\n', '')
        text = preprocess(text)
        firsttime = time.time()
        ent = entity_recognition_stanford(text)
        lasttime = time.time()
        print ent
        print str(lasttime-firsttime) + " s"

if __name__ == "__main__":
    main()