import itertools

import pytest
from automata.fa.nfa import NFA

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA


def all_words(alphabet, max_length):
    """Every word over `alphabet` of length 0 to `max_length`."""
    for length in range(max_length + 1):
        for letters in itertools.product(sorted(alphabet), repeat=length):
            yield "".join(letters)


def eliminate_all(gnfa, key=str, reverse=False):
    """Eliminate every intermediate state, in the order given by `key`."""
    for state in sorted(gnfa.intermediate_states(), key=key, reverse=reverse):
        gnfa = gnfa.eliminate_state(state)
    return gnfa


def final_label(gnfa):
    """Label of the edge from the initial state to the final state."""
    return gnfa.transitions[gnfa.initial_state][gnfa.final_state]


def assert_regex_matches_automaton(regex, automaton):
    """Check that `regex` and `automaton` accept the same words (length <= 6)."""
    regex_nfa = None if regex is None else NFA.from_regex(regex, input_symbols=set(automaton.input_symbols))
    for word in all_words(automaton.input_symbols, 6):
        expected = automaton.accepts_input(word)
        actual = False if regex_nfa is None else regex_nfa.accepts_input(word)
        assert actual == expected, f"word {word!r}, regex {regex!r}"


def make_ends_with_ab_dfa():
    return ExtendedDFA(
        states={'s0', 's1', 's2'},
        input_symbols={'a', 'b'},
        transitions={
            's0': {'a': 's1', 'b': 's0'},
            's1': {'a': 's1', 'b': 's2'},
            's2': {'a': 's1', 'b': 's0'},
        },
        initial_state='s0',
        final_states={'s2'},
    )


def make_even_a_dfa():
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


# ------------------------------------------------------------------ to_gnfa

def test_to_gnfa_builds_a_normalized_gnfa_from_a_dfa_and_an_nfa():
    for automaton in (make_ends_with_ab_dfa(), make_epsilon_nfa()):
        gnfa = automaton.to_gnfa()
        assert type(gnfa) is ExtendedGNFA
        assert gnfa.initial_state != gnfa.final_state
        assert gnfa.intermediate_states() == set(automaton.states)


# -------------------------------------------------------- #39 eliminate_state

def test_eliminate_state_removes_one_state_and_keeps_the_original():
    gnfa = make_ends_with_ab_dfa().to_gnfa()
    smaller = gnfa.eliminate_state('s1')
    assert type(smaller) is ExtendedGNFA
    assert smaller.states == gnfa.states - {'s1'}
    assert 's1' in gnfa.states  # l'original n'a pas changé


def test_eliminate_state_computes_the_expected_labels():
    chain = ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q1'}, 'q1': {}},
        initial_state='q0',
        final_states={'q1'},
        allow_partial=True,
    )
    assert final_label(eliminate_all(chain.to_gnfa())) == 'a'

    loop = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    assert final_label(eliminate_all(loop.to_gnfa())) == 'a*'


def test_eliminating_all_states_preserves_the_language_of_a_dfa():
    for dfa in (make_ends_with_ab_dfa(), make_even_a_dfa()):
        gnfa = dfa.to_gnfa()
        assert_regex_matches_automaton(final_label(eliminate_all(gnfa)), dfa)


def test_the_elimination_order_does_not_change_the_language():
    dfa = make_ends_with_ab_dfa()
    gnfa = dfa.to_gnfa()
    forward = final_label(eliminate_all(gnfa))
    backward = final_label(eliminate_all(gnfa, reverse=True))
    assert_regex_matches_automaton(forward, dfa)
    assert_regex_matches_automaton(backward, dfa)


def test_eliminating_all_states_preserves_the_language_of_an_epsilon_nfa():
    nfa = make_epsilon_nfa()
    regex = final_label(eliminate_all(nfa.to_gnfa()))
    assert_regex_matches_automaton(regex, nfa)


def test_eliminating_all_states_of_an_empty_language_gives_no_transition():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states=set(),
    )
    assert final_label(eliminate_all(dfa.to_gnfa())) is None


def test_eliminate_state_rejects_initial_final_and_unknown_states():
    gnfa = make_even_a_dfa().to_gnfa()
    with pytest.raises(ValueError):
        gnfa.eliminate_state(gnfa.initial_state)
    with pytest.raises(ValueError):
        gnfa.eliminate_state(gnfa.final_state)
    with pytest.raises(ValueError):
        gnfa.eliminate_state('zzz')