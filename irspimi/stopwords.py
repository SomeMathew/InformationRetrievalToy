"""
Script to build the list of 200 stop words for the Reuters Corpus.

This uses collection frequency to select the 200 most commonly used words are stop words in reverse frequency order

The ir system then uses this list to create a dictionary compression from first 30 and 150 stop words
"""
from reuters import ReutersCorpus

dictionary = {}
rc = ReutersCorpus(["reuters/reut2-0{:02}.sgm".format(k) for k in range(0, 23)])
for tok in rc:
    if tok.token in dictionary:
        dictionary[tok.token] += 1
    else:
        dictionary[tok.token] = 1

frequency_sorted = sorted(dictionary.items(), key=lambda t: t[1], reverse=True)
stopwords200 = [t[0] for t in frequency_sorted[0:200]]

print(stopwords200)

with open("stopwords.list", "w+") as f:
    for w in stopwords200:
        f.write(w + "\n")
    f.close()
