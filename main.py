import logging
import json

from analyzer import Analyzer

from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# curl -i -H "Content-Type: application/json" -X POST -d '{"query":"Richard Harrison Death"}' http://localhost:5000/analyze

@app.route("/analyze", methods=['POST'])
def analyze():
    analyzer = Analyzer(request.json['query'])
    result = json.dumps(analyzer.do())
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)