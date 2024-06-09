from pyformlang.rsa import RecursiveAutomaton
from pyformlang.cfg import CFG
import networkx as nx
from copy import deepcopy
from project.task8 import cfg_to_rsm


def cfpq_with_gll(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:

    def push(g_node, rsm_s, stack_s):
        s = (g_node, rsm_s, stack_s)
        if s not in vis:
            queue.add(s)
            vis.add(s)

    if isinstance(rsm, CFG):
        rsm = cfg_to_rsm(rsm)
    start_nodes = graph.nodes if start_nodes is None else start_nodes
    final_nodes = graph.nodes if final_nodes is None else final_nodes
    label = "S"
    res = set()
    pop = {}
    start_nodes = {(label, v) for v in start_nodes}
    stack_graph = {s: set() for s in start_nodes}
    if rsm.initial_label.value is not None:
        label = rsm.initial_label.value

    vis = {
        (
            state[1],
            (label, rsm.boxes[rsm.initial_label].dfa.start_state.value),
            state,
        )
        for state in start_nodes
    }
    queue = deepcopy(vis)
    while len(queue) > 0:
        graph_node, rsm_state, stack_state = queue.pop()

        if rsm_state[1] in rsm.boxes[rsm_state[0]].dfa.final_states:
            if stack_state in start_nodes:
                if graph_node in final_nodes:
                    res.add((stack_state[1], graph_node))
            pop.setdefault(stack_state, set()).add(graph_node)
            for ss, rs in stack_graph.setdefault(stack_state, set()):
                push(graph_node, rs, ss)

        ns = {}
        for _, u, l in graph.edges(graph_node, data="label"):
            ns.setdefault(l, set()).add(u)

        box_dfa_dict = rsm.boxes[rsm_state[0]].dfa.to_dict()
        if rsm_state[1] not in box_dfa_dict:
            continue
        for s, to in box_dfa_dict[rsm_state[1]].items():
            if s not in rsm.labels:
                if s.value not in ns:
                    continue
                for node in ns[s.value]:
                    push(node, (rsm_state[0], to.value), stack_state)
            else:
                ss = (s.value, graph_node)
                if ss in pop:
                    for gn in pop[ss]:
                        push(gn, (rsm_state[0], to.value), stack_state)
                stack_graph.setdefault(ss, set()).add(
                    (stack_state, (rsm_state[0], to.value))
                )
                push(graph_node, (s.value, rsm.boxes[s].dfa.start_state.value), ss)
    return res
