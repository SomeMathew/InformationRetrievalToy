from nltk import word_tokenize
from typing import Callable, List, Type


class ParseTree:
    BINARY_OPERATORS = ["AND", "OR"]
    UNARY_OPERATORS = ["NOT"]

    def __init__(self, expression: str):
        self._tokens = word_tokenize(expression)
        self._parse_expression(self._tokens)

    def _parse_expression(self, expression: List[str]):
        pstack = []
        current = self._root = ParseTree._Node()
        unary_op = None
        for tok in expression:
            if unary_op is not None:
                current.unary_operator = unary_op
                unary_op = None

            if tok == "(":
                pstack.append(current)
                current.left_child = ParseTree._Node()
                current = current.left_child
            elif tok == ")":
                if pstack:
                    current = pstack.pop()
            elif tok in ParseTree.BINARY_OPERATORS:
                current.value = tok
                pstack.append(current)
                current.right_child = ParseTree._Node()
                current = current.right_child
            elif tok in ParseTree.UNARY_OPERATORS:
                unary_op = tok
            else:
                current.value = tok
                current = pstack.pop()

    def _traverse(self, node, inorder_nodes: list):
        if node.left_child:
            self._traverse(node.left_child, inorder_nodes)

        inorder_nodes.append(node)

        if node.right_child:
            self._traverse(node.right_child, inorder_nodes)
        return inorder_nodes

    def __str__(self):
        inorder_nodes = []
        self._traverse(self._root, inorder_nodes)
        return " ".join([str(n) for n in inorder_nodes])

    class _Node:
        def __init__(self, value = None, unary_operator = None):
            self.value = value
            self.unary_operator = unary_operator
            self.left_child = None
            self.right_child = None

        def __str__(self):
            s = "{} {}".format(self.unary_operator or "", self.value or "").strip()
            return s


class ExpressionParserException(Exception):
    pass



# TODO remove this test
pt = ParseTree("(George AND Bush)")
print(pt)
pt = ParseTree("(NOT (George OR Georgie) AND Bush)")
print(pt)

pt = ParseTree("(NOT (George OR Georgie))")
print(pt)

pt = ParseTree("(NOT George)")
print(pt)
