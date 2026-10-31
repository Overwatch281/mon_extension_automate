import itertools

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def all_words(max_length):
    """Every word over {a, b} of length 0 to `max_length`."""
    for length in range(max_length + 1):
        for letters in itertools.product('ab', repeat=length):
            yield ''.join(letters)


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


def make_partial_a_dfa():
    """Partial DFA over {a, b} recognizing the language {a}."""
    return ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q1'}, 'q1': {}},
        initial_state='q0',
        final_states={'q1'},
        allow_partial=True,
    )


def make_ends_with_ab_nfa():
    """NFA over {a, b} accepting the words ending with 'ab'."""
    return ExtendedNFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': {'q0', 'q1'}, 'b': {'q0'}},
            'q1': {'b': {'q2'}},
            'q2': {},
        },
        initial_state='q0',
        final_states={'q2'},
    )


def make_epsilon_nfa():
    """NFA with an epsilon transition, accepting the language a b*."""
    return ExtendedNFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'': {'q1'}},
            'q1': {'a': {'q2'}},
            'q2': {'b': {'q2'}},
        },
        initial_state='q0',
        final_states={'q2'},
    )


ALL_AUTOMATA = [
    make_even_a_dfa,
    make_partial_a_dfa,
    make_ends_with_ab_nfa,
    make_epsilon_nfa,
]


# ------------------------------------------------------------ #47 left quotient

def test_left_quotient_definition_on_every_small_word():
    for make in ALL_AUTOMATA:
        automaton = make()
        for u in all_words(3):
            quotient = automaton.left_quotient(u)
            for w in all_words(4):
                assert quotient.accepts(w) == automaton.accepts(u + w), (make.__name__, u, w)


def test_left_quotient_of_a_dfa_moves_the_initial_state():
    dfa = make_even_a_dfa()
    quotient = dfa.left_quotient('a')
    assert type(quotient) is ExtendedDFA
    assert quotient.initial_state == 'odd'
    assert quotient.states == dfa.states
    assert dfa.initial_state == 'even'  # l'original n'a pas changé


def test_left_quotient_by_a_blocked_word_is_empty():
    quotient = make_partial_a_dfa().left_quotient('b')
    assert quotient.is_empty() is True
    assert type(quotient) is ExtendedDFA


def test_left_quotient_of_an_nfa_adds_an_initial_state_with_epsilon_transitions():
    nfa = make_ends_with_ab_nfa()
    quotient = nfa.left_quotient('a')
    assert type(quotient) is ExtendedNFA
    assert quotient.initial_state == 'init'
    # après 'a', on peut être dans q0 ou q1
    assert quotient.epsilon_closure('init') == {'init', 'q0', 'q1'}
    assert nfa.states == {'q0', 'q1', 'q2'}


def test_left_quotient_by_the_empty_word_keeps_the_language():
    for make in ALL_AUTOMATA:
        automaton = make()
        assert automaton.left_quotient('').language_equals(automaton) is True


def test_left_quotient_by_a_longer_word_is_the_composition_of_two_quotients():
    dfa = make_even_a_dfa()
    step_by_step = dfa.left_quotient('a').left_quotient('b')
    assert step_by_step.language_equals(dfa.left_quotient('ab')) is True


# ----------------------------------------------------------- #48 right quotient

def test_right_quotient_definition_on_every_small_word():
    for make in ALL_AUTOMATA:
        automaton = make()
        for u in all_words(3):
            quotient = automaton.right_quotient(u)
            for w in all_words(4):
                assert quotient.accepts(w) == automaton.accepts(w + u), (make.__name__, u, w)


def test_right_quotient_of_ends_with_ab_by_b():
    quotient = make_ends_with_ab_nfa().right_quotient('b')
    # w b se termine par ab  <=>  w se termine par a
    assert type(quotient) is ExtendedNFA
    assert quotient.accepts('a') is True
    assert quotient.accepts('ba') is True
    assert quotient.accepts('ab') is False
    assert quotient.accepts('') is False


def test_right_quotient_by_the_empty_word_keeps_the_language():
    for make in ALL_AUTOMATA:
        automaton = make()
        assert automaton.right_quotient('').language_equals(automaton) is True


def test_quotients_reject_symbols_outside_the_alphabet():
    dfa = make_even_a_dfa()
    with pytest.raises(ValueError):
        dfa.left_quotient('abc')
    with pytest.raises(ValueError):
        dfa.right_quotient('abc')