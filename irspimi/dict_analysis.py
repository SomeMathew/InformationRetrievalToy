import irsystem
import dict_compression
from inverted_index import extern_input
import json
import os

INDEX_STATS_FOLDER = "index_stats"
INDEX_STATS_FILENAME = "index_stats.txt"


def build_indexes(dfilters: dict):
    """Build inverted index with each compression techniques in dict_filters"""
    for dname, dfilter in dfilters.items():
        print("Creating inverted index with compressions: {}".format(dfilter))
        outfile = irsystem.build_index(["reuters/reut2-0{:02}.sgm".format(k) for k in range(0, 22)],
                                       "./index_{}".format(dname), dfilter)
        print(outfile)


def analyze(dfilters: dict):
    """Create statistics for terms, non-positional postings and positional postings for each index"""
    stats = {}
    for dname, dfilter in dfilters.items():
        with open("./index_{}/{}".format(dname, irsystem.INVERTED_INDEX_FILENAME), "r") as f:
            term_count = 0
            postings_count = 0
            positional_postings_count = 0
            for line in f:
                term_posting = extern_input(line)
                if not term_posting.term:
                    raise Exception("This should not happen")
                term_count += 1
                postings_count += len(term_posting.postings)
                for posting in term_posting.postings:
                    positional_postings_count += len(posting.positions)
            f.close()
        stats[dname] = {
            "term_count": term_count,
            "postings_count": postings_count,
            "positional_postings_count": positional_postings_count
        }
    return stats


stopwords_path = "stopwords.list"
dict_filters = {"none": None,
                "nonumbers": dict_compression.NoNumbers(),
                "casefold": dict_compression.MultipleCompression(
                    [dict_compression.NoNumbers(),
                     dict_compression.CaseFolding()]),
                "stop30": dict_compression.MultipleCompression(
                    [dict_compression.NoNumbers(),
                     dict_compression.CaseFolding(),
                     dict_compression.NoStopWords(30, stopwords_path)]),
                "stop150": dict_compression.MultipleCompression(
                    [dict_compression.NoNumbers(),
                     dict_compression.CaseFolding(),
                     dict_compression.NoStopWords(150, stopwords_path)]),
                "porter": dict_compression.MultipleCompression(
                    [dict_compression.NoNumbers(),
                     dict_compression.CaseFolding(),
                     dict_compression.NoStopWords(150, stopwords_path),
                     dict_compression.PorterStemmer()])}

build_indexes(dict_filters)
stats_analysis = analyze(dict_filters)

print(json.dumps(stats_analysis, indent=4))
if not os.path.exists(INDEX_STATS_FOLDER):
    os.makedirs(INDEX_STATS_FOLDER)
with open("./{}/{}".format(INDEX_STATS_FOLDER, INDEX_STATS_FILENAME), "w") as f:
    json.dump(stats_analysis, f, indent=4)
    f.close()
