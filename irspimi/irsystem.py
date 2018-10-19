## TODO Description of this file
from reuters import ReutersCorpus
from spimi import SPIMI
from merge import MergeSPIMI


def build(files: list):
    corpus = ReutersCorpus(files)
    # TODO add a preprocessor for the stream
    spimi_inverter = SPIMI(token_stream = corpus, dir="./blocks/")

    lst = []
    while True:
        d = spimi_inverter.invert()
        if d:
            # print(d)
            lst.append(d)
        else:
            break
    return lst


def merge_index(files: list, dir: str):
    pass


def load_index(filename: str):
    index = {}
    with open(filename, "r") as f:
        for next_line in f:
            next_line = next_line.strip()
            if next_line:
                term, postings = next_line.split(" : ")
                postings = [int(i) for i in postings.split(",")]
                index[term] = postings
    return index


# fileList = build(["reuters/reut2-0{:02}.sgm".format(k) for k in range(0, 22) if k is not 17])
# # fileList = build(["reuters/reut2-017.sgm"])
# fileList = [f.name for f in fileList]
# print(fileList)
# ms = MergeSPIMI(fileList, "merge_test.index")
# ms.external_merge()

t = load_index("merge_test.index")
# while True:
#     test = input("Search for what?")
#     if test in t:
#         print(t[test])
# print(t['test'] if 'test' in t else t['the'])


import search

res = search.intersect(t["George"], t["Bush"])
print(res)

res = search.intersect(t["John"], t["Ford"])
print(res)

res = search.subtract(t["George"], t["Bush"])
print(res)
