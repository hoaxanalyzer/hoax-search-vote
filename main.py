from __future__ import unicode_literals

import os
import sys
import logging
import json
import re
import itertools
import time

from core import Analyzer
from core import Feedback
from core import Management

from flask import Flask, Response
from flask import request, abort
from flask_cors import CORS, cross_origin

from linebot import (
	LineBotApi, WebhookParser
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage,
)

import config

channel_secret = config.line_channel_secret
channel_access_token = config.line_channel_access_token
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

application = Flask(__name__)
CORS(application)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# curl -i -H "Content-Type: application/json" -X POST -d '{"query":"Richard Harrison Death"}' http://localhost:5000/analyze

def detect_client():
	client = {}
	client['ip'] = '0.0.0.0'
	client['browser'] = 'Undetected'

	if 'ip' in request.json:
		client['ip'] = request.json['ip']
	if 'browser' in request.json:
		client['browser'] = request.json['browser']

	return client

@application.route("/")
def index():
	return "Hoax Analyzer - Search and Vote API"

@application.route("/analyze", methods=['POST'])
def analyze():
	try:
		client = detect_client()
		query = request.json['query']
		query = query.replace('\n', '')
		
		logging.info("Getting query: " + query)

		extracted_query = query
		#extracted_query = generate_query(query)
		#extracted_query = re.sub(r"(null_)\d", "", extracted_query)
		extracted_query = extracted_query.strip()
		extracted_query = extracted_query.lower()
		analyzer = Analyzer(query, extracted_query, client)
		result = json.dumps(analyzer.do())
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/analyze/stream", methods=['POST'])
def analyze_stream():
	try:
		if request.headers.get('accept') == 'text/event-stream':
			client = detect_client()
			query = request.json['query']
			query = query.replace('\n', '')
			
			logging.info("Getting query: " + query)

			extracted_query = query
			#extracted_query = generate_query(query)
			#extracted_query = re.sub(r"(null_)\d", "", extracted_query)
			extracted_query = extracted_query.strip()
			extracted_query = extracted_query.lower()
			analyzer = Analyzer(query, extracted_query, client)

			return Response(analyzer.do_stream(), content_type='text/event-stream')
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
	return result

@application.route("/result", methods=['POST'])
def result():
	try:
		client = detect_client()
		quuid = request.json['id']
		
		analyzer = Analyzer("", "", client)
		result = json.dumps(analyzer.retrieve(quuid))
	except Exception as e:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters", "details": str(e)})
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
			client = {}
			client['ip'] = '0.0.0.0'
			client['browser'] = 'LINE BOT'

			query = event.message.text
			analyzer = Analyzer(query, query, client)
			result = analyzer.do()

			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text=result["conclusion"])
			)

	return 'OK'

@application.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response

if __name__ == "__main__":
	application.run(host="0.0.0.0", port=8080)