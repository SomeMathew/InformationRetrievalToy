from reuters import ReutersCorpus
from spimi import SPIMI


# sentences = nltk.tokenize.sent_tokenize("This is a,test. With a non complete!".translate(str.maketrans('string.punctuation, ' ', string.punctuation)))
# print(word_tokenize("This is a test. With a non complete"))

# for s in sentences:
#     print(word_tokenize(s))


# doc = open("test.txt")
# rtdoc = ReutersDocument(doc.read())
# print(rtdoc.get_tokens())


# rtdoc_text = rtdoc.get_text()

# toks = sent_tokenize(rtdoc_text)
#
# print(toks)
#
# sentences_toks = [word_tokenize(sent) for sent in toks]
# word_toks =
# print (word_toks)

# print(list(string.punctuation))
# test = [t for t in word_toks if t not in list(string.punctuation)]
# print(test)
#
# doc_testful = open("reut2-000.sgm")
# soup = BeautifulSoup(doc_testful, 'html.parser')
# print(soup.reuters.get_text())
#
# rtdoc = ReutersDocument(soup.reuters)
# print(rtdoc.get_tokens())
#
# print(rtdoc._soup.find_all("unknown"))
#
#
# docs = soup.find_all('reuters')
#
# # for d in print(docs[0]['newid'])
#
# print([d['newid'] for d in docs])


# rc = ReutersCorpus(["reut2-000.sgm", "bad_file.txt", "reut2-001.sgm"])
#
# # docs = rc._fetch_next_chunk()
#
# # print(docs[0].get_tokens())
#
# # lst = []
# # while rc.has_next_doc():
# #     nextdoc = rc.next_doc()
# #     lst.append(nextdoc.docid)
# #
# # print(lst)
#
# # ts = TokenStream(rc)
#
# toklst = [t for t in rc]
# # while True:
# #     tok = ts.next_token()
# #     if tok is None:
# #         break
# #     toklst.append(tok)
# #
# # print(toklst)
# # print(len(toklst))
# test = [t.docid for t in toklst]
# print(test)
# ordered_test = list(dict.fromkeys(test))
# print(ordered_test)
#
# i = 1
# for k in ordered_test:
#     if int(k) != i:
#         print("Invalid k:{}, i:{}".format(k, i))
#         break
#     i += 1


def test_spimi():
    rc = ReutersCorpus(["reut2-000.sgm", "bad_file.txt", "reut2-001.sgm"])
    spimi = SPIMI(rc, "./blocks/")


# test_spimi()

# merged = []
# i = 0
# j = 0
# while i < len(p1) and j < len(p2):
#     if p1[i] <= p2[j]:
#         if len(merged) == 0 or p1[i] != merged[len(merged) - 1]:
#             merged.append(p1[i])
#         i += 1
#     else:
#         if len(merged) == 0 or p2[j] != merged[len(merged) - 1]:
#             merged.append(p2[j])
#         j += 1
#
# while i < len(p1):
#     if len(merged) == 0 or p1[i] != merged[len(merged) - 1]:
#         merged.append(p1[i])
#     i += 1
# while j < len(p2):
#     if len(merged) == 0 or p2[j] != merged[len(merged) - 1]:
#         merged.append(p2[j])
#     j += 1


from merge import MergeSPIMI


def test_merge():
    l1 = [4, 1, 2, 5]
    l2 = [3, 1, 2, 7, 8, 6, 2, 3, 3, 3, 3]

    print("l1: {}, l2: {}".format(l1, l2))
    merged = MergeSPIMI._merge_postings(l1, l2)
    print("l1: {}, l2: {}, merged: {}".format(l1, l2, merged))

    l1 = []
    l2 = [3, 1, 2, 7, 8, 6, 2, 3, 3, 3, 3]
    print("l1: {}, l2: {}".format(l1, l2))
    merged = MergeSPIMI._merge_postings(l1, l2)
    print("l1: {}, l2: {}, merged: {}".format(l1, l2, merged))

    l2 = []
    l1 = [3, 1, 2, 7, 8, 6, 2, 3, 3, 3, 3]
    print("l1: {}, l2: {}".format(l1, l2))
    merged = MergeSPIMI._merge_postings(l1, l2)
    print("l1: {}, l2: {}, merged: {}".format(l1, l2, merged))

    l1 = []
    l2 = []
    print("l1: {}, l2: {}".format(l1, l2))
    merged = MergeSPIMI._merge_postings(l1, l2)
    print("l1: {}, l2: {}, merged: {}".format(l1, l2, merged))

    l1 = None
    l2 = None
    print("l1: {}, l2: {}".format(l1, l2))
    merged = MergeSPIMI._merge_postings(l1, l2)
    print("l1: {}, l2: {}, merged: {}".format(l1, l2, merged))


# test_merge()


def test_spimi_merge():
    ms = MergeSPIMI(["blocktest_0.blk", "blocktest_1.blk"], "merge_test.index")


test_spimi_merge()
