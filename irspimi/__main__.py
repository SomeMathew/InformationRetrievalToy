import argparse
import os
import irsystem
import dict_compression
from inverted_index import InvertedIndex
from expression_eval import Parser, Evaluator


# parser = argparse.ArgumentParser(description='irspimi is a information retrieval system for the Reuters21578 corpus using the SPIMI algorithm.')
# parser.add_argument(
#     '-v',
#     dest='verbose',
#     action='store_true',
#     help='Prints debugging messages.')
# parser.add_argument(
#     '-d',
#     dest='dir',
#     type=int,
#     help=(
#         'Specifies the port number that the server will listen and serve at. '
#         'Default is {}.'.format(DEFAULT_PORT)),
#     default=DEFAULT_PORT,
#     metavar='PORT')
# parser.add_argument(
#     '-d',
#     dest='dir',
#     help=
#     ('Specifies the directory to fetch the Reuters21578 archive.'
#      ),
#     default='.',
#     metavar='PATH-TO-DIR')

# parser.add_argument(
#     '--compress',
#     help=('Specifies a dictionary compression technique'),
#     default='???' ????,
#     metavar='COMPRESS-ALG'
# )


# args = parser.parse_args()
#
# print(os.listdir("."))
# test = docprocessor.TokenStream(["test.txt", "invalid.txt"], ".")
# test.test()
# test.test()

def build_index():
    print("Building index with multipass merge")
    outfile = irsystem.build_index(["reuters/reut2-0{:02}.sgm".format(k) for k in range(0, 22)], "./index_mp", None)
    print(outfile)


def search_mode():
    index = irsystem.load_index("./index_mp")
    while True:
        expr = input("What do you want to search for?")
        for resp in irsystem.search_expr(index, expr):
            print(resp)
        # print(irsystem.search_expr(index, expr))


# import time
# start_time = time.time()
# build_index()
# print("--- %s seconds ---" % (time.time() - start_time))

search_mode()
