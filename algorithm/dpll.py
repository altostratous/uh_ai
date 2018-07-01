from copy import deepcopy


def assign(clauses, literal, value):
    copy = deepcopy(clauses)
    for c in clauses:
        for l in c:
            if l[0] == literal and l[1] == value:
                copy.remove(c)  # satisfied
                break
    return copy


def DPLL(clauses, variables, solution=[]):

    if len(variables) == 0:
        if len(clauses) == 0:
            return solution
        else:
            return False

    variables_t = deepcopy(variables)
    var_t = variables_t.pop()
    clauses_t = assign(clauses, var_t, True)
    solution_t = deepcopy(solution)
    solution_t.append((var_t, True))

    variables_f = deepcopy(variables)
    var_f = variables_f.pop()
    clauses_f = assign(clauses, var_f, False)
    solution_f = deepcopy(solution)
    solution_f.append((var_f, False))

    return DPLL(clauses_t, variables_t, solution_t) or DPLL(clauses_f, variables_f, solution_f)


def print_c(clauses):
    for i in clauses:
        for j in i:
            if j[1]:
                print(j[0], end="  ")
            else:
                print(j[0], end="' ")
        print()


clause = []
a = "a"
b = "b"
variables = [a, b]
clause.append([(a, False), (b, False)])
clause.append([(a, True), (b, True)])

print_c(clause)

print(DPLL(clause, variables))
