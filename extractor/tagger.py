"""
TAGGER

Module for giving tags to text's tokens
Usage: python tagger.py [file]
Example: python tagger.py jackie.txt

"""

from extractor.preprocessor import preprocess, tokenize
from nltk import pos_tag
import sys

def tagging(text):
	return pos_tag(tokenize(preprocess(text)))

def main():
    filename = sys.argv[1]
    with open(filename, 'r') as myfile:
        text = myfile.read().replace('\n', '')
    print("Pos tag:", tagging(text))

if __name__ == "__main__":
    main()