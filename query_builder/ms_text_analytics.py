"""
MICROSOFT'S TEXT ANALYTCIS

Simple program that demonstrates how to invoke Azure ML Text Analytics API: key phrases, language and sentiment detection.
Usage: 
Example: 

"""

from query_builder.config import microsoft_text_analytics_account_key as account_key
import base64
import codecs
import json
import sys
import urllib.request, urllib.parse, urllib.error

# Language constant
LANG_ID = "id"
LANG_EN = "en"
LANG_UNKNOWN = "unknown"

# Azure portal URL.
base_url = 'https://westus.api.cognitive.microsoft.com/'

headers = {'Content-Type':'application/json', 'Ocp-Apim-Subscription-Key':account_key, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}
            
# input_texts = '{"documents":[{"id":"1","text":"Ad sales boost Time Warner profit Quarterly profits at US media giant TimeWarner jumped 76% to $1.13bn (600m) for the three months to December, from $639m year-earlier. The firm, which is now one of the biggest investors in Google, benefited from sales of high-speed internet connections and higher advert sales. TimeWarner said fourth quarter sales rose 2% to $11.1bn from $10.9bn. Its profits were buoyed by one-off gains which offset a profit dip at Warner Bros, and less users for AOL. Time Warner said on Friday that it now owns 8% of search-engine Google. But its own internet business, AOL, had has mixed fortunes. It lost 464,000 subscribers in the fourth quarter profits were lower than in the preceding three quarters. However, the company said AOL\'s underlying profit before exceptional items rose 8% on the back of stronger internet advertising revenues. It hopes to increase subscribers by offering the online service free to TimeWarner internet customers and will try to sign up AOL\'s existing customers for high-speed broadband. TimeWarner also has to restate 2000 and 2003 results following a probe by the US Securities Exchange Commission (SEC), which is close to concluding. Time Warner\'s fourth quarter profits were slightly better than analysts\' expectations. But its film division saw profits slump 27% to $284m, helped by box-office flops Alexander and Catwoman, a sharp contrast to year-earlier, when the third and final film in the Lord of the Rings trilogy boosted result"}]}'

num_detect_langs = 1

def text_to_post_data(text):
    json_data = {}
    json_doc = []
    json_text = {}
    json_text["id"] = "1"
    json_text["text"] = text
    json_doc.append(json_text)
    json_data["documents"] = json_doc
    data = json.dumps(json_data)
    return data.encode("utf-8")

# Detect key phrases.
def detect_key_phrases(input_texts):
    try:
        data = text_to_post_data(input_texts)
        batch_keyphrase_url = base_url + 'text/analytics/v2.0/keyPhrases'
        req = urllib.request.Request(batch_keyphrase_url, data, headers) 
        response = urllib.request.urlopen(req)
        result = response.read()
        obj = json.loads(result.decode("utf-8"))
        return obj['documents']
    except ConnectionError as e:
        return []

# Detect language.
def detect_language(input_texts):
    data = text_to_post_data(input_texts)
    language_detection_url = base_url + 'text/analytics/v2.0/languages' + ('?numberOfLanguagesToDetect=' + num_detect_langs if num_detect_langs > 1 else '')
    req = urllib.request.Request(language_detection_url, data, headers)
    try:
        response = urllib.request.urlopen(req)
        result = response.read().decode("utf-8")
        obj = json.loads(result)
        lang = ""
        for language in obj['documents']:
            lang = (language['detectedLanguages'][0]['name'])
        if lang == "Indonesian":
            return LANG_ID
        elif lang == "English":
            return LANG_EN
        else:
            return LANG_UNKNOWN
    except ConnectionError as e:
        return LANG_UNKNOWN

# Detect sentiment.
def detect_sentiment(input_texts):
    data = text_to_post_data(input_texts)
    batch_sentiment_url = base_url + 'text/analytics/v2.0/sentiment'
    req = urllib.request.Request(batch_sentiment_url, data, headers) 
    response = urllib.request.urlopen(req)
    result = response.read()
    obj = json.loads(result)
    for sentiment_analysis in obj['documents']:
        print('Sentiment ' + str(sentiment_analysis['id']) + ' score: ' + str(sentiment_analysis['score']))
        