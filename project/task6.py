from pyformlang.cfg import *
from networkx import DiGraph


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    cfg = cfg.eliminate_unit_productions().remove_useless_symbols()
    return CFG(
        start_symbol=cfg.start_symbol,
        productions=cfg._decompose_productions(
            cfg._get_productions_with_only_single_terminals()
        ),
    )


def cfpq_with_hellings(
    cfg: CFG,
    graph: DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    cfg = cfg_to_weak_normal_form(cfg)
    eps = set()
    terms = {}
    NN = {}
    for p in cfg.productions:
        if len(p.body) == 0:
            eps.add(p.head)
        if len(p.body) == 1 and isinstance(p.body[0], Terminal):
            terms.setdefault(p.head, set()).add(p.body[0])
        elif len(p.body) == 2:
            NN.setdefault(p.head, set()).add((p.body[0], p.body[1]))
    r = {(N, v, v) for N in eps for v in graph.nodes}
    r |= {
        (N, v, u)
        for N, ls in terms.items()
        for v, u, tag in graph.edges(data="label")
        if Terminal(tag) in ls
    }
    new = r.copy()
    while len(new) != 0:
        N_i, v, u = new.pop()
        to_add = set()
        for N_j, v_, u_ in r:
            if v == u_:
                for N_k, NNs in NN.items():
                    if (N_j, N_i) in NNs and (N_k, v_, u) not in r:
                        new.add((N_k, v_, u))
                        to_add.add((N_k, v_, u))
            if v_ == u:
                for M_k, NNs in NN.items():
                    if (N_i, N_j) in NNs and (M_k, v, u_) not in r:
                        new.add((M_k, v, u_))
                        to_add.add((M_k, v, u_))
        r |= to_add
    return {
        (v, u)
        for N_i, v, u in r
        if v in start_nodes and u in final_nodes and N_i == cfg.start_symbol
    }
