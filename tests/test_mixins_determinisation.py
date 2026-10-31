import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA

SAMPLE_WORDS = ['', 'a', 'b', 'ab', 'aab', 'abb', 'ba', 'bab', 'abab']


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


def make_ends_with_ab_dfa():
    """Minimal complete DFA over {a, b} accepting the words ending with 'ab'."""
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


def make_epsilon_cycle_nfa():
    """NFA whose epsilon transitions form the cycle q0 -> q1 -> q2 -> q0."""
    return ExtendedNFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a'},
        transitions={
            'q0': {'': {'q1'}},
            'q1': {'': {'q2'}},
            'q2': {'': {'q0'}, 'a': {'q2'}},
        },
        initial_state='q0',
        final_states={'q2'},
    )


# --------------------------------------------------------- #33 is_deterministic

def test_is_deterministic_true_for_a_dfa():
    assert make_ends_with_ab_dfa().is_deterministic() is True


def test_is_deterministic_false_with_several_destinations():
    assert make_ends_with_ab_nfa().is_deterministic() is False


def test_is_deterministic_true_for_a_deterministic_looking_nfa():
    nfa = ExtendedNFA(
        states={'q0', 'q1'},
        input_symbols={'a'},
        transitions={'q0': {'a': {'q1'}}, 'q1': {}},
        initial_state='q0',
        final_states={'q1'},
    )
    assert nfa.is_deterministic() is True


def test_is_deterministic_false_with_an_epsilon_transition():
    assert make_epsilon_nfa().is_deterministic() is False


# ----------------------------------------------------------- #34 epsilon closure

def test_epsilon_closure_of_a_state_and_of_a_set():
    nfa = make_epsilon_nfa()
    assert nfa.epsilon_closure('q0') == {'q0', 'q1'}
    assert nfa.epsilon_closure('q1') == {'q1'}
    assert nfa.epsilon_closure_of_set({'q0', 'q2'}) == {'q0', 'q1', 'q2'}


def test_epsilon_closure_follows_chains_and_terminates_on_cycles():
    nfa = make_epsilon_cycle_nfa()
    assert nfa.epsilon_closure('q1') == {'q0', 'q1', 'q2'}


def test_epsilon_closure_of_a_dfa_state_is_the_state_itself():
    dfa = make_ends_with_ab_dfa()
    assert dfa.epsilon_closure('s0') == {'s0'}


def test_epsilon_closure_rejects_unknown_state():
    nfa = make_epsilon_nfa()
    with pytest.raises(ValueError):
        nfa.epsilon_closure('zzz')
    with pytest.raises(ValueError):
        nfa.epsilon_closure_of_set({'q0', 'zzz'})


# ---------------------------------------------------------------- #35 determinize

def test_determinize_builds_only_accessible_subsets():
    nfa = make_ends_with_ab_nfa()
    dfa = nfa.determinize()
    # 3 sous-ensembles accessibles sur 8 possibles
    assert dfa.states == {
        frozenset({'q0'}),
        frozenset({'q0', 'q1'}),
        frozenset({'q0', 'q2'}),
    }
    assert type(dfa) is ExtendedDFA
    assert dfa.is_complete() is True
    assert dfa.is_deterministic() is True
    for word in SAMPLE_WORDS:
        assert dfa.accepts(word) == nfa.accepts(word)
    assert dfa.is_isomorphic(make_ends_with_ab_dfa()) is True


def test_determinize_handles_epsilon_transitions_and_empty_subset():
    nfa = make_epsilon_nfa()
    dfa = nfa.determinize()
    assert dfa.initial_state == frozenset({'q0', 'q1'})
    assert dfa.states == {
        frozenset({'q0', 'q1'}),
        frozenset({'q2'}),
        frozenset(),  # puits : atteint quand aucune transition n'existe
    }
    assert dfa.final_states == {frozenset({'q2'})}
    for word in SAMPLE_WORDS:
        assert dfa.accepts(word) == nfa.accepts(word)


def test_determinize_returns_a_deterministic_automaton_unchanged():
    dfa = make_ends_with_ab_dfa()
    assert dfa.determinize() is dfa


def test_determinize_does_not_modify_original():
    nfa = make_ends_with_ab_nfa()
    nfa.determinize()
    assert nfa.states == {'q0', 'q1', 'q2'}
    assert nfa.is_deterministic() is False