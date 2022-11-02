from typing import NamedTuple, Dict

from pyformlang.finite_automaton import EpsilonNFA
from pyformlang.cfg import Variable

from project.ecfg import ECFG


class RecursiveStateMachine(NamedTuple):
    start_symbol: Variable
    boxes: Dict[Variable, EpsilonNFA]

    @classmethod
    def from_ecfg(cls, ecfg: ECFG):
        boxes: Dict[Variable, EpsilonNFA] = dict()
        for var, regex in ecfg.productions.items():
            boxes[var] = regex.to_epsilon_nfa()
        return cls(ecfg.start_symbol, boxes)

    def minimize(self):
        boxes = {v: enfa.minimize() for v, enfa in self.boxes.items()}
        return RecursiveStateMachine(self.start_symbol, boxes)
