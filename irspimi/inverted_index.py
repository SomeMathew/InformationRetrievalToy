from typing import List, Dict
from functools import total_ordering
import re
from dict_compression import MultipleCompression, NoNumbers, CaseFolding, NoStopWords, PorterStemmer
import dict_compression
import json

DICTIONARY_FILE_SUFFIX = "dictionary"
INVERTED_INDEX_DESCRIPTOR_SUFFIX = "desc"


class InvertedIndex:
    def __init__(self, index_filename: str):
        self._dictionary = {}
        self._descriptor = None
        self._index_file = open(index_filename)
        self._load_dictionary("{}.{}".format(index_filename, DICTIONARY_FILE_SUFFIX))
        self._load_descriptor("{}.{}".format(index_filename, INVERTED_INDEX_DESCRIPTOR_SUFFIX))
        self.avg_doclength = sum(self._descriptor.doclengths.values()) / len(self._descriptor.doclengths)

    def _load_dictionary(self, filename: str):
        with open(filename, "r") as f:
            for next_line in f:
                next_line = next_line.strip()
                if next_line:
                    term, file_pos = next_line.split(" : ")
                    self._dictionary[term] = int(file_pos)

    def _load_descriptor(self, filename):
        self._descriptor = InvertedIndexDescriptor.build_from_file(filename)

    def get_postings(self, term: str):
        """Retrieves the postings for a given term

        :param term: term to search for
        :return: Postings list for the search term
        :rtype: TermPostings
        """
        if self._descriptor.compression:
            term = self._descriptor.compression.compress(term)
        # Fix for compression which filters out words, differentiates the case where no postings are found from
        # the case where the term should be disregarded for the search
        if term is None:
            return None
        if term in self._dictionary:
            self._index_file.seek(self._dictionary[term])
            return extern_input(self._index_file.readline())
        else:
            return TermPostings(term, [])

    def get_multiple_postings(self, terms: List[str]):
        postings_map = {}
        for term in terms:
            postings = self.get_postings(term)
            postings_map[term] = postings
        return postings_map

    def get_universe(self):
        return self._descriptor.docid_list

    def get_doclength(self, docid: int):
        docid = int(docid)
        if docid in self._descriptor.doclengths:
            return self._descriptor.doclengths[docid]
        else:
            return 0



class InvertedIndexDescriptor:
    def __init__(self, docid_list: list, doclengths: Dict[int, int], compression: dict_compression.Compression = None):
        self.docid_list = sorted(docid_list) if docid_list else None
        self.doclengths = doclengths
        self.compression = compression

    def _as_dict(self):
        return {"compression": repr(self.compression), "doclengths": self.doclengths}

    def write_to_file(self, filename: str):
        f = open(filename, "w")
        json.dump(self._as_dict(), f, indent=4)
        f.close()

    @staticmethod
    def build_from_file(filename: str):
        """Builds a descriptor from a JSON file

        :param filename: Filename to find the descriptor details
        :return: Inverted Index Descriptor
        :rtype: InvertedIndexDescriptor
        """
        f = open(filename, "r")
        descriptor_dict = json.load(f)
        doclengths = descriptor_dict["doclengths"]
        docid_list = list(doclengths.keys())
        compression = eval(descriptor_dict["compression"]) if "compression" in descriptor_dict and \
                                                              descriptor_dict["compression"] else None
        descriptor = InvertedIndexDescriptor(docid_list, doclengths, compression)

        return descriptor


@total_ordering
class Posting:
    def __init__(self, docid: int, positions: List[int]):
        self.docid = docid
        self.positions = positions

    def __eq__(self, other):
        if isinstance(other, int):
            return self.docid == other
        elif isinstance(other, Posting):
            return self.docid == other.docid
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, int):
            return self.docid < other
        elif isinstance(other, Posting):
            return self.docid < other.docid
        else:
            return NotImplemented

    def __repr__(self):
        return "Posting(docid={}, positions={})".format(self.docid, self.positions)

    def __str__(self):
        positions_str = ",".join(str(pos) for pos in self.positions) if self.positions else None
        return "({}, {})".format(self.docid, positions_str)


class TermPostings:
    def __init__(self, term: str, postings: List[Posting]):
        self.term = term
        self.postings = postings


def extern_output(term_postings: TermPostings):
    return "{} : {}\n".format(term_postings.term,
                              ",".join(
                                  "{}[{}]".format(str(posting.docid),
                                                  "|".join(str(pos) for pos in posting.positions))
                                  for posting in term_postings.postings))


def extern_input(line: str):
    """Parse an external string representation of postings for a term

    :param line: Expression from external file to parse
    :type line: str
    :return: Postings for this line ***(term, List[(docid, List[position])]
    :rtype: TermPostings
    """
    term, raw_postings = line.split(" : ")
    raw_postings = [p for p in raw_postings.split(",")]
    pos_pattern = re.compile("([0-9]+)\[(.*)\]")

    postings = []
    for posting in raw_postings:
        match = pos_pattern.match(posting)
        if not match:
            raise Exception("Error when parsing string for postings: Aborting")
        docid = int(match.group(1))
        positions = [int(p) for p in match.group(2).split("|")]
        postings.append(Posting(docid, positions))

    return TermPostings(term, postings)
