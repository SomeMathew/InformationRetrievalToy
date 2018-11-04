from typing import List, Tuple
from inverted_index import Posting
from collections import OrderedDict
import reuters


class EvaluationResult:
    def __init__(self):
        self.postings_map = {}
        self.term_map = {}
        self.results = None
        self.complete = False
        self.ranked = None

    def add_postings(self, term: str, postings: List[Posting]):
        """Add postings list to the evaluation result"""
        self.postings_map[term] = postings
        for p in postings:
            if p.docid not in self.term_map:
                self.term_map[p.docid] = []
            self.term_map[p.docid].append(term)

    def update_results(self, query_result: List[Posting]):
        """Update the results once they are computed for query"""
        self.results = {posting.docid: {
            "positions": posting.positions,
            "terms": self.term_map[posting.docid] if posting.docid in self.term_map else []
        } for posting in query_result}

        self.complete = True
        self.ranked = False

    def update_ranked_results(self, query_results: List[Tuple[int, float]]):
        """ Update the ranked results. This should be used after postings list have been added with add_postings.

        :param query_results: Ordered list of tuple (docid, weight)
        :type query_results: List[Tuple[int, float]]
        :return: None
        """
        self.results = OrderedDict(
            (docid, {
                "terms": self.term_map[docid] if docid in self.term_map else [],
                "weight": weight
            }) for docid, weight in query_results)

        self.complete = True
        self.ranked = True

    def get_postings(self, term: str):
        """Retrieves the postings for a given term"""
        postings = None
        if term in self.postings_map:
            postings = self.postings_map[term]
        else:
            postings = []

    def get_terms(self, docid: int):
        """Retrieves the terms found in the given docid"""
        terms = None
        if docid in self.term_map:
            terms = self.term_map[docid]

        return terms if terms is not None else []

    def update_details(self, reuters_path: str, docid: int = None):
        """Updates the results with the title of each doc and the doc reference"""
        if docid:
            reuters_details = reuters.docs_details([docid], reuters_path)
        else:
            reuters_details = reuters.docs_details(self.results.keys(), reuters_path)

        for docid, doc in reuters_details.items():
            if docid in self.results:
                self.results[docid]["title"] = doc.get_title()
                self.results[docid]["doc"] = doc
