#
# from messthaler_wulff.parsing import parse_crystal, crystal_re, allowed_characters
#
#
# @given(st.lists(st.lists(st.integers(), min_size=1).map(tuple)))
# def test_random_lists(l: list[tuple]):
#     assert parse_crystal(str(l)) == l
#
#
# @given(st.from_regex(crystal_re, fullmatch=True))
# def test_random_data(string: str):
#     result = parse_crystal(string)
#     assert isinstance(result, list)
#
# @given(st.lists(st.lists(st.integers(), min_size=1).map(tuple)))
# def test_allowed_characters(l: list[tuple]):
#     assert frozenset(str(l)) < allowed_characters
from pathlib import Path

from hypothesis import given, strategies as st

from messthaler_wulff.math.bravais import CommonBravais
from messthaler_wulff.parsing.graphs import GraphType

tests = Path("tests")


def test_graph1():
    t = GraphType.from_path(tests / "graphs" / "graph1.json")
    g = t.graph([])
    assert len(g) == 7
    assert len(g.edges) == 7


bravais_data = {
    CommonBravais.square: 4,
    CommonBravais.cubic: 6,
    CommonBravais.triangular: 6,
    CommonBravais.fcc: 12
}


@given(st.one_of(map(st.just, CommonBravais)))
def test_builtin_bravais(name: CommonBravais):
    t = GraphType.from_path(Path(name.name))
    g = t.graph([1])

    assert name in bravais_data
    degree = bravais_data[name]
    assert len(g) == degree + 1
