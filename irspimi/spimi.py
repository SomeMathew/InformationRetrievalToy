## Implements the spimi algorithm to build an inverted index
import os
import sys
from typing import Iterable, List, Dict
from reuters import DocToken
from inverted_index import extern_output, TermPostings, Posting


class SPIMI:
    BLOCK_NAME_PREFIX = "SPIMIBLOCK"
    DEFAULT_BLOCK_SIZE = 65536  # 64 KB (about 500 Reuter's article)

    def __init__(self, token_stream: Iterable[DocToken], blocksize: int = DEFAULT_BLOCK_SIZE, dir: str = "."):
        self._next_block_suffix = 0
        self._blocksize = blocksize
        self._token_stream = token_stream
        self._dir = dir
        if not os.path.exists(dir):
            os.makedirs(dir)

    def invert(self):
        """Executes the SPIMI algorithm with the given token stream during construction.

        :return: disk block file name
        :rtype: str
        """
        dictionary = {}
        if sys.getsizeof(dictionary) < self._blocksize:
            for token in self._token_stream:
                if token.token not in dictionary:
                    posting_list = self._add_to_dict(dictionary, token.token)
                else:
                    posting_list = self._get_posting_list(dictionary, token.token)
                self._add_to_posting_list(posting_list, token.docid, token.pos)

                # Since we're using an iterator, check if free mem before next token
                if sys.getsizeof(dictionary) >= self._blocksize:
                    break
        sorted_terms = sorted(dictionary.keys())

        return self._write_to_disk(sorted_terms, dictionary) if sorted_terms else None

    @staticmethod
    def _add_to_dict(dictionary: dict, term: str):
        """Add the term to the dictionary and create an empty postings list

        :param dictionary: Dictionary onto which to add the term
        :param term: Term to add to the dictionary
        :type dictionary: dict
        :type term: str
        :return: New postings list
        :rtype: List
        """
        dictionary[term] = []
        return dictionary[term]

    @staticmethod
    def _get_posting_list(dictionary: dict, term: str):
        """Retrieves the postings list from thedictionary for the given term

        :param dictionary: Dictionary to search in
        :param term: Term to search
        :type dictionary: dict
        :type term: str
        :return: Existing postings list for term
        :rtype: List[Posting]
        """
        return dictionary[term]

    @staticmethod
    def _add_to_posting_list(posting_list: List[Posting], docid: str, pos: int):
        """Adds the given docid and position to the posting_list

        :param posting_list: Posting List to add the docid and pos
        :param docid: Docid to add
        :param pos: Pos of the term in this doc
        :type posting_list: List[Posting]
        :type docid: str
        :type pos: int
        :return: None
        """

        existing_postings = [item for item in posting_list if item.docid is docid]
        # Sanity check, big error if this is called
        if len(existing_postings) > 1:
            raise SPIMIException("This behaviour should never happen: Error in implementation")
        if not existing_postings:
            posting_list.append(Posting(docid, [pos]))
        else:
            for p in existing_postings:
                p.positions.append(pos)

    def _write_to_disk(self, sorted_terms: list, dictionary: dict):
        """Writes a the partial index to a file block on disk.

        :param sorted_terms: List of sorted terms in the index
        :param dictionary: inverted index
        :type sorted_terms: List[str]
        :type dictionary: Dict[str, List[Posting]]
        :return: block file name
        """
        output_file_name = "{}/{}_{}.blk".format(self._dir, SPIMI.BLOCK_NAME_PREFIX, self._next_block_suffix)
        try:
            output_file = open(output_file_name, "w+")
            for term in sorted_terms:
                postings = dictionary[term]
                output_file.write(extern_output(TermPostings(term, postings)))
            output_file.flush()
            output_file.close()
            self._next_block_suffix += 1
            return output_file.name
        except IOError as e:
            print("Unable to open block to write the file {}".format(output_file_name))
            print(e)


class SPIMIException(Exception):
    pass
