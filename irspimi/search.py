from typing import List
from inverted_index import TermPostings, Posting


def intersect(postings1: List[Posting], postings2: List[Posting]):
    intersection = []
    i = 0
    j = 0
    if postings1 and postings2:
        while i < len(postings1) and j < len(postings2):
            if postings1[i] == postings2[j]:
                intersection.append(
                    Posting(postings1[i].docid, sorted(postings1[i].positions + postings2[j].positions)))
                i += 1
                j += 1
            elif postings1[i] < postings2[j]:
                i += 1
            else:
                j += 1
    return intersection


def union(postings1: List[Posting], postings2: List[Posting]):
    union_set = []
    i = 0
    j = 0
    postings1 = postings1 if postings1 is not None else []
    postings2 = postings2 if postings2 is not None else []
    while i < len(postings1) and j < len(postings2):
        if postings1[i] == postings2[j]:
            union_set.append(Posting(postings1[i].docid, sorted(postings1[i].positions + postings2[j].positions)))
            i += 1
            j += 1
        elif postings1[i] < postings2[j]:
            union_set.append(postings1[i])
            i += 1
        else:
            union_set.append(postings2[j])
            j += 1

    # Empty the remaining lists
    while i < len(postings1):
        union_set.append(postings1[i])
        i += 1

    while j < len(postings2):
        union_set.append(postings2[j])
        j += 1

    return union_set


def neg(universe: List[int], postings: List[int]):
    return subtract(universe, postings)


def subtract(postings1: List[int], postings2: List[int]):
    difference = []
    postings1 = postings1 if postings1 is not None else []
    postings2 = postings2 if postings2 is not None else []
    i = 0
    j = 0
    while i < len(postings1) and j < len(postings2):
        if postings1[i] == postings2[j]:
            i += 1
            j += 1
        elif postings1[i] < postings2[j]:
            difference.append(postings1[i])
            i += 1
        else:
            j += 1

    # When here, either postings 1 is done or postings 2 is done
    # No other possibility, thus if its postings1 then add the rest
    while i < len(postings1):
        difference.append(postings1[i])
        i += 1

    return difference
