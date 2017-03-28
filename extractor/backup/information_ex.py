from collections import Counter
from key_phrase import *
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import enchant
import json
import nltk
import operator
import pattern.en as en
import re
import string
import sys


# st = StanfordNERTagger('lib/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', 'lib/stanford-ner/stanford-ner.jar')
n_entities = 3
n_term_max = 6
n_term_min = 2
change_threshold = 1.0

dictionary = enchant.Dict("en_US")

with open('stopwords_en.txt', 'r') as myfile:
    hoax_stopwords = myfile.read()
    hoax_stopwords = word_tokenize(hoax_stopwords)

##################
### PREPROCESS ###
##################

def preprocess(text):
	text = text.decode("ascii", "replace").replace(u"\ufffd", "_").replace("___", "'").replace("'s", " ").replace("``", " ").replace("''", " ").replace("_", " ")
	tokens = text.split(" ")
	result = ""
	for token in tokens:
		word = token.split(" ")[0]
		if word.isupper():
			if dictionary.check(word.lower()):
				found = True
				result += token.lower() + " "
			else:
				found = False
				result += token.title() + " "
		else:
			result += token + " "
	return result

def tokenize(text):
	tokens = word_tokenize(text)
	return tokens


def chunk_words(tokens):
    return ne_chunk(pos_tag(tokens))

##########################
### ENTITY RECOGNITION ###
##########################

# def entity_recognition_stanford(text):
#     for sent in nltk.sent_tokenize(text):
#         tokens = nltk.tokenize.word_tokenize(sent)
#         tags = st.tag(tokens)
#         for tag in tags:
#             print tag

def entity_recognition(chunked):
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
            if type(i) == Tree:
                    current_chunk.append(" ".join([token for token, pos in i.leaves()]))
                    print i.leaves()
            elif current_chunk:
                    named_entity = " ".join(current_chunk)
                    if named_entity not in continuous_chunk:
                            continuous_chunk.append(named_entity)
                            current_chunk = []
            else:
                    continue

    # entities = []
    # for entity in continuous_chunk:
    # 	ent = ''
    # 	for idx, word in enumerate(entity.split(' ')):
    # 		if idx > 0:
    # 			if word == entity[idx-1]:
    # 				continue
    # 			elif len(ent) > 0:
    # 				ent += ' ' + word
    # 			else:
    # 				ent += word
    # 		else:
    # 			ent += word
    # 		if ent not in entities:
    # 			entities.append(ent)
    # return entities
    return continuous_chunk

def count_entity(entities, text, key_phrase_tokens):
	tf = {}
	sentences = text.split('.')
	# key_phrase_result = " ".join(key_phrase_tokens)
	for entity in entities:
		parsed_entity = entity.split(' ')
		first_appear = 0
		for pars in parsed_entity:
			n_match = 0
			for idx, sentence in enumerate(sentences):
				matching = re.findall('\w*' + pars.lower() +  '\w*', sentence.lower())
				if len(matching) > 0 and (first_appear == 0 or first_appear > (idx+1)):
					first_appear = idx + 1
					break
			matching = re.findall(r"([^.]*?" + pars.lower() + "[^.]*\.)", text.lower())
			n_match = len(matching)
			try:
				tf[entity]['count'] += n_match/(len(parsed_entity) * 1.0)
			except KeyError:
				tf[entity] = {}
				tf[entity]['count'] = n_match/(len(parsed_entity) * 1.0)

			# matching = re.findall('\w*' + pars.lower() +  '\w*', key_phrase_result.lower())
			# n_match = len(matching)
			# try:
			# 	tf[entity]['count'] += 2.0 * n_match/(len(parsed_entity) * 1.0)
			# except KeyError:
			# 	tf[entity] = {}
			# 	tf[entity]['count'] = 2.0 * n_match/(len(parsed_entity) * 1.0)
		tf[entity]['first_appear'] = first_appear
	return tf

def select_entity(entities):
	if len(entities) >= n_entities:
		sorted_ent = sorted(entities.items(), key=operator.itemgetter(1), reverse=True)
		return sorted_ent[:n_entities]
	else:
		i = 1
		while len(entities) < n_entities:
			entities["null_" + str(i)] = {}
			entities["null_" + str(i)]['count'] = 0
			entities["null_" + str(i)]['first_appear'] = 0
			i += 1
		sorted_ent = sorted(entities.items(), key=operator.itemgetter(1), reverse=True)
		return sorted_ent

################################
### EXTRACT MOST COMMON WORD ###
################################

def term_frequencies(tokens, selected_entities, key_phrase_tokens):
	# lmtzr = WordNetLemmatizer()
	# stemmer = SnowballStemmer("english")
	punctuations = list(string.punctuation)
	entities = ""
	for entity in selected_entities:
		entities += str(entity[0]) + ' '
	entities = tokenize(entities.lower())

	tf = {}
	i = 0
	len_token = len(tokens)
	for token in tokens:
		# token = stemmer.stem(token)
		# token = lmtzr.lemmatize(token)
		if dictionary.check(token.lower()):
			token = en.lemma(token)
		if token not in stopwords.words('english') and token not in punctuations and token not in hoax_stopwords and len(token) > 1 and token != "''" and token != "``":
			# print token, 1.0 * (len_token - i) / (len_token * 1.0)
			if i == 0:
				try:
					tf[token] += 2.0 * (len_token - i) / (len_token * 1.0)
				except KeyError:
					tf[token] = 2.0 * (len_token - i) / (len_token * 1.0)
			else:
				try:
					tf[token] += 1.0 * (len_token - i) / (len_token * 1.0)
				except KeyError:
					tf[token] = 1.0 * (len_token - i) / (len_token * 1.0)
		elif token == ".":
			i += 1

	for token in key_phrase_tokens:
		# token = stemmer.stem(token)
		# token = lmtzr.lemmatize(token)
		if dictionary.check(token.lower()):
			token = en.lemma(token)
		if token not in stopwords.words('english') and token not in punctuations and token not in hoax_stopwords and len(token) > 1 and token != "''" and token != "``":
			# print token, 1.0 * (len_token - i) / (len_token * 1.0)
			if i == 0:
				try:
					tf[token] += 2.0 * (len_token - i) / (len_token * 1.0)
				except KeyError:
					tf[token] = 2.0 * (len_token - i) / (len_token * 1.0)
			else:
				try:
					tf[token] += 1.0 * (len_token - i) / (len_token * 1.0)
				except KeyError:
					tf[token] = 1.0 * (len_token - i) / (len_token * 1.0)
		elif token == ".":
			i += 1

	tf = sorted(tf.items(), key=operator.itemgetter(1), reverse=True)
	return tf

def select_words(tf):
	sliced_tf = []
	for term in tf:
		if len(sliced_tf) < n_term_max:
			sliced_tf.append(term)
		else:
			break
	return sliced_tf

def build_query(selected_entities, selected_words):
	query = ''
	for entity in selected_entities:
		query += str(entity[0]) + ' '
		break

	prev_count = 0
	i = 1
	found = False
	for word in selected_words:
		term = str(word[0])
		cur_count = word[1]
		# if prev_count != 0:
		# 	if (prev_count - cur_count) > change_threshold and i > n_term_min:
		# 		# query += " [[ "
		# 		# found = True
		# 		break
		if term.lower() not in query.lower().split(' '):
			query += term + ' '
		prev_count = cur_count
		i += 1
	# if found:
	# 	query += " ]]"
	# else:
	# 	query += " [[ ]]"
	return query

def generate_query(text):
    # filename = sys.argv[1]
    # with open(filename, 'r') as myfile:
    #     text = myfile.read().replace('\n', '')
    text = preprocess(text)
    
    json_data = {}
    json_doc = []
    json_text = {}
    json_text["id"] = "1"
    json_text["text"] = text
    json_doc.append(json_text)
    json_data["documents"] = json_doc
    json_data = json.dumps(json_data)
    key_phrase_analysis = detect_key_phrases(json_data)
    key_phrase_result = ""
    for key in key_phrase_analysis:
        key_phrase_result += " ".join(map(str,key['keyPhrases']))
    key_phrase_tokens = tokenize(key_phrase_result)

    tokens = tokenize(text)
    ne_chunk = chunk_words(tokens)
    ent = entity_recognition(ne_chunk)
    ent_res = count_entity(ent, " ".join(tokens), key_phrase_tokens)
    print ent_res
    selected_entities = select_entity(ent_res)

    tf = term_frequencies(tokens, selected_entities, key_phrase_tokens)
    selected_words = select_words(tf)

    query = build_query(selected_entities, selected_words)
    return query

def test():
    filename = sys.argv[1]
    with open(filename, 'r') as myfile:
        text = myfile.read().replace('\n', '')
    print generate_query(text)
	# text = preprocess(text)    
	# print text, "\n\n"

	# print "# DETECT KEY PHRASE #"
	# json_data = {}
	# json_doc = []
	# json_text = {}
	# json_text["id"] = "1"
	# json_text["text"] = text
	# json_doc.append(json_text)
	# json_data["documents"] = json_doc
	# json_data = json.dumps(json_data)
	# key_phrase_analysis = detect_key_phrases(json_data)
	# key_phrase_result = ""
	# for key in key_phrase_analysis:
	# 	key_phrase_result += " ".join(map(str,key['keyPhrases']))
	# key_phrase_tokens = tokenize(key_phrase_result)
	# print key_phrase_tokens
	# print "\n\n"


	# print "# ENTITY RECOGNITION #"
 #    tokens = tokenize(text)
 #    ne_chunk = chunk_words(tokens)
 #    ent = entity_recognition(ne_chunk)
 #    print "All entity:", ent
 #    ent_res = count_entity(ent, " ".join(tokens), key_phrase_tokens)
 #    selected_entities = select_entity(ent_res)
 #    print "Selected entity:", selected_entities
 #    print "\n\n"

 #    print "# TERM FREQUENCY #"
 #    tf = term_frequencies(tokens, selected_entities, key_phrase_tokens)
 #    print tf
 #    selected_words = select_words(tf)
 #    print selected_words
 #    print "\n\n"

 #    print "# QUERY RESULT #"
 #    query = build_query(selected_entities, selected_words)
 #    print query

############
### MAIN ###
############

def main():
	test()


if __name__ == "__main__":
    main()