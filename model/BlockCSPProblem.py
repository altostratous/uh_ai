from model import Block


class BlockCSPProblem(object):
    def __init__(self, variables, space=None):
        super().__init__()
        self.variables = variables

        if space is not None:
            for variable in self.variables:
                variable.domain = variable.get_consistent_domain_with_space(space)

    def get_propositional_logic_cnf(self):

        logic_variables = []
        clauses = []
        for variable in self.variables:
            clause_to_ensure_at_least_one_assignment = []
            for value in variable.domain:
                logic_variable = (variable, value)
                logic_variables.append(
                    logic_variable
                )
                clause_to_ensure_at_least_one_assignment.append((logic_variable, True))
                for other_value in variable.domain:
                    other_logic_variable = (variable, other_value)
                    if value is other_value:
                        continue
                    clause_to_ensure_at_most_one_assignment = [
                        (logic_variable, False), (other_logic_variable, False)
                    ]
                    clauses.append(clause_to_ensure_at_most_one_assignment)
            clauses.append(clause_to_ensure_at_least_one_assignment)

        for first_logic_variable in logic_variables:
            for second_logic_variable in logic_variables:
                if first_logic_variable is second_logic_variable:
                    continue
                there_is_conflict = not Block.check_constraint(
                    first_logic_variable[0], first_logic_variable[1],
                    second_logic_variable[0], second_logic_variable[1]
                )
                if there_is_conflict:
                    clause_to_ensure_constraint = [
                        (first_logic_variable, False), (second_logic_variable, False)
                    ]

                    clauses.append(clause_to_ensure_constraint)

                    if len(clauses) > 1298:
                        pass

        return clauses
