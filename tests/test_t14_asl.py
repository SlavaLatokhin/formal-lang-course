import pytest

from project.gql.parser import *


@pytest.mark.parametrize(
    "input_str, result",
    [("i", True), ("I", True), ("a1", True), ("1a", False), ("_a", False)],
)
def test_var(input_str, result):
    assert check(input_str, lambda p: p.var()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [
        ('"String"', True),
        ("'c'", True),
        ("2048", True),
        ("True", True),
        ("{5, 33}", True),
    ],
)
def test_val(input_str, result):
    assert check(input_str, lambda p: p.val()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [
        ('load_graph("atom")', True),
        ("load_graph(5)", False),
        ('load_graph_from("data/wine.dot")', True),
        ("set_start(get_vertices(graph), graph)", True),
        ("set_final(get_start(graph), graph)", True),
        ('set_final(load_graph("atom"), graph)', False),
    ],
)
def test_graph(input_str, result):
    assert check(input_str, lambda p: p.graph()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [
        ("get_vertices(graph)", True),
        ("get_start(graph)", True),
        ("get_reachable(graph)", True),
    ],
)
def test_vertices(input_str, result):
    assert check(input_str, lambda p: p.vertices()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [("get_edges(graph)", True), ("get_edges(graph, graph2)", False)],
)
def test_edges(input_str, result):
    assert check(input_str, lambda p: p.edges()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [
        ("get_labels(graph)", True),
        ("get_edges(graph)", False),
    ],
)
def test_labels(input_str, result):
    assert check(input_str, lambda p: p.labels()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [
        ("map(fun(i) {i}, get_vertices(graph))", True),
        ("filter(fun(i) {i}, get_vertices(graph))", True),
        ("filter(fun(i) {i})", False),
        ("(i)", True),
        ("(i", False),
        ("intersect (graph, x)", True),
        ('intersect (graph, union("label1", "label2"))', True),
    ],
)
def test_expr(input_str, result):
    assert check(input_str, lambda p: p.expr()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [
        ("let a = 5;", True),
        ('let variable = "veeeeeeeeeeeeeery long string";', True),
        ("let char = 'c';", True),
        ("let bool = true;", True),
        ("let number = 12345678;", True),
        ('let graph = load_graph("atom");', True),
        ("let inter = intersect (graph, x);", True),
        ('let tuple = (load_graph("atom"), load_graph("wine"));', False),
        ("print(inter);", True),
        ("print graph;", False),
        ("print(let inter = intersect (graph, x));", False),
    ],
)
def test_stat(input_str, result):
    assert check(input_str, lambda p: p.stat()) == result


@pytest.mark.parametrize(
    "input_str, result",
    [
        (
            """
        let graph = load_graph("atom"); /* загрузка графа по названию */
        let graph = load_graph_from("data/wine.dot"); /* загрузка графа из файла */

        let graph = set_start(get_vertices(graph), graph); /* получение одной из вершин графа и назначение ее стартовой */
        let graph = set_final(get_start(graph), graph); /* получение стартовых вершин графа и назначение их финальными */

        let x = union("label1", "label2"); /* создание запроса */

        let inter = intersect (graph, x); /* набор вершин, удовлетворяющих запросу */

        print(inter); /* печать переменной */
        """,
            True,
        ),
        (
            """
        /* просто комментарий */
        """,
            True,
        ),
        (
            """
        /*  let graph = load_graph("atom"); /* комментарий в комментарии */ */
        """,
            True,
        ),
        (
            """
        /* просто комментарий без закрывающей части */
        /*
        """,
            False,
        ),
    ],
)
def test_prog(input_str, result):
    assert check(input_str, lambda p: p.prog()) == result
