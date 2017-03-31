import logging
import searcher
import time
from urllib.request import urlopen 
import urllib
import re

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

start = time.time()

def ngrams(text, n):
	text = text.split(' ')
	output = {}
	for i in range(len(text)-n+1):
		g = ' '.join(text[i:i+n])
		output.setdefault(g, 0)
		output[g] += 1
	return output

def aa():
	data = (searcher.search_all("vaksin menyebabkan autisme"))
	article = data[0][2]

	print(data[0][0])

	content_clean = re.sub(r"[^\w]|_+", ' ', article.lower())
	content_clean = re.sub(r" +", ' ', content_clean)

	monogram = ngrams(content_clean, 1)
	digram = ngrams(content_clean, 2)
	trigram = ngrams(content_clean, 3)

	print(trigram["tidak ada bukti"])
	print(digram["ada bukti"])
	print(monogram["bukti"])

aa()

stop = time.time()
print("Time elapsed: " + str(stop-start))