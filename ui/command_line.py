from model import Block, BlockCSPProblem
from algorithm.csp import dfs_with_ac3
from shapely.geometry import Polygon, Point

m, n, p = map(int, input().split())

space = Polygon([(0, 0), (n, 0), (n, m), (0, m)])

domain = []
for i in range(n):
    for j in range(m):
        for rotation in range(0, 360, 90):
            domain.append(Block.Value(i, j, rotation))

blocks = []
for i in range(p):
    k, c = map(int, input().split())
    pieces = []
    for j in range(k):
        line = input()
        for x in range(len(line)):
            if line[x] == '*':
                pieces.append(Polygon([(x, j), (x + 1, j), (x + 1, j + 1), (x, j + 1)]))

    block_polygon = pieces[0]
    for piece in pieces:
        block_polygon = block_polygon.union(piece).simplify(0)
    blocks.append(Block(block_polygon, c, domain))

problem = BlockCSPProblem(blocks, space)
solution = dfs_with_ac3(problem)

if solution is None:
    print("There is no solution!")
    exit(0)

screen = [[0 for j in range(m)] for i in range(n)]
for i in range(n):
    for j in range(m):
        for v in range(len(solution.variables)):
            polygon = solution.variables[v].polygon_from_value(solution.variables[v].domain[0])
            if polygon.contains(Point(i + 0.5, j + 0.5)):
                if screen[i][j] != 0:
                    screen[i][j] = '@'
                    continue
                screen[i][j] = v + 1

for j in range(m):
    for i in range(n):
        print(screen[i][j], end=" ")
    print()