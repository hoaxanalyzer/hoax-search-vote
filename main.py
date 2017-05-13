from __future__ import unicode_literals

import os
import sys
import logging
import json
import re
import itertools
import time
import urllib.request

import requests

from core import Analyzer
from core import Feedback
from core import Management

from flask import Flask, Response
from flask import request, abort
from flask_cors import CORS, cross_origin

import multiprocessing as mp
from multiprocessing import Queue

from linebot import (
	LineBotApi, WebhookParser
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage,
	SourceUser, SourceGroup, SourceRoom,
)

import searcher
import config

channel_secret = config.line_channel_secret
channel_access_token = config.line_channel_access_token
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

application = Flask(__name__)
CORS(application)

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def detect_client():
	client = {}
	client['ip'] = '0.0.0.0'
	client['browser'] = 'Undetected'

	try:
		if 'ip' in request.json:
			client['ip'] = request.json['ip']
		if 'browser' in request.json:
			client['browser'] = request.json['browser']
	except:
		logging.info("Client data not found")

	return client

def create_text_query(query):
	logging.info("Getting query: " + query)

	try:
		query = query.replace('\n', ' ').replace('\r', ' ')
		query = ''.join([i if ord(i) < 128 else ' ' for i in query])
		query = (query.encode('utf-8')).decode('utf-8')
		payload = json.dumps({'text': query}).encode('utf8')
		req = urllib.request.Request("http://hsecondary.lelah.ga/extract/text", payload, {'Content-Type': 'application/json'}) 
		con = urllib.request.urlopen(req, timeout=20)
		result = json.loads(con.read().decode('utf-8'))

		extracted_query = result["query"]
		extracted_query = extracted_query.strip()
		extracted_query = extracted_query.lower()
	except Exception as e:
		logging.info("Getting query excp: " + str(e))
		extracted_query = query
		lang = "en"
		qtype = "unknown"

	try:
		query_neg = result["is_negation"]
		lang = result["language"]
		qtype = result["type"]
	except:
		query_neg = False
		lang = "en"
		qtype = "text"

	logging.info("Extracted query: " + extracted_query)
	return (extracted_query, query_neg, lang, qtype)

def create_image_query(image):
	logging.info("Getting image")
	extracted_query = ""
	text = "error"
	try:
		req = urllib.request.Request("http://hsecondary.lelah.ga/extract/image", image.read()) 
		con = urllib.request.urlopen(req, timeout=20)
		result = json.loads(con.read().decode('utf-8'))

		extracted_query = result["query"]
		text = result["text"]
		lang = result["language"]
		qtype = result["type"]
	except Exception as e:
		logging.info("Getting image excp: " + str(e))
		extracted_query = ""
		text = "error"
		lang = "unk"
		qtype = "image"

	return (extracted_query, text, lang, qtype)

def get_factcheck(query, queue):
	logging.info("Factcheck query: " + query)
	try:
		query = query.replace('\n', ' ').replace('\r', ' ')
		query = ''.join([i if ord(i) < 128 else ' ' for i in query])
		query = (query.encode('utf-8')).decode('utf-8')
		payload = json.dumps({'text': query}).encode('utf8')
		req = urllib.request.Request("http://hfc.lelah.ga/check", payload, {'Content-Type': 'application/json'}) 
		con = urllib.request.urlopen(req, timeout=5)
		#result = json.loads(con.read().decode('utf-8'))
		result = con.read().decode('utf-8')
	except:
		result = "{\"code\":3, \"details\": \"no result\", \"is_negate\": false}"
	logging.info("Factcheck result: " + str(result))
	queue.put(result)

@application.route("/")
def index():
	return "Hoax Analyzer - Search and Vote API"

@application.route("/analyze", methods=['POST'])
def analyze():
	#try:
	client = detect_client()
	query = request.json['query']
	query = query.replace('\n', ' ')

	logging.info("Starting Extract Query " + query[:25])
	
	the_queue = Queue()
	thread_fc = mp.Process(target=get_factcheck, args=(query, the_queue,))
	thread_fc.start()

	extracted_query, qneg, lang, qtype = create_text_query(query)
	analyzer = Analyzer(query, extracted_query, client, qneg, lang, qtype)
	result = analyzer.do()

	thread_fc.join
	factcheck = json.loads(the_queue.get())
	result["factcheck"] = factcheck

	analyzer.recalculate_factcheck(factcheck)
	result["scores"] = analyzer.conclusion
	result["conclusion"] = Analyzer.target[analyzer.ridx]

	result = json.dumps(result)

	logging.info("Finish Analyze " + query[:25])
	#except Exception as e:
	#	result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/analyze/image", methods=['POST'])
def analyze_image():
	try:
		#client = detect_client()
		print(request.files)

		if 'image' not in request.files:
			return json.dumps({"status": "Failed", "message": "No image file found", "details": "No image file uploaded"})

		file = request.files['image']
		if file.filename == '':
			return json.dumps({"status": "Failed", "message": "No image file found", "details": "No filename"})

		if file:
			extracted_query, text, lang, qtype = create_image_query(file)

			if len(extracted_query) <= 2:
				return json.dumps({"status": "Failed", "message": "No query extracted", "details": "No query extracted"})
			
			analyzer = Analyzer(text, extracted_query, None, lang, qtype)
			result = json.dumps(analyzer.do())
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/result", methods=['POST'])
def result():
	#try:
	client = detect_client()
	quuid = request.json['id']

	analyzer = Analyzer("", "", client)
	full_query = analyzer.init_retrieve(quuid)

	if not full_query == None:
		the_queue = Queue()
		thread_fc = mp.Process(target=get_factcheck, args=(full_query, the_queue,))
		thread_fc.start()
	
	result = analyzer.retrieve(quuid)

	if not full_query == None:
		thread_fc.join
		factcheck = json.loads(the_queue.get())
		result["factcheck"] = factcheck
		analyzer.recalculate_factcheck(factcheck)
		result["scores"] = analyzer.conclusion
		result["conclusion"] = Analyzer.target[analyzer.ridx]
	result = json.dumps(result)

	#except Exception as e:
	#	result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/feedback/result", methods=['POST'])
def feedback_result():
	try:
		client = detect_client()

		is_know = request.json['isKnow']
		label = request.json['label']
		reason = request.json['reason']
		quuid = request.json['id']
		
		feedback = Feedback(client)
		result = json.dumps(feedback.result(is_know, label, reason, quuid))
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/feedback/reference", methods=['POST'])
def feedback_reference():
	try:
		client = detect_client()

		is_related = request.json['isRelated']
		label = request.json['label']
		reason = request.json['reason']
		auuid = request.json['id']
		
		feedback = Feedback(client)
		result = json.dumps(feedback.reference(is_related, label, reason, auuid	))
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/references/<qhash>", methods=['GET'])
def get_references(qhash):
	try:
		management = Management()
		result = json.dumps(management.get_references(qhash))
	except:
		result = json.dumps({"status": "Failed", "message": "Request error"})
	return result

@application.route("/logs/query", methods=['GET'])
def get_log_query():
	try:
		management = Management()
		result = json.dumps(management.get_query_log())
	except:
		result = json.dumps({"status": "Failed", "message": "Request error"})
	return result

@application.route("/callback", methods=['POST'])
def callback():
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)

	# parse webhook body
	try:
		events = parser.parse(body, signature)
	except InvalidSignatureError:
		abort(400)

	# if event is MessageEvent and message is TextMessage, then echo text
	for event in events:
		if not isinstance(event, MessageEvent):
			continue
		if not isinstance(event.message, TextMessage):
			continue

		if isinstance(event.source, SourceUser):
			profile = line_bot_api.get_profile(event.source.user_id)
			profile_id = profile.user_id

			client = {}
			client['ip'] = profile_id[:15]
			client['browser'] = 'LINE BOT'

			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text="Please wait, we are analyzing your input, this shouldn't take more than 1 minute ^_^")
			)

			query = event.message.text

			payload = json.dumps({'query': query}).encode('utf8')
			req = urllib.request.Request("https://hprimary.lelah.ga/analyze", payload, {'Content-Type': 'application/json'}) 
			con = urllib.request.urlopen(req, timeout=20)
			result = json.loads(con.read().decode('utf-8'))

			text_result = "The result is [" + (result["conclusion"]).upper() + "]"
			check_out = "For further information, please check at http://hoaxanalyzer.com/results/" + result["id"]

			line_bot_api.push_message(
				profile_id,
				TextSendMessage(text=text_result)
			)
			line_bot_api.push_message(
				profile_id,
				TextSendMessage(text=check_out)
			)

	return 'OK'

@application.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response

if __name__ == "__main__":
	application.run(host="0.0.0.0", port=8090)