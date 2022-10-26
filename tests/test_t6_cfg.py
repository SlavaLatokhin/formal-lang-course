from pyformlang.cfg import Terminal

from project.cfg import *


def is_weakened__normal_form(cfq):
    def is_normal_form_prod(prod):
        if len(prod.body) == 2:
            return isinstance(prod.body[0], Variable) and isinstance(
                prod.body[1], Variable
            )
        if len(prod.body) == 1:
            return isinstance(prod.body[0], Terminal)
        if len(prod.body) == 0:
            return True
        return False

    return all([is_normal_form_prod(production) for production in cfq.productions])


def test_cfg():
    a = cfg_from_file("data/cfq", Variable("S"))
    # cfq in file: '''S -> a S b S | x S y S | $'''
    b = to_weakened_normal_form(a)
    right_words = ["", "ab", "xy", "abxyaxybxaby", "xaxaaxybaxybbyby"]
    wrong_words = ["a", "ba", "y", "yx", "axby"]
    assert all(all([a.contains(word), b.contains(word)]) for word in right_words)
    assert all(
        all([not a.contains(word), not b.contains(word)]) for word in wrong_words
    )
    assert is_weakened__normal_form(b)
