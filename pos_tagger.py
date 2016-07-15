# Part of speech tagger for speech synthesis front-end

# Current implementation simply uses nltk 

# Requirements
# Download the following nltk packages using nltk.download() GUI
# models/maxent_treebank_pos_tagger
# models/punkt
# models/tagsets
# models/universal_tagset
# corpora/brown
# corpora/treebank

# Tagset
# The universal tagset and link to paper can be found here: https://github.com/slavpetrov/universal-pos-tags
# To find out what the tag means: nltk.help.upenn_tagset('PRP$')
# Or, to list all the tags and their descriptions: nltk.help.upenn_tagset()

# Universal tagset:
# The tagset consists of the following 12 coarse tags:

# VERB - verbs (all tenses and modes)
# NOUN - nouns (common and proper)
# PRON - pronouns
# ADJ - adjectives
# ADV - adverbs
# ADP - adpositions (prepositions and postpositions)
# CONJ - conjunctions
# DET - determiners
# NUM - cardinal numbers
# PRT - particles or other function words
# X - other: foreign words, typos, abbreviations
# . - punctuation

# To simplify tags from the default tagger:
# import nltk
# from nltk.tag import pos_tag, map_tag
# text = nltk.word_tokenize("And now for something completely different")
# posTagged = pos_tag(text)
# simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]


import nltk

class POSTagger:
    def __init__(self):
        self.tagdict = nltk.data.load('help/tagsets/upenn_tagset.pickle')
        self.univeral_tagset = ['VERB', 'NOUN', 'PRON', 'ADJ', 'ADV', 'ADP', 'CONJ',
            'DET', 'NUM', 'PRT', 'X', '.']
        self.universal_tagset_to_idx = {tag: i for i, tag in enumerate(self.univeral_tagset)}

    def tokenize(self, text):
        return nltk.word_tokenize(text)

    def pos_tag(self, tokenized):
        return nltk.pos_tag(tokenized)

    def pos_tag_simplified(self, tokenized):
        tagged = self.pos_tag(tokenized)
        simplified = [(word, nltk.map_tag('en-ptb', 'universal', tag)) for word, tag in tagged]
        return simplified

if __name__ == '__main__':
    tagger = POSTagger()
    while True:
        s = raw_input()
        tagged =tagger.pos_tag(tagger.tokenize(s))
        print tagged
