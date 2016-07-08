# For all the spoken words in 1st pilot, calculate percent that were real words

import enchant
import pickle
import garbage_detector

d = enchant.Dict("en_US")
gd = garbage_detector.GarbageDetector()

spoken_words = pickle.load(open('data/logs/spoken_words.pkl', 'rb'))
real, not_real = [], []
garbage, not_garbage = [], []
for path, log in spoken_words:
	if 'speak' in log:
		continue
	word = log.split(' ')[1].replace('\n', '')
	if d.check(word):
		real.append(word)
	else:
		# print(word)
		not_real.append(word)

	if gd.is_good(word):
		print 'Not garbage: ', word
		not_garbage.append(word)
	else:
		print 'Garbage: ', word 
		garbage.append(word)

def perc_real(real, not_real):
	r, nr = len(real), len(not_real)
	return 1.0 * r / (r + nr)



# print(len(real), len(not_real), perc_real(real, not_real))
# Percent real words (8%)
print(len(set(real)), len(set(not_real)), perc_real(set(real), set(not_real)))

# Percent garbage (31%)
# print(len(garbage), len(not_garbage), perc_real(garbage, not_garbage))
print(len(set(garbage)), len(set(not_garbage)), perc_real(set(garbage), set(not_garbage)))