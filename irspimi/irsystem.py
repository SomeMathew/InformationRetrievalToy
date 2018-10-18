## TODO Description of this file
from reuters import ReutersCorpus
from spimi import SPIMI


def build(files: list):
    corpus = ReutersCorpus(files)
    # TODO add a preprocessor for the stream
    spimi_inverter = SPIMI(token_stream = corpus, dir="./blocks/")

    lst = []
    while True:
        d = spimi_inverter.invert()
        if d:
            print(d)
            lst.append(d)
        else:
            break


def merge_index(files: list, dir: str):
    pass

build(["reut2-000.sgm"])

