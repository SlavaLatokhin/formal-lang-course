from typing import Callable, Any, Union, IO

import pydot
from antlr4 import (
    ParserRuleContext,
    TerminalNode,
    InputStream,
    CommonTokenStream,
    ParseTreeWalker,
)

from project.gql.ASLLexer import ASLLexer
from project.gql.ASLParser import ASLParser
from project.gql.ASLListener import ASLListener


class DotTreeListener(ASLListener):
    def __init__(self):
        self.dot = pydot.Dot("parse_tree", strict=True)
        self._curr_id = 0
        self._id_stack = []

    def enterEveryRule(self, ctx: ParserRuleContext):
        self.dot.add_node(
            pydot.Node(self._curr_id, label=ASLParser.ruleNames[ctx.getRuleIndex()])
        )
        if len(self._id_stack) > 0:
            self.dot.add_edge(pydot.Edge(self._id_stack[-1], self._curr_id))
        self._id_stack.append(self._curr_id)
        self._curr_id += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        self._id_stack.pop()

    def visitTerminal(self, node: TerminalNode):
        self.dot.add_node(pydot.Node(self._curr_id, label=f"'{node}'"))
        self.dot.add_edge(pydot.Edge(self._id_stack[-1], self._curr_id))
        self._curr_id += 1


def _get_parser(input_str: str) -> ASLParser:
    chars = InputStream(input_str)
    lexer = ASLLexer(chars)
    tokens = CommonTokenStream(lexer)
    return ASLParser(tokens)


def check(
    input_str: str, parser_token: Callable[[ASLParser], Any] = lambda p: p.program()
) -> bool:
    parser = _get_parser(input_str)
    parser.removeErrorListeners()
    parser_token(parser)
    return parser.getNumberOfSyntaxErrors() == 0


def save_parse_tree_as_dot(input_str: str, file: Union[str, IO]) -> None:
    parser = _get_parser(input_str)
    if parser.getNumberOfSyntaxErrors() > 0:
        raise ValueError("Bad GQL syntax")
    listener = DotTreeListener()
    walker = ParseTreeWalker()
    walker.walk(listener, parser.prog())
    listener.dot.write(str(file))
