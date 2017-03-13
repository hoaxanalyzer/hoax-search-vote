import logging
import json

from analyzer import Analyzer

queries = ["Alan Rickman Death",
			"Death of Alan Rickman"]

for query in queries:
	analyzer = Analyzer(query)
	result = analyzer.do()
	print(result["scores"])
	print(result["conclusion"])
