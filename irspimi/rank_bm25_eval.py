# Search module for ranked retrieval using the bag of words model and BM25 ranking function.
from inverted_index import InvertedIndex, TermPostings
from nltk import word_tokenize
from typing import List, Dict
from math import log2
from eval_result import EvaluationResult
from operator import itemgetter


class RankedSearchBM25:
    def __init__(self, query: str, index: InvertedIndex, k1: float = 1.2, b: float = 0.75):
        """Initializes the query processor for Ranked Retrieval using Okapi BM25.
        To use: create the object then call the evaluate method.

        :param query: Search query - Will be processed as a bag of word (no boolean ops)
        :type query: str
        :param index: InvertedIndex to search with
        :type index: InvertedIndex
        :param k1: Weight of the term frequency effect on scoring. 0 disregards tf.
        :type k1: float
        :param b: Scaling in of document length, b in [0,1]. 0 -> no length normalization, 1 -> full scaling.
        :type b: float
        """
        self.query = word_tokenize(query)
        self.index = index
        self.k1 = k1
        self.b = b

    def evaluate(self):
        """Evaluates the search query.

        :return: Ranked Search query results
        :rtype: EvaluationResult
        """
        term_postings_list = []
        for t in self.query:
            term_postings = self.index.get_postings(t)
            if term_postings is not None:
                term_postings.term = t
                term_postings_list.append(term_postings)

        scored_results = self._search_scored(term_postings_list)
        ranked_results = self._build_result(term_postings_list, scored_results)
        return ranked_results

    @staticmethod
    def _build_result(term_postings_list: List[TermPostings], scored_result: Dict[int, float]):
        """ Build the evaluation result structure based on the scoring.

        :param scored_result: Dictionary of docid to weight
        :return: Ranked result as and EvaluationResult
        :rtype: EvaluationResult
        """
        results = EvaluationResult()
        for term_posting in term_postings_list:
            results.add_postings(term_posting.term, term_posting.postings)

        ranked_score = sorted(scored_result.items(), key=itemgetter(1), reverse=True)
        results.update_ranked_results(ranked_score)
        return results

    def _search_scored(self, term_postings_list: List[TermPostings]):
        """ Score the resulting list of documents using the BM25 weight.

        Term at a time ranking is used in this implementation.

        :param term_postings_list: List of TermPostings for the terms in the search
        :type term_postings_list: List[TermPostings]
        :return: Dictionary of docid to bm25 weight
        :rtype: Dict[int, float]
        """
        accumulators = {}
        doc_count = self.index.get_doc_count()
        for term_postings in term_postings_list:
            idf = log2(doc_count / len(term_postings.postings)) if term_postings.postings else 0
            for p in term_postings.postings:
                tf = len(p.positions)
                dl = self.index.get_doclength(p.docid)

                if p.docid not in accumulators:
                    accumulators[p.docid] = 0
                termWeight = self._compute_bm25_term(idf, tf, dl)
                # Useful output to evaluate the weighting components - Used in the report
                # if p in [20891, 4008, 16780, 8593, 3560, 20860, 20719, 7525, 8500, 16824]:
                #     print("term:{}, doc: {}, doc_len: {}, idf: {:.2f}, tf: {}, term weight: {:.2f}".format(
                #         term_postings.term,
                #         p.docid, dl, idf, tf,
                #         termWeight))
                accumulators[p.docid] += termWeight
        return accumulators

    def _compute_bm25_term(self, idf, tf, dl):
        """Computes the partial bm25 weight for 1 term in a doc. This result should be accumulated for each doc"""
        davg = self.index.avg_doclength
        return idf * ((self.k1 + 1) * tf) / (
                self.k1 * ((1 - self.b) + self.b * (dl / davg)) + tf)
