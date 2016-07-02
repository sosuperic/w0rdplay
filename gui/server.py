# Run server to test garbage_detector

import json
import os
import time
from flask import Flask, Response, request

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

import uuid
import csv
import pickle
import random
import string

import garbage_detector
import string_splitter


SPOKEN_WORDS_PATH = 'data/logs/spoken_words_all.csv'
SB_WORDS_N = 20

#############################################################################
# Non-routing functions
#############################################################################

def sb_initialize_words():
    """
    Create set from csv file
    """
    words = set()
    f = open(SPOKEN_WORDS_PATH, 'rb')
    for line in iter(f):
        if line.endswith('speak\n'):
            word = line.split('|')[1].strip('\n')
        else:
            word = line.strip('\n')
        words.add(word)

    words = [{'text': w, 'id':str(uuid.uuid4())} for w in list(words)]
    random.shuffle(words)

    return words

def clean_word(word):
    """
    Clean word of punctuation and special characters before analyzing it
    """
    return word.strip('\r')

def handle_new_word(request):
    """
    Analyze word, update session_words & all_words, write all_words to file
    """
    with open('gui/words.json', 'r') as f:
        all_words = json.loads(f.read())

    if request.method == 'POST':
        new_word = request.form.to_dict()
        new_word['text'] = clean_word(new_word['text'])
        new_word['id'] = int(time.time() * 1000)
        new_word['is_good'] = gd.is_good(new_word['text'])
        new_word['spaced'] = ss.infer_spaces(new_word['text'])

        session_words.append(new_word)
        all_words.append(new_word)

        with open('gui/words.json', 'w') as f:
            f.write(json.dumps(all_words, indent=4, separators=(',', ': ')))

def update_sb_words(request):
    """
    Remove word from cur_sb_words, add new one from all_sb_words
    """
    global all_sb_words, cur_sb_words, cur_sb_idx
    if request.method == 'POST':
        word = request.form.to_dict()
        cur_sb_words = [w for w in cur_sb_words if w['text'] != word['text']]
        cur_sb_words.insert(int(word['i']), all_sb_words[cur_sb_idx])
        cur_sb_idx += 1

#############################################################################
# Setup upon server initialization
#############################################################################

gd = garbage_detector.GarbageDetector()
ss = string_splitter.StringSplitter()

session_words = []

all_sb_words = sb_initialize_words()
cur_sb_words = all_sb_words[0:SB_WORDS_N]
cur_sb_idx = SB_WORDS_N + 1

#############################################################################
# API
#############################################################################

@app.route('/api/speechblocks/get_words', methods=['GET'])
def sb_get_words():
    """
    Pop a word
    """
    return Response(
        json.dumps(cur_sb_words),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/api/submit_word', methods=['GET', 'POST'])
def submit_word_handler():
    """
    Write word to file and return words submitted in this sessions
    """
    handle_new_word(request)

    return Response(
        json.dumps(session_words[::-1]),    # Reverse to show latest at top
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/api/submit_speechblocks_word', methods=['GET', 'POST'])
def submit_sb_word_handler():
    """
    Analyze word, write word to file, and return updated words and sb words
    """
    handle_new_word(request)
    update_sb_words(request)

    return Response(
        json.dumps({
            'speechblocks_words': cur_sb_words, 
            'session_words': session_words[::-1]
            }),
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/api/analyze_word/<s>')
def analyze_string(s):
    """
    Used to analyze strings while typing
    """
    is_good = gd.is_good(s)
    spaced = ss.infer_spaces(s)

    return Response(
        json.dumps([is_good, spaced]),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 3000)), debug=True)
