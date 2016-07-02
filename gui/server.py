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

import garbage_detector
import string_splitter

SPOKEN_WORDS_PATH = 'data/logs/spoken_words_all.csv'

gd = garbage_detector.GarbageDetector()
ss = string_splitter.StringSplitter()

session_words = []

def speechblocks_initialize_words():
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

    words = [{'word': w, 'id':str(uuid.uuid4())} for w in list(words)]
    random.shuffle(words)

    return words

speechblocks_words = speechblocks_initialize_words()

@app.route('/api/speechblocks/get_words', methods=['GET'])
def speechblocks_get_words():
    """
    Pop a word
    """
    return Response(
        json.dumps(speechblocks_words[0:20]),
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
    with open('gui/words.json', 'r') as f:
        all_words = json.loads(f.read())

    if request.method == 'POST':
        new_word = request.form.to_dict()
        new_word['id'] = int(time.time() * 1000)
        new_word['is_good'] = gd.is_good(new_word['text'])
        new_word['spaced'] = ss.infer_spaces(new_word['text'])

        session_words.append(new_word)
        all_words.append(new_word)

        with open('gui/words.json', 'w') as f:
            f.write(json.dumps(all_words, indent=4, separators=(',', ': ')))

    return Response(
        json.dumps(session_words[::-1]),    # Reverse to show latest at top
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/api/analyze_word/<s>')
def analyze_string(s):
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
    app.run(port=int(os.environ.get("PORT", 3000)))
