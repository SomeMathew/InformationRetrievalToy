import argparse
import os
import irsystem
import dict_compression
from inverted_index import InvertedIndex
from expression_eval import Parser, Evaluator
from dict_compression import PorterStemmer, NoStopWords, CaseFolding, NoNumbers, MultipleCompression
import json


def build_index(args: argparse.Namespace):
    print("Building index with multipass merge")
    # outfile = irsystem.build_index(["reuters/reut2-0{:02}.sgm".format(k) for k in range(0, 22)], "./index_mp", None)
    outfile = irsystem.build_index(args.corpus_files, args.directory, None)
    print(outfile)


def search_mode(args: argparse.Namespace):
    index = irsystem.load_index(args.directory)
    while True:
        expr = input("What do you want to search for? (Type q to exit)")
        if expr == "q":
            print("Goodbye!")
            break
        eval_result = irsystem.search_expr(index, expr)
        if args.show_title:
            eval_result.update_details(args.corpus_dir[0])
        result_count = 0
        for docid, details in sorted(eval_result.results.items(),
                                     key=lambda item: (len(item[1]['terms']), len(item[1]['positions'])),
                                     reverse=True):
            result_count += 1
            if args.show_title:
                print("#{num}: {title} - DocId {docid}".format(num=result_count, title=details['title'], docid=docid))
            else:
                print("#{num}: DocId {docid}".format(num=result_count, docid=docid))

            print("\tCount:{count}, Terms:{terms}\n".format(count=len(details['positions']),
                                                            terms=", ".join(details['terms'])))
        print('\nRetrieved {} results.'.format(result_count))
        if result_count > 0:
            doc_retrieval_mode(eval_result)


def doc_retrieval_mode(eval_result):
    results = eval_result.results
    while True:
        resp = input("Enter a document id to retrieve it, q to search again")
        if resp == "q":
            break
        else:
            try:
                docid = int(resp)
                if docid not in results:
                    raise ValueError
                else:
                    if "doc" not in results[docid]:
                        eval_result.update_details(args.corpus_dir[0], docid)

                    print(results[docid]["doc"])
            except ValueError:
                print("Invalid docid")
                continue


# Argument Parser
parser = argparse.ArgumentParser(
    description="irspimi is a information retrieval system for the Reuters21578 corpus using the SPIMI algorithm.",
    epilog="Use \"irspimi [command] --help\" for more information about a command.")

subparsers = parser.add_subparsers(
    description="Select the mode of operation of the information retrieval system.",
    help="build constructs the inverted index.\nsearch executes the search query module.")

# Build Inverted Index Sub Parser
build_parser = subparsers.add_parser(
    "build",
    description="Builds the inverted index for the Reuters Corpus")
build_parser.add_argument(
    "--dest-dir", "-d",
    help="Selects the destination directory for the inverted index",
    action="store",
    default=".",
    metavar="DIR",
    dest="directory"
)
build_parser.add_argument(
    "corpus_files",
    help="List of files for the Reuters Corpus, MUST BE GIVEN IN ORDER",
    action="store",
    metavar="CORPUS_FILE",
    nargs="+"
)
build_parser.set_defaults(func=build_index)

# Search Sub Parser
search_parser = subparsers.add_parser(
    "search",
    description="Search in the Reuters Corpus using the previously built index")
search_parser.add_argument(
    "--title", "-t",
    help="Show titles in results found, This slows down the results",
    action="store_true",
    dest="show_title"
)
search_parser.add_argument(
    "--src-dir", "-d",
    help="Selects the directory of the inverted index, descriptor and dictionary",
    action="store",
    default=".",
    metavar="DIR",
    dest="directory"
)
search_parser.add_argument(
    "corpus_dir",
    help="Directory where the Reuters Corpus can be found.",
    action="store",
    metavar="CORPUS_DIR",
    nargs=1
)
search_parser.set_defaults(func=search_mode)

args = parser.parse_args("search -t -d ../index reuters".split(" "))
args.func(args)
