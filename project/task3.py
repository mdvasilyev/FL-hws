from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
from scipy.sparse import dok_matrix, kron
from project.task2 import graph_to_nfa, regex_to_dfa


def as_set(obj):
    if not isinstance(obj, set):
        return {obj}
    return obj


class FiniteAutomaton:
    m = None
    start = None
    final = None
    mapping = None
    gg = True
    null_symbols = None
    states = None

    def __init__(
        self, obj, start=set(), final=set(), mapping=dict(), matrix_class=dok_matrix
    ):
        if isinstance(
            obj, (DeterministicFiniteAutomaton, NondeterministicFiniteAutomaton)
        ):
            matrix = nfa_to_matrix(obj, matrix_class=matrix_class)
            self.m = matrix.m
            self.start = matrix.start
            self.final = matrix.final
            self.mapping = matrix.mapping
        else:
            self.m = obj
            self.start = start
            self.final = final
            self.mapping = mapping

    def accepts(self, word) -> bool:
        nfa = matrix_to_nfa(self)
        real_word = "".join(list(word))
        return nfa.accepts(real_word)

    def is_empty(self) -> bool:
        if len(self.m) == 0:
            return True
        m = sum(self.m.values())
        for _ in range(m.shape[0]):
            m += m @ m
        if m.shape[0] != 0 or m.shape[1] != 0:
            return True
        for u in self.start:
            for v in self.final:
                if m[u, v] != 0:
                    return False
        return True

    def size(self):
        return len(self.mapping)

    def map_for(self, u) -> int:
        return self.mapping[State(u)]

    def labels(self):
        return self.mapping.keys() if self.gg else self.m.keys()


def nfa_to_matrix(
    automaton: NondeterministicFiniteAutomaton, matrix_class=dok_matrix
) -> FiniteAutomaton:
    states = automaton.to_dict()
    len_states = len(automaton.states)
    mapping = {v: i for i, v in enumerate(automaton.states)}
    m = dict()

    for label in automaton.symbols:
        m[label] = matrix_class((len_states, len_states), dtype=bool)
        for u, edges in states.items():
            if label in edges:
                for v in as_set(edges[label]):
                    m[label][mapping[u], mapping[v]] = True

    res = FiniteAutomaton(m, automaton.start_states, automaton.final_states, mapping)
    res.states = len(automaton.states)
    return res


def matrix_to_nfa(automaton: FiniteAutomaton) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton()
    for label in automaton.m.keys():
        m_size = automaton.m[label].shape[0]
        for u in range(m_size):
            for v in range(m_size):
                if automaton.m[label][u, v]:
                    nfa.add_transition(
                        automaton.map_for(u), label, automaton.map_for(v)
                    )
    for s in automaton.start:
        nfa.add_start_state(automaton.map_for(s))
    for s in automaton.final:
        nfa.add_final_state(automaton.map_for(s))
    return nfa


def transitive_closure(automaton: FiniteAutomaton):
    if len(automaton.m.values()) == 0:
        return dok_matrix((0, 0), dtype=bool)
    adj = sum(automaton.m.values())
    lst = -1
    while adj.count_nonzero() != lst:
        lst = adj.count_nonzero()
        adj += adj @ adj
    return adj


def intersect_automata(
    automaton1: FiniteAutomaton,
    automaton2: FiniteAutomaton,
    matrix_class_id="csr",
    g=True,
) -> FiniteAutomaton:
    automaton1.gg = not g
    automaton2.gg = not g
    labels = automaton1.labels() & automaton2.labels()
    m = dict()
    start = set()
    final = set()
    mapping = dict()
    for label in labels:
        m[label] = kron(automaton1.m[label], automaton2.m[label], matrix_class_id)
    for u, i in automaton1.mapping.items():
        for v, j in automaton2.mapping.items():
            k = len(automaton2.mapping) * i + j
            mapping[State(k)] = k
            if u in automaton1.start and v in automaton2.start:
                start.add(State(k))
            if u in automaton1.final and v in automaton2.final:
                final.add(State(k))
    return FiniteAutomaton(m, start, final, mapping)


def reachability_with_constraints_transitive(
    graph_nfa, regex_dfa, matrix_class_id="csr"
) -> list[tuple[object, object]]:
    intersection = intersect_automata(
        graph_nfa, regex_dfa, matrix_class_id=matrix_class_id, g=False
    )
    closure = transitive_closure(intersection)
    mapping = {v: i for i, v in graph_nfa.mapping.items()}
    result = list()
    for u, v in zip(*closure.nonzero()):
        if u in intersection.start and v in intersection.final:
            result.append(
                (mapping[u // regex_dfa.size()], mapping[v // regex_dfa.size()])
            )
    return result


def paths_ends(
    graph: MultiDiGraph,
    start_nodes: set[int],
    final_nodes: set[int],
    regex: str,
    matrix_class=dok_matrix,
    matrix_class_id="csr",
) -> list[tuple[object, object]]:
    graph_nfa = nfa_to_matrix(
        graph_to_nfa(graph, start_nodes, final_nodes), matrix_class=matrix_class
    )
    regex_dfa = nfa_to_matrix(regex_to_dfa(regex), matrix_class=matrix_class)
    return reachability_with_constraints_transitive(
        graph_nfa, regex_dfa, matrix_class_id=matrix_class_id
    )
