import pytest

from automata_extensions.fa import ExtendedDFA


def make_even_a_dfa():
    """DFA over {a, b} accepting words with an even number of 'a'."""
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


def test_accepts_general_case():
    dfa = make_even_a_dfa()
    assert dfa.accepts('aab') is True
    assert dfa.accepts('a') is False
    assert dfa.accepts('bab') is False


def test_accepts_empty_word():
    dfa = make_even_a_dfa()
    # L'état initial est final : le mot vide est accepté
    assert dfa.accepts('') is True


def test_trace_general_case():
    dfa = make_even_a_dfa()
    assert dfa.trace('aab') == [
        frozenset({'even'}),
        frozenset({'odd'}),
        frozenset({'even'}),
        frozenset({'even'}),
    ]


def test_trace_empty_word_is_just_initial_configuration():
    dfa = make_even_a_dfa()
    assert dfa.trace('') == [frozenset({'even'})]


def test_trace_blocked_partial_dfa_gives_empty_set():
    dfa = ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q1'}, 'q1': {}},
        initial_state='q0',
        final_states={'q1'},
        allow_partial=True,
    )
    # "b" n'a pas de transition depuis q0 : l'automate est bloqué
    assert dfa.trace('bb') == [
        frozenset({'q0'}),
        frozenset(),
        frozenset(),
    ]
    assert dfa.accepts('bb') is False
    assert dfa.accepts('a') is True


def test_accepts_rejects_symbol_outside_alphabet():
    dfa = make_even_a_dfa()
    with pytest.raises(ValueError):
        dfa.accepts('abc')