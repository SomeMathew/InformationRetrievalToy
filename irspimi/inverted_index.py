from typing import List
from functools import total_ordering
import re


class InvertedIndex:
    DICTIONARY_FILE_SUFFIX = "dictionary"

    def __init__(self, filename: str):
        self._dictionary = {}
        self._index_file = open(filename)
        self._load_dictionary("{}.{}".format(filename, InvertedIndex.DICTIONARY_FILE_SUFFIX))

    def _load_dictionary(self, filename: str):
        with open(filename, "r") as f:
            for next_line in f:
                next_line = next_line.strip()
                if next_line:
                    # term_posting = extern_input(next_line)
                    # self._dictionary[term_posting.term] = term_posting
                    term, file_pos = next_line.split(" : ")
                    self._dictionary[term] = int(file_pos)

    def get_postings(self, term: str):
        """Retrieves the postings for a given term

        :param term: term to search for
        :return: Postings list for the search term
        :rtype: List[Posting]
        """
        if term in self._dictionary:
            self._index_file.seek(self._dictionary[term])
            return extern_input(self._index_file.readline()).postings
        else:
            return []

    def get_multiple_postings(self, terms: List[str]):
        map = {}
        for term in terms:
            postings = self.get_postings(term)
            map[term] = postings
        return map


@total_ordering
class Posting:
    def __init__(self, docid: int, positions: List[int]):
        self.docid = docid
        self.positions = positions

    def __eq__(self, other):
        if not isinstance(other, Posting):
            return NotImplemented
        return self.docid == other.docid

    def __lt__(self, other):
        if not isinstance(other, Posting):
            return NotImplemented
        return self.docid < other.docid

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
