from hypothesis import given, strategies as st
from hypothesis.strategies import DrawFn

from messthaler_wulff.math.bravais import CommonBravais, Bravais
from messthaler_wulff.sim import energies as nrg
from messthaler_wulff.sim.anneal import Anneal

GRAPH_RADIUS = 2
UPPER_BOUND = 1
DEFAULT_TIMEOUT = 0.1
GRAPHS = {bravais: bravais.graph(GRAPH_RADIUS) for bravais in CommonBravais.all}
ENERGIES: dict[Bravais, dict[int, int]] = {}
CRYSTAL_COUNT = 0
RANDOM_BRAVAIS = st.sampled_from(CommonBravais.all)

for _bravais in CommonBravais.all:
    _graph = GRAPHS[_bravais]
    _anneal = Anneal(_graph, min(UPPER_BOUND, len(_graph)))
    ENERGIES[_bravais] = nrg.find(_anneal.generate_states(), DEFAULT_TIMEOUT)


def random_initial(draw: DrawFn, bravais: Bravais, optimal: bool):
    graph = GRAPHS[bravais]
    upper_bound = min(len(graph), UPPER_BOUND)
    anneal = Anneal(graph, upper_bound)
    target_size = draw(st.integers(0, upper_bound - 1))
    optimal_energy = ENERGIES[bravais][target_size]

    for state in anneal.generate_states():
        if state.size == target_size:
            if optimal:
                if state.energy == optimal_energy:
                    return frozenset(state.nodes)
            else:
                return frozenset(state.nodes)


@st.composite
def bravais_initial(draw: DrawFn):
    bravais = draw(RANDOM_BRAVAIS)

    match draw(st.integers(1, 3)):
        case 1:
            return bravais, random_initial(draw, bravais, False)
        case 2:
            return bravais, random_initial(draw, bravais, True)
        case _:
            return bravais, tuple()


@given(bravais_initial())
def test_energies(stuff):
    bravais, initial = stuff
    graph = GRAPHS[bravais]
    upper_bound = min(len(graph), UPPER_BOUND)
    anneal = Anneal(graph, upper_bound, initial)

    energies = nrg.find(anneal.generate_states(), DEFAULT_TIMEOUT)
    assert set(energies.keys()) == set(range(len(initial), upper_bound + 1))
