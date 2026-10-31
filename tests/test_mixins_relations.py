import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_even_a_dfa():
    """Complete DFA over {a, b} accepting an even number of 'a'."""
    return ExtendedDFA(
        states={'even', 'odd'},
        input_symbols={'a', 'b'},
        transitions={
            'even': {'a': 'odd', 'b': 'even'},
            'odd': {'a': 'even', 'b': 'odd'},
        },
        initial_state='even',
        final_states={'even'},
    )


def make_renamed_even_a_dfa():
    """Same automaton as make_even_a_dfa, with states renamed x and y."""
    return ExtendedDFA(
        states={'x', 'y'},
        input_symbols={'a', 'b'},
        transitions={
            'x': {'a': 'y', 'b': 'x'},
            'y': {'a': 'x', 'b': 'y'},
        },
        initial_state='x',
        final_states={'x'},
    )


def make_partial_a_dfa(first='p0', second='p1'):
    """Partial DFA over {a, b} recognizing {a}, with chosen state names."""
    return ExtendedDFA(
        states={first, second},
        input_symbols={'a', 'b'},
        transitions={first: {'a': second}, second: {}},
        initial_state=first,
        final_states={second},
        allow_partial=True,
    )


def test_is_isomorphic_after_renaming_states():
    assert make_even_a_dfa().is_isomorphic(make_renamed_even_a_dfa()) is True


def test_is_isomorphic_is_symmetric():
    first = make_even_a_dfa()
    second = make_renamed_even_a_dfa()
    assert second.is_isomorphic(first) is True


def test_is_isomorphic_false_when_final_states_differ():
    odd_language = ExtendedDFA(
        states={'x', 'y'},
        input_symbols={'a', 'b'},
        transitions={
            'x': {'a': 'y', 'b': 'x'},
            'y': {'a': 'x', 'b': 'y'},
        },
        initial_state='x',
        final_states={'y'},
    )
    assert make_even_a_dfa().is_isomorphic(odd_language) is False


def test_is_isomorphic_false_when_same_language_but_different_size():
    redundant = ExtendedDFA(
        states={'e1', 'e2', 'o'},
        input_symbols={'a', 'b'},
        transitions={
            'e1': {'a': 'o', 'b': 'e2'},
            'e2': {'a': 'o', 'b': 'e1'},
            'o': {'a': 'e1', 'b': 'o'},
        },
        initial_state='e1',
        final_states={'e1', 'e2'},
    )
    even = make_even_a_dfa()
    assert even.language_equals(redundant) is True
    assert even.is_isomorphic(redundant) is False


def test_is_isomorphic_false_when_transitions_do_not_match():
    # Même nombre d'états, même état initial final, mais structure différente
    other = ExtendedDFA(
        states={'s0', 's1'},
        input_symbols={'a', 'b'},
        transitions={
            's0': {'a': 's1', 'b': 's0'},
            's1': {'a': 's1', 'b': 's0'},
        },
        initial_state='s0',
        final_states={'s0'},
    )
    assert make_even_a_dfa().is_isomorphic(other) is False


def test_is_isomorphic_ignores_unreachable_states():
    with_unreachable = ExtendedDFA(
        states={'x', 'y', 'z'},
        input_symbols={'a', 'b'},
        transitions={
            'x': {'a': 'y', 'b': 'x'},
            'y': {'a': 'x', 'b': 'y'},
            'z': {'a': 'z', 'b': 'z'},  # inaccessible
        },
        initial_state='x',
        final_states={'x'},
    )
    assert make_even_a_dfa().is_isomorphic(with_unreachable) is True


def test_is_isomorphic_false_with_different_alphabets():
    only_a = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    assert make_even_a_dfa().is_isomorphic(only_a) is False


def test_is_isomorphic_with_partial_automata():
    assert make_partial_a_dfa('p0', 'p1').is_isomorphic(
        make_partial_a_dfa('u', 'v')
    ) is True

    # Une transition de plus (b) : plus isomorphe
    with_extra = ExtendedDFA(
        states={'u', 'v'},
        input_symbols={'a', 'b'},
        transitions={'u': {'a': 'v', 'b': 'u'}, 'v': {}},
        initial_state='u',
        final_states={'v'},
        allow_partial=True,
    )
    assert make_partial_a_dfa('p0', 'p1').is_isomorphic(with_extra) is False


def test_is_isomorphic_rejects_nfa():
    nfa = ExtendedNFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': {'q0'}, 'b': {'q0'}}},
        initial_state='q0',
        final_states={'q0'},
    )
    with pytest.raises(NotImplementedError):
        make_even_a_dfa().is_isomorphic(nfa)