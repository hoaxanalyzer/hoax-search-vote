import logging
import json
import time
import sys

from core import Analyzer
from article import Article

if __name__ == "__main__":
	queryhash = sys.argv[1]
	analyzer = Analyzer(query, query)
	result = analyzer.do()