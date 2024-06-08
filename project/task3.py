from typing import Iterable, Union
from networkx import MultiDiGraph
from copy import deepcopy
from pyformlang.finite_automaton import (
    Symbol,
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
import scipy.sparse as sparse
from project.task2 import regex_to_dfa, graph_to_nfa


def as_set(obj):
    if not isinstance(obj, set):
        return {obj}
    return obj


class FiniteAutomaton:
    def __init__(
        self, obj: Union[NondeterministicFiniteAutomaton, DeterministicFiniteAutomaton]
    ):
        self.start = obj.start_states
        self.final = obj.final_states
        states = obj.to_dict()
        len_states = len(obj.states)
        self.mapping = {v: i for i, v in enumerate(obj.states)}
        self.matrix = dict()
        for label in obj.symbols:
            self.matrix[label] = sparse.dok_matrix((len_states, len_states), dtype=bool)
            for u, edges in states.items():
                if label in edges:
                    for v in as_set(edges[label]):
                        self.matrix[label][self.mapping[u], self.mapping[v]] = True

    def is_empty(self) -> bool:
        return len(self.matrix.values()) == 0

    def size(self) -> int:
        return len(self.mapping)

    def accepts(self, word: Iterable[Symbol]) -> bool:
        real_word = "".join(word)
        return self.to_automaton().accepts(real_word)

    def transitive_closure(self) -> sparse.dok_matrix:
        if self.is_empty():
            return sparse.dok_matrix((0, 0), dtype=bool)
        adj = sum(self.matrix.values()) + sparse.eye(
            self.size(), self.size(), dtype=bool
        )
        for _ in range(adj.shape[0]):
            adj += adj @ adj
        return adj

    def to_automaton(self) -> NondeterministicFiniteAutomaton:
        automaton = NondeterministicFiniteAutomaton()
        for label in self.matrix.keys():
            size = self.matrix[label].shape[0]
            for x in range(size):
                for y in range(size):
                    if self.matrix[label][x, y]:
                        automaton.add_transition(
                            self.mapping[State(x)],
                            label,
                            self.mapping[State(y)],
                        )
        for s in self.start:
            automaton.add_start_state(self.mapping[State(s)])
        for s in self.final:
            automaton.add_final_state(self.mapping[State(s)])
        return automaton


def intersect_automata(
    automaton1: FiniteAutomaton, automaton2: FiniteAutomaton
) -> FiniteAutomaton:
    res = deepcopy(automaton1)
    symbols = automaton1.matrix.keys() & automaton2.matrix.keys()
    matrices = {
        label: sparse.kron(automaton1.matrix[label], automaton2.matrix[label], "csr")
        for label in symbols
    }
    start = set()
    final = set()
    mapping = dict()
    for u, i in automaton1.mapping.items():
        for v, j in automaton2.mapping.items():
            k = len(automaton2.mapping) * i + j
            mapping[State(k)] = k
            if u in automaton1.start and v in automaton2.start:
                start.add(State(k))
            if u in automaton1.final and v in automaton2.final:
                final.add(State(k))
    res.matrix = matrices
    res.mapping = mapping
    res.start = start
    res.final = final
    return res


def paths_ends(
    graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int], regex: str
) -> list[tuple[any, any]]:
    q = FiniteAutomaton(regex_to_dfa(regex))
    automaton = FiniteAutomaton(graph_to_nfa(graph, start_nodes, final_nodes))
    intersection = intersect_automata(automaton, q)
    closure = intersection.transitive_closure()
    size = q.size()
    res = set()
    for u, v in zip(*closure.nonzero()):
        if u in intersection.start and v in intersection.final:
            res.add(
                (
                    automaton.mapping[u // size],
                    automaton.mapping[v // size],
                )
            )
    if len(q.start & q.final) > 0:
        res |= {(i, i) for i in start_nodes & final_nodes}
    res = list(res)
    return res
