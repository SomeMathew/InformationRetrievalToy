from typing import TextIO, List
from heapq import heappush, heappop


class MergeSPIMI:
    def __init__(self, in_files: List[str], out_file: str):
        self._files = in_files
        try:
            self._out = open(out_file, 'w')
        except IOError as e:
            print("Unable to open output file {} to write the index.".format(out_file))
            print(e)

        # Build the input buffer for each file
        self._input_buffer = [None] * len(self._files)
        for i in range(0, len(self._files)):
            try:
                f_name = self._files[i]
                f = open(f_name, "r")
                self._input_buffer[i] = self._fetch_next_chunks(f)
            except IOError as e:
                print("Unable to open input file {}".format(f_name))
                print(e)

        # Build the heap with each next postings in the input buffers
        self._next_terms_heap = []
        for i in range(0, len(self._next_terms_heap)):
            if self._input_buffer[i]:
                term, ifile = self._input_buffer[i]
                heappush(self._next_terms_heap, (term, ifile))

    @staticmethod
    def _fetch_next_chunks(file: TextIO, line_count=10):
        lines = []
        for i in range(0,line_count):
            next_line = file.readline()
            if next_line:
                term, postings = next_line.split(" : ")
                postings = [int(i) for i in postings.split(",")]
                lines.append((term, postings))
        return lines

    def external_merge(self):
        pass

    def _get_next_postings(self):
        postings_merged = []
        if self._next_terms_heap:
            next_term, next_ifile = self._next_terms_heap[0] # peek next tuple
            while self._next_terms_heap and self._next_terms_heap[0][0] == next_term:
                next_term, next_ifile = heappop(self._next_terms_heap)
                buffer_term, postings = self._input_buffer[next_ifile].pop(0)
                postings_merged = MergeSPIMI._merge_postings(postings_merged, postings)
                # Fetch next chunks if the input buffer is now empty
                if not self._input_buffer[next_ifile]:
                    MergeSPIMI._fetch_next_chunks(self._files[next_ifile])
        return next_term, postings_merged


    @staticmethod
    def _merge_postings(p1: List[int], p2: List[int]):
        p1 = p1 if p1 is not None else []
        p2 = p2 if p2 is not None else []
        list.sort(p1)
        list.sort(p2)
        merged = []
        while p1 and p2:
            next_list = p1 if p1[0] <= p2[0] else p2
            next_posting = next_list.pop(0)
            if len(merged) == 0 or next_posting != merged[len(merged) - 1]:
                merged.append(next_posting)

        # Empty the remaining list
        remaining_list = p1 if p1 else p2
        while remaining_list:
            next_posting = remaining_list.pop(0)
            if len(merged) == 0 or next_posting != merged[len(merged) - 1]:
                merged.append(next_posting)

        return merged
