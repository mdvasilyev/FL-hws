from networkx import MultiDiGraph
from typing import Set
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State


def regex_to_dfa(reg):
    regex = Regex(reg)
    return regex.to_epsilon_nfa().minimize()


def graph_to_nfa(graph: MultiDiGraph, start: Set[int], final: Set[int]):
    nfa = NondeterministicFiniteAutomaton()
    if start is None or len(start) == 0:
        for node in graph.nodes:
            nfa.add_start_state(node)
    for node in start:
        nfa.add_start_state(node)
    if final is None or len(final) == 0:
        for node in graph.nodes:
            nfa.add_final_state(node)
    for node in final:
        nfa.add_final_state(node)
    for u, v, label in graph.edges(data="label"):
        nfa.add_transition(State(u), label, State(v))
    return nfa
