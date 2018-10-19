from typing import TextIO, List
from heapq import heappush, heappop


class MergeSPIMI:
    def __init__(self, in_files: List[str], out_file: str, output_buffer_length: int = 50, input_buffer_length: int = 50):
        self._input_buffer_length = input_buffer_length
        self._output_buffer_length = output_buffer_length
        self._output_buffer = []
        self._files = []
        for file_name in in_files:
            try:
                f = open(file_name, "r")
                self._files.append(f)
            except IOError as e:
                print("Unable to open input file {}".format(file_name))
                print(e)

        try:
            self._out = open(out_file, 'w')
        except IOError as e:
            print("Unable to open output file {} to write the index.".format(out_file))
            print(e)

        # Build the input buffer and heap
        self._next_terms_heap = []
        self._input_buffer = [None] * len(self._files)
        for i in range(0, len(self._files)):
            self._refill_buffer(i)

    def external_merge(self):
        while self._next_terms_heap:
            self._output_buffer.append(self._get_next_postings())
            if self._output_buffer_full() or not self._next_terms_heap:
                self._write_out_buffer()

    def _write_out_buffer(self):
        for term, postings in self._output_buffer:
            self._out.write("{} : {}\n".format(term, ",".join(str(x) for x in postings)))
        self._out.flush()
        self._output_buffer = []

    def _output_buffer_full(self):
        return len(self._output_buffer) >= self._output_buffer_length

    @staticmethod
    def _fetch_next_chunks(file: TextIO, line_count=10):
        """Retrieves the next lines from the given file stream.

        Args:
            file (TextIO): Opened file stream seeked at the next line to retrieve.
            line_count (int): Number of lines to read.

        Returns:
            List[(str, List[int])]: Lines from the files as (Term, postings) tuples.
        """
        lines = []
        for i in range(0,line_count):
            next_line = file.readline().strip()
            if next_line:
                term, postings = next_line.split(" : ")
                postings = [int(i) for i in postings.split(",")]
                lines.append((term, postings))
        return lines

    def _get_next_postings(self):
        """Retrieves the next merged postings from all input buffers in alphabetical Order.

        This will replenish an input buffer if it is empty.

        Returns:
            (str, List[int]): Merged postings list for the next term from the input buffer.
        """
        postings_merged = []
        if self._next_terms_heap:
            next_term, next_ifile = self._next_terms_heap[0] # peek next tuple
            while self._next_terms_heap and self._next_terms_heap[0][0] == next_term:
                next_term, next_ifile = heappop(self._next_terms_heap)
                buffer_term, postings = self._input_buffer[next_ifile].pop(0)
                postings_merged = MergeSPIMI._merge_postings(postings_merged, postings)
                # Fetch next chunks if the input buffer is now empty
                if not self._input_buffer[next_ifile]:
                    self._refill_buffer(next_ifile)
        return next_term, postings_merged

    def _refill_buffer(self, ifile: int):
        """ Fills the input buffer for the given file index

        :param ifile:
        :return:
        """
        next_lines = MergeSPIMI._fetch_next_chunks(self._files[ifile], self._input_buffer_length)

        if self._input_buffer[ifile] is None:
            self._input_buffer[ifile] = []
        self._input_buffer[ifile].extend(next_lines)

        # Build the heap with each next postings in the input buffers
        for l in next_lines:
            term, postings = l
            heappush(self._next_terms_heap, (term, ifile))


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
