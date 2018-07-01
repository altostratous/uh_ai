import random

import sys
from shapely.affinity import translate, rotate
from algorithm.normalization import move_to_top_left_corner


class Block(object):
    def __init__(self, polygon, color, domain):
        super(Block, self).__init__()
        self.polygon = move_to_top_left_corner(polygon)
        self.color = color
        self.domain = domain
        self.polygon_cache = {}
        self.id = random.randrange(0, sys.maxsize)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Block):
            return False
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return "Block " + (self.id % 1000)

    class Value(object):
        def __init__(self, x, y, rotation) -> None:
            super().__init__()
            self.x = x
            self.y = y
            self.rotation = rotation

        def __hash__(self):
            return 31 * self.x + self.y + 91 * int(self.rotation / 90)

        def __eq__(self, other):
            if other is None:
                return False
            if not isinstance(other, Block.Value):
                return False
            return self.x == other.x and self.y == other.y and self.rotation == other.rotation

        def __str__(self):
            return str((self.x, self.y, self.rotation))

    def polygon_from_value(self, value):
        if value not in self.domain:
            raise ValueError("The given value is not in the domain of this variable.")
        if value in self.polygon_cache:
            return self.polygon_cache[value]
        polygon = rotate(self.polygon, value.rotation)
        polygon = translate(polygon, value.x - polygon.bounds[0], value.y - polygon.bounds[1])
        self.polygon_cache[value] = polygon
        return polygon

    @staticmethod
    def check_constraint(first_block, first_value, second_block, second_value):
        first_polygon = first_block.polygon_from_value(first_value)
        second_polygon = second_block.polygon_from_value(second_value)
        intersection = first_polygon.intersection(second_polygon)
        if intersection.area > 0:
            return False
        if intersection.length > 0:
            if first_block.color == second_block.color:
                return False
        return True

    def get_arc_consistent_domain_with(self, other):
        consistent_domain = []
        for source_value in self.domain:
            for destination_value in other.domain:
                if Block.check_constraint(self, source_value, other, destination_value):
                    consistent_domain.append(source_value)
                    break
        return consistent_domain

    def is_arc_consistent_with(self, other):
        return len(self.domain) == len(self.get_arc_consistent_domain_with(other))

    def get_consistent_domain_with_space(self, space):
        consistent_domain = []
        for value in self.domain:
            if space.covers(self.polygon_from_value(value)):
                consistent_domain.append(value)
        return consistent_domain
