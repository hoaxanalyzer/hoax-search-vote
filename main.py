import logging
import json
import re

from analyzer import Analyzer
from feedback import Feedback
from management import Management

from information_ex import generate_query

from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

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

		extracted_query = generate_query(query)
		extracted_query = re.sub(r"(null_)\d", "", extracted_query)
		extracted_query = extracted_query.strip()
		extracted_query = extracted_query.lower()
		analyzer = Analyzer(query, extracted_query, client)
		result = json.dumps(analyzer.do())
	except:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters"})
	return result

@application.route("/result", methods=['POST'])
def result():
	try:
		client = detect_client()
		quuid = request.json['id']
		
		analyzer = Analyzer("", "", client)
		result = json.dumps(analyzer.retrieve(quuid))
	except:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters"})
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
	except:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters"})
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
	except:
		result = json.dumps({"status": "Failed", "message": "Incorrect parameters"})
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

@application.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)