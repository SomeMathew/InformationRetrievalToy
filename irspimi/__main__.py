import argparse
import irsystem
from itertools import islice
from dict_compression import PorterStemmer, NoStopWords, CaseFolding, NoNumbers, MultipleCompression

filters_dict = {"nonum": NoNumbers(),
                "casefold": CaseFolding(),
                "stopw30": NoStopWords(30, "stopwords.list"),
                "stopw150": NoStopWords(150, "stopwords.list"),
                "portstem": PorterStemmer()}


def build_index(args: argparse.Namespace):
    # Create Compression filters
    compress_filter = None
    if args.filters:
        filters = [filters_dict[x] for x in args.filters if x in filters_dict]
        if filters:
            compress_filter = MultipleCompression(filters)
    """Builds the Inverted Index"""
    print("Building index with multipass merge")
    outfile = irsystem.build_index(args.corpus_files, args.directory, compress_filter)
    print(outfile)


def search_mode(args: argparse.Namespace):
    """Search a corpus using a pre-built Inverted Index"""
    index = irsystem.load_index(args.directory)
    while True:
        expr = input("What do you want to search for? (Type q to exit)\n")
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


def search_ranked_mode(args: argparse.Namespace):
    """Search a corpus with ranked retrieval using a pre-built Inverted Index"""
    index = irsystem.load_index(args.directory)
    k1 = args.k1
    b = args.b
    resultLimit = args.resultLimit
    while True:
        query = input("What do you want to search for? (Type q to exit)\n")
        if query == "q":
            print("Goodbye!")
            break
        eval_result = irsystem.search_ranked(index, query, k1, b)
        if args.show_title:
            eval_result.update_details(args.corpus_dir[0], max_topk=resultLimit)
        result_count = 0
        for docid, details in eval_result.results.items():
            result_count += 1
            if args.show_title:
                print("#{num}: {title} - DocId {docid}".format(num=result_count, title=details['title'], docid=docid))
            else:
                print("#{num}: DocId {docid}".format(num=result_count, docid=docid))

            print("\tTerms:{terms}\t\tWeight: {weight:.2f}\n".format(terms=", ".join(details['terms']),
                                                                     weight=details['weight']))
            if resultLimit and result_count >= resultLimit:
                break
        print('\nRetrieved {} results out of {}.'.format(result_count, len(eval_result.results.items())))
        if result_count > 0:
            doc_retrieval_mode(eval_result, resultLimit)


def doc_retrieval_mode(eval_result, max_topk=None):
    """Retrieves document from a search result."""
    results = eval_result.results
    ordered_docid = [docid for docid, details in
                     (eval_result.results.items() if not max_topk else islice(eval_result.results.items(), max_topk))]
    while True:
        print("Document Id List: {}".format(ordered_docid))
        resp = input("Enter a document id to retrieve it. (Type q to search again)\n")
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
    "--compress-dict", "-c",
    help="Select a dictionary compression algorithms.",
    choices=filters_dict.keys(),
    action="append",
    dest="filters"
)
build_parser.add_argument(
    "corpus_files",
    help="List of ordered files for the Reuters Corpus.",
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
    "--ranked", "-r",
    help="Retrieval using BM25 ranked retrieval with bag of words model",
    action="store_const",
    dest="func",
    const=search_ranked_mode,
    default=search_mode
)
search_parser.add_argument(
    "-k1",
    help="BM25 parameter, weight of the term frequency effect on scoring. 0 disregards tf. DEFAULT 1.2",
    default=1.2,
    type=float,
    action="store",
    dest="k1"
)
search_parser.add_argument(
    "-b",
    help="BM25 Parameter, scaling of document length, b in [0,1]. 0 -> no length normalization, 1 -> full scaling. DEFAULT 0.75",
    default=0.75,
    type=float,
    action="store",
    dest="b"
)
search_parser.add_argument(
    "--limit", "-l",
    help="Limit the number of results to return",
    type=int,
    action="store",
    dest="resultLimit"
)
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

# args = parser.parse_args("search -r -t -l15 -d ../index_norm ../reuters".split(" "))
# args = parser.parse_args("build -d testindex -c nonum -c casefold -c portstem ../reuters/reut2-017.sgm".split(" "))
# args.func(args)
args = parser.parse_args()
try:

    args.func(args)
except AttributeError as e:
    print(e)
    parser.print_help()
