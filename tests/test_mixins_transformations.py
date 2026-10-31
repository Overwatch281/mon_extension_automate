from automata_extensions.fa import ExtendedDFA, ExtendedNFA

WORDS = ['', 'a', 'b', 'ab', 'ba', 'aab', 'abb', 'bab', 'abab', 'baab', 'bba']


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


# ------------------------------------------------------------------ #36 reverse

def test_reverse_reverses_the_words_of_a_dfa_language():
    dfa = make_ends_with_ab_dfa()
    reverse = dfa.reverse()
    for word in WORDS:
        assert reverse.accepts(word[::-1]) == dfa.accepts(word)


def test_reverse_swaps_initial_and_final_states():
    dfa = make_ends_with_ab_dfa()
    reverse = dfa.reverse()
    assert type(reverse) is ExtendedNFA
    assert reverse.initial_state == 'init'
    assert reverse.final_states == {'s0'}
    assert reverse.states == {'s0', 's1', 's2', 'init'}
    assert dfa.states == {'s0', 's1', 's2'}  # l'original n'a pas changé


def test_reverse_of_an_nfa_with_epsilon_transitions():
    nfa = make_epsilon_nfa()
    reverse = nfa.reverse()
    for word in WORDS:
        assert reverse.accepts(word[::-1]) == nfa.accepts(word)


def test_reverse_twice_gives_back_the_same_language():
    dfa = make_ends_with_ab_dfa()
    twice = dfa.reverse().reverse()
    assert twice.determinize().language_equals(dfa) is True


def test_reverse_of_an_automaton_without_final_state_is_empty():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states=set(),
    )
    assert dfa.reverse().is_empty() is True


def test_reverse_picks_a_fresh_initial_state_name():
    dfa = ExtendedDFA(
        states={'init'},
        input_symbols={'a'},
        transitions={'init': {'a': 'init'}},
        initial_state='init',
        final_states={'init'},
    )
    reverse = dfa.reverse()
    assert reverse.initial_state == 'init1'
    assert reverse.states == {'init', 'init1'}
    assert reverse.accepts('aa') is True


# ------------------------------------------------ #37 remove_epsilon_transitions

def test_remove_epsilon_transitions_propagates_transitions():
    nfa = make_epsilon_nfa()
    result = nfa.remove_epsilon_transitions()
    assert type(result) is ExtendedNFA
    assert all('' not in paths for paths in result.transitions.values())
    assert result.initial_state == 'q0'
    assert result.final_states == {'q2'}
    assert result.transitions['q0']['a'] == {'q2'}
    for word in WORDS:
        assert result.accepts(word) == nfa.accepts(word)
    # L'original garde sa transition epsilon
    assert nfa.epsilon_closure('q0') == {'q0', 'q1'}


def test_remove_epsilon_transitions_makes_states_final_when_needed():
    nfa = ExtendedNFA(
        states={'q0', 'q1'},
        input_symbols={'a'},
        transitions={'q0': {'': {'q1'}}, 'q1': {'a': {'q1'}}},
        initial_state='q0',
        final_states={'q1'},
    )
    result = nfa.remove_epsilon_transitions()
    # q0 atteint q1 (final) par epsilon : q0 devient final
    assert result.final_states == {'q0', 'q1'}
    assert result.accepts('') is True
    for word in ['', 'a', 'aa']:
        assert result.accepts(word) == nfa.accepts(word)


def test_remove_epsilon_transitions_with_an_epsilon_cycle():
    nfa = make_epsilon_cycle_nfa()
    result = nfa.remove_epsilon_transitions()
    assert result.transitions['q0']['a'] == {'q0', 'q1', 'q2'}
    assert result.final_states == {'q0', 'q1', 'q2'}
    for word in ['', 'a', 'aa']:
        assert result.accepts(word) == nfa.accepts(word)


def test_remove_epsilon_transitions_returns_a_dfa_unchanged():
    dfa = make_ends_with_ab_dfa()
    assert dfa.remove_epsilon_transitions() is dfa