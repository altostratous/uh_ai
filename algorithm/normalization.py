from shapely import affinity


def move_to_top_left_corner(polygon):
    bounds = polygon.bounds
    return affinity.translate(polygon, -bounds[0], -bounds[1])
