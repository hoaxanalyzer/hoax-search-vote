"""
WORD FEATURE

Class for word feature for English

word_feature.py
TW (2017)

"""

class WordFeature:
    null = "null"

    def __init__(self, token, word_pos, sentence_pos, n):
        self.token = token
        self.word_pos = word_pos
        self.sentence_pos = sentence_pos
        self.kp_count = 0
        if token == self.null:
            self.prob = 0
            self.w_count = 0
        else:
            self.prob = n
            self.w_count = 1


    def increment_count(self, n):
        self.prob += n
        self.w_count += 1

    def increment_key_phrase(self):
        self.kp_count += 1
        self.prob += 1