from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_prefix_closed_dfa():
    """Partial DFA recognizing the prefix-closed language {'', a, aa, ab}."""
    return ExtendedDFA(
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1'},
            'q1': {'a': 'q2', 'b': 'q3'},
            'q2': {},
            'q3': {},
        },
        initial_state='q0',
        final_states={'q0', 'q1', 'q2', 'q3'},
        allow_partial=True,
    )


def make_not_prefix_closed_dfa():
    """Complete DFA where 'aa' is accepted but its prefix 'a' is not."""
    return ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q2', 'b': 'q1'},
            'q2': {'a': 'q2', 'b': 'q2'},
        },
        initial_state='q0',
        final_states={'q0', 'q2'},
    )


def make_all_words_nfa():
    """NFA over {a, b} accepting every word (a prefix-closed language)."""
    return ExtendedNFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': {'q0'}, 'b': {'q0'}}},
        initial_state='q0',
        final_states={'q0'},
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


# ------------------------------------------------------ #27 is_prefix_closed

def test_is_prefix_closed_true():
    assert make_prefix_closed_dfa().is_prefix_closed() is True


def test_is_prefix_closed_false():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q1'}, 'q1': {'a': 'q2'}, 'q2': {}},
        initial_state='q0',
        final_states={'q2'},  # langage {aa} : le mot vide et 'a' manquent
        allow_partial=True,
    )
    assert dfa.is_prefix_closed() is False


def test_is_prefix_closed_ignores_non_final_dead_sink():
    dfa = ExtendedDFA(
        states={'q0', 'q1', 'sink'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'sink'},
            'q1': {'a': 'sink', 'b': 'sink'},
            'sink': {'a': 'sink', 'b': 'sink'},
        },
        initial_state='q0',
        final_states={'q0', 'q1'},  # langage {'', a}
    )
    assert dfa.is_prefix_closed() is True


def test_is_prefix_closed_empty_language():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states=set(),
    )
    assert dfa.is_prefix_closed() is True


def test_is_prefix_closed_single_final_state_looping():
    dfa = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    assert dfa.is_prefix_closed() is True


def test_is_prefix_closed_determinizes_an_nfa_first():
    assert make_all_words_nfa().is_prefix_closed() is True
    assert make_ends_with_ab_nfa().is_prefix_closed() is False


# ------------------------------------------- #28 prefix_closed_sublanguage

def test_prefix_closed_sublanguage_general_case():
    dfa = make_not_prefix_closed_dfa()
    sub = dfa.prefix_closed_sublanguage()
    # Seuls les mots b* ont tous leurs préfixes dans le langage
    assert sub.states == {'q0'}
    assert sub.accepts('') is True
    assert sub.accepts('bb') is True
    assert sub.accepts('a') is False
    assert sub.accepts('aa') is False  # 'aa' est dans L mais pas son préfixe 'a'
    assert sub.accepts('ba') is False
    assert sub.is_prefix_closed() is True
    assert sub.language_subset(dfa) is True


def test_prefix_closed_sublanguage_empty_when_initial_state_not_final():
    dfa = ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q1'}, 'q1': {'a': 'q1'}},
        initial_state='q0',
        final_states={'q1'},
    )
    sub = dfa.prefix_closed_sublanguage()
    assert sub.is_empty() is True
    assert sub.states == {'q0'}


def test_prefix_closed_sublanguage_of_prefix_closed_language_is_itself():
    dfa = make_prefix_closed_dfa()
    assert dfa.prefix_closed_sublanguage().language_equals(dfa) is True


def test_prefix_closed_sublanguage_does_not_modify_original():
    dfa = make_not_prefix_closed_dfa()
    dfa.prefix_closed_sublanguage()
    assert dfa.states == {'q0', 'q1', 'q2'}
    assert dfa.final_states == {'q0', 'q2'}


def test_prefix_closed_sublanguage_determinizes_an_nfa_first():
    nfa = make_all_words_nfa()
    sub = nfa.prefix_closed_sublanguage()
    assert type(sub) is ExtendedDFA
    assert sub.language_equals(nfa) is True
    # 'ab' est dans le langage mais pas le mot vide : sous-langage vide
    assert make_ends_with_ab_nfa().prefix_closed_sublanguage().is_empty() is True