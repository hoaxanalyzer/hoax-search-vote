import logging
import json

from analyzer import Analyzer

queries = ["Dota 9 has officially released"]

for query in queries:
	analyzer = Analyzer(query)
	result = analyzer.do()
	print(result["scores"])
	print(result["conclusion"])
