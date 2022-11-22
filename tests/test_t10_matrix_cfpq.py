import pytest
from pyformlang.cfg import Variable, CFG
import cfpq_data

from project.cfpq import cfpg_by_matrix


@pytest.mark.parametrize(
    "cfg_text, expected_edges",
    [
        ("""S -> a b""", {(2, 3)}),
        (
            """S -> a S b S | $""",
            {(0, 0), (1, 1), (0, 3), (2, 0), (2, 3), (3, 3), (2, 2), (1, 0), (1, 3)},
        ),
        (
            """S -> a S | P
        P -> b P | b""",
            {(0, 0), (0, 3), (2, 0), (3, 0), (2, 3), (3, 3), (1, 0), (1, 3)},
        ),
        (
            """S -> a S | P
        P -> b P | $""",
            {
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (1, 0),
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 0),
                (2, 1),
                (2, 2),
                (2, 3),
                (3, 0),
                (3, 3),
            },
        ),
    ],
)
def test_hellings(cfg_text, expected_edges):
    graph = cfpq_data.labeled_two_cycles_graph(2, 1, labels=("a", "b"))
    cfg = CFG.from_text(cfg_text, Variable("S"))

    assert cfpg_by_matrix(graph, cfg) == expected_edges
