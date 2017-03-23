import logging
import json
import re

from analyzer import Analyzer
from information_ex import generate_query

from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

application = Flask(__name__)
CORS(application)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# curl -i -H "Content-Type: application/json" -X POST -d '{"query":"Richard Harrison Death"}' http://localhost:5000/analyze

@application.route("/")
def index():
	return "Hoax Analyzer - Search and Vote API"

@application.route("/analyze", methods=['POST'])
def analyze():
	client = {}
	client['ip'] = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	client['browser'] = request.headers.get('User-Agent')

	query = request.json['query']
	query = query.replace('\n', '')
	
	logging.info("Getting query: " + query)

	extracted_query = generate_query(query)
	extracted_query = re.sub(r"(null_)\d", "", extracted_query)
	extracted_query = extracted_query.strip()
	extracted_query = extracted_query.lower()
	analyzer = Analyzer(query, extracted_query, client)
	result = json.dumps(analyzer.do())
	return result

@application.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)