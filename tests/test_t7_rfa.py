import pytest
from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex

from project.ecfg import ECFG
from project.rsm import RecursiveStateMachine


@pytest.mark.parametrize(
    "ecfg_prod",
    [
        {Variable("S"): Regex("(((x.(S.(y.S)))|$)|(a.(S.(b.S))))")},
        {
            Variable("P"): Regex("((Q|(b.P))|$)"),
            Variable("S"): Regex("(($|(a.S))|P)"),
            Variable("Q"): Regex("((c.Q)|$)"),
        },
    ],
)
class TestRSM:
    def test_create_rsm_from_ecfg(self, ecfg_prod):
        ecfg = ECFG(ecfg_prod.keys(), ecfg_prod, Variable("S"))
        rsm = RecursiveStateMachine.from_ecfg(ecfg)
        assert rsm.start_symbol == ecfg.start_symbol
        assert all(
            rsm.boxes[v] == ecfg.productions[v].to_epsilon_nfa()
            for v in ecfg.productions.keys()
        )

    def test_minimize(self, ecfg_prod):
        ecfg = ECFG(ecfg_prod.keys(), ecfg_prod, Variable("S"))
        minimize_rsm = RecursiveStateMachine.from_ecfg(ecfg).minimize()
        assert minimize_rsm.start_symbol == ecfg.start_symbol
        assert all(
            minimize_rsm.boxes[v] == ecfg.productions[v].to_epsilon_nfa().minimize()
            for v in ecfg.productions.keys()
        )
