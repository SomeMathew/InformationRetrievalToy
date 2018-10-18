## Module to load and parse the reuters corpus
import string
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from itertools import chain


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
        if not self._soup:
            raise ReutersCorpusException("Could not parse the reuters SGML")
        # remove new line or carriage return escape chars
        text = self._soup.get_text().translate(str.maketrans('\n\r', '  '))
        # tokenize by words using the default NLTK word tokenizer
        # and remove stray punctuation
        sentences = sent_tokenize(text)
        tokens = [tok for tok in chain.from_iterable([word_tokenize(sent) for sent in sentences]) if
                  tok not in list(string.punctuation)]
        return tokens


class ReutersToken:
    """ Token from a particular document.

    Attributes:
        token (str): Token String.
        docid (str): Document Id of this token.
    """

    def __init__(self, token: str, docid: str):
        self.token = token
        self.docid = docid


class ReutersCorpus:
    def __init__(self, files: list):
        self._files = files if files else []
        self._docs = []
        self._current_tokens = None
        self._current_docid = None
        # self._current_doc = None

    def __iter__(self):
        return self

    def __next__(self):
        if not self._current_tokens:
            nextdoc = self._next_doc()
            if not nextdoc:
                raise StopIteration
            self._current_docid = nextdoc.docid
            self._current_tokens = nextdoc.get_tokens()
        if self._current_tokens:
            return ReutersToken(self._current_tokens.pop(0), self._current_docid)
        else:
            raise StopIteration

    def _next_doc(self):
        if not self._docs:
            self._docs = self._fetch_next_chunk()
        return self._docs.pop(0) if self._docs else None

    def has_next_doc(self):
        if not self._docs:
            self._docs = self._fetch_next_chunk()
        return self._docs is not None and len(self._docs) != 0

    def _fetch_next_chunk(self):
        reuters_docs = []
        current_file = None
        while self._files and not current_file:
            filename = self._files.pop(0)
            try:
                current_file = open(filename, 'r')
                soup = BeautifulSoup(current_file, "html.parser")
                reuters_docs = [ReutersDocument(doc) for doc in soup.find_all("reuters")]
            except IOError:
                print("Could not find {}".format(filename))
        return reuters_docs


# class TokenStream:
#     def __init__(self, corpus: ReutersCorpus):
#         self._corpus = corpus
#         self._docid = None
#         self._tokens = None
#
#     def set_preprocessor(self, preprocessor):
#         ## TODO method stub
#         pass
#
#     def next_token(self):
#         if not self._tokens:
#             self._fetch_next_doc()
#         if self._tokens:
#             return Token(self._tokens.pop(0), self._docid)
#         else:
#             return None
#
#     def has_next_token(self):
#         return self._corpus.has_next_doc() or len(self._tokens) != 0
#
#     def _fetch_next_doc(self):
#         if not self._corpus:
#             raise ReutersCorpusException("Reuters Corpus does not exists")
#         nextdoc = self._corpus.next_doc()
#         if nextdoc:
#             self._docid = nextdoc.docid
#             self._tokens = nextdoc.get_tokens()


class ReutersCorpusException(Exception):
    pass
