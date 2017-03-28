"""
PREPROCESS

Preprocess input text

"""

import nltk, sys
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')

print("Input user: ")
print(sys.argv[1:])

data = "Earlier this week, a story went viral about a man who claimed he purchased a yak while high on sleeping pills. But it turns out that the journalists who reported were the ones snoozing: The story is fake, according to the people who supposedly sold the yak."
sentences = data.split('.')
for i in range(0,len(sentences)):
	sentences[i] = sentences[i].lower()
	tokens = tokenizer.tokenize(sentences[i])
	processed_sentences = [word for word in tokens if word not in stopwords.words('english')]
	print("#", i)
	print("-> ", sentences[i])
	print("-> ", processed_sentences)