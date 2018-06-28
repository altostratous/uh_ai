class BlockCSPProblem(object):
    def __init__(self, variables, space=None):
        super().__init__()
        self.variables = variables

        if space is not None:
            for variable in self.variables:
                variable.domain = variable.get_consistent_domain_with_space(space)
