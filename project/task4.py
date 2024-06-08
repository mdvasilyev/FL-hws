import scipy.sparse as sparse
from pyformlang.finite_automaton import State
from project.task3 import FiniteAutomaton


def reachability_with_constraints(
    fa: FiniteAutomaton, constraints_fa: FiniteAutomaton
) -> dict[int, set[int]]:

    def diagonalise(mat):
        res = sparse.dok_matrix(mat.shape, dtype=bool)
        for i in range(mat.shape[0]):
            for j in range(mat.shape[0]):
                if mat[j, i]:
                    res[i] += mat[j]
        return res

    m = constraints_fa.size()
    n = fa.size()
    labels = fa.matrix.keys() & constraints_fa.matrix.keys()
    res = {s: set() for s in fa.start}
    adj = {
        label: sparse.block_diag((constraints_fa.matrix[label], fa.matrix[label]))
        for label in labels
    }
    start_indeces = [constraints_fa.mapping[State(i)] for i in constraints_fa.start]
    for v in [fa.mapping[State(k)] for k in fa.start]:
        front = sparse.dok_matrix((m, m + n), dtype=bool)
        for i in start_indeces:
            front[i, i] = True
        for i in range(m):
            front[i, v + m] = True
        for i in [
            constraints_fa.mapping[State(k)]
            for k in (constraints_fa.final & constraints_fa.start)
        ]:
            for j in [fa.mapping[State(k)] for k in (fa.final & fa.start)]:
                if front[i, i] and front[i, j + m]:
                    res[v].add(j)

        for _ in range(m * n):
            new_front = sparse.dok_matrix((m, m + n), dtype=bool)
            for sym in labels:
                new_front += diagonalise(front @ adj[sym])
            front = new_front

            for i in [constraints_fa.mapping[State(k)] for k in constraints_fa.final]:
                for j in [fa.mapping[State(k)] for k in fa.final]:
                    if front[i, j + m]:
                        res[v].add(j)
    return res
