from argparse import ArgumentParser
from time import time

import mydefaults

from messthaler_wulff import mylog
from messthaler_wulff.parsing import crystals as crystal_parsing
from messthaler_wulff.parsing import crystals as crystals_parser
from messthaler_wulff.parsing.graphs import GraphType
from messthaler_wulff.sim.anneal import Anneal


@mydefaults.sub_command
def crystals(parser: ArgumentParser) -> mydefaults.MAGIC:
    GraphType.add_args_graph(parser)
    parser.add_argument("atom_count", type=int)
    parser.add_argument("energy", type=int, help="The energy to search for."
                                                 "If this parameter is -1 then the energy is ignored")

    parser.add_argument("-m", "--maximum", type=int, default=10)
    parser.add_argument("-c", "--initial-crystal", default=tuple(), type=crystal_parsing.from_path)

    args = yield

    atom_count = args.atom_count
    energy = args.energy
    crystal = args.initial_crystal

    graph = GraphType.graph_from_args(args)
    anneal = Anneal(graph, min(len(graph), 2 * atom_count + 5), crystal)

    crystal_count = 0

    last_change = time()

    for state in anneal.generate_states():
        if last_change is not None and time() - last_change > 1:
            last_change = None
            mylog.log.warning("I seem to struggle to find any crystals matching the criteria. "
                              "Maybe you need to increase the radius of the generated graph?")

        if state.size == atom_count and (energy == -1 or state.energy == energy):
            last_change = time()
            print(crystals_parser.to_json(state.nodes))
            crystal_count += 1
            if crystal_count > args.maximum:
                break
