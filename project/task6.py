from pyformlang.cfg import CFG, Variable, Terminal, Epsilon
import networkx as nx
from copy import deepcopy


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    cfg = cfg.eliminate_unit_productions().remove_useless_symbols()
    tmp = cfg._get_productions_with_only_single_terminals()
    new = set(cfg._decompose_productions(tmp))
    return CFG(start_symbol=Variable("S"), productions=new)


def cfpq_with_hellings(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    gr = cfg_to_weak_normal_form(cfg)
    terms = {}
    eps = set()
    NN = {}
    for p in gr.productions:
        p_len = len(p.body)
        if p_len == 1 and isinstance(p.body[0], Terminal):
            terms.setdefault(p.head, set()).add(p.body[0])
        elif p_len == 0 or p_len == 1 and isinstance(p.body[0], Epsilon):
            eps.add(p.head)
        elif p_len == 2:
            NN.setdefault(p.head, set()).add((p.body[0], p.body[1]))
    r = {(n, v, v) for n in eps for v in graph.nodes}
    r |= {
        (N, v, u)
        for (v, u, tag) in graph.edges.data("label")
        for N in terms
        if Terminal(tag) in terms[N]
    }
    new = deepcopy(r)
    while len(new) != 0:
        N_i, v, u = new.pop()
        to_add = set()
        for N_j, v_, u_ in r:
            if v == u_:
                for n_k in NN:
                    if (N_j, N_i) in NN[n_k] and (n_k, v_, u) not in r:
                        new.add((n_k, v_, u))
                        to_add.add((n_k, v_, u))
        for N_j, v_, u_ in r:
            if u == v_:
                for n_k in NN:
                    if (N_i, N_j) in NN[n_k] and (n_k, v, u_) not in r:
                        new.add((n_k, v, u_))
                        to_add.add((n_k, v, u_))
        r |= to_add
    return {
        (v, u)
        for (N_i, v, u) in r
        if v in start_nodes and u in final_nodes and Variable(N_i) == cfg.start_symbol
    }
