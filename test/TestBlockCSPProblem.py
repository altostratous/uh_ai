import unittest

from shapely.geometry import Polygon

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
