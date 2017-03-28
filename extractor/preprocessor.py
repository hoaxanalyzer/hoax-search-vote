"""
PREPROCESSOR

Module for preprocessing text
Usage: python preprocessor.py [file]
Example: python preprocessor.py jackie.txt

(C) TW

"""

from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import enchant
import re
import string
import sys

lemmatizer = WordNetLemmatizer()
dictionary = enchant.Dict("en_US")
punctuations = list(string.punctuation)
with open('resource/stopwords_en.txt', 'r') as myfile:
    hoax_stopwords = myfile.read()
    hoax_stopwords = word_tokenize(hoax_stopwords)

def preprocess(text):
    text = text.encode('utf-8').decode("ascii", "replace").replace(u"\ufffd", "_").replace("___", "'").replace("'s", " ").replace("``", " ").replace("''", " ").replace("_", " ").replace("'"," ").replace("`"," ")
    text = re.sub("[^0-9a-zA-Z !\"/:;<=>?.,!@#$%^&-_|()']+", " ", text)
    tokens = text.split(" ")
    result = ""
    for token in tokens:
        word = token.split(" ")[0]
        if word not in stopwords.words('english') and token not in punctuations and token not in hoax_stopwords:
            if len(word) > 0:
                if word.isupper() and dictionary.check(word.lower()):
                    new_token = lemmatizer.lemmatize(token.lower())
                    if new_token == token.lower():
                        new_token = lemmatizer.lemmatize(token.lower(), pos='v')
                    result += new_token + " "
                elif word.isupper():
                    result += token.title() + " "
                elif dictionary.check(word.lower()):
                    new_token = lemmatizer.lemmatize(token.lower())
                    if new_token == token.lower():
                        new_token = lemmatizer.lemmatize(token.lower(), pos='v')
                    result += new_token + " "
                else:
                    result += token + " "
            else:
                result += token + " "
    return result

def tokenize(text):
    tokens = word_tokenize(text)
    return tokens

def chunk_words(tokens):
    return ne_chunk(pos_tag(tokens))

def main():
    filename = sys.argv[1]
    with open(filename, 'r') as myfile:
        text = myfile.read().replace('\n', '')
    processed_text = preprocess(text)
    print("Preprocess: ", processed_text, "\n")
    print("Tokenize: ", tokenize(processed_text), "\n")

if __name__ == "__main__":
    main()