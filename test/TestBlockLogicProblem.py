import unittest

from shapely.geometry import Polygon

from algorithm.csp import dfs_with_ac3
from model import BlockCSPProblem, Block


class TestBlockLogicProblem(unittest.TestCase):

    def setUp(self):
        super().setUp()

    @staticmethod
    def does_solution_satisfy_logic_problem(solution, logic_problem):
        logic_problem_evaluates_to_true = True
        for i in range(len(logic_problem)):
            clause_evaluates_to_true = False
            for j in range(len(logic_problem[i])):
                for variable in solution.variables:
                    if logic_problem[i][j][0][0] == variable:
                        if (variable.domain[0] == logic_problem[i][j][0][1]) == logic_problem[i][j][1]:
                            clause_evaluates_to_true = True
            if not clause_evaluates_to_true:
                logic_problem_evaluates_to_true = False
        return logic_problem_evaluates_to_true

    def test_simple_csp_to_logic_conversion(self):

        domain = []
        for x in range(3):
            for y in range(3):
                for rotation in range(0, 360, 90):
                    domain.append(
                        Block.Value(x, y, rotation)
                    )

        original_problem = BlockCSPProblem([
            Block(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), 1, domain),
            Block(Polygon([(0, 0), (3, 0), (3, 3), (1, 3), (1, 2), (0, 2)]), 2, domain),
            ], Polygon([(0, 0), (3, 0), (3, 3), (0, 3)])
        )

        logic_problem = original_problem.get_propositional_logic_cnf()

        solved_problem = dfs_with_ac3(original_problem)

        self.assertIsNotNone(solved_problem)

        self.assertTrue(TestBlockLogicProblem.does_solution_satisfy_logic_problem(solved_problem, logic_problem))

        self.assertFalse(TestBlockLogicProblem.does_solution_satisfy_logic_problem(original_problem, logic_problem))
