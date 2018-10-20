import irsystem
import dict_compression
from inverted_index import extern_input
import json

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

analysis = {}


def build_indexes():
    for dname, dfilter in dict_filters.items():
        files = irsystem.build(["reuters/reut2-0{:02}.sgm".format(k) for k in range(0, 22)], dfilter)
        files = [f.name for f in files]
        outfile = irsystem.merge_index(files, "./index_{}".format(dname), multipass=True)
        print(outfile)


def analyze():
    for dname, dfilter in dict_filters.items():
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
        analysis[dname] = {
            "term_count": term_count,
            "postings_count": postings_count,
            "positional_postings_count": positional_postings_count
        }


build_indexes()
analyze()

print(json.dumps(analysis, indent=4))
with open("index_analysis.txt", "w") as f:
    json.dump(analysis, f, indent=4)
    f.close()
