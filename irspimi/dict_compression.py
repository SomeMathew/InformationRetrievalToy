from abc import ABC, abstractmethod
from nltk.stem.porter import PorterStemmer as PS
from typing import List
import string
import re


class Compression(ABC):
    @abstractmethod
    def compress(self, token: str):
        pass


class MultipleCompression(Compression):
    def __init__(self, filters: List[Compression]):
        self.filters = filters

    def compress(self, token: str):
        last_tok = token
        for sf in self.filters:
            last_tok = sf.compress(last_tok)
            if not last_tok:
                return last_tok
        return last_tok


class NoNumbers(Compression):
    def __init__(self):
        self._regex_punct = re.compile("[{}]".format(string.punctuation))
        self._regex_num = re.compile("^-?[0-9]+(.[0-9]+)?$")

    def compress(self, token: str):
        if self._regex_num.match(re.sub(self._regex_punct, '', token)) is not None:
            return None
        else:
            return token

    def __repr__(self):
        return "NoNumbers()"


class CaseFolding(Compression):
    def compress(self, token: str):
        return token.casefold()

    def __repr__(self):
        return "CaseFolding()"


class NoStopWords(Compression):
    def __init__(self, count: int, filename: str):
        self._count = count
        self._filename = filename
        try:
            f = open(filename, "r")
            self._stop_words = []
            for i in range(0,count):
                w = f.readline().strip()
                if w:
                    self._stop_words.append(w)
        except IOError as e:
            print("Error while reading {}: {}".format(filename, e))

    def compress(self, token: str):
        return token if token not in self._stop_words else None

    def __repr__(self):
        return "NoStopWords(count={}, filename=\"{}\")".format(self._count, self._filename)


class PorterStemmer(Compression):
    def __init__(self):
        self._porter_stemmer = PS()

    def compress(self, token: str):
        return self._porter_stemmer.stem(token)

    def __repr__(self):
        return "PorterStemmer()"
