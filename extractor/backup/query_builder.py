"""
QUERY BUILDER

Create query from text
Usage: python query_builder.py [dir] [output file]
Example: python query_builder.py test result_x.csv

"""

from information_ex import *
import csv, os

def query_builder(text):
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
    selected_entities = select_entity(ent_res)

    tf = term_frequencies(tokens, selected_entities, key_phrase_tokens)
    selected_words = select_words(tf)

    query = build_query(selected_entities, selected_words)
    return query

def query_builder(text):
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
    selected_entities = []

    tf = term_frequencies(tokens, selected_entities, key_phrase_tokens)
    selected_words = select_words(tf)

    query = build_query(selected_entities, selected_words)
    return query



def main():
    if (len(sys.argv) >= 3):
        directory = sys.argv[1]
        file_output = sys.argv[2]

        csvfile = open(file_output, 'wb')
        # result = ["filename", "ent_name_1", "ent_occ_1", "ent_first_1", "ent_name_2", "ent_occ_2", "ent_first_2", "ent_name_3", "ent_occ_3", "ent_first_3", "word_count", "ent_res"]
        # wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        # wr.writerow(result)

        for subdir, dirs, files in os.walk(directory):
            for filename in files:
                with open(directory + "/" + filename, 'r') as myfile:
                    text = myfile.read().replace('\n', '')
                    myfile.close()

                query = query_builder(text)
                result = [filename, query]
                # # result = [filename, text, query]
                # tokens = tokenize(preprocess(text))
                # ne_chunk = chunk_words(tokens)
                # ent = entity_recognition(ne_chunk)
                # ent_res = count_entity(ent, " ".join(tokens))
                # selected_entities = select_entity(ent_res)

                # result = [filename]
                # for entity in selected_entities:
                #     result.append(entity[0])
                #     result.append(entity[1]['count'] * 1.0)
                #     result.append(entity[1]['first_appear'] * 1.0)
                # result.append(len(tokens))

                wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                wr.writerow(result)
                print filename, "done!"
    else:
        filename = sys.argv[1]
        with open(filename, 'r') as myfile:
            text = myfile.read().replace('\n', '')
            myfile.close()

        query = query_builder(text)
        print query

if __name__ == "__main__":
    main()