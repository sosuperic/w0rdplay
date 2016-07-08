# w0rdplay

Modules to:

1. help analyze Speechblocks log data (e.g. detecting intentionality of word construction)
2. help build the text analysis portion of a speech synthesizer

## Garbage Word Detector ##
Detect words that are not pronounceable, e.g. xlkokm

## String Splitter ##
Split a string into words, e.g. lionxballcatyu -> lion x ball cat yu

## Running ##
A front-end is availble to explore some of the modules. Currently, you can type words and have them classified as pronounceable or not (green is pronounceable, red is not).
The classification happens dynamically as you type. String splitting into words occurs once you hit enter.

You can also click on a list of words from Speechblocks log data, which are all the words that were pronounced during the pilot study.

Download word frequency list by running:
```
./dl_wiki_subset.sh
```
Start server by running:
```
python gui/server.py
```
Visit:
```
localhost:3000
```
