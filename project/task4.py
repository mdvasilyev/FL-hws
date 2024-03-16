from scipy.sparse import *
from project.task3 import FiniteAutomaton


def diagonalise(mat):
    result = dok_matrix(mat.shape, dtype=bool)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[0]):
            if mat[j, i]:
                result[i] += mat[j]
    return result


def reachability_with_constraints(
    fa: FiniteAutomaton, constraints_fa: FiniteAutomaton
) -> dict[int, set[int]]:

    m, n = constraints_fa.size, fa.size

    labels = fa.labels & constraints_fa.labels
    result = {s: set() for s in fa.start}
    adj = {
        label: block_diag((constraints_fa.m[label], fa.m[label])) for label in labels
    }

    for v in fa.start_idx:
        front = dok_matrix((m, m + n), dtype=bool)
        for i in constraints_fa.start_idx:
            front[i, i] = True
        for i in range(m):
            front[i, v + m] = True
        for _ in range(m * n):
            front = sum(
                [dok_matrix((m, m + n), dtype=bool)]
                + [diagonalise(front @ adj[label]) for label in labels]
            )
            for i in constraints_fa.final_idx:
                for j in fa.final_idx:
                    if front[i, j + m]:
                        result[v].add(j)
    return result
