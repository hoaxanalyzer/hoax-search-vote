"""
PREPROCESSOR

Module for preprocessing text
Usage: python preprocessor.py [file]
Example: python preprocessor.py jackie.txt

(C) TW

"""

import enchant
import multiprocessing
import re
import string
import sys
import time
import unicodedata
from multiprocessing.pool import Pool
from nltk.corpus import stopwords
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer

with open('resource/stopwords_en.txt', 'r') as myfile:
    hoax_stopwords = myfile.read()
    hoax_stopwords = word_tokenize(hoax_stopwords)

dictionary = enchant.Dict("en_US")
lemmatizer = WordNetLemmatizer()
en_stopwords = stopwords.words('english')
punctuations = list(string.punctuation)
all_stopwords = set(en_stopwords + hoax_stopwords + punctuations)


CORE_NUM = multiprocessing.cpu_count()
if CORE_NUM == 1:
    CORE_NUM = 2

def process_tokens_worker(token):
    word = token.split(" ")[0]
    if len(word) > 0:
        if word.isupper() and dictionary.check(word.lower()):
            return token.lower()
        elif word.isupper():
            return token.title()
        else:
            return token

def preprocess(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode("ascii", "ignore")
    text = text.replace("'s", " ").replace("'"," ").replace("`"," ")
    # text = re.sub("[^0-9a-zA-Z !\"/:;<=>?.,!@#$%^&-_|()']+", " ", text)
    tokens = tokenize(text)
    try:
        # Create new threads
        pool = Pool(CORE_NUM)
        results = pool.starmap(process_tokens_worker, zip(tokens))
        for idx, token in enumerate(results):
            if dictionary.check(token.lower()):
                results[idx] = lemmatizer.lemmatize(token.lower())
                results[idx] = lemmatizer.lemmatize(token.lower(), pos='v')
        return results
    except Exception as e:
        print(str(e))

def stopword_checker(word):
    if word not in all_stopwords:
        return word
    else:
        return ""

def remove_stopwords(tokens):
    pool = Pool(CORE_NUM)
    results = pool.starmap(stopword_checker, zip(tokens))
    return results

def tokenize(text):
    tokens = word_tokenize(text)
    return tokens

def chunk_words(tokens):
    return ne_chunk(pos_tag(tokens))

def main():
    start = time.time()

    filename = sys.argv[1]
    with open(filename, 'r') as myfile:
        text = myfile.read().replace('\n', '')
    processed_text = preprocess(text)
    print("Preprocess: ", processed_text, "\n")

    end = time.time()
    elapsed = end - start
    print("Time elapsed:", elapsed, "s")

if __name__ == "__main__":
    main()