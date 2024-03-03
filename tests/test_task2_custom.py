from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
import project.task2 as automatons
import pytest


def test_regex_dfa():
    dfa = automatons.regex_to_dfa("abc (abc* def*)*")
    expected = NondeterministicFiniteAutomaton()
    expected.add_start_state(0)
    expected.add_final_state(1)
    expected.add_transitions([(0, "abc", 1), (1, "abc", 1), (1, "def", 1)])
    assert expected.is_equivalent_to(dfa)


@pytest.mark.parametrize(
    "regex", ["abc def", "abc|def", "abc def*", "abc def | def abc", "(abc* def*)*"]
)
def test_regex_dfa_minimal(regex):
    dfa = automatons.regex_to_dfa(regex)
    min_dfa = dfa.minimize()
    assert dfa.is_deterministic()
    assert dfa.is_equivalent_to(min_dfa)
    assert len(min_dfa.states) == len(dfa.states)
    assert min_dfa.get_number_transitions() == dfa.get_number_transitions()
