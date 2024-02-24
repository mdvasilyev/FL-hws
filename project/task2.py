from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton


def regex_to_dfa(reg):
    regex = Regex(reg)
    nfa = regex.to_epsilon_nfa()
    return nfa.minimize()


def graph_to_nfa(graph, start, final):
    nfa = NondeterministicFiniteAutomaton(graph)
    for node in start:
        nfa.add_start_state(node)
    for node in final:
        nfa.add_final_state(node)
    for v, u, data in graph.edges(data=True):
        nfa.add_transition(v, data["label"], u)
    return nfa
