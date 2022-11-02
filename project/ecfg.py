from typing import NamedTuple, AbstractSet, Dict

from pyformlang.cfg import Variable, Terminal, CFG
from pyformlang.regular_expression import Regex


class ECFG(NamedTuple):
    variables: AbstractSet[Variable]
    productions: Dict[Variable, Regex]
    start_symbol: Variable = Variable("S")

    @classmethod
    def from_cfg(cls, cfg: CFG):
        productions: Dict[Variable, Regex] = dict()
        for _, production in enumerate(cfg.productions):
            body = Regex(
                " ".join(
                    [x.to_text() for x in production.body]
                    if len(production.body) > 0
                    else "$"
                )
            )
            productions[production.head] = (
                body
                if production.head not in productions
                else productions[production.head].union(body)
            )
        return cls(cfg.variables, productions, cfg.start_symbol)

    @classmethod
    def from_text(cls, text, start_symbol=Variable("S")):
        variables = set()
        productions: Dict[Variable, Regex] = dict()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            head_s, body_s = line.split("->")
            head = Variable(head_s.strip())
            variables.add(head)
            productions[head] = Regex(body_s)
        return cls(variables, productions, start_symbol)

    @classmethod
    def from_file(cls, filepath, start_symbol=Variable("S")):
        return cls.from_text(open(filepath).read(), start_symbol)
