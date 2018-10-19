class InvertedIndex:
    def __init__(self, filename: str):
        self._index = {}
        self.load_index(filename)

    def _load_index(self, filename: str):
        with open(filename, "r") as f:
            for next_line in f:
                next_line = next_line.strip()
                if next_line:
                    term, postings = next_line.split(" : ")
                    postings = [int(i) for i in postings.split(",")]
                    self._index[term] = postings

    def get_postings(self, term: str):
        if term in self._index:
            return self._index[term]
        else:
            return []
