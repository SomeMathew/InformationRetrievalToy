from typing import List
from inverted_index import Posting
import reuters


class EvaluationResult:
    def __init__(self):
        self.postings_map = {}
        self.term_map = {}
        self.query_result = None
        self.results = None
        self.complete = False

    def add_postings(self, term: str, postings: List[Posting]):
        """Add postings list to the evaluation result"""
        self.postings_map[term] = postings
        for p in postings:
            if p.docid not in self.term_map:
                self.term_map[p.docid] = []
            self.term_map[p.docid].append(term)

    def update_results(self, query_result: List[Posting]):
        """Update the results once they are computed for query"""
        self.query_result = query_result
        self.results = {posting.docid: {
            "positions": posting.positions,
            "terms": self.term_map[posting.docid] if posting.docid in self.term_map else []
        } for posting in self.query_result}

        self.complete = True

    def update_ranked_results(self, query_result: Heap):

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
