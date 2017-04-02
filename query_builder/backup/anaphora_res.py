"""
ANAPHORA RESOLUTION

Change personal pronouns to their real entity
Usage python anaphora-res.py test/jackie.txt

"""

from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import enchant
import nltk
import re
import requests
import string
import sys
import xml.etree.ElementTree as ET

BART_SERVER = 'http://localhost:8125'
d = enchant.Dict("en_US")

def bart_coref(text):
    response = requests.post(BART_SERVER + '/BARTDemo/ShowText/process/', data=text)
    return(response.content)

def extract_entity_names(t):
    entity_names = []
    
    if hasattr(t, 'node') and t.node:
        if t.node == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
                
    return entity_names

def anaphora_resolution(s):
    root = ET.fromstring(s)
    # tree = ET.parse('jackie.xml')
    # root = tree.getroot()

    coref_matrix = {}
    i = 0
    for coref in root.iter('coref'):
        cur_coref = int(string.replace(coref.attrib.get('set-id'), 'set_', ''))
        cur_array = []
        if cur_coref in coref_matrix:
            cur_array = coref_matrix.get(cur_coref)
        phrase = ''
        for child in coref:
            pos = child.attrib.get('pos')
            if pos is not None:
                if phrase == '':
                    phrase = child.text
                else:
                    phrase = phrase + ' ' + child.text
            else:
                for grandchild in child:
                    pos = child.attrib.get('pos')
                    if pos is not None:
                        if phrase == '':
                            phrase = child.text
                        else:
                            phrase = phrase + ' ' + child.text
        cur_array.append([pos, phrase])
        coref_matrix[cur_coref] = cur_array

    sp_change = ['he', 'she', 'it', 'i', 'you', 'we', 'they']
    pd_change = ['his', 'her', 'its', 'my', 'your', 'our', 'their']
    pp_change = ['hers', 'mine', 'yours', 'ours', 'theirs']
    pos_change = ['prp', 'prp$']
    pattern = r'^[A-Z][a-z]*(?:_[A-Z][a-z]*)*$'

    cur_nnp = {}
    for idx, coref in coref_matrix.iteritems():
        key = ''
        value = ''
        for coref_content in coref:
            content = ''.join(str(x) for x in coref_content[1])
            first_content = str(content).replace(',', ' ').split(' ')
            if (coref_content[0] == 'nnp' or d.check(first_content[0]) is False):
                cur_nnp[coref_content[1]] = coref_content[0]
                if len(value) < len(coref_content[1]):
                    key = coref_content[0]
                    value = coref_content[1]
            else:
                r = re.compile(".*" + coref_content[1] + "*.")
                matching = filter(r.match, cur_nnp.keys())
                if len(matching) > 0 and re.match(pattern, coref_content[1][0]):
                    key = cur_nnp[matching[0]]
                    value = matching[0]
        if value != '':
            for coref_xml in root.iter('coref'):
                cur_coref = int(string.replace(coref_xml.attrib.get('set-id'), 'set_', ''))
                if cur_coref == idx:
                    i = 0
                    for w in coref_xml.iter('w'):
                        if i==0 and (w.get('pos') in pos_change):
                            w.text = str(value)
                            w.set('pos', key)
                        i = i + 1
        with open('output.xml','w') as f: ## Write document to file
            f.write(ET.tostring(root))

    # result = ''.join(root.itertext()).replace('\n', ' ').replace('  ', ' ').replace(' ,', ',').replace(" 's", "'s")
    result = {}
    result['word'] = []
    result['pos'] = []

    for w in root.iter('w'):
            result['word'].append(w.text)
            result['pos'].append(w.get('pos'))
    
    return result

def parse(s):
    sentences = s.split(".")
    for idx, s in enumerate(sentences):
        if s[0] == ' ':
            sentences[idx] = sentences[idx][1:]
        if s[len(s)-1] == ' ':
            sentences[idx] = sentences[idx][:len(s)-1]
        if len(s) <= 1:
            sentences.pop(idx)
    return sentences

def extract_event():

    return

def get_tdm(word_list):
    punctuations = list(string.punctuation)
    
    # make a copy of the word_list
    filtered_word_list = {}
    filtered_word_list['word'] = word_list['word'][:]
    filtered_word_list['pos'] = word_list['pos'][:]

    # iterate over word_list, remove stopwords and punctuations
    i = 0
    for word in word_list['word']:
        if word in stopwords.words('english') or word in punctuations:
            del filtered_word_list['word'][i]
            del filtered_word_list['pos'][i]
        else:
            i+=1

    tf = Counter()
    tf_pos = {}
    for idx, word in enumerate(filtered_word_list['word']):
        tf[word] += 1
        tf_pos[word] = filtered_word_list['pos'][idx]

    sorted(tf, key=tf.get, reverse=True)
    tdm = {}
    tdm['word'] = tf
    tdm['pos'] = tf_pos
    return tdm

def get_most_common(word_list, n):
    most =  word_list.most_common(n)
    query = ''
    for word in most:
        query += str(word[0]) + ' '
    return query

def check_all_tdm(tdm):
    result = ''
    word_list = tdm['word'].most_common()
    for word in word_list:
        result += str(word[0]) + ' (' + tdm['pos'][str(word[0])] + ')\n'
    return result

def create_query(tdm, sentences, n):
    # find top 10 nnp in tdm, if not found, get the most nnp only
    top_nnp = []
    i = 0
    word_list = tdm['word'].most_common()
    pos_list = tdm['pos']
    for word in word_list:
        if pos_list[str(word[0])] == 'nnp':
            top_nnp.append(word)
        if i >= 10:
            break
        else:
            i += 1
    
    # if cannot found in big 10
    if len(top_nnp) == 0:
        for word in word_list:
            if pos_list[str(word[0])] == 'nnp':
                top_nnp.append(word)
                break

    # if still can't find nnp
    if len(top_nnp) == 0:
        return get_most_common(word_list, 7)

    print "top_nnp: ", top_nnp

    # eliminate nnp
    n_top_nnp = top_nnp[0][1]
    if len(top_nnp) > 1:
        remove = False
        i = 0
        for idx, nnp in enumerate(top_nnp[1:]):
            if remove:
                top_nnp.remove(nnp)
            elif n_top_nnp/2 > nnp[1]:
                remove = True
                top_nnp.remove(nnp)

    print "eliminated_nnp: ", top_nnp, "\m"

    # get all matching sentences with nnp
    matching = ''
    for nnp in top_nnp:
        matching += " ".join(extract_sentences_with_phrase(str(nnp[0]), sentences))
    print "matching:", matching, "\n"

    # count all word
    word_counter = Counter()
    for word in word_list:
        word_counter[word[0]] = matching.count(word[0])
        if i >= 10:
            break
        else:
            i += 1

    # sorting
    query = get_most_common(word_counter, n)
    return query

def extract_sentences_with_phrase(nnp, sentences):
    print nnp
    r = r"([^.]*?" + nnp + "[^.]*\.)"
    matching = re.findall(r, sentences)  
    return matching

def result_to_string(word_list):
    result = " ".join(word_list['word'][:])
    return result

def main():
    filename = sys.argv[1]
    with open(filename, 'r') as myfile:
        data = myfile.read().replace('\n', '')

    data = data.decode("ascii", "replace").replace(u"\ufffd", "_").replace("___", "'") 
        # .encode('utf-8').strip()

    coref_res = bart_coref(data)
    result = (anaphora_resolution(coref_res))

    tdm = get_tdm(result)
    string_result = result_to_string(result)

    # get all tdm result
    # print "tdm:\n"
    # print check_all_tdm(tdm)

    # build query for matching

    # get most common word in the article

    query_2 = create_query(tdm, string_result, 5)
    print "\n\n\n"
    print "========================================================="
    print "query_2: ", query_2
    query_1 = get_most_common(tdm['word'], 6)
    print "query_1: ", query_1



if __name__ == "__main__":
    main()