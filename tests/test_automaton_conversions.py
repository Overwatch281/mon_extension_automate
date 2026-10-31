import itertools

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def all_words(max_length):
    """Every word over {a, b} of length 0 to `max_length`."""
    for length in range(max_length + 1):
        for letters in itertools.product('ab', repeat=length):
            yield ''.join(letters)


def make_redundant_ends_with_ab_dfa():
    """DFA for the words ending with 'ab', where s0 is duplicated by t0."""
    return ExtendedDFA(
        states={'s0', 't0', 's1', 's2'},
        input_symbols={'a', 'b'},
        transitions={
            's0': {'a': 's1', 'b': 't0'},
            't0': {'a': 's1', 'b': 's0'},
            's1': {'a': 's1', 'b': 's2'},
            's2': {'a': 's1', 'b': 's0'},
        },
        initial_state='s0',
        final_states={'s2'},
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


def make_empty_language_dfa():
    return ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q0', 'b': 'q1'},
        },
        initial_state='q0',
        final_states=set(),
    )


def minimal_dfa_of(automaton):
    """The minimal complete DFA, computed by the partition method."""
    return automaton.determinize().minimize()


# ------------------------------------------------------------- to_nfa / to_dfa

def test_to_nfa_turns_a_dfa_into_an_equivalent_nfa():
    dfa = make_partial_a_dfa()
    nfa = dfa.to_nfa()
    assert type(nfa) is ExtendedNFA
    assert nfa.states == dfa.states
    assert nfa.is_deterministic() is True
    for word in all_words(4):
        assert nfa.accepts(word) == dfa.accepts(word)


def test_to_nfa_keeps_set_states_intact():
    first, second = frozenset({'x'}), frozenset({'x', 'y'})
    dfa = ExtendedDFA(
        states={first, second},
        input_symbols={'a'},
        transitions={first: {'a': second}, second: {'a': second}},
        initial_state=first,
        final_states={second},
    )
    nfa = dfa.to_nfa()
    assert nfa.states == {first, second}
    assert nfa.accepts('a') is True
    assert nfa.accepts('') is False


def test_to_nfa_returns_an_nfa_unchanged_and_to_dfa_a_dfa_unchanged():
    nfa = make_ends_with_ab_nfa()
    dfa = make_redundant_ends_with_ab_dfa()
    assert nfa.to_nfa() is nfa
    assert dfa.to_dfa() is dfa


def test_to_dfa_is_the_subset_construction():
    nfa = make_epsilon_nfa()
    dfa = nfa.to_dfa()
    assert type(dfa) is ExtendedDFA
    assert dfa.is_complete() is True
    for word in all_words(4):
        assert dfa.accepts(word) == nfa.accepts(word)


def test_dfa_to_nfa_to_dfa_keeps_the_language():
    dfa = make_redundant_ends_with_ab_dfa()
    assert dfa.to_nfa().to_dfa().language_equals(dfa) is True


# ------------------------------------------------------ #50 brzozowski_automaton

def test_brzozowski_automaton_is_minimal_and_equivalent():
    for make in (make_redundant_ends_with_ab_dfa, make_ends_with_ab_nfa,
                 make_epsilon_nfa, make_partial_a_dfa):
        automaton = make()
        result = automaton.brzozowski_automaton()
        assert type(result) is ExtendedDFA
        assert result.is_minimal() is True, make.__name__
        assert result.language_equals(automaton) is True, make.__name__


def test_brzozowski_automaton_is_isomorphic_to_the_partition_minimization():
    for make in (make_redundant_ends_with_ab_dfa, make_ends_with_ab_nfa,
                 make_epsilon_nfa, make_partial_a_dfa):
        automaton = make()
        expected = minimal_dfa_of(automaton)
        assert automaton.brzozowski_automaton().is_isomorphic(expected) is True, make.__name__


def test_brzozowski_automaton_merges_equivalent_states():
    result = make_redundant_ends_with_ab_dfa().brzozowski_automaton()
    assert len(result.states) == 3


def test_brzozowski_automaton_of_the_empty_language_has_a_single_state():
    result = make_empty_language_dfa().brzozowski_automaton()
    assert len(result.states) == 1
    assert result.is_empty() is True


def test_brzozowski_automaton_is_idempotent_and_leaves_the_original_alone():
    nfa = make_ends_with_ab_nfa()
    result = nfa.brzozowski_automaton()
    assert result.brzozowski_automaton().is_isomorphic(result) is True
    assert nfa.states == {'q0', 'q1', 'q2'}