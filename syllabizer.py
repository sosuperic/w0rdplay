# Utilities related to syllables, e.g. counting number of syllables in a word, or splitting a word into syllables

import nltk

class Syllabizer:
	def __init__(self):
		self.cmudict = nltk.corpus.cmudict.dict()

	def word_to_phonemes(self, s):
		"""
		TODO: Replace cmudict with trained g2p model
		"""
		return self.cmudict[s][0]

	def is_vowel(self, phoneme):
		return not set('AEIOU').isdisjoint(set(phoneme))

	def count_number_of_syllables(self, s):
		"""
		Return number of vowel phonemes
		"""
		phonemes = self.word_to_phonemes(s)
		return self._count_number_of_syllables_in_phonemes(phonemes)

	def _count_number_of_syllables_in_phonemes(self, phonemes):
		return len([p for p in phonemes if self.is_vowel(p)])

	def _phoneme_syllabize(self, phonemes):
		"""
		Main helper function for phoneme_syllabize
		"""
		def next_phoneme_is_vowel(phonemes, cur_i):
			next_i = cur_i + 1
			if next_i >= len(phonemes):
				return False
			else:
				return self.is_vowel(phonemes[next_i])

		if self._count_number_of_syllables_in_phonemes(phonemes) == 1:
			return [phonemes]

		syllables = []
		cur_syllable = []
		prev_phoneme_is_vowel = False
		i = 0
		while i < len(phonemes):
			p = phonemes[i]
			if self.is_vowel(p):
				if prev_phoneme_is_vowel:
					syllables.append(cur_syllable)
					cur_syllable = [p]
				else:
					cur_syllable.append(p)
				prev_phoneme_is_vowel = True
			else:
				if next_phoneme_is_vowel(phonemes, i):
					syllables.append(cur_syllable)
					cur_syllable = [p]
					prev_phoneme_is_vowel = False
				elif prev_phoneme_is_vowel:
					cur_syllable.append(p)
					prev_phoneme_is_vowel = False
				else:
					syllables.append(cur_syllable)
					cur_syllable = [p]
					while (i + 1 < len(phonemes)) and (not self.is_vowel(p)):	# Append until next vowel
						i += 1
						p = phonemes[i]
						cur_syllable.append(p)

					if sum([1 for p in cur_syllable if self.is_vowel(p)]) == 0:	# Didn't hit any more vowels
						syllables[-1] += cur_syllable 							# Test case: apologized
						cur_syllable = []										# Clear so it gets filtered out

					prev_phoneme_is_vowel = True
			i += 1
		syllables.append(cur_syllable)

		# Filter out initial empty syllable, e.g. hello
		syllables = [syl for syl in syllables if len(syl) > 0]

		return syllables

	def phoneme_syllabize(self, s):
		"""
		Given string, return phonemes grouped by syllable

		Examples
		--------
		green -> [[u'G', u'R', u'IY1', u'N']]
		hello -> [[u'HH', u'AH0'], [u'L', u'OW1']]
		invisible -> [[u'IH0', u'N'], [u'V', u'IH1'], [u'Z', u'AH0'], [u'B', u'AH0', u'L']]
		newspaper -> [[u'N', u'UW1', u'Z'], [u'P', u'EY2'], [u'P', u'ER0']]
		explicit -> [[u'IH0', u'K'], [u'S', u'P', u'L', u'IH1'], [u'S', u'AH0', u'T']]
		airplane -> [[u'EH1', u'R'], [u'P', u'L', u'EY2', u'N']]
		idea -> [[u'AY0'], [u'D', u'IY1'], [u'AH0']]
		apologized -> [[u'AH0'], [u'P', u'AA1'], [u'L', u'AH0'], [u'JH', u'AY2', u'Z', u'D']]

		Pseudocode
		----------
		If word has only one syllable, return phonemes

		If current phoneme is vowel:
			If previous phoneme is vowel:
				this is start of new syllable 
			Else (previous phoneme is consonant):
				this is part of previous syllable

		Else (current phoneme is consonant):
			If next phoneme is vowel:
		      	this is start of new syllable
		  	Else if previous phoneme is vowel:
		      	this is part of previous syllable
		  	Else (both previous and next aren't vowels), e.g. airplane EH1 R *P* L EY2 N; scogin *S* K OW1 G IH0 N 
				this is start of new syllable
				append until next vowel

		Notes
		-----
		This can be used to build the context for linguistic features for a synthesizer. While a word is split into
		the basic unit of a phoneme, we want to know for every phoneme, which syllable, word, and phrase it belongs to. 
		"""
		phonemes = self.word_to_phonemes(s)
		return self._phoneme_syllabize(phonemes)

	def grapheme_syllabize(self,s):
		"""
		Return graphemes grouped by syllables, e.g. invisible -> [in, vi, si, ble]
		"""
		pass

	def rhymer(self, s1, s2):
		"""
		Return true if s1 rhymes with s2
		"""
		pass

if __name__ == '__main__':
    syllabizer = Syllabizer()
    while True:
        s = raw_input()
        print syllabizer.phoneme_syllabize(s)
        print syllabizer.count_number_of_syllables(s)
