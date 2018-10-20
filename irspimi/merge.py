from typing import TextIO, List
from heapq import heappush, heappop
from inverted_index import extern_input, extern_output, TermPostings, Posting
from collections import deque


class MergeSPIMI:
    DICTIONARY_FILE_SUFFIX = "dictionary"

    def __init__(self, in_files: List[str], out_file: str, output_buffer_length: int = 50,
                 input_buffer_length: int = 50):
        """Initializes a merger object for the SPIMI algorithm.
        This object uses an external k-way merge to complete the work.

        :param in_files: List of index blocks filename to merge
        :param out_file: Name of the output file for the merged index
        :param output_buffer_length: Length of the output buffer, for each term and posting list
        :param input_buffer_length: Length of each input buffer for each block
        """
        self._input_buffer_length = input_buffer_length
        self._output_buffer_length = output_buffer_length
        self._output_buffer = deque(maxlen=output_buffer_length)
        self._files = []
        for file_name in in_files:
            try:
                f = open(file_name, "r")
                self._files.append(f)
            except IOError as e:
                print("Unable to open input file {}".format(file_name))
                print(e)

        try:
            cur_file = out_file
            self._out = open(cur_file, "w")
            cur_file = "{}.{}".format(out_file, MergeSPIMI.DICTIONARY_FILE_SUFFIX)
            self._out_dict = open(cur_file, "w")
        except IOError as e:
            print("Unable to open output file {} to write.".format(cur_file))
            print(e)

        # Build the input buffer and heap
        self._next_terms_heap = []
        self._input_buffer = [None] * len(self._files)
        for i in range(0, len(self._files)):
            self._refill_buffer(i)

    def external_merge(self):
        """Execute the merge according to the initialized settings.

        :return: None
        """
        while self._next_terms_heap:
            self._output_buffer.append(self._get_next_postings())
            if self._output_buffer_full() or not self._next_terms_heap:
                self._write_out_buffer()
        self._out.close()
        self._out_dict.close()

    def _write_out_buffer(self):
        """Empties and writes the current output buffer to the index file on disk.

        :return: None
        """

        while self._output_buffer:
            term_postings = self._output_buffer.popleft()
            file_pos = self._out.tell()
            self._out.write(extern_output(term_postings))
            self._out_dict.write("{} : {}\n".format(term_postings.term, file_pos))

        self._out.flush()
        self._out_dict.flush()

    def _output_buffer_full(self):
        """Checks if the output buffer is full.

        :return: True if the buffer is full, False otherwise
        :rtype: bool
        """
        return len(self._output_buffer) >= self._output_buffer_length

    def _get_next_postings(self):
        """Retrieves the next merged postings from all input buffers in alphabetical Order.

        This will replenish an input buffer if it is empty.

        :return: Merged postings list for the next term from the input buffers.
        :rtype: TermPostings
        """
        postings_merged = []
        if self._next_terms_heap:
            next_term, next_ifile = self._next_terms_heap[0]  # peek next tuple

            while self._next_terms_heap and self._next_terms_heap[0][0] == next_term:
                next_term, next_ifile = heappop(self._next_terms_heap)
                next_term_postings = self._input_buffer[next_ifile].popleft()

                postings_merged = MergeSPIMI._merge_postings(postings_merged, next_term_postings.postings)

                # Fetch next chunks if the input buffer is now empty
                if not self._input_buffer[next_ifile]:
                    self._refill_buffer(next_ifile)
        return TermPostings(next_term, postings_merged)

    def _refill_buffer(self, ifile: int, line_count: int = 10):
        """ Fills the input buffer for the given file index

        :param ifile: File and buffer index to refill
        :param line_count: Number of lines to fill
        :return: None
        """
        if self._input_buffer[ifile] is None:
            self._input_buffer[ifile] = deque()

        buffer = self._input_buffer[ifile]
        file = self._files[ifile]
        for i in range(0, line_count):
            next_line = file.readline().strip()
            if next_line:
                term_postings = extern_input(next_line)
                buffer.append(term_postings)
                heappush(self._next_terms_heap, (term_postings.term, ifile))

    @staticmethod
    def _merge_postings(l1, l2):
        """Merge the given lists and return a new merged List.
        If the input are Posting then the positions will also be merged by the same process.

        :param l1: List to merge
        :param l2: List to merge
        :type l1: List[Posting], List[int]
        :type l2: List[Posting], List[int]
        :return: New merged list with the elements of l1 and l2
        :rtype: List[Posting]
        """
        l1 = l1 if l1 is not None else []
        l2 = l2 if l2 is not None else []
        list.sort(l1)
        list.sort(l2)
        merged = []
        i = 0
        j = 0
        while i < len(l1) and j < len(l2):
            if l1[i] <= l2[j]:
                next_item = l1[i]
                i += 1
            else:
                next_item = l2[j]
                j += 1

            if len(merged) == 0 or next_item != merged[len(merged) - 1]:
                merged.append(next_item)
            elif isinstance(next_item, Posting) and next_item == merged[len(merged) - 1]:
                last_posting = merged[len(merged) - 1]
                last_posting.positions = MergeSPIMI._merge_postings(last_posting.positions, next_item.positions)

        # Empty the remaining list
        remaining_list, h = (l1, i) if i < len(l1) else (l2, j)
        while h < len(remaining_list):
            next_item = remaining_list[h]
            h += 1
            if len(merged) == 0 or next_item != merged[len(merged) - 1]:
                merged.append(next_item)
            elif isinstance(next_item, Posting) and next_item == merged[len(merged) - 1]:
                last_posting = merged[len(merged) - 1]
                last_posting.positions = MergeSPIMI._merge_postings(last_posting.positions, next_item.positions)

        return merged


## TODO remove this test
# mergeSpimi = MergeSPIMI(["blocktest_0.blk", "blocktest_1.blk"], "merge_test.index")
# mergeSpimi.external_merge()
