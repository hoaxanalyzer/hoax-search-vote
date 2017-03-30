import requests
from lxml import html

def search(keywords, max_results=None):
	url = 'https://duckduckgo.com/html/'
	params = {
		'q': keywords,
		's': '0',
	}

	yielded = 0
	while True:
		res = requests.post(url, data=params)
		doc = html.fromstring(res.text)

		results = [a.get('href') for a in doc.cssselect('#links .links_main a.result__a')]
		title = [a.text_content() for a in doc.cssselect('#links .links_main a.result__a')]
		for result in results:
			yield {"url": result, "title": title[yielded], "se": "duckduckgo"}
			yielded += 1
			if max_results and yielded >= max_results:
				return
		try:
			form = doc.cssselect('.results_links_more form')[-1]
		except IndexError:
			return
		params = dict(form.fields)