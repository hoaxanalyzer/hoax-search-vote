"""
HOAX ANALYZER

Hoax Analyzer
Usage: -
Example: -

hoax_analyzer.py
TW (2017) 

"""

from extractor.feature_extractor import extract_tag
from extractor.feature_extractor import acceptible_tags as en_acceptible_tags
from extractor.preprocessor import preprocess as en_preprocess
from extractor.ms_text_analytics import detect_language
from subprocess import Popen, PIPE, STDOUT
from extractor.weka_classifier import classify_json_object, LANG_ID, LANG_ENG
import weka.core.jvm as jvm
import json
import re
import string
import sys


query_len = 14
lang_not_supported = "LANGUAGE NOT SUPPORTED"
id_acceptible_tags = ["nnp", "nn", "cdp"]

def is_query(text):
	text = text.encode('utf-8').decode("ascii", "replace").replace(u"\ufffd", "_").replace("___", "'").replace("'s", " ").replace("``", " ").replace("''", " ").replace("_", " ").replace("'"," ").replace("`"," ")
	text = re.sub('[^0-9a-zA-Z]+', ' ', text)
	if len(text.split(" ")) > 14:
		return False
	else:
		return True

def generate_query(lang, json_tag):
	query = []

	if lang == LANG_ID:
		acceptible_tags = id_acceptible_tags
	elif lang == LANG_ENG:
		acceptible_tags = en_acceptible_tags

	for tag in acceptible_tags:
		tag = tag.lower()
		pred = classify_json_object(lang, tag, json_tag)
		pred = int(pred[len(pred)-1:])
		for i in range(0, pred):
			token = json_tag[tag + str(i + 1)][tag + str(i + 1) + "_token"]
			if token not in query and token != "null" and token != "u" and token != "_url_" and token not in string.punctuation:
				query.append(token)

	return " ".join(query).replace("\"", " ")

def generate_json(text):
	tag_feature = extract_tag(text)
	json_tag = {}
	for tag in en_acceptible_tags:
		i = 1
		for val in tag_feature[tag]:
			json_tag[tag.lower() + str(i)] = {}
			json_tag[tag.lower() + str(i)][tag.lower() + str(i) + "_token"] = val.token
			json_tag[tag.lower() + str(i)][tag.lower() + str(i) + "_prob"] = val.prob
			json_tag[tag.lower() + str(i)][tag.lower() + str(i) + "_wcount"] = val.w_count
			json_tag[tag.lower() + str(i)][tag.lower() + str(i) + "_kpcount"] = val.kp_count
			json_tag[tag.lower() + str(i)][tag.lower() + str(i) + "_wseq"] = val.word_pos
			json_tag[tag.lower() + str(i)][tag.lower() + str(i) + "_sseq"] = val.sentence_pos
			i += 1
	
	return json_tag

def build_query(text):
	lang = detect_language(text)
	query = lang_not_supported

	# English Query
	if is_query(text) and lang == "English":
		query = en_preprocess(text)

	# Indonesian Query
	elif is_query(text) and lang == "Indonesian":
		p = Popen(['java', '-jar', 'lib/HoaxAnalyzer.jar', 'preprocess', text], stdout=PIPE, stderr=STDOUT)
		result = []
		for line in p.stdout:
			arr_token = line.decode("ascii", "replace").split(" ")
			for token in arr_token:
				if token not in result and token != '_url_' and len(token) > 0:
					result.append(token)
		query = " ".join(result)

	# English Text
	elif not is_query(text) and lang == "English":
		try:
			json_data = generate_json(text)
			query = generate_query(LANG_ENG, json_data)
		except Exception as e:
			print(traceback.format_exc())
		finally:
			None

	# Indonesian Text
	elif not is_query(text) and lang == "Indonesian":
		p = Popen(['java', '-jar', 'lib/HoaxAnalyzer.jar', 'extract', text], stdout=PIPE, stderr=STDOUT)
		result = ""
		for line in p.stdout:
			result += line.decode("ascii", "replace") + " "

		json_res = json.loads(result)
		
		try:
			query = generate_query(LANG_ID, json_res)
		except Exception as e:
			print(traceback.format_exc())
		finally:
			None

	# Not supported
	
	return query

def main():
	filename = sys.argv[1]
	with open(filename, 'r') as myfile:
		text = myfile.read().replace('\n', '')
		query = build_query(text)
		print(query)

if __name__ == "__main__":
	main()