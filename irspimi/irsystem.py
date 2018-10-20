## TODO Description of this file
from reuters import ReutersCorpus
from spimi import SPIMI
from merge import MergeSPIMI
from inverted_index import InvertedIndex
from expression_eval import Parser, Evaluator
import os
import dict_compression

INVERTED_INDEX_FILENAME = "inverted_index.ii"


def build(files: list, compression: dict_compression.Compression = None):
    corpus = ReutersCorpus(files, compression)
    spimi_inverter = SPIMI(token_stream=corpus, dir="./blocks/")

    lst = []
    while True:
        d = spimi_inverter.invert()
        if d:
            lst.append(d)
        else:
            break
    return lst


def merge_index(filenames: list, directory: str = "."):
    """Merge the given list of blocks.

    :param filenames: List of block filename
    :param directory: directory to output the inverted index file
    :return: path to the inverted index on disk
    :rtype:str
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    out_path = "{}/{}".format(directory, INVERTED_INDEX_FILENAME)
    ms = MergeSPIMI(filenames, out_path, output_buffer_length=500, input_buffer_length=500)
    ms.external_merge()

    return out_path


def search_expr(index: InvertedIndex, expr: str):
    parser = Parser(expr)
    evaluator = Evaluator(parser, index)
    res = evaluator.evaluate()
    return res
    # pt = Parser("George AND Bush OR Maria AND Ford")
    # tree = pt.parse()
    # print(tree)
    # pt = ParseTree("(NOT (George OR Georgie) AND Bush)")
    # print(pt)
    #
    # pt = ParseTree("(NOT (George OR Georgie))")
    # print(pt)
    #
    # pt = ParseTree("(NOT George)")
    # print(pt)


def load_index(filename: str):
    index = InvertedIndex(filename)
    return index
