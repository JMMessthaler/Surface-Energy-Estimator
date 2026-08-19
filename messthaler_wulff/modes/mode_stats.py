from argparse import ArgumentParser

import mydefaults

from messthaler_wulff.parsing import crystals
from messthaler_wulff.parsing.graphs import GraphType
from messthaler_wulff.sim.qbv_simulation import QBVSimulation


@mydefaults.sub_command
def stats(parser: ArgumentParser) -> mydefaults.MAGIC:
    GraphType.add_args_graph(parser)
    parser.add_argument("crystal", default=tuple(), type=crystals.from_path)

    args = yield

    graph = GraphType.graph_from_args(args)
    crystal = args.crystal
    sim = QBVSimulation(graph)

    for x in crystal:
        sim.toggle(x)

    assert sim.size == len(crystal)

    print(f"Atom count: {sim.size}")
    print(f"Energy: {sim.energy}")
