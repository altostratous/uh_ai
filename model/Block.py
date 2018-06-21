from shapely.affinity import translate, rotate
from algorithm.normalization import move_to_top_left_corner


class Block(object):
    def __init__(self, polygon, color, domain):
        super(Block, self).__init__()
        self.polygon = move_to_top_left_corner(polygon)
        self.color = color
        self.domain = domain

    class Value(object):
        def __init__(self, x, y, rotation) -> None:
            super().__init__()
            self.x = x
            self.y = y
            self.rotation = rotation

        def __hash__(self):
            return 31 * self.x + self.y + 91 * (self.rotation / 90)

        def __eq__(self, other):
            if other is None:
                return False
            if not isinstance(other, Block.Value):
                return False
            return self.x == other.x and self.y == self.y and self.rotation == other.rotation

    def polygon_from_value(self, value):
        if value not in self.domain:
            raise ValueError("The given value is not in the domain of this variable.")
        polygon = translate(self.polygon, value.x, value.y)
        polygon = rotate(polygon, value.rotation)
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
