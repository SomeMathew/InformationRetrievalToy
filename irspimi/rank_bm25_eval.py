# Search module for ranked retrieval using the bag of words model and BM25 ranking function.
from inverted_index import InvertedIndex, TermPostings
from nltk import word_tokenize
from typing import List, Dict
from math import log2
from eval_result import EvaluationResult


class RankedSearchBM25:
    def __init__(self, query: str, index: InvertedIndex, k1: float = 1.2, b: float = 0.75):
        # TODO documentation
        self.query = word_tokenize(query)
        self.index = index
        self.k1 = k1
        self.b = b

    def evaluate(self):
        # TODO documentation
        term_postings_list = []
        for t in self.query:
            term_postings = self.index.get_postings(t)
            if term_postings is not None:
                term_postings_list.append(term_postings)

        scored_results = self._search_scored(term_postings_list)
        ranked_results = self._build_result(term_postings_list, scored_results)
        return ranked_results

    def _build_result(self, term_postings_list: List[TermPostings], scored_result: Dict[int, float]):
        """ Build the evaluation result structure based on the scoring.

        :param scored_result: Dictionary of docid to
        :return: Ranked result as and EvaluationResult
        :rtype: EvaluationResult
        """
        results = EvaluationResult()
        for term_posting in term_postings_list:
            results.add_postings(term_posting.term, term_posting.postings)


    def _search_scored(self, term_postings_list: List[TermPostings]):
        """ Score the resulting list of documents using the BM25 weight.

        :param term_postings_list: List of TermPostings for the terms in the search
        :type term_postings_list: List[TermPostings]
        :return: Dictionary of docid to bm25 weight
        :rtype: Dict[int, float]
        """
        accumulators = {}
        for term_postings in term_postings_list:
            idf = log2(len(term_postings.postings))
            for p in term_postings.postings:
                tf = len(p.positions)
                dl = self.index.get_doclength(p.docid)

                if p.docid not in accumulators:
                    accumulators[p.docid] = 0
                accumulators[p.p.docid] += self._compute_bm25_term(idf, tf, dl)
        return accumulators

    def _compute_bm25_term(self, idf, tf, dl):
        # TODO documentation
        davg = self.index.avg_doclength
        return idf * ((self.k1 + 1) * tf) / (
                self.k1 * ((1 - self.b) + self.b * (dl / davg)) + tf)
