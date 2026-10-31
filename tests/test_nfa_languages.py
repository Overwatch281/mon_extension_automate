from automata_extensions.fa import ExtendedDFA, ExtendedNFA


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


def test_an_nfa_and_an_equivalent_dfa_have_the_same_language():
    nfa = make_ends_with_ab_nfa()
    assert nfa.language_equals(make_ends_with_ab_dfa()) is True
    assert make_ends_with_ab_dfa().language_equals(nfa) is True
    assert nfa.language_equals(make_even_a_dfa()) is False


def test_language_subset_between_an_nfa_and_a_dfa():
    nfa = make_ends_with_ab_nfa()
    ends_with_b = ExtendedDFA(
        states={'x', 'y'},
        input_symbols={'a', 'b'},
        transitions={'x': {'a': 'x', 'b': 'y'}, 'y': {'a': 'x', 'b': 'y'}},
        initial_state='x',
        final_states={'y'},
    )
    assert nfa.language_subset(ends_with_b) is True   # finir par 'ab' => finir par 'b'
    assert ends_with_b.language_subset(nfa) is False


def test_an_epsilon_nfa_equals_its_version_without_epsilon_transitions():
    nfa = make_epsilon_nfa()
    assert nfa.language_equals(nfa.remove_epsilon_transitions()) is True


def test_reversing_twice_gives_the_same_language_without_explicit_determinization():
    dfa = make_ends_with_ab_dfa()
    assert dfa.reverse().reverse().language_equals(dfa) is True


def test_complement_of_an_epsilon_nfa():
    nfa = make_epsilon_nfa()
    complement = nfa.complement()
    for word in ['', 'a', 'b', 'ab', 'abb', 'ba', 'aab']:
        assert complement.accepts(word) == (not nfa.accepts(word))
    assert nfa.product(complement, lambda x, y: x and y).is_empty() is True