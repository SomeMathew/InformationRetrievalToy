from reuters import ReutersCorpusStream
from spimi import SPIMI
from merge import MergeSPIMI, MultiPassMergeSPIMI
from typing import List
from inverted_index import InvertedIndex, InvertedIndexDescriptor, INVERTED_INDEX_DESCRIPTOR_SUFFIX
from expression_eval import Parser, Evaluator
from eval_result import EvaluationResult
from rank_bm25_eval import RankedSearchBM25
import os
import dict_compression

INVERTED_INDEX_FILENAME = "inverted_index.ii"


def build_index(files: List[str], directory: str = ".", compression: dict_compression.Compression = None):
    """ Build the inverted index and merges it.

    Builds using SPIMI and merges using an external multipass k-way merge

    :param files: Ordered files of the Reuters Corpus
    :param directory: Directory to output the index
    :param compression: Dictionary Compression technique
    :type files: List[str]
    :type directory: str
    :type compression: Compression
    :return: Filename of the index on disk
    :rtype: str
    """
    corpus = ReutersCorpusStream(files, compression)
    spimi_inverter = SPIMI(token_stream=corpus, dir="./blocks/")

    blocks_filenames = []
    while True:
        d = spimi_inverter.invert()
        if d:
            blocks_filenames.append(d)
        else:
            break

    index_filename = _merge_index(blocks_filenames, directory, multipass=True)

    descriptor = InvertedIndexDescriptor(corpus.docid_list, corpus.doclength_map, compression)
    descriptor.write_to_file("{}/{}.{}".format(directory, INVERTED_INDEX_FILENAME, INVERTED_INDEX_DESCRIPTOR_SUFFIX))
    return index_filename


def _merge_index(filenames: list, directory: str = ".", multipass: bool = True):
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
        ms = MultiPassMergeSPIMI(filenames, out_path, input_buffer_length=10000, input_buffer_count=4)
    else:
        ms = MergeSPIMI(filenames, out_path, input_buffer_length=100)
    ms.external_merge()

    return out_path


def search_expr(index: InvertedIndex, expr: str):
    """Search for an expression in the Inverted Index"""
    parser = Parser(expr)
    evaluator = Evaluator(parser, index)
    res = evaluator.evaluate()
    return res


def search_ranked(index: InvertedIndex, query: str, k1: float = 1.2, b: float = 0.5):
    """Ranked search for a query (bag of word) in the Inverted Index.

    :param index: Inverted index to use for the search
    :param query: Bag of words query (No operators)
    :return: Ranked Evaluated Results
    :rtype: EvaluationResult
    """
    evaluator = RankedSearchBM25(query, index, k1, b)
    result = evaluator.evaluate()
    return result


def load_index(directory: str):
    """Load an inverted index object"""
    index = InvertedIndex("{}/{}".format(directory, INVERTED_INDEX_FILENAME))
    return index
