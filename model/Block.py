class Block(object):
    TANGENT = 0
    FAR = 1
    INTERSECTING = 2

    def __init__(self, points, color, coordinates=(0, 0), rotation=0):
        super(Block, self).__init__()
        self.points = points
        self.color = color
        self.coordinates = coordinates
        self.rotation = rotation

    def inter_relation(self, other_block):
        raise NotImplementedError()
