import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


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


def make_redundant_ends_with_ab_dfa():
    """Same language, but s0 is duplicated by the equivalent state t0."""
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


def make_redundant_even_a_dfa():
    """Even number of 'a', with two equivalent final states e1 and e2."""
    return ExtendedDFA(
        states={'e1', 'e2', 'o'},
        input_symbols={'a', 'b'},
        transitions={
            'e1': {'a': 'o', 'b': 'e2'},
            'e2': {'a': 'o', 'b': 'e1'},
            'o': {'a': 'e1', 'b': 'o'},
        },
        initial_state='e1',
        final_states={'e1', 'e2'},
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


# ------------------------------------------------ #29 distinguishable_pairs

def test_distinguishable_pairs_general_case():
    pairs = make_redundant_even_a_dfa().distinguishable_pairs()
    assert pairs == {frozenset({'e1', 'o'}), frozenset({'e2', 'o'})}


def test_distinguishable_pairs_needs_several_rounds():
    pairs = make_ends_with_ab_dfa().distinguishable_pairs()
    # {s0, s1} n'est distingué qu'au deuxième tour (via 'b')
    assert pairs == {
        frozenset({'s0', 's1'}),
        frozenset({'s0', 's2'}),
        frozenset({'s1', 's2'}),
    }


def test_distinguishable_pairs_requires_complete_automaton():
    partial = make_partial_a_dfa()
    with pytest.raises(ValueError):
        partial.distinguishable_pairs()
    with pytest.raises(ValueError):
        partial.equivalence_classes()


# ------------------------------------------------- #30 equivalence_classes

def test_equivalence_classes_general_case():
    classes = make_redundant_even_a_dfa().equivalence_classes()
    assert set(classes) == {frozenset({'e1', 'e2'}), frozenset({'o'})}


def test_equivalence_classes_form_a_partition():
    dfa = make_redundant_ends_with_ab_dfa()
    classes = dfa.equivalence_classes()
    assert set(classes) == {
        frozenset({'s0', 't0'}),
        frozenset({'s1'}),
        frozenset({'s2'}),
    }
    assert sum(len(cls) for cls in classes) == len(dfa.states)


def test_equivalence_classes_of_minimal_automaton_are_singletons():
    classes = make_ends_with_ab_dfa().equivalence_classes()
    assert all(len(cls) == 1 for cls in classes)
    assert len(classes) == 3


# ------------------------------------------------------------ #31 is_minimal

def test_is_minimal_true():
    assert make_ends_with_ab_dfa().is_minimal() is True


def test_is_minimal_false_with_equivalent_states():
    assert make_redundant_ends_with_ab_dfa().is_minimal() is False


def test_is_minimal_false_with_unreachable_state():
    dfa = ExtendedDFA(
        states={'s0', 's1', 's2', 'z'},
        input_symbols={'a', 'b'},
        transitions={
            's0': {'a': 's1', 'b': 's0'},
            's1': {'a': 's1', 'b': 's2'},
            's2': {'a': 's1', 'b': 's0'},
            'z': {'a': 'z', 'b': 'z'},  # inaccessible
        },
        initial_state='s0',
        final_states={'s2'},
    )
    assert dfa.is_minimal() is False


def test_is_minimal_false_when_automaton_is_partial():
    assert make_partial_a_dfa().is_minimal() is False


# ------------------------------------------------------------ #32 minimize

def test_minimize_merges_equivalent_states_and_preserves_language():
    original = make_redundant_ends_with_ab_dfa()
    minimized = original.minimize()
    assert len(minimized.states) == 3
    assert minimized.is_minimal() is True
    assert minimized.language_equals(original) is True
    # L'automate minimal est unique à isomorphisme près
    assert minimized.is_isomorphic(make_ends_with_ab_dfa()) is True


def test_minimize_completes_partial_automaton():
    original = make_partial_a_dfa()
    minimized = original.minimize()
    # q0, q1 et un état puits ajouté
    assert len(minimized.states) == 3
    assert minimized.is_complete() is True
    assert minimized.is_minimal() is True
    assert minimized.language_equals(original) is True


def test_minimize_does_not_modify_original_and_is_idempotent():
    original = make_redundant_ends_with_ab_dfa()
    minimized = original.minimize()
    assert original.states == {'s0', 't0', 's1', 's2'}
    assert minimized.minimize().is_isomorphic(minimized) is True


def test_minimization_family_rejects_nfa():
    nfa = ExtendedNFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': {'q0'}, 'b': {'q0'}}},
        initial_state='q0',
        final_states={'q0'},
    )
    with pytest.raises(NotImplementedError):
        nfa.minimize()
    with pytest.raises(NotImplementedError):
        nfa.is_minimal()
    with pytest.raises(NotImplementedError):
        nfa.equivalence_classes()