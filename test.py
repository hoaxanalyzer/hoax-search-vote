import logging
import json

from analyzer import Analyzer

queries = ["Free Cone Day from Daily Queen Holding"]

for query in queries:
	analyzer = Analyzer(query)
	result = analyzer.do()
	print(result["scores"])
	print(result["conclusion"])
