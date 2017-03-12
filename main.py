import logging
import json

from analyzer import Analyzer

from flask import Flask
from flask import request, response
from flask_cors import CORS, cross_origin

application = Flask(__name__)
CORS(application)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# curl -i -H "Content-Type: applicationlication/json" -X POST -d '{"query":"Richard Harrison Death"}' http://localhost:5000/analyze

@application.route("/")
def index():
	return "Hoax Analyzer - Search and Vote API"

@application.route("/analyze", methods=['POST'])
def analyze():
    analyzer = Analyzer(request.json['query'])
    result = json.dumps(analyzer.do())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return result

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)