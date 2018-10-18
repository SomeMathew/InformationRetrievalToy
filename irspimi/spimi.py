## Implements the spimi algorithm to build an inverted index
import os
import sys
from typing import Iterable
from reuters import ReutersToken


class SPIMI:
    BLOCK_NAME_PREFIX = "SPIMIBLOCK"
    DEFAULT_BLOCK_SIZE = 65536  # 64 KB (about 500 Reuter's article)

    def __init__(self, token_stream: Iterable[ReutersToken], blocksize: int = DEFAULT_BLOCK_SIZE, dir: str = "."):
        self._next_block_suffix = 0
        self._blocksize = blocksize
        self._token_stream = token_stream
        self._dir = dir
        if not os.path.exists(dir):
            os.makedirs(dir)

    def invert(self):
        dictionary = {}
        if sys.getsizeof(dictionary) < self._blocksize:
            for token in self._token_stream:
                if token.token not in dictionary:
                    posting_list = self._add_to_dict(dictionary, token.token)
                else:
                    posting_list = self._get_posting_list(dictionary, token.token)
                self._add_to_posting_list(posting_list, token.docid)

                # Since we're using an iterator, check if free mem before next token
                if sys.getsizeof(dictionary) >= self._blocksize:
                    break
        sorted_terms = sorted(dictionary.keys())

        return self._write_to_disk(sorted_terms, dictionary) if sorted_terms else None
        # return dictionary ## TODO this is a test

    @staticmethod
    def _add_to_dict(dictionary: dict, term: str):
        dictionary[term] = []
        return dictionary[term]

    @staticmethod
    def _get_posting_list(dictionary: dict, term: str):
        return dictionary[term]

    @staticmethod
    def _add_to_posting_list(posting_list: list, docid: str):
        if docid not in posting_list:
            posting_list.append(docid)

    def _write_to_disk(self, sorted_terms: list, dictionary: dict):
        output_file_name = "{}/{}_{}.blk".format(self._dir, SPIMI.BLOCK_NAME_PREFIX, self._next_block_suffix)
        try:
            output_file = open(output_file_name, "w+")
            for term in sorted_terms:
                output_file.write("{} : {}\n".format(term, ",".join(str(x) for x in dictionary[term])))
            output_file.flush()
            output_file.close()
            self._next_block_suffix += 1
            return output_file
        except IOError as e:
            print("Unable to open block to write the file {}".format(output_file_name))
            print(e)
