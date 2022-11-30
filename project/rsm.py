from typing import NamedTuple, Dict

from pyformlang.finite_automaton import EpsilonNFA, State
from pyformlang.cfg import Variable

from project.ecfg import ECFG


class RecursiveStateMachine(NamedTuple):
    start_symbol: Variable
    boxes: Dict[Variable, EpsilonNFA]

    @classmethod
    def from_ecfg(cls, ecfg: ECFG):
        boxes: Dict[Variable, EpsilonNFA] = dict()
        for v, regex in ecfg.productions.items():
            boxes[v] = regex.to_epsilon_nfa()
        return cls(ecfg.start_symbol, boxes)

    def minimize(self):
        boxes = {v: enfa.minimize() for v, enfa in self.boxes.items()}
        return RecursiveStateMachine(self.start_symbol, boxes)

    def to_nfa(self):
        nfa = EpsilonNFA()
        for v, enfa in self.boxes.items():
            for state in enfa.start_states:
                nfa.add_start_state(State((v, state.value)))
            for state in enfa.final_states:
                nfa.add_final_state(State((v, state.value)))
            for (start, symbol, finish) in enfa:
                nfa.add_transition(
                    State((v, start)),
                    symbol,
                    State((v, finish)),
                )
        return nfa
