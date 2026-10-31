from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_partial_dfa():
    """Partial DFA over {a, b} recognizing the language {a}."""
    return ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q1'}, 'q1': {}},
        initial_state='q0',
        final_states={'q1'},
        allow_partial=True,
    )


def make_odd_a_dfa():
    """Complete DFA over {a, b} accepting an odd number of 'a'."""
    return ExtendedDFA(
        states={'even', 'odd'},
        input_symbols={'a', 'b'},
        transitions={
            'even': {'a': 'odd', 'b': 'even'},
            'odd': {'a': 'even', 'b': 'odd'},
        },
        initial_state='even',
        final_states={'odd'},
    )


def make_ends_with_ab_nfa():
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


SAMPLE_WORDS = ['', 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aab', 'abb', 'bab']


def test_is_complete_false_on_partial_dfa():
    assert make_partial_dfa().is_complete() is False


def test_is_complete_true_on_complete_dfa():
    assert make_odd_a_dfa().is_complete() is True


def test_is_complete_false_on_incomplete_nfa():
    assert make_ends_with_ab_nfa().is_complete() is False


def test_complete_adds_sink_and_preserves_language():
    dfa = make_partial_dfa()
    completed = dfa.complete()
    assert completed.is_complete() is True
    assert 'sink' in completed.states
    assert completed.transitions['q0']['b'] == 'sink'
    for word in SAMPLE_WORDS:
        assert completed.accepts(word) == dfa.accepts(word)


def test_complete_on_complete_automaton_adds_no_state():
    dfa = make_odd_a_dfa()
    completed = dfa.complete()
    assert completed.states == dfa.states


def test_complete_picks_a_fresh_sink_name():
    dfa = ExtendedDFA(
        states={'q0', 'sink'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'sink'}, 'sink': {'a': 'sink'}},
        initial_state='q0',
        final_states={'sink'},
        allow_partial=True,
    )
    completed = dfa.complete()
    assert 'sink1' in completed.states
    assert completed.is_complete() is True


def test_complete_does_not_modify_original():
    dfa = make_partial_dfa()
    dfa.complete()
    assert dfa.states == {'q0', 'q1'}
    assert dfa.is_complete() is False


def test_complete_nfa_preserves_language():
    nfa = make_ends_with_ab_nfa()
    completed = nfa.complete()
    assert completed.is_complete() is True
    assert type(completed) is ExtendedNFA
    for word in SAMPLE_WORDS:
        assert completed.accepts(word) == nfa.accepts(word)


def test_complement_general_case():
    dfa = make_odd_a_dfa()
    complement = dfa.complement()
    assert complement.accepts('a') is False
    assert complement.accepts('aa') is True
    assert complement.accepts('') is True
    assert complement.accepts('ab') is False


def test_complement_completes_partial_dfa_first():
    dfa = make_partial_dfa()  # langage {a}
    complement = dfa.complement()
    assert complement.accepts('a') is False
    assert complement.accepts('') is True
    assert complement.accepts('b') is True
    assert complement.accepts('aa') is True


def test_complement_twice_gives_back_the_same_language():
    dfa = make_odd_a_dfa()
    twice = dfa.complement().complement()
    for word in SAMPLE_WORDS:
        assert twice.accepts(word) == dfa.accepts(word)


def test_complement_of_an_nfa_determinizes_it_first():
    nfa = make_ends_with_ab_nfa()
    complement = nfa.complement()
    assert type(complement) is ExtendedDFA
    for word in SAMPLE_WORDS:
        assert complement.accepts(word) == (not nfa.accepts(word))