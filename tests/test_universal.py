from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_all_words_dfa():
    """DFA over {a, b} accepting every word."""
    return ExtendedDFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0', 'b': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
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


def test_is_universal_true_for_the_language_of_all_words():
    assert make_all_words_dfa().is_universal() is True


def test_is_universal_false_for_a_proper_language():
    assert make_even_a_dfa().is_universal() is False


def test_is_universal_false_for_a_partial_automaton():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
        allow_partial=True,
    )
    # Tout état est final, mais les mots contenant 'b' sont bloqués
    assert dfa.is_universal() is False


def test_is_universal_false_for_the_empty_language():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states=set(),
    )
    assert dfa.is_universal() is False


def test_is_universal_works_on_nfa():
    universal = ExtendedNFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': {'q0'}, 'b': {'q0'}}},
        initial_state='q0',
        final_states={'q0'},
    )
    ends_with_ab = ExtendedNFA(
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
    assert universal.is_universal() is True
    assert ends_with_ab.is_universal() is False


def test_language_united_with_its_complement_is_universal():
    dfa = make_even_a_dfa()
    union = dfa.product(dfa.complement(), lambda x, y: x or y)
    assert union.is_universal() is True