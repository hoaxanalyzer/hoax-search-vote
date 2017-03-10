from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import os
import hashlib
import subprocess
import sys
import nltk
import tfidf

# SUMY - Library
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Get the first 5 hits for "google 1.9.1 python" in Google US
from google import search, get_page

reload(sys)  
sys.setdefaultencoding('utf8')

LANGUAGE = "english"
SENTENCES_COUNT = 10

# TEST_SENTENCE = 'flat earth'
# TEST_QUERY = TEST_SENTENCE + ' hoax'
TEST_THRESHOLD_HOAX = 0.0255
TEST_THRESHOLD_FACT = 0.03
TEST_THRESHOLD_IMPORTANT = 0.005

BLACKLIST = ['youtube.com']


# folder_name = hashlib.sha256(TEST_QUERY).hexdigest()
# directory = 'data/' + folder_name

# if not os.path.exists(directory):
# 	os.makedirs(directory)

# 	counter = 0
# 	for url in search(TEST_QUERY, tld='com', lang='en', stop=10):
# 		file_name = directory + '/' + str(counter) + '.html'
		
# 		print("Saving: " + file_name)

#  		table = tfidf.tfidf()
# 		file_target = open(file_name + '.html', 'w')
#   	file_target.write(get_page(url))
#   	file_target.close()

#   	p = subprocess.Popen(["./Imagine_Hoax", file_name], stdout=subprocess.PIPE)
#   	p.wait()
#   	print(p.communicate()[0])

# 		#table.addDocument("the_document", words)
#  		#print(table.similarities(TEST_QUERY.split()))

#   	counter += 1

def isContain(url):
	for u in BLACKLIST:
		return u in url

if __name__ == "__main__":
	TEST_SENTENCE = sys.argv[1]
	TEST_QUERY = TEST_SENTENCE + ' hoax'

	print("Search for " + TEST_QUERY)

	hoax = 0;
	fact = 0;
	unknown = 0;

	for url in search(TEST_QUERY, tld='com', lang='en', stop=10):		
		table = tfidf.tfidf()

		print("================================================")
		print("url: " + url)

		try:
			if not isContain(url):
				parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
				stemmer = Stemmer(LANGUAGE)

				summarizer = Summarizer(stemmer)
				summarizer.stop_words = get_stop_words(LANGUAGE)

				count = 0
				try:
					for sentence in summarizer(parser.document, SENTENCES_COUNT):
						# print(">> " + str(sentence))
						words = []
						for word in str(sentence).split():
							words.append(word)
						count += 1
						table.addDocument("sen" + str(count), words)
				except:
					print('Error', sys.exc_info()[0])

				# print(table.similarities(TEST_QUERY.split()))
				hoaxw = []
				for w in TEST_QUERY.split():
					hoaxw.append(w)
				hoaxw.append("hoax")
				hoaxw.append("lie")
				hoaxw.append("fake")

				ct = 1
				cs = 0
				for t in table.similarities(hoaxw):
					cs += t[1]
					ct += 1

				if (cs/ct > TEST_THRESHOLD_IMPORTANT):
					if (cs/ct > TEST_THRESHOLD_HOAX):
						hoax += 1
					else:
						fact += 1
				else:
					unknown += 1

				print("HOAX PROB: " + str(cs/ct))

				factw = []
				for w in TEST_QUERY.split():
					factw.append(w)
				factw.append("confirmed")
				factw.append("fact")
				factw.append("real")
				factw.append("debunk")
				factw.append("debunked")

				ct = 1
				cs = 0
				for t in table.similarities(factw):
					cs += t[1]
					ct += 1

				if (cs/ct > TEST_THRESHOLD_IMPORTANT):
					if (cs/ct > TEST_THRESHOLD_FACT):
						fact += 1
				else:
					unknown += 1

				print("FACT PROB: " + str(cs/ct))

			else:
				print('BLACKLIST')
		except:
			print('Error', sys.exc_info()[0])

	print("HOAX: " + str(hoax) + " | FACT: " + str(fact) + " | UNKNOWN: " + str(unknown))

	if (hoax > fact):
		print(TEST_SENTENCE + " is HOAX")
	elif (hoax < fact):
		print(TEST_SENTENCE + " is FACT")
	else:
		print(TEST_SENTENCE + " is UNKNOWN")
