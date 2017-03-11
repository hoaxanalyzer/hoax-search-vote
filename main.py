import json

from analyzer import Analyzer

from flask import Flask
from flask import request

app = Flask(__name__)

# curl -i -H "Content-Type: application/json" -X POST -d '{"query":"Richard Harrison Death"}' http://localhost:5000/analyze

@app.route("/analyze", methods=['POST'])
def analyze():
    analyzer = Analyzer(request.json['query'])
    result = json.dumps(analyzer.do())
    return result

if __name__ == "__main__":
    app.run()