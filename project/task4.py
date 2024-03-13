from scipy.sparse import *
from project.task3 import FiniteAutomaton


def diagonalise(m):
    h = m.shape[0]
    res = dok_matrix(m.shape, dtype=bool)
    for i in range(h):
        for j in range(h):
            if m[j, i]:
                res[i] += m[j]
    return res


def reachability_with_constraints(
    fa: FiniteAutomaton, constraints_fa: FiniteAutomaton
) -> dict[int, set[int]]:
    m_source = dict()
    ls = fa.matrix.keys() & constraints_fa.matrix.keys()
    m = len(constraints_fa.i_to_state)
    n = len(fa.i_to_state)
    for l in ls:
        a = constraints_fa.matrix[l]
        b = fa.matrix[l]
        m_source[l] = block_diag((a, b))
    h = m
    w = m + n
    res = {s.value: set() for s in fa.i_to_state}
    for state in fa.start_states:
        wv = dok_matrix((h, w), dtype=bool)
        for cst in constraints_fa.start_states:
            wv[cst, cst] = True
        for i in range(h):
            wv[i, state + m] = True
        for _ in range(m * n):
            new_wv = dok_matrix((h, w), dtype=bool)
            for l in ls:
                new_wv += diagonalise(wv @ m_source[l])
            wv = new_wv
            for i in range(h):
                if i in constraints_fa.final_states and wv[i, i]:
                    for j in range(n):
                        if j in fa.final_states and wv[i, j + m]:
                            res[fa.i_to_state[state]].add(fa.i_to_state[j])
    return res
