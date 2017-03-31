import requests
from lxml import html
import urllib.parse

def search(keywords, max_results=None):
	data =[]
	url = 'https://duckduckgo.com/html/?'
	params = {
		'q': keywords,
		's': '0',
	}

	yielded = 0

	req = urllib.request.Request(url + urllib.parse.urlencode(params)) 
	con = urllib.request.urlopen(req)
	doc = html.fromstring(str(con.read()))

	results = [a.get('href') for a in doc.cssselect('#links .links_main a.result__a')]
	title = [a.text_content() for a in doc.cssselect('#links .links_main a.result__a')]
	for result in results:
		if check_url(result):
			data.append({"url": sanitize_url(result), "title": title[yielded], "se": "duckduckgo"})
			yielded += 1
		if max_results and yielded >= max_results:
			return data
	return data

def sanitize_url(url):
	parsed_url = urllib.parse.urlparse(url)
	redirect_url = urllib.parse.parse_qs(parsed_url.query)['uddg']
	return redirect_url[0]

def check_url(url):
	exclusion = ["facebook.com", "youtube.com", "twitter.com", "blogspot.com", "pinterest.com", "amazon.com", "wordpress.com", "smule.com", "tumblr.com", "instagram.com", "scribd.com"]
	for blacklist in exclusion:
		if blacklist in url.lower():
			return False
	return True

def main():
	print(search('habibie meninggal'))

if __name__== "__main__":
	main()