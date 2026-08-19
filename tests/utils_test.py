from collections import Counter

from hypothesis import given, example, strategies as st

from messthaler_wulff.utils import duplicates, unordered_remove


@example([1, 1, 2])
@example([1, 1, 2, 2])
@example(range(10))
@given(st.lists(st.integers(0, 10)))
def test_duplicates(lst):
    dups = duplicates(lst)
    dups_check = {k for k, v in Counter(lst).items() if v > 1}
    assert dups == dups_check


@example(range(10))
@given(st.lists(st.integers(0, 10), unique=True))
def test_duplicates_empty(lst):
    assert duplicates(lst) == set()


@given(st.lists(st.integers(0, 10), min_size=1, unique=True), st.integers(0, 100))
def test_unordered_remove(lst, index):
    index %= len(lst)

    el = lst[index]
    old = set(lst)

    unordered_remove(lst, index)
    assert set(lst) == old - {el}
