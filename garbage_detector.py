# Detect whether a word does not look like an English word, e.g. mwoeirp
# These are called 'garbage' words, as opposed to 'nonsense' words that look like real words, e.g. 'flomker'

# Notes / Considerations:
# 1) Length of string
#    - Currently, the probability is normalized by the length of the string. This is
#      so we can compare strings of different lengths. However, this means that
#      prob('xx') = prob('xxxxxx'). You could argue that the latter should be more
#      unlikely, or more of a garbage word.
#    - One proposal to address the above problem: Have many 'good' and garbage words
#      of different lengths. Instead of one threshold, have a threshold for each length.
#      (Remember, a 'good' word doesn't have to be an actual word -- we can concatenate
#      words in order to create words of sufficient length, e.g. ballcatlookatmeno)
# 
# 2) Adding rules
#  	 - While this is currently a purely stats based approach, we could add some
# 	   rules, e.g. n consonants in a row without a vowel, or a string with all vowels
#	 - We could also have a dictionary to make sure certain words are not classified as garbage
# 
# 3) RNN for probability
#    - I've trained a char-rnn that can be swapped in for the probability calculations.
# 	   This would let us take advantage of the entire string instead of simply the 
#	   preceding character. However, thie current approach appears to work well enough,
#      and the char-rnn would be much slower / cumbersome (i.e. loading the model / 
#	   keeping it in memory)

# TODO: How to normalize log probability by length of string?
# Idea 1: Go over some corpus and calc log prob for each word.
# Also just go over all permutations (so we can compare to real words)? See if there's decent separation in log prob
# At runtime, compare against average (or distribution whatever) of strings of same length
# TODO: do this, and then plot distribution for each length
	# TODO: How to handle long strings that may not have many words to compare to?
# Idea 2: Simply normalize by length (i.e. number of bigrams)
# Problem: P('xx') == P('xxx') === P('xxxx')
# Idea 2a: Add penalty for length of sequence somehow...

# TODO: Still unclear if this approach will be able to have a reasonable threshold
# Are there rule-based approaches we can take?
# E.g. n consonants in a row without a vowel 
# Maybe instead of summing log prob, any instance or 2 instances of very rare bigram?
# Ideas for rule-based approach

import pickle
import math
from itertools import product
from string import ascii_lowercase
from collections import defaultdict

class GarbageDetector:
	def __init__(self):
		LETTER_BIGRAM_COUNTS_PATH = 'data/garbage/letter_bigram_counts.txt'
		# GOOD_WORDS_PATH = 'data/word_freqs/google_10k_words_by_freq.txt'
		GOOD_WORDS_PATH = 'data/garbage/good.txt'
		GARBAGE_WORDS_PATH = 'data/garbage/garbage.txt'

		self.letter_bigram_counts_path = LETTER_BIGRAM_COUNTS_PATH
		self.good_words_path = GOOD_WORDS_PATH
		self.garbage_words_path = GARBAGE_WORDS_PATH
		self.probs = self.calc_bigram_probs()

	def calc_bigram_probs(self):
		"""
		Calculate log transition probs from one character to the next

		Return
		------
		probs: dict of dicts

		Notes
		-----
		Character 2-gram counts taken from http://norvig.com/ngrams/
		"""
		probs = defaultdict(dict)

		# Read bigram counts
		f = open(self.letter_bigram_counts_path, 'rb')
		for line in f:
			bigram, count = line.split('\t')[0], int(line.split('\t')[1].strip('\n'))
			probs[bigram[0]][bigram[1]] = count 
		f.close()

		# Calculate transition probabilities from character1 to character2
		# Normalize for each starting character
		for c1, d in probs.items():
			total_count = sum(d.values()) * 1.0
			probs[c1] = {c2: math.log(count / total_count) for c2, count in d.items()}

		return probs

	def prob(self, s):
		"""
		Return probability of string
		"""
		if len(s) == 1:
			return 1.0 / 26

		log_prob = 0.0
		for i in range(len(s) - 1):
			window = s[i:i+2]
			log_prob += self.probs[window[0]][window[1]]
		log_prob /= (len(s) - 1)					# Normalize by length of string
		prob = math.exp(log_prob)

		return prob

	def train(self):
		"""
		Calculate the threshold between good and garbage words
		"""
		print 'Training Detector' 
		good_probs = [self.prob(s.strip('\n')) for s in open(self.good_words_path)]
		garbage_probs = [self.prob(s.strip('\n')) for s in open(self.garbage_words_path)]

		print max(garbage_probs), min(good_probs)
		assert max(garbage_probs) < min(good_probs)

		threshold = 0.5 * (max(garbage_probs) + min(good_probs))
		self.threshold = threshold
		print threshold

	def is_good(self, s):
		"""
		Determine if string is good or garbage
		"""
		return self.prob(s) > self.threshold


if __name__ == '__main__':
	gd = GarbageDetector()
	gd.train()
	while True:
		s = raw_input()
		print gd.is_good(s)
