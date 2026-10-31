from automata_extensions.fa import ExtendedDFA

S = frozenset({'x'})
T = frozenset({'x', 'y'})


def make_frozenset_dfa():
    """DFA whose states are themselves frozensets (as after minimize)."""
    return ExtendedDFA(
        states={S, T},
        input_symbols={'a'},
        transitions={S: {'a': T}, T: {'a': T}},
        initial_state=S,
        final_states={T},
    )


def test_frozenset_state_is_not_mistaken_for_a_set_of_destinations():
    dfa = make_frozenset_dfa()
    assert dfa._successors(S) == {T}
    assert dfa.accessible_states() == {S, T}
    assert dfa.coaccessible_states() == {S, T}


def test_simulation_with_frozenset_state_names():
    dfa = make_frozenset_dfa()
    assert dfa.trace('a') == [frozenset({S}), frozenset({T})]
    assert dfa.accepts('a') is True
    assert dfa.accepts('') is False


def test_complete_with_frozenset_state_names():
    partial = ExtendedDFA(
        states={S, T},
        input_symbols={'a'},
        transitions={S: {'a': T}, T: {}},
        initial_state=S,
        final_states={T},
        allow_partial=True,
    )
    assert partial.is_complete() is False
    completed = partial.complete()
    assert completed.is_complete() is True
    assert completed.accepts('a') is True
    assert completed.accepts('aa') is False


def test_induced_subautomaton_with_frozenset_state_names():
    sub = make_frozenset_dfa().induced_subautomaton({S})
    assert sub.states == {S}
    assert dict(sub.transitions[S]) == {}  # la transition vers T est retirée
    assert sub.final_states == set()


def test_empty_frozenset_is_a_valid_state_name():
    empty = frozenset()
    dfa = ExtendedDFA(
        states={empty, S},
        input_symbols={'a'},
        transitions={empty: {'a': S}, S: {'a': empty}},
        initial_state=empty,
        final_states={S},
    )
    assert dfa.is_complete() is True
    assert dfa.accessible_states() == {empty, S}
    assert dfa.accepts('a') is True
    assert dfa.accepts('aa') is False