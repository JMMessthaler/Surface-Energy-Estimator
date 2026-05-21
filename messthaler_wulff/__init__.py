# PYTHON_ARGCOMPLETE_OK


from argparse import ArgumentParser

import argcomplete
import mydefaults

from . import mylog
from .modes import mode_energies, mode_crystals, mode_stats, mode_plot
from .version import program_version

mylog.init()


@mydefaults.command(version=program_version)
def messthaler_wulff(parser: ArgumentParser):
    """Blazingly fast code for finding all crystals
    (subsets of a graph) that can be constructed
    using only transformations that locally minimize
    surface energy."""

    subparsers = parser.add_subparsers(title="Modes", description="Possible modes of operation", required=True)
    mydefaults.add_sub_commands(subparsers)

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    mylog.set_level(args.quiet - args.verbose)
    mylog.log.debug("Starting program...")

    mydefaults.run_sub_command(args)
