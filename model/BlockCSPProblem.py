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

        return clauses

    def import_cnf_model(self, model):
        for symbol in model.keys():
            if model[symbol]:
                self.set_variable(symbol[0], symbol[1])

    def set_variable(self, query_variable, value):
        for variable in self.variables:
            if variable == query_variable:
                if value in variable.domain:
                    variable.domain = [value]
                    return
                else:
                    raise ValueError('Value is not in the domain of the variable.')
        ValueError('Variable not found!')

    @staticmethod
    def is_solution_sound(solved_problem):
        for source_variable in solved_problem.variables:
            for destination_variable in solved_problem.variables:
                if source_variable is destination_variable:
                    continue
                if source_variable.domain.__len__() !=  1:
                    return False
                if destination_variable.domain.__len__() != 1:
                    return False
                constraint_is_complied = Block.check_constraint(
                    source_variable, source_variable.domain[0],
                    destination_variable, destination_variable.domain[0]
                )
                if not constraint_is_complied:
                    return False
        return True
