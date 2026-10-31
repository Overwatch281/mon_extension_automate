from automata_extensions.fa import ExtendedNFA


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


def test_nfa_trace_keeps_several_active_states():
    nfa = make_ends_with_ab_nfa()
    assert nfa.trace('ab') == [
        frozenset({'q0'}),
        frozenset({'q0', 'q1'}),
        frozenset({'q0', 'q2'}),
    ]


def test_nfa_accepts_words_ending_with_ab():
    nfa = make_ends_with_ab_nfa()
    assert nfa.accepts('ab') is True
    assert nfa.accepts('aab') is True
    assert nfa.accepts('abb') is False
    assert nfa.accepts('') is False


def test_nfa_epsilon_transition_is_followed():
    nfa = make_epsilon_nfa()
    # La fermeture epsilon de q0 contient q1 dès le départ
    assert nfa.trace('ab') == [
        frozenset({'q0', 'q1'}),
        frozenset({'q2'}),
        frozenset({'q2'}),
    ]
    assert nfa.accepts('abb') is True
    assert nfa.accepts('') is False
    assert nfa.accepts('b') is False


def test_nfa_accessible_states_handles_sets_of_destinations():
    nfa = make_ends_with_ab_nfa()
    assert nfa.accessible_states() == {'q0', 'q1', 'q2'}
    assert nfa.has_cycle() is True  # boucle q0 -> q0
    assert nfa.is_empty() is False