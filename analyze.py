# For all the spoken words in 1st pilot, calculate percent that were real words

import enchant
import pickle

d = enchant.Dict("en_US")

spoken_words = pickle.load(open('data/logs/spoken_words.pkl', 'rb'))
real, not_real = [], []
for path, log in spoken_words:
	if 'speak' in log:
		continue
	word = log.split(' ')[1].replace('\n', '')
	if d.check(word):
		real.append(word)
	else:
		print(word)
		not_real.append(word)

def perc_real(real, not_real):
	r, nr = len(real), len(not_real)
	return 1.0 * r / (r + nr)

print(len(real), len(not_real), perc_real(real, not_real))
print(len(set(real)), len(set(not_real)), perc_real(set(real), set(not_real)))

