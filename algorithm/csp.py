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
    for i in problem.variables:
        for j in problem.variables:
            arcs.add((i, j))
    while len(arcs) != 0:
        arc = arcs[0]
        arcs.remove(arc)
        if removed_a_value_from_domain(arc):
            for i in problem.variables:
                arcs.add((arc[0], i))
    return problem

def dfs_with_ac3(original_problem):
    problem = arc_consistency_checking_algorithm(original_problem)
    for v in problem.variables:
        if len(v.domain) > 1:
            for d in v.domain:
                newlist = []
                newlist.append(d)
                v.domain = newlist
                dfs_with_ac3(problem)
    return problem



