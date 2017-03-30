import requests
from lxml import html
import json
import urllib.parse

def search(keywords, max_results=None):
	url = 'https://api.cognitive.microsoft.com/bing/v5.0/search?'
	params = {
		'q': keywords,
		'count': '10',
	}
	headers = {'Ocp-Apim-Subscription-Key': 'b1168966984e49eda59e502ee2b8fe94'}

	yielded = 0
	while True:
		res = requests.get(url + urllib.parse.urlencode(params), headers=headers)
		results = json.loads(res.text)
		webs = results["webPages"]["value"]

		for web in webs:
			yield {"url": web["displayUrl"], "title": web["name"], "se": "bing"}
			yielded += 1
			if max_results and yielded >= max_results:
				return