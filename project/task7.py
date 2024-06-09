from pyformlang.cfg import *
import networkx as nx
from project.task6 import cfg_to_weak_normal_form
import scipy.sparse as sparse

def cfpq_with_matrix(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    start_nodes = graph.nodes if start_nodes is None else start_nodes
    final_nodes = graph.nodes if final_nodes is None else final_nodes
    gr = cfg_to_weak_normal_form(cfg)
    nodes = graph.number_of_nodes()
    new_matr = {}
    ts = {}
    eps = set()
    nn = {}
    for p in gr.productions:
        new_matr[p.head.to_text()] = sparse.dok_matrix((nodes, nodes), dtype=bool)
        if len(p.body) == 0:
            eps.add(p.head.to_text())
        if len(p.body) == 1 and isinstance(p.body[0], Terminal):
            ts.setdefault(p.body[0].to_text(), set()).add(
                p.head.to_text()
            )
        if len(p.body) == 2:
            nn.setdefault(p.head.to_text(), set()).add(
                (p.body[0].to_text(), p.body[1].to_text())
            )
    for u, v, label in graph.edges(data="label"):
        if label in ts:
            for term_var in ts[label]:
                new_matr[term_var][u, v] = True
    for sym in eps:
        new_matr[sym].setdiag(True)
    mat = {
        p.head.to_text(): sparse.dok_matrix((nodes, nodes), dtype=bool)
        for p in gr.productions
    }
    for _ in range(graph.number_of_nodes() ** 2):
        for sym, prod in nn.items():
            for lhs, rhs in prod:
                mat[sym] += new_matr[lhs] @ new_matr[rhs]
        for sym, m in mat.items():
            new_matr[sym] += m
    start = gr.start_symbol.to_text()
    ns, ms = new_matr[start].nonzero()

    return {(n, m) for n, m in zip(ns, ms) if n in start_nodes and m in final_nodes}
