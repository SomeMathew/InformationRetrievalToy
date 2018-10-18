import argparse
import os

parser = argparse.ArgumentParser(description='irspimi is a information retrieval system for the Reuters21578 corpus using the SPIMI algorithm.')
parser.add_argument(
    '-v',
    dest='verbose',
    action='store_true',
    help='Prints debugging messages.')
# parser.add_argument(
#     '-d',
#     dest='dir',
#     type=int,
#     help=(
#         'Specifies the port number that the server will listen and serve at. '
#         'Default is {}.'.format(DEFAULT_PORT)),
#     default=DEFAULT_PORT,
#     metavar='PORT')
parser.add_argument(
    '-d',
    dest='dir',
    help=
    ('Specifies the directory to fetch the Reuters21578 archive.'
     ),
    default='.',
    metavar='PATH-TO-DIR')

# parser.add_argument(
#     '--compress',
#     help=('Specifies a dictionary compression technique'),
#     default='???' ????,
#     metavar='COMPRESS-ALG'
# )


args = parser.parse_args()

print(os.listdir("."))
test = docprocessor.TokenStream(["test.txt", "invalid.txt"], ".")
test.test()
test.test()
