from networkx import MultiDiGraph
from typing import Set
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State


def regex_to_dfa(reg):
    regex = Regex(reg)
    nfa = regex.to_epsilon_nfa()
    return nfa.to_deterministic().minimize()


def graph_to_nfa(graph: MultiDiGraph, start: Set[int], final: Set[int]):
    nfa = NondeterministicFiniteAutomaton(graph)
    if not start:
        for i in graph.nodes():
            start.add(i)
    if not final:
        for i in graph.nodes():
            final.add(i)
    for node in start:
        nfa.add_start_state(State(node))
    for node in final:
        nfa.add_final_state(State(node))
    for v, u, data in graph.edges(data=True):
        nfa.add_transition(v, data["label"], u)
    return nfa
