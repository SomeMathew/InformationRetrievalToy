from abc import ABC, abstractmethod
from nltk.stem.porter import PorterStemmer as PS
import string
import re


class Compression(ABC):
    @abstractmethod
    def compress(self, token: str):
        pass


class NoNumbers(Compression):
    def __init__(self):
        self._regex_punct = re.compile("[{}]".format(string.punctuation))
        self._regex_num = re.compile("^-?[0-9]+(.[0-9]+)?$")

    def compress(self, token: str):
        if self._regex_num.match(re.sub(self._regex_punct, '', token)) is not None:
            return None
        else:
            return token


class CaseFolding(Compression):
    def compress(self, token: str):
        return token.casefold()


class NoStopWords(Compression):
    def __init__(self, count: int, filename: str):
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


class PorterStemmer(Compression):
    def __init__(self):
        self._porter_stemmer = PS()

    def compress(self, token: str):
        return self._porter_stemmer.stem(token)
