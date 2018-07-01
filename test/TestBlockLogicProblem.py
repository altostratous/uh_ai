import unittest

import subprocess
from unittest import skip

from shapely.geometry import Polygon

from algorithm.csp import dfs_with_ac3
from algorithm.logic import dpll, evaluate_clauses_with_model
from algorithm.normalization import normalize_output
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

    def test_dpll_simple(self):
        clauses = [
            [('a', True)]
        ]

        result_model = dpll(clauses)

        self.assertIsNotNone(result_model)
        self.assertTrue(result_model['a'])

        variable = 'a'
        clauses = [
            [(variable, True)],
            [(variable, False)]
        ]

        result_model = dpll(clauses)

        self.assertIsNone(result_model)

    def test_dpll_complex(self):
        first_variable = 'a'
        second_variable = 'b'
        third_variable = 'c'

        clauses = [
            [(first_variable, True), (second_variable, False), (third_variable, False)],
            [(first_variable, False), (second_variable, True)],
            [(third_variable, True)]
        ]

        result_model = dpll(clauses)

        self.assertIsNotNone(result_model)
        self.assertTrue(result_model[third_variable])
        self.assertEqual(result_model[first_variable], result_model[second_variable])

        clauses = [
            [(first_variable, True), (second_variable, True), (third_variable, False)],
            [(first_variable, False), (second_variable, False)],
            [(third_variable, True)]
        ]

        result_model = dpll(clauses)

        self.assertIsNotNone(result_model)
        self.assertTrue(result_model[third_variable])
        self.assertNotEqual(result_model[first_variable], result_model[second_variable])

        clauses = [
            [(first_variable, True), (second_variable, True), (third_variable, False)],
            [(first_variable, False), (second_variable, False)],
            [(third_variable, True)],
            [(first_variable, True), (second_variable, False)],
            [(first_variable, False), (second_variable, True)],
        ]

        result_model = dpll(clauses)

        self.assertIsNone(result_model)

    def test_simple_block_logic_problem(self):
        domain = []
        for x in range(2):
            for y in range(1):
                for rotation in range(0, 360, 90):
                    domain.append(
                        Block.Value(x, y, rotation)
                    )

        original_problem = BlockCSPProblem([
            Block(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), 1, domain),
            Block(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), 0, domain),
        ], Polygon([(0, 0), (3, 0), (3, 3), (0, 3)]))

        logic_problem = original_problem.get_propositional_logic_cnf()

        solved_problem = dpll(logic_problem)

        self.assertIsNotNone(solved_problem)

        self.assertTrue(evaluate_clauses_with_model(logic_problem, solved_problem))

        original_problem.import_cnf_model(solved_problem)
        self.assertTrue(BlockCSPProblem.is_solution_sound(original_problem))

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

        solved_problem = dpll(logic_problem)

        self.assertIsNotNone(solved_problem)

        self.assertTrue(evaluate_clauses_with_model(logic_problem, solved_problem))

        original_problem.import_cnf_model(solved_problem)
        self.assertTrue(BlockCSPProblem.is_solution_sound(original_problem))

    @skip
    def test_ui_simple(self):
        for i in range(3):
            with open('resources/test/in/simple_{}.txt'.format(i)) as input_file:
                result = subprocess.check_output(
                    ['python', 'ui/command_line.py', '--dpll'],
                    stdin=input_file,
                    universal_newlines=True
                )
                with open('resources/test/out/simple_{}.txt'.format(i)) as output_file:
                    expected_outputs = normalize_output(output_file.read())
                    normalized_output = normalize_output(result)
                    self.assertTrue(
                        normalized_output in expected_outputs,
                        msg='Output does not match for test simple_{}!\n{}\nnot in\n{}'.format(
                            i,
                            normalized_output,
                            expected_outputs
                        )
                    )

    @skip('Due to our dpll performance issue.')
    def test_ui_complex(self):
        for i in range(1):
            with open('resources/test/in/{}.txt'.format(i)) as input_file:
                result = subprocess.check_output(
                    ['python', 'ui/command_line.py', '--dpll'],
                    stdin=input_file,
                    universal_newlines=True
                )
                with open('resources/test/out/{}.txt'.format(i)) as output_file:
                    expected_outputs = normalize_output(output_file.read())
                    normalized_output = normalize_output(result)
                    self.assertTrue(
                        normalized_output in expected_outputs,
                        msg='Output does not match for test simple_{}!\n{}\nnot in\n{}'.format(
                            i,
                            normalized_output,
                            expected_outputs
                        )
                    )
