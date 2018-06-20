from shapely.geometry.polygon import Polygon

p = Polygon(
    [
        (0, 0),
        (1, 0),
        (1, 1),
    ]
)

p2 = Polygon(
    [
        (1, -20),
        (0, 0),
        (-2, -3),
    ]
)

print(p.overlaps(p2))
print(p.crosses(p2))
print(p.intersects(p2))
