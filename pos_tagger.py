# Part of speech tagger for speech synthesis front-end

# Current implementation simply uses nltk 

# Requirements
# Download the following nltk packages using nltk.download() GUI
# models/maxent_treebank_pos_tagger
# models/punkt
# models/tagsets
# models/universal_tageset
# corpora/brown
# corpora/treebank

# Tagset
# The universal tagset and link to paper can be found here: https://github.com/slavpetrov/universal-pos-tags
# To find out what the tag means: nltk.help.upenn_tagset('PRP$')
# Or, to list all the tags and their descriptions: nltk.help.upenn_tagset()

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

    def tokenize(self, text):
        return nltk.word_tokenize(text)

    def pos_tag(self, tokenized):
        return nltk.pos_tag(tokenized)

if __name__ == '__main__':
    tagger = POSTagger()
    while True:
        s = raw_input()
        tagged =tagger.pos_tag(tagger.tokenize(s))
        print tagged
