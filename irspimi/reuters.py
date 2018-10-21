## Module to load and parse the reuters corpus
import string
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from itertools import chain
from dict_compression import Compression
from collections import namedtuple, deque, OrderedDict
from typing import List

LAST_DOCID = 21578
DOC_PER_FILE = 1000


class ReutersDocument:
    SOUP_CACHE_SIZE = 5
    _soup_cache = OrderedDict()

    def __init__(self, soup):
        self._soup = soup
        self.docid = int(self._soup['newid'])
        self._clean_tags()

    def _clean_tags(self):
        """Remove the bogus or unnecessary tags that shouldn't be indexed (UNKNOWN, MKNOTE)."""
        for unknown_tag in self._soup.find_all("unknown"):
            unknown_tag.extract()
        for mknote_tag in self._soup.find_all("unknown"):
            mknote_tag.extract()

    def get_tokens(self):
        """Retrieves a buffer of tokens for this document.

        :return: Queue of tokens for this document
        :rtype: deque
        """
        if not self._soup:
            raise ReutersCorpusException("Could not parse the reuters SGML")
        # remove new line or carriage return escape chars
        text = self._soup.get_text().translate(str.maketrans('\n\r', '  '))
        # tokenize by words using the default NLTK word tokenizer
        # and remove stray punctuation
        sentences = sent_tokenize(text)
        tokens = deque(tok for tok in chain.from_iterable([word_tokenize(sent) for sent in sentences]) if
                       tok not in list(string.punctuation))
        return tokens

    def get_title(self):
        if not self._soup:
            raise ReutersCorpusException("Could not parse the reuters SGML")
        title_list = self._soup.find_all("title")
        if title_list:
            return "\n".join(title.get_text() for title in title_list)
        else:
            return ""

    def __str__(self):
        return str(self._soup)

    @staticmethod
    def retrieve_doc(docid, reuters_path="."):
        """ Factory to get a ReutersDocument from a given docid

        :param docid: Document Id
        :param reuters_path: Path to the reuters corpus
        :return: The ReutersDocument for this docid
        :rtype: ReutersDocument
        """

        filename = ReutersDocument._docid_location_filename(docid)
        if not filename:
            return None
        filepath = "{}/{}".format(reuters_path, filename)

        if filename in ReutersDocument._soup_cache:
            soup = ReutersDocument._soup_cache[filename]
            ReutersDocument._soup_cache.move_to_end(filename)
        else:
            try:
                file = open(filepath, 'r', errors='ignore')
                soup = BeautifulSoup(file, "html.parser")
                ReutersDocument._cache_soup(filename, soup)
            except IOError as e:
                print("Could not find {}".format(filename))
                print(e)

        docs = soup.select("reuters[newid=\"{}\"]".format(docid))
        if docs:
            return ReutersDocument(docs[0])
        return None

    @staticmethod
    def _cache_soup(filename, soup):
        if len(ReutersDocument._soup_cache) >= ReutersDocument.SOUP_CACHE_SIZE:
            ReutersDocument._soup_cache.popitem(last=False)
        ReutersDocument._soup_cache[filename] = soup

    @staticmethod
    def _docid_location_filename(docid):
        """Returns the filename to where this docid resides in the Corpus"""
        docid = int(docid)

        if docid < 1 or docid > LAST_DOCID:
            return None
        file_id = int((docid - 1) / DOC_PER_FILE)
        return "reut2-{:03}.sgm".format(file_id)


DocToken = namedtuple("DocToken", ['token', 'docid', 'pos'])


class ReutersCorpusStream:
    def __init__(self, files: list, compression: Compression = None):
        self._files = files if files else []
        self._docs = []
        self._current_tokens = None
        self._current_docid = None
        self._current_pos = 0
        self._compression = compression
        self.docid_list = []

    def __iter__(self):
        return self

    def __next__(self):
        if not self._current_tokens:
            nextdoc = self._next_doc()
            if not nextdoc:
                raise StopIteration
            self._current_docid = nextdoc.docid
            self.docid_list.append(nextdoc.docid)
            self._current_tokens = nextdoc.get_tokens()
            self._current_pos = 0
        if self._current_tokens:
            next_token = self._current_tokens.popleft()
            self._current_pos += 1
            if self._compression:
                next_token = self._compression.compress(next_token)
                if not next_token:
                    return self.__next__()
            return DocToken(token=next_token, docid=self._current_docid, pos=self._current_pos)
        else:
            raise StopIteration

    def _next_doc(self):
        if not self._docs:
            self._docs = self._fetch_next_chunk()
        return self._docs.popleft() if self._docs else None

    def has_next_doc(self):
        if not self._docs:
            self._docs = self._fetch_next_chunk()
        return self._docs is not None and len(self._docs) != 0

    def _fetch_next_chunk(self):
        """Retrieves the next chunk of documents for the Reuters Corpus

        :return: Buffer of ReutersDocument
        :rtype: deque
        """
        reuters_docs = deque()
        current_file = None
        while self._files and not current_file:
            filename = self._files.pop(0)
            try:
                current_file = open(filename, 'r', errors='ignore')
                soup = BeautifulSoup(current_file, "html.parser")
                reuters_docs.extend(ReutersDocument(doc) for doc in soup.find_all("reuters"))
            except IOError:
                print("Could not find {}".format(filename))
        return reuters_docs


class ReutersCorpusException(Exception):
    pass


def docs_details(docids: List[int], reuters_path: str):
    details = {}
    for docid in docids:
        doc = ReutersDocument.retrieve_doc(docid, reuters_path)
        if doc:
            details[docid] = doc
    return details
