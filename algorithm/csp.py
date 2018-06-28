from model import BlockCSPProblem, Block
from copy import deepcopy


def removed_a_value_from_domain(arc):
    length = len(arc[0].domain)
    arc[0].domain = arc[0].get_arc_consistent_domain_with(arc[1])
    if len(arc[0].domain) == length:
        return False
    return True


def arc_consistency_checking_algorithm(original_problem):
    problem = deepcopy(original_problem)
    arcs = set()
    for first_variable in problem.variables:
        for second_variable in problem.variables:
            if first_variable is second_variable:
                continue
            arcs.add((first_variable, second_variable))
    while len(arcs) != 0:
        arc = arcs.pop()
        if removed_a_value_from_domain(arc):
            for variable in problem.variables:
                if variable is arc[0]:
                    continue
                arcs.add((variable, arc[0]))
    return problem


def dfs_with_ac3(original_problem):
    problem = arc_consistency_checking_algorithm(original_problem)

    for v in problem.variables:
        if len(v.domain) == 0:
            return None

    for v in problem.variables:
        if len(v.domain) > 1:
            original_domain = v.domain
            for value in original_domain:
                v.domain = [value]
                sub_problem = dfs_with_ac3(problem)
                if sub_problem is not None:
                    return sub_problem
            return None

    return problem
