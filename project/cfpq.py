from typing import Set

from pyformlang.cfg import CFG
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix, eye, csr_matrix

from project.boolean_matrix_automata import BooleanMatrixAutomata
from project.cfg import to_weakened_normal_form
from project.ecfg import ECFG
from project.finite_automata import build_nfa_from_graph
from project.rsm import RecursiveStateMachine


def cfpq_cyk(s: str, cfg: CFG):
    if not s:
        return cfg.generate_epsilon()
    cfg = cfg.to_normal_form()
    n = len(s)
    m = list(list(set() for _ in range(n)) for _ in range(n))
    t = list()
    nt = list()
    for p in cfg.productions:
        if len(p.body) == 1:
            t.append(p)
        if len(p.body) == 2:
            nt.append(p)
    for i, c in enumerate(s):
        m[i][i] = set(p.head for p in t if p.body[0].value == c)
    for z in range(1, n):
        for y in range(n - z):
            x = z + y
            for i in range(y, x):
                j = i + 1
                for p in nt:
                    if p.body[0] in m[y][i] and p.body[1] in m[j][x]:
                        m[y][x].add(p.head)
    return cfg.start_symbol in m[0][n - 1]


def cfpg_by_hellings(
    graph: MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
):
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    start_symbol = cfg.start_symbol.value

    result = {
        (x, y)
        for (label, x, y) in eval_hellings(graph, cfg)
        if x in start_nodes and y in final_nodes and label == start_symbol
    }
    return result


def eval_hellings(graph: MultiDiGraph, cfg: CFG):
    r = set(tuple())
    wcnf = to_weakened_normal_form(cfg)
    eps_nonterm = {p.head.value for p in wcnf.productions if not p.body}
    terms_prod = {p for p in wcnf.productions if len(p.body) == 1}
    nonterm_prod = {p for p in wcnf.productions if len(p.body) == 2}

    r = {(label, x, x) for x in graph.nodes for label in eps_nonterm} | {
        (p.head.value, v, u)
        for (v, u, label) in graph.edges(data="label")
        for p in terms_prod
        if p.body[0].value == label
    }
    m = r.copy()
    while m:
        label1, v1, u1 = m.pop()
        r_changes = set()
        for (label2, v2, _) in (t for t in r if t[2] == v1):
            for triple in (
                (p.head.value, v2, u1)
                for p in nonterm_prod
                if (p.head.value, v2, u1) not in r
                and p.body[0].value == label2
                and p.body[1].value == label1
            ):
                m.add(triple)
                r_changes.add(triple)
        for (label2, _, u2) in (t for t in r if t[1] == u1):
            for triple in (
                (p.head.value, v1, u2)
                for p in nonterm_prod
                if (p.head.value, v1, u2) not in r
                and p.body[0].value == label1
                and p.body[1].value == label2
            ):
                m.add(triple)
                r_changes.add(triple)
        r |= r_changes
    return r


def cfpg_by_matrix(
    graph: MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
):
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    start_symbol = cfg.start_symbol.value

    result = {
        (x, y)
        for (label, x, y) in eval_matrix(graph, cfg)
        if x in start_nodes and y in final_nodes and label == start_symbol
    }
    return result


def eval_matrix(graph: MultiDiGraph, cfg: CFG):
    n = graph.number_of_nodes()

    wcnf = to_weakened_normal_form(cfg)
    eps_nonterm = {p.head.value for p in wcnf.productions if not p.body}
    terms_prod = {p for p in wcnf.productions if len(p.body) == 1}
    nonterm_prod = {p for p in wcnf.productions if len(p.body) == 2}

    matrices = {
        nonterm.value: dok_matrix((n, n), dtype=bool) for nonterm in wcnf.variables
    }

    for i, j, label in graph.edges(data="label"):
        for nonterm in (
            tp.head.value for tp in terms_prod if tp.body[0].value == label
        ):
            matrices[nonterm][i, j] = True

    for i in range(n):
        for nonterm in eps_nonterm:
            matrices[nonterm][i, i] = True

    while True:
        changed = False
        for nonterm in nonterm_prod:
            nnz = matrices[nonterm.head.value].count_nonzero()
            matrices[nonterm.head.value] += (
                matrices[nonterm.body[0].value] @ matrices[nonterm.body[1].value]
            )
            if matrices[nonterm.head.value].count_nonzero() != nnz:
                changed = True
        if not changed:
            break

    return {
        (nonterm, i, j)
        for nonterm, matrix in matrices.items()
        for i, j in zip(*matrix.nonzero())
    }


def cfpg_by_tensor_product(
    graph: MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
):
    # return eval_tensor_product(graph, cfg)
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    start_symbol = cfg.start_symbol.value

    result = {
        (x, y)
        for (label, x, y) in eval_tensor_product(graph, cfg)
        if x in start_nodes and y in final_nodes and label == start_symbol
    }
    return result


def eval_tensor_product(graph: MultiDiGraph, cfg: CFG):
    bma_graph = BooleanMatrixAutomata(build_nfa_from_graph(graph))
    bma_rsm = BooleanMatrixAutomata(
        RecursiveStateMachine.from_ecfg(ECFG.from_cfg(cfg)).minimize().to_nfa()
    )
    loop_matrix = eye(bma_graph.number_of_states, dtype=bool, format="dok")
    for nonterm in cfg.get_nullable_symbols():
        if nonterm.value not in bma_graph.boolean_matrix:
            bma_graph.boolean_matrix[nonterm.value] = loop_matrix
        else:
            bma_graph.boolean_matrix[nonterm.value] += loop_matrix
    tc_nnz = 0
    while True:
        transitive_closure = bma_rsm.intersect(bma_graph).transitive_closure()
        if transitive_closure.nnz == tc_nnz:
            break
        tc_nnz = transitive_closure.nnz
        for (i, j) in list(zip(*transitive_closure.nonzero())):
            graph_n_of_states = bma_graph.number_of_states
            graph_i = i % graph_n_of_states
            graph_j = j % graph_n_of_states
            rsm_i = i // graph_n_of_states
            rsm_j = j // graph_n_of_states
            state_i = bma_rsm.indexes_states[rsm_i]
            state_j = bma_rsm.indexes_states[rsm_j]
            nonterm = state_i.value[0]
            if (
                state_i in bma_rsm.start_state_indexes
                and state_j in bma_rsm.final_state_indexes
            ):
                if nonterm.value not in bma_graph.boolean_matrix.keys():
                    bma_graph.boolean_matrix[nonterm] = dok_matrix(
                        (bma_graph.number_of_states, bma_graph.number_of_states),
                        dtype=bool,
                    )
                bma_graph.boolean_matrix[nonterm][graph_i, graph_j] = True

    return {
        (nonterm, bma_graph.indexes_states[i], bma_graph.indexes_states[j])
        for nonterm, matrix in bma_graph.boolean_matrix.items()
        for i, j in zip(*matrix.nonzero())
    }
