## Module to load and parse the reuters corpus
import string
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from itertools import chain
from dict_compression import Compression
from collections import namedtuple, deque


class ReutersDocument:
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


DocToken = namedtuple("DocToken", ['token', 'docid', 'pos'])


class ReutersCorpus:
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
