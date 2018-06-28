import unittest

import subprocess
from shapely.geometry import Polygon

from algorithm.csp import arc_consistency_checking_algorithm, dfs_with_ac3
from model import BlockCSPProblem, Block


class TestBlockCSPProblem(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.reference_polygon = Polygon([
            (0, 0),
            (1, 0),
            (1, 1),
            (0, 1),
        ])
        self.side_tangent_polygon = Polygon([
            (1, 0),
            (2, 0),
            (2, 1),
            (1, 1),
        ])
        self.point_tangent_polygon = Polygon([
            (1, 1),
            (2, 1),
            (2, 2),
            (1, 2),
        ])
        self.crossing_polygon = Polygon([
            (0, 0.5),
            (1, 0.5),
            (1, 1.5),
            (0, 1.5),
        ])
        domain = []
        for x in range(3):
            for y in range(3):
                for rotation in range(0, 360, 90):
                    domain.append(
                        Block.Value(x, y, rotation)
                    )
        self.domain = domain

    def test_create_problem_from_structured_data(self):
        BlockCSPProblem(
            [
                Block(
                    Polygon(
                        [
                            (0, 0),
                            (1, 0),
                            (1, 1),
                            (0, 1),
                        ]
                    ),
                    1,
                    self.domain,
                ),
                Block(
                    Polygon(
                        [
                            (0, 0),
                            (1, 0),
                            (1, 1),
                            (0, 1),
                        ]
                    ),
                    1,
                    self.domain,
                ),

            ]
        )

    def test_shapely_intersection(self):
        self.assertGreater(self.crossing_polygon.intersection(self.reference_polygon).area, 0)
        self.assertEqual(self.point_tangent_polygon.intersection(self.reference_polygon).area, 0)
        self.assertEqual(self.side_tangent_polygon.intersection(self.reference_polygon).area, 0)
        self.assertGreater(self.side_tangent_polygon.intersection(self.reference_polygon).length, 0)
        self.assertEqual(self.point_tangent_polygon.intersection(self.reference_polygon).length, 0)

    def test_constraint(self):
        reference_block = Block(self.reference_polygon, 1, self.domain)
        reference_value = Block.Value(0, 0, 0)
        block_with_same_color = Block(self.reference_polygon, 1, self.domain)
        block_with_different_color = Block(self.reference_polygon, 2, self.domain)

        self.assertTrue(Block.check_constraint(
            reference_block, reference_value,
            block_with_different_color, Block.Value(1, 0, 0)
        ))

        self.assertFalse(Block.check_constraint(
            reference_block, reference_value,
            block_with_same_color, Block.Value(1, 0, 0)
        ))

        self.assertFalse(Block.check_constraint(
            reference_block, reference_value,
            block_with_different_color, Block.Value(0, 0, 0)
        ))

        self.assertFalse(Block.check_constraint(
            reference_block, reference_value,
            block_with_same_color, Block.Value(0, 0, 0)
        ))

        self.assertTrue(Block.check_constraint(
            reference_block, reference_value,
            block_with_different_color, Block.Value(1, 1, 0)
        ))

        self.assertTrue(Block.check_constraint(
            reference_block, reference_value,
            block_with_same_color, Block.Value(1, 1, 0)
        ))

    def test_arc_consistency_checking_algorithm(self):

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

        still_consistent = True
        for source_variable in original_problem.variables:
            for destination_variable in original_problem.variables:
                if source_variable is destination_variable:
                    continue
                if not source_variable.is_arc_consistent_with(destination_variable):
                    still_consistent = False

        self.assertFalse(still_consistent)

        consistent_problem = arc_consistency_checking_algorithm(original_problem)

        for source_variable in consistent_problem.variables:
            for destination_variable in consistent_problem.variables:
                if source_variable is destination_variable:
                    continue
                self.assertTrue(source_variable.is_arc_consistent_with(destination_variable))

    def help_test_dfs_with_ac3_with_problem(self, original_problem):

        still_consistent = True
        for source_variable in original_problem.variables:
            for destination_variable in original_problem.variables:
                if source_variable is destination_variable:
                    continue
                if not source_variable.is_arc_consistent_with(destination_variable):
                    still_consistent = False

        self.assertFalse(still_consistent)

        solved_problem = dfs_with_ac3(original_problem)

        for source_variable in solved_problem.variables:
            for destination_variable in solved_problem.variables:
                if source_variable is destination_variable:
                    continue
                self.assertEqual(source_variable.domain.__len__(), 1)
                self.assertEqual(destination_variable.domain.__len__(), 1)
                self.assertTrue(
                    Block.check_constraint(
                        source_variable, source_variable.domain[0],
                        destination_variable, destination_variable.domain[0]
                    )
                )

    def test_dfs_with_ac3_simple(self):

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

        self.help_test_dfs_with_ac3_with_problem(original_problem)

    def test_dfs_with_ac3_complicated(self):

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

        self.help_test_dfs_with_ac3_with_problem(original_problem)

    @staticmethod
    def normalize_output(output):
        output = output.replace(' \n', '\n')
        return output

    def test_ui(self):
        for i in range(2):
            with open('resources/test/in/{}.txt'.format(i)) as input_file:
                result = subprocess.check_output(['python', 'ui/command_line.py'], stdin=input_file, universal_newlines=True)
                with open('resources/test/out/{}.txt'.format(i)) as output_file:
                    self.assertEqual(
                        TestBlockCSPProblem.normalize_output(output_file.read()),
                        TestBlockCSPProblem.normalize_output(result),
                        msg='Output does not match for test number {}!'.format(i)
                    )

