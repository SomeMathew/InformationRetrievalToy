from nltk import word_tokenize
from typing import Callable, List, Type
from enum import Enum


class TokenType(Enum):
    TERM = "TERM"
    OR = "OR"
    AND = "AND"
    NOT = "NOT"
    LPAREN = "("
    RPAREN = ")"
    EOF = "##EOF##"


class Token:
    def __init__(self, value, type: TokenType):
        self.value = value
        self.type = type

    def __str__(self):
        return "({type}, {value})".format(type=self.type, value=self.value)


def lexer(tokens: List[str]):
    """
    Creates tuple with terms,type.
    :param tokens:List of tokens in the expression
    :return: List of Tokens tuple (value,type)
    """
    toks = []
    for t in tokens:
        if t == TokenType.OR.value:
            toks.append(Token(value=t, type=TokenType.OR))
        elif t == TokenType.AND.value:
            toks.append(Token(value=t, type=TokenType.AND))
        elif t == TokenType.NOT.value:
            toks.append(Token(value=t, type=TokenType.NOT))
        elif t == TokenType.LPAREN.value:
            toks.append(Token(value=t, type=TokenType.LPAREN))
        elif t == TokenType.RPAREN.value:
            toks.append(Token(value=t, type=TokenType.RPAREN))
        elif t == TokenType.EOF.value:
            toks.append(Token(value=t, type=TokenType.EOF))
        else:
            toks.append(Token(value=t, type=TokenType.TERM))
    return toks


class ParseTree:
    pass


class BinOp(ParseTree):
    def __init__(self, left_child, op, right_child):
        self.left_child = left_child
        self.right_child = right_child
        self.op = op


class Term(ParseTree):
    def __init__(self, term):
        self.term = term


class Parser:
    def __init__(self, expression: str):
        # self._expression = expression
        self._tokens = word_tokenize(expression)
        self._tokens.append(TokenType.EOF.value)
        self._tokens = lexer(self._tokens)
        self._tokens_stream = iter(self._tokens)
        self._current_token = next(self._tokens_stream)

    def parse(self):
        """
        Creates the ParseTree from the initialized expression
        :return ParseTree: Abstract Syntax Tree of the expression for evaluation
        """
        return self._expression()

    def _ingest(self, type: TokenType):
        if self._current_token.type == type:
            self._current_token = next(self._tokens_stream)
        else:
            raise ExpressionParserException(
                "Invalid Syntax. Expected type: {}, received: {}".format(type, self._current_token.type))

    def _expression(self):
        node = self._conjunction()
        while self._current_token.type == TokenType.OR:
            op_tok = self._current_token
            self._ingest(TokenType.OR)
            node = BinOp(node, op_tok, self._conjunction())
        return node

    def _conjunction(self):
        node = self._term()
        while self._current_token.type == TokenType.AND:
            op_tok = self._current_token
            self._ingest(TokenType.AND)
            node = BinOp(node, op_tok, self._term())
        return node

    def _term(self):
        tok = self._current_token
        if tok.type == TokenType.TERM:
            self._ingest(TokenType.TERM)
            node = Term(tok)
        elif tok.type == TokenType.LPAREN:
            self._ingest(TokenType.LPAREN)
            node = self._expression()
            self._ingest(TokenType.RPAREN)
        return node


class ExpressionParserException(Exception):
    pass


# TODO remove this test
pt = Parser("George AND Bush OR Maria AND Ford")
tree = pt.parse()
print(tree)
# pt = ParseTree("(NOT (George OR Georgie) AND Bush)")
# print(pt)
#
# pt = ParseTree("(NOT (George OR Georgie))")
# print(pt)
#
# pt = ParseTree("(NOT George)")
# print(pt)
