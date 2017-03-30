import logging
import searcher
import time
from urllib.request import urlopen 
import urllib

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

start = time.time()

def aa():
	print(searcher.search_all("habibie meninggal"))

aa()

stop = time.time()
print("Time elapsed: " + str(stop-start))