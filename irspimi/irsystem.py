## TODO Description of this file
from reuters import ReutersCorpus
from spimi import SPIMI
from merge import MergeSPIMI, MultiPassMergeSPIMI
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


def merge_index(filenames: list, directory: str = ".", multipass: bool = True):
    """Merge the given list of blocks.

    :param filenames: List of block filename
    :param directory: directory to output the inverted index file
    :param multipass: Set to true for the multi pass k-way merge algorithm
    :return: path to the inverted index on disk
    :rtype:str
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    out_path = "{}/{}".format(directory, INVERTED_INDEX_FILENAME)
    if multipass:
        ms = MultiPassMergeSPIMI(filenames, out_path, input_buffer_length=5000, input_buffer_count=8)
    else:
        ms = MergeSPIMI(filenames, out_path, input_buffer_length=100)
    ms.external_merge()

    return out_path


def search_expr(index: InvertedIndex, expr: str):
    parser = Parser(expr)
    evaluator = Evaluator(parser, index)
    res = evaluator.evaluate()
    return res


def load_index(filename: str):
    index = InvertedIndex(filename)
    return index
