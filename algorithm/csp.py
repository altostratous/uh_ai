from model import BlockCSPProblem, Block
from copy import deepcopy


def removed_a_value_from_domain(arc):
    length = len(arc[0].domain)
    arc[0].domain = arc[0].get_arc_consistent_domain_with(arc[1])
    if len(arc[0].domain) == length:
        return False
    return True


def arc_consistency_checking_algorithm(original_problem, variable_index=None):
    arcs = set()
    problem = deepcopy(original_problem)
    if variable_index is None:
        for first_variable in problem.variables:
            for second_variable in problem.variables:
                if first_variable is second_variable:
                    continue
                arcs.add((first_variable, second_variable))
    else:
        for first_variable in problem.variables:
            if first_variable is problem.variables[variable_index]:
                continue
            arcs.add((first_variable, problem.variables[variable_index]))

    while len(arcs) != 0:
        arc = arcs.pop()
        if removed_a_value_from_domain(arc):
            for variable in problem.variables:
                if variable is arc[0]:
                    continue
                arcs.add((variable, arc[0]))
    return problem


def dfs_with_ac3(original_problem, variable=None):
    problem = arc_consistency_checking_algorithm(original_problem, variable)

    for v in problem.variables:
        if len(v.domain) == 0:
            return None

    for v in range(len(problem.variables)):
        if len(problem.variables[v].domain) > 1:
            original_domain = problem.variables[v].domain
            for value in original_domain:
                problem.variables[v].domain = [value]
                sub_problem = dfs_with_ac3(problem, v)
                if sub_problem is not None:
                    return sub_problem
            return None

    return problem
