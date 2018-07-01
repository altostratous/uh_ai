from shapely import affinity
import re


def move_to_top_left_corner(polygon):
    bounds = polygon.bounds
    return affinity.translate(polygon, -bounds[0], -bounds[1])


def normalize_output(output):
    output = re.sub(r'Solved in.*seconds\n', '', output)
    output = output.replace(' \n', '\n')
    return output
