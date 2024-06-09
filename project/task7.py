from typing import Set
from copy import deepcopy
import pyformlang
from scipy.sparse import dok_matrix
import networkx as nx
from project.task6 import cfg_to_weak_normal_form


def cfpq_with_matrix(
    cfg: pyformlang.cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> set[tuple[int, int]]:
    start_nodes = graph.nodes if start_nodes is None else start_nodes
    final_nodes = graph.nodes if final_nodes is None else final_nodes
    gr = cfg_to_weak_normal_form(cfg)
    m = {}
    eps = set()
    ts = {}
    nn = {}
    for p in gr.productions:
        if len(p.body) == 0:
            eps.add(p.head.to_text())
        if isinstance(p.body[0], pyformlang.cfg.Terminal) and len(p.body) == 1:
            ts.setdefault(p.body[0].to_text(), set()).add(p.head.to_text())
        m[p.head.to_text()] = dok_matrix(
            (graph.number_of_nodes(), graph.number_of_nodes()), dtype=bool
        )
        if len(p.body) == 2:
            nn.setdefault(p.head.to_text(), set()).add(
                (p.body[0].to_text(), p.body[1].to_text())
            )
    for b, e, t in graph.edges(data="label"):
        if t in ts:
            for T in ts[t]:
                m[T][b, e] = True
    for N in eps:
        m[N].setdiag(True)
    new = deepcopy(m)
    for m in new.values():
        m.clear()
    for i in range(graph.number_of_nodes() ** 2):
        for N, NN in nn.items():
            for Nl, Nr in NN:
                new[N] += m[Nl] @ m[Nr]
        for N, m in new.items():
            m[N] += m
    S = gr.start_symbol.to_text()
    ns, ms = m[S].nonzero()

    return {(n, m) for n, m in zip(ns, ms) if n in start_nodes and m in final_nodes}
