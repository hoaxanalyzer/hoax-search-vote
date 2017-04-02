"""
MICROSOFT'S COMPUTER VISION

Computer Vision
Usage: 
Example: 

"""

from query_builder.config import microsoft_computer_vision_account_key as account_key
import http.client, urllib.request, urllib.parse, urllib.error, base64
import base64
import json
import sys

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': account_key,
}

params = urllib.parse.urlencode({
    # Request parameters
    'language': 'unk',
    'detectOrientation ': 'true',
})
def detect_text(image):
    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/vision/v1.0/ocr?%s" % params, image, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        result = ""
        json_data = json.loads(data.decode("utf-8"))["regions"]
        for i in json_data:
            for j in i["lines"]:
                for k in j["words"]:
                    result += k["text"] + " "

        return result
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def main():
    filename = sys.argv[1]
    with open(filename, "rb") as imageFile:
        f = imageFile.read()
        b = bytearray(f)
    result = detect_text(b)
    print(result)
    # query = hoax_analyzer.build_query(result)
    # print("Query:", query)

if __name__ == "__main__":
    main()