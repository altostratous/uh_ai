from collections import Counter
from copy import deepcopy


def is_consistent(clauses):
    for c in clauses:
        if len(c) != 1:
            return False
    for c1 in clauses:
        for c2 in clauses:
            if c1[0][0] == c2[0][0] and c1[0][1] != c2[0][1]:
                return False

    return True


def contains_empty(clauses):
    for c in clauses:
        if len(c) == 0:
            return True
    return False


def DPLL(clauses, solution=[]):

    if is_consistent(clauses):
        return solution

    if contains_empty(clauses):
        return False

    literals_index = set()
    copy = deepcopy(clauses)
    for c in range(len(copy)):
        if len(copy[c]) == 1:
            continue
        for l in range(len(copy[c])):
            literals_index.add((c, l))

    if len(literals_index) == 0:
        print("no literals")
        return solution

    var = literals_index.pop()
    solution_t = deepcopy(solution)
    solution_t.append((clauses[var[0]][var[1]][0], True))
    clauses_t = deepcopy(clauses)
    clauses_t[var[0]].pop(var[1])
    clauses_t.append([(clauses[var[0]][var[1]], True)])

    solution_f = deepcopy(solution)
    solution_f.append((clauses[var[0]][var[1]][0], False))
    clauses_f = deepcopy(clauses)
    clauses_f[var[0]].pop(var[1])
    clauses_f.append([(clauses[var[0]][var[1]], False)])

    return DPLL(clauses_t, solution_t) or DPLL(clauses_f, solution_f)


def print_result(literals):
    if not literals:
        print("There is no solution!")
        return False
    result = set()
    for j in literals:
        if j[1]:
            result.add((j[0][0].__str__(), j[0][1].__str__()))
    print(result)
