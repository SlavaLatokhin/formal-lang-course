import pytest
from pyformlang.cfg import Variable, CFG

from project.cfpq import cfpq_cyk


@pytest.mark.parametrize(
    "cfg_text, right_strings, wrong_strings",
    [
        (
            """S -> a S b S | x S y S | $""",
            {"", "ab", "xy", "abxyaxybxaby", "xaxaaxybaxybbyby"},
            {"a", "ba", "y", "yx", "axby"},
        ),
        (
            """S -> a S | P
        P -> b P | Q
        Q -> c Q | c""",
            {"c", "abc", "acc", "aaaaabccccc", "abccc"},
            {"", "ca", "acb", "ab", "aaaaaabbbbb"},
        ),
    ],
)
def test_is_string_deducible_from_grammar(cfg_text, right_strings, wrong_strings):
    cfg = CFG.from_text(cfg_text, Variable("S"))
    assert all(cfpq_cyk(s, cfg) for s in right_strings)
    assert all(not cfpq_cyk(s, cfg) for s in wrong_strings)
