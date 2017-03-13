import logging
import json

from analyzer import Analyzer

queries = ["dementor zambia"]

for query in queries:
	analyzer = Analyzer(query)
	result = analyzer.do()
	print(result["scores"])
	print(result["conclusion"])
