from typing import NamedTuple

import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex

from project.gql.parser import get_parser
from project.graph_module import get_graph_info, get_graph_by_name
from project.interpreter.interpreterVisitor import InterpreterVisitor
from project.rpq import rpq


@pytest.mark.parametrize(
    "text, expected_local_stacks",
    [
        ('let variable_name123 = "string";', [{"variable_name123": "string"}]),
        ("let v = 123;", [{"v": 123}]),
    ],
)
def test_bind(text, expected_local_stacks):
    ctx = get_parser(text).stat()
    visitor = InterpreterVisitor()

    visitor.visitStat(ctx)
    assert visitor.local_stacks == expected_local_stacks


@pytest.mark.parametrize(
    "text, expected_output",
    [
        ('print("string");', "string"),
        ("print('c');", "c"),
        ("print(123);", "123"),
        ("print(true);", "True"),
        ("print(false);", "False"),
        ("print({1, false, '5'});", "{False, 1, '5'}"),
    ],
)
def test_print(text, expected_output):
    ctx = get_parser(text).prog()
    visitor = InterpreterVisitor()

    visitor.visitProg(ctx)
    assert visitor.output == expected_output


@pytest.mark.parametrize(
    "text, expected_local_stacks",
    [
        ('let variable_name123 = "string";', [{"variable_name123": "string"}]),
        ("let v = 'c';", [{"v": "c"}]),
        ("let v = 123;", [{"v": 123}]),
        ("let v = true;", [{"v": True}]),
        ("let v = false;", [{"v": False}]),
        ("let v = {1, false, '5'};", [{"v": {False, 1, "5"}}]),
    ],
)
def test_val(text, expected_local_stacks):
    ctx = get_parser(text).stat()
    visitor = InterpreterVisitor()

    visitor.visitStat(ctx)
    assert visitor.local_stacks == expected_local_stacks


class GraphNFAInfo(NamedTuple):
    nodes: int
    edges: int
    labels: set
    start_states: int
    final_states: int

    @staticmethod
    def graph_nfa_info(graph_nfa: NondeterministicFiniteAutomaton):
        return GraphNFAInfo(
            len(graph_nfa.states),
            len(graph_nfa.transition_function),
            set(str(a) for a in graph_nfa.symbols),
            len(graph_nfa.start_states),
            len(graph_nfa.final_states),
        )

    @staticmethod
    def get_graph_graph_info(
        name: str, count_of_start_node: int, count_of_final_node: int
    ):
        graph_info = get_graph_info(name)
        return GraphNFAInfo(
            graph_info.nodes,
            graph_info.edges,
            graph_info.labels,
            count_of_start_node,
            count_of_final_node,
        )


@pytest.mark.parametrize(
    "text, expected_graph_info",
    [
        (
            'let graph = load_graph("skos");',
            GraphNFAInfo.get_graph_graph_info("skos", 0, 0),
        ),
        (
            """
        let graph = load_graph("skos");
        let graph = set_start(get_vertices(graph), graph);
        """,
            GraphNFAInfo.get_graph_graph_info("skos", 144, 0),
        ),
        (
            """
        let graph = load_graph("skos");
        let vs = get_vertices(graph);
        let graph = set_final(vs, set_start(vs, graph));
        """,
            GraphNFAInfo.get_graph_graph_info("skos", 144, 144),
        ),
        (
            """
        let set = {4};
        let graph = load_graph("skos");
        let graph = add_start(get_vertices(graph), graph);
        let graph = set_start(set, graph);
        """,
            GraphNFAInfo.get_graph_graph_info("skos", 1, 0),
        ),
    ],
)
def test_graph(text, expected_graph_info):
    ctx = get_parser(text).prog()
    visitor = InterpreterVisitor()

    visitor.visitProg(ctx)
    graph: NondeterministicFiniteAutomaton = visitor.local_stacks[0].get("graph")
    assert GraphNFAInfo.graph_nfa_info(graph) == expected_graph_info


@pytest.mark.parametrize(
    "text, expected_vertices",
    [
        (
            'let vs = get_vertices(load_graph("skos"));',
            set(get_graph_by_name("skos").nodes),
        ),
        (
            """
        let set = {4};
        let graph = set_start(set, load_graph("skos"));
        let vs = get_start(graph);
        """,
            {4},
        ),
        (
            """
        let graph = set_final({1, 2, 3}, load_graph("skos"));
        let vs = get_final(graph);
        """,
            {1, 2, 3},
        ),
    ],
)
def test_vertices(text, expected_vertices):
    ctx = get_parser(text).prog()
    visitor = InterpreterVisitor()

    visitor.visitProg(ctx)
    actual_vertices = visitor.local_stacks[0].get("vs")
    assert actual_vertices == expected_vertices


@pytest.mark.parametrize(
    "text, name_of_file, start_states, final_states",
    [
        (
            """
        let graph = load_graph("skos");
        let graph = set_start({1, 2}, set_final(get_vertices(graph), graph));
        let vs = get_reachable(graph);
        """,
            "skos",
            {1, 2},
            None,
        ),
        (
            """
        let graph = load_graph("atom");
        let vertices = get_vertices(graph);
        let graph = set_start(vertices, set_final(vertices, graph));
        let vs = get_reachable(graph);
        """,
            "atom",
            None,
            None,
        ),
    ],
)
def test_get_reachable(text, name_of_file, start_states, final_states):
    graph = get_graph_by_name(name_of_file)
    labels = get_graph_info(name_of_file).labels
    regex = "(" + labels.pop()
    for label in labels:
        regex += "|" + label
    regex += ")*"
    rpq_res = rpq(graph, Regex(regex), start_states, final_states)
    expected_vertices = set(j for (i, j) in rpq_res)
    ctx = get_parser(text).prog()
    visitor = InterpreterVisitor()

    visitor.visitProg(ctx)
    actual_vertices = visitor.local_stacks[0].get("vs")
    assert actual_vertices == expected_vertices
