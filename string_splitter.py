# Split string of words, e.g. ballcatzox -> ball cat z o x

import enchant
from math import log
from collections import defaultdict

# TODO / Notes:
# 1) Speechblocks corpus
#   - The corpus should include all default words in speechblocks.
#   - These should also be pushed to the top of the word-freq list
#
# 2) Short 'words'
#   - These corpuses include a lot of short 'words' that don't seem like words (they
#     might just be abbreviations. In any case, we could filter these out by checking
#     that these short words exist in the nltk word corpus, e.g.
#           from nltk.corpus import words as nltk_words
#           nltk_words = nltk_words.words()
#
# 3) The DEFAULT_OOV_COST 
#   - We might want to have a less harsh penalty for being out of vocabulary.
#     For instance, we could have all oov words have cost equal to some multiple of the Nth ranked word
#   - We might also want to hardcode a default value for single characters
#
# 4) wict corpus
#   - I haven't tried this one yets
#   - Text file includes comments that should be filtered out. I think text also has to
#     be normalized (e.g. remove capitalization)

class StringSplitter:
    def __init__(self):
        CORPUS_PATH = 'data/word_freqs/wiki_subset_125k_words_by_freq.txt'
        # CORPUS_PATH = 'data/word_freqs/google_10k_words_by_freq.txt'
        DEFAULT_OOV_COST = float('inf')

        self.corpus_path = CORPUS_PATH
        self.oov_cost = DEFAULT_OOV_COST
        self.word_costs = self.build_word_costs()

        # 
        self.oov_cost = sorted(self.word_costs.values())[-1] * 10

    def build_word_costs(self):
        """
        Use Zipf's law to build a cost dictionary

        Notes
        -----
        - Probability of a word is given according to 1 / (n log N)
            n := word frequency rank
            N := number of words
        - Because probabilities can be small, we avoid overflow by taking the inverse and log


        Return
        ------
        word_costs: dict
            key: str; word
            value: float; log(inverse probability)
        """

        words = open(self.corpus_path).read().split()
        zipf_prob = {word: 1 / ((i+1) * log(len(words))) for i, word in enumerate(words)}
        word_costs = {word: log(1 / prob) for word,  prob in zipf_prob.items()}
        word_costs = defaultdict(lambda: self.oov_cost, word_costs)
        return word_costs

    def infer_spaces(self, s, keywords=[]):
        """
        Return string with spaces inserted

        Input
        -----
        s: str to split
        keywords: list of preferred words that should be their own split
            - Example: keywords = ['ball']
            - ballerina -> 'ball' 'erina' instead of 'ballerina'

        Dynamic Programming Formula
        ---------------------------
        Costs: Memoizes previously calculated costs of substrings
        Base case: c0 = 0
        Formula: c_i = min_j { c_(j-1) + word_costs[i] }
            1 <= j <= i
        """
        # costs: memoizes cost of substring, i.e. costs[i] is cost of s[:i+1]
        # split_indices: stores where to insert space, i.e. for s[:i+1], insert space at split_indices[i]
        costs = [0]                          # Initialize cost of empty string '' to 0
        split_indices = []      
        for i in range(len(s)):              # Build out costs for each substring

            # For the current substring (e.g. 'hith' from 'hithere'), figure out best place to split, e.g. 'hi', 'th'
            # Split can occur at the beginning of substring, i.e. '', 'hith'
                # This corresponds to a split_index of 0
            best_split_cost, best_split_index = float('inf'), -1
            for j in range(i+1):                                    # j is index at which to insert space before

                # If either substring is in keywords, then definitely split
                # TODO: I'm not sure what the best_split_cost should be exactly 
                if (s[0:j] in keywords) or (s[j:i+1] in keywords):
                    best_split_index = j

                split_cost = costs[j] + self.word_costs[s[j:i+1]]   # Use memoized costs
                if split_cost < best_split_cost:
                    best_split_cost = split_cost
                    best_split_index = j

            costs.append(best_split_cost)
            split_indices.append(best_split_index)

        # Backtrack to get spaces
        # Start from last split_index, extract substring, then move pointer to split_index - 1
        words = []
        i = len(s) - 1
        while i >= 0:
            split_idx = split_indices[i]
            words.insert(0, s[split_idx:i+1])                 # Going backwards, so prepend instead of append
            i = split_idx - 1

        return " ".join(words)

    def count_num_real_words(self, spaced):
        """
        Given string with spaces inserted, return number of real and not real words

        Purpose
        -------
        Rudimentary look at intent, e.g. high ratio of real to not real words may mean string was purposeful
        """
        d = enchant.Dict("en_US")
        real, not_real = 0, 0
        for w in spaced.split(" "):
            if d.check(w):
                real += 1
            else:
                not_real += 1
        return real, not_real

if __name__ == '__main__':
    ss = StringSplitter()
    while True:
        s = raw_input()
        spaced = ss.infer_spaces(s)
        print spaced
