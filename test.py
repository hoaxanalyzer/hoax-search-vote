import logging
import json

from analyzer import Analyzer

queries = ["free cone day queen daily hold hoax"]

for query in queries:
	analyzer = Analyzer(query)
	result = analyzer.do()
	print(result["scores"])
	print(result["conclusion"])
