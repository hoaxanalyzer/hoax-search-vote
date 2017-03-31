import requests
from lxml import html
import json
import urllib.parse

def search(keywords, max_results=None):
	exclusion = " -facebook.com -youtube.com -twitter.com -blogspot.com -pinterest.com -amazon.com -wordpress.com -smule.com -tumblr.com -instagram.com -scribd.com"

	data =[]
	url = 'https://bing.com/search?'
	params = {
		'q': keywords,
		'qs': 'n',
		'form': 'QBLH',
		'sp': '-1',
		'pq': keywords,
		'sc': '0-0',
	}

	yielded = 0

	req = urllib.request.Request(url + urllib.parse.urlencode(params)) 
	con = urllib.request.urlopen(req)
	doc = html.fromstring(str(con.read()))

	results = [a.get('href') for a in doc.cssselect('.b_algo h2 a')]
	title = [a.text_content() for a in doc.cssselect('.b_algo h2 a')]
	for result in results:
		if check_url(result):
			data.append({"url": (result), "title": title[yielded], "se": "bing"})
			yielded += 1
		if max_results and yielded >= max_results:
			return data
	return data

def api_search(keywords, max_results=None):
	data = []
	url = 'https://api.cognitive.microsoft.com/bing/v5.0/search?'
	params = {
		'q': keywords,
		'count': '10',
	}
	headers = {'Ocp-Apim-Subscription-Key': 'b1168966984e49eda59e502ee2b8fe94'}

	yielded = 0

	req = urllib.request.Request(url + urllib.parse.urlencode(params), headers=headers) 
	con = urllib.request.urlopen(req)

	results = json.loads(con.read())
	webs = results["webPages"]["value"]

	for web in webs:
		data.append({"url": sanitize_url(web["url"]), "title": web["name"], "se": "bing"})
		yielded += 1
		if max_results and yielded >= max_results:
			return data
	return data

def sanitize_url(url):
	parsed_url = urllib.parse.urlparse(url)
	redirect_url = urllib.parse.parse_qs(parsed_url.query)['r']
	return redirect_url[0]

def check_url(url):
	exclusion = ["facebook.com", "youtube.com", "twitter.com", "blogspot.com", "pinterest.com", "amazon.com", "wordpress.com", "smule.com"]
	for blacklist in exclusion:
		if blacklist in url.lower():
			return False
	return True
	
def main():
	print(search('habibie meninggal'))

if __name__== "__main__":
	main()