from typing import List


def search(expression: str):
    pass

def intersect(postings1: List[int], postings2: List[int]):
    intersection = []
    i = 0
    j = 0
    if postings1 and postings2:
        while i < len(postings1) and j < len(postings2):
            if postings1[i] == postings2[j]:
                intersection.append(postings1[i])
                i += 1
                j += 1
            elif postings1[i] < postings2[j]:
                i += 1
            else:
                j += 1
    return intersection


def union(postings1: List[int], postings2: List[int]):
    union_set = []
    i = 0
    j = 0
    postings1 = postings1 if postings1 is not None else []
    postings2 = postings2 if postings2 is not None else []
    while i < len(postings1) and j < len(postings2):
        if postings1[i] == postings2[j]:
            union_set.append(postings1[i])
            i += 1
            j += 1
        elif postings1[i] < postings2[j]:
            union_set.append(postings1[i])
            i += 1
        else:
            union_set.append(postings2[j])
            j += 1

    remaining_list = postings1 if i < len(postings1) else postings2 if j < len(postings2) else None

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


# Test TODO remove
# a = [3, 4, 5, 6, 7, 8, 10]
# b = [1, 2, 5, 10]
# c = [6, 10]
# d = []
# e = None
# print("Intersection")
# print(intersect(a, b))
# print(intersect(a, c))
# print(intersect(a, d))
# print(intersect(e, a))
# print(intersect(a, a))
#
# print("Union")
# print(union(a, b))
# print(union(a, c))
# print(union(a, d))
# print(union(e, a))
# print(union(a, a))
#
# print("Difference")
# print("A={}, B={}, A-B={}".format(a, b, subtract(a, b)))
# print("A={}, B={}, A-B={}".format(a, c, subtract(a, c)))
# print("A={}, B={}, A-B={}".format(a, d, subtract(a, d)))
# print("A={}, B={}, A-B={}".format(e, a, subtract(e, a)))
# print("A={}, B={}, A-B={}".format(a, a, subtract(a, a)))
#
# U = [x for x in range(1,21)]
# print("Neg")
# print("A={}, Not A={}".format(a, subtract(U, a)))
# print("A={}, Not A={}".format(b, subtract(U, b)))
# print("A={}, Not A={}".format(c, subtract(U, c)))
# print("A={}, Not A={}".format(d, subtract(U, d)))
# print("A={}, Not A={}".format(e, subtract(U, e)))
