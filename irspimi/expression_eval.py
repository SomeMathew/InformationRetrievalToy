from nltk import word_tokenize
from typing import List
from enum import Enum
import search
from inverted_index import InvertedIndex
from eval_result import EvaluationResult


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
    def __init__(self, left_child, op: Token, right_child):
        self.left_child = left_child
        self.right_child = right_child
        self.op = op


class Term(ParseTree):
    def __init__(self, term: Token):
        self.term = term


class UnaryOp(ParseTree):
    def __init__(self, op: Token, child):
        self.op = op
        self.child = child


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

        Grammar:
            expr : conj (OR conj)*
            conj : term (AND term)*
            term : (NOT) TERM | LPAR expr RPAR
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
        """expr : conj (OR conj)*"""
        node = self._conjunction()
        while self._current_token.type == TokenType.OR:
            op_tok = self._current_token
            self._ingest(TokenType.OR)
            node = BinOp(node, op_tok, self._conjunction())
        return node

    def _conjunction(self):
        """term (AND term)*"""
        node = self._term()
        while self._current_token.type == TokenType.AND:
            op_tok = self._current_token
            self._ingest(TokenType.AND)
            node = BinOp(node, op_tok, self._term())
        return node

    def _term(self):
        """term : (NOT) TERM | LPAR expr RPAR"""
        tok = self._current_token
        if tok.type == TokenType.NOT:
            self._ingest(TokenType.NOT)
            node = UnaryOp(tok, self._term())
        elif tok.type == TokenType.TERM:
            self._ingest(TokenType.TERM)
            node = Term(tok)
        elif tok.type == TokenType.LPAREN:
            self._ingest(TokenType.LPAREN)
            node = self._expression()
            self._ingest(TokenType.RPAREN)
        return node


class Evaluator:
    def __init__(self, parser: Parser, index: InvertedIndex):
        self._parser = parser
        self._index = index
        self._reset()

    def _reset(self):
        self.eval_result = EvaluationResult()

    def _visit(self, node):
        if isinstance(node, BinOp):
            return self._visit_binop(node)
        elif isinstance(node, Term):
            return self._visit_term(node)
        elif isinstance(node, UnaryOp):
            return self._visit_unaryop(node)
        else:
            raise ExpressionParserException("Invalid Node Type: Aborting!")

    def _visit_binop(self, node):
        if node.op.type == TokenType.AND:
            left_postings = self._visit(node.left_child)
            right_postings = self._visit(node.right_child)
            # Fix to disregard compression which removes terms (Stop Words, no numbers)
            # This is required for AND operation to not erroneously return no documents
            if left_postings is None and right_postings is None:
                return None
            elif left_postings is None:
                return right_postings
            elif right_postings is None:
                return left_postings
            else:
                return search.intersect(left_postings, right_postings)
        elif node.op.type == TokenType.OR:
            return search.union(self._visit(node.left_child), self._visit(node.right_child))
        else:
            raise ExpressionParserException("Invalid Binary Operator Type: Aborting!")

    def _visit_term(self, node):
        term_postings = self._index.get_postings(node.term.value)

        if term_postings is None:
            self.eval_result.add_postings(node.term.value, [])
        else:
            self.eval_result.add_postings(node.term.value, term_postings.postings)
        return term_postings.postings

    def _visit_unaryop(self, node):
        return search.neg(self._index.get_universe(), self._visit(node.child))

    def evaluate(self):
        self._reset()
        tree = self._parser.parse()
        query_result = self._visit(tree)
        query_result = query_result if query_result is not None else []
        self.eval_result.update_results(query_result)

        return self.eval_result


class ExpressionParserException(Exception):
    pass
