# Read pickle file and write to csv

import csv
import pickle
import re

sw = pickle.load(open('data/logs/spoken_words.pkl', 'rb'))

def spoken_words_to_csv():
    """
    Ignore special words, i.e. spoken words with a speak in the log 

    These lines use a separate phoneme library?
    """
    with open('data/logs/spoken_words.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        for path, log in sw:
            if 'speak' in log:
              continue
            word = log.split(' ')[1].replace('\n', '')
            writer.writerow([word])

def all_spoken_words_to_csv():
    """
    Write all spoken words to csv, but ignore 

    These lines use a separate phoneme library?
    """
    sw_all = open('data/logs/spoken_words_all.csv', 'wb')
    writer = csv.writer(sw_all, delimiter='|')
    for path, log in sw:
        if 'speak' in log:
            m = re.match(r'.+>(\w+)</phoneme>.+', log)
            word = m.group(1)
            writer.writerow([word, 'speak'])
        else:
            word = log.split(' ')[1].replace('\n', '')
            writer.writerow([word])
    sw_all.close()

def logs_to_csv():
    """
    Write all logs to csv
    """
    with open('data/logs/logs.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        for path, log in sw:
            writer.writerow([path, log])

if __name__ == '__main__':
    logs_to_csv()
    spoken_words_to_csv()
    all_spoken_words_to_csv()
