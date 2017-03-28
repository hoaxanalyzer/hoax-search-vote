from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import sys

LANGUAGE = "english"
SENTENCES_COUNT = 3

def main():
    filename = sys.argv[1]
    # or for plain text files
    fp = open(filename)
    content = fp.read()
    fp.close()

    fp2 = open(filename, "w")
    result = content.decode("ascii", "replace").replace(u"\ufffd", " ")
    fp2.write(result)
    fp2.close()  

    parser = PlaintextParser.from_file(filename, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        print(sentence)

if __name__ == "__main__":
    main()