from argparse import ArgumentParser

import mydefaults
import numpy as np
import sys
from matplotlib.pyplot import show
from scipy.spatial import ConvexHull

from messthaler_wulff import mylog
from messthaler_wulff.math.bravais import plot_bravais_points, ax_bravais, Bravais, plot_bravais_lines
from messthaler_wulff.parsing import crystals
from messthaler_wulff.parsing.graphs import GraphType


def lines(bravais: Bravais, crystal):
    crystal = set(crystal)
    lines = set()

    for point in crystal:
        for i in range(bravais.degree):
            n = bravais.neighbor(point, i)
            if n in crystal:
                lines.add((point, n))

    return frozenset(lines)


def correct_face(points, triangle):
    center = sum(points) / len(points)
    a, b, c = triangle
    x = points[b] - points[a]
    y = points[c] - points[a]
    z = np.linalg.cross(x, y)
    test = center - points[a]

    if np.dot(z, test) >= 0:
        return [a, b, c]
    else:
        return [c, b, a]


def plot_convex_hull(bravais, points, ax=None, color=None, alpha=1.0):
    if ax is None:
        ax = ax_bravais(bravais)

    kwargs = {
        'antialiased': True,
        'shade': True,
        'alpha': alpha,
        'color': color
    }

    pos = lambda n: bravais.transform @ n
    points = np.array([pos(v) for v in points])

    ch = ConvexHull(points)

    vertices = ch.points
    x, y, z = np.transpose(np.array(vertices))
    triangles = [correct_face(points, t) for t in ch.simplices]

    ax.plot_trisurf(x, y, triangles, z, **kwargs)


@mydefaults.sub_command
def plot(parser: ArgumentParser) -> mydefaults.MAGIC:
    GraphType.add_args(parser)
    parser.add_argument("mode", help="Possible flag values are p,l,c standing for "
                                     "points, lines, convex hull respectively")

    parser.add_argument("crystal", default=tuple(), type=crystals.from_path)
    parser.add_argument("-o", "--orthogonal", action="store_true")
    parser.add_argument("-a", "--axis", action="store_true")
    parser.add_argument("-n", "--node-color", default="black")
    parser.add_argument("-e", "--edge-color", default="black")
    parser.add_argument("--hull-color", default=None)
    parser.add_argument("--node-alpha", default=1.0, type=float)
    parser.add_argument("--edge-alpha", default=1.0, type=float)
    parser.add_argument("--hull-alpha", default=1.0, type=float)

    args = yield

    assert set(args.mode) <= set("plc")

    graph_type = GraphType.from_args(args)
    bravais = graph_type.bravais()
    crystal = args.crystal
    ax = ax_bravais(bravais)
    if bravais.dimension == 3:
        ax.set_proj_type('ortho' if args.orthogonal else 'persp')

    if not args.axis:
        ax.axis("off")

    if "p" in args.mode:
        plot_bravais_points(bravais, crystal, ax, args.node_color, args.node_alpha)

    if "l" in args.mode:
        plot_bravais_lines(bravais, lines(bravais, crystal), ax, args.edge_color, args.edge_alpha)

    if "c" in args.mode:
        if bravais.dimension != 3:
            mylog.log.error(f"Cannot plot convex hull with a {bravais.dimension}d bravais lattice")
            sys.exit(-1)
        plot_convex_hull(bravais, crystal, ax, args.hull_color, args.hull_alpha)

    ax.set_aspect('equal')
    show()
