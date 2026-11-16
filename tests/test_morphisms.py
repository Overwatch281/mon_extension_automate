import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.fa.morphisms import AutomatonMorphism
from tests.regex_helpers import all_words


def make_minimal_dfa():
    """Minimal complete DFA over {a, b} for the words ending with 'ab'."""
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


def make_redundant_dfa():
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


def make_renamed_minimal_dfa():
    return ExtendedDFA(
        states={'x', 'y', 'z'},
        input_symbols={'a', 'b'},
        transitions={
            'x': {'a': 'y', 'b': 'x'},
            'y': {'a': 'y', 'b': 'z'},
            'z': {'a': 'y', 'b': 'x'},
        },
        initial_state='x',
        final_states={'z'},
    )


def make_partial_a_dfa():
    return ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q1'}, 'q1': {}},
        initial_state='q0',
        final_states={'q1'},
        allow_partial=True,
    )


def make_dfa_with_an_unreachable_state():
    return ExtendedDFA(
        states={'s0', 's1', 's2', 'z'},
        input_symbols={'a', 'b'},
        transitions={
            's0': {'a': 's1', 'b': 's0'},
            's1': {'a': 's1', 'b': 's2'},
            's2': {'a': 's1', 'b': 's0'},
            'z': {'a': 'z', 'b': 'z'},
        },
        initial_state='s0',
        final_states={'s2'},
    )


def same_language(first, second):
    return all(
        first.accepts(word) == second.accepts(word)
        for word in all_words(first.input_symbols, 5)
    )


# ---------------------------------------------------------- the class itself

def test_the_identity_is_a_morphism_and_an_isomorphism():
    dfa = make_minimal_dfa()
    identity = AutomatonMorphism(dfa, dfa, {s: s for s in dfa.states})
    assert identity.is_isomorphism() is True
    assert identity.is_surjective() is True and identity.is_injective() is True
    assert identity('s1') == 's1'
    assert identity.image() == {'s0', 's1', 's2'}
    assert identity.kernel() == {frozenset({'s0'}), frozenset({'s1'}), frozenset({'s2'})}
    assert identity.mapping == {'s0': 's0', 's1': 's1', 's2': 's2'}
    with pytest.raises(ValueError):
        identity('zzz')


def test_a_renaming_of_the_states_is_an_isomorphism():
    first, second = make_minimal_dfa(), make_renamed_minimal_dfa()
    renaming = AutomatonMorphism(first, second, {'s0': 'x', 's1': 'y', 's2': 'z'})
    assert renaming.is_isomorphism() is True
    assert same_language(first, second)


def test_a_map_that_is_not_a_morphism_is_rejected():
    first, second = make_minimal_dfa(), make_renamed_minimal_dfa()
    good = {'s0': 'x', 's1': 'y', 's2': 'z'}
    with pytest.raises(ValueError):                       # état initial
        AutomatonMorphism(first, second, {**good, 's0': 'y'})
    with pytest.raises(ValueError):                       # finalité
        AutomatonMorphism(first, second, {**good, 's2': 'x'})
    with pytest.raises(ValueError):                       # transitions
        AutomatonMorphism(first, second, {**good, 's1': 'x', 's2': 'z'})
    with pytest.raises(ValueError):                       # état source oublié
        AutomatonMorphism(first, second, {'s0': 'x', 's1': 'y'})
    with pytest.raises(ValueError):                       # image inconnue
        AutomatonMorphism(first, second, {**good, 's1': 'nope'})
    only_a = ExtendedDFA(
        states={'q'}, input_symbols={'a'}, transitions={'q': {'a': 'q'}},
        initial_state='q', final_states={'q'},
    )
    with pytest.raises(ValueError):                       # alphabets différents
        AutomatonMorphism(only_a, first, {'q': 's0'})


def test_morphisms_are_only_defined_for_deterministic_automata():
    nfa = ExtendedNFA(
        states={'q0'}, input_symbols={'a', 'b'},
        transitions={'q0': {'a': {'q0'}, 'b': {'q0'}}},
        initial_state='q0', final_states={'q0'},
    )
    dfa = make_minimal_dfa()
    with pytest.raises(NotImplementedError):
        AutomatonMorphism(nfa, dfa, {'q0': 's0'})
    with pytest.raises(NotImplementedError):
        nfa.merge_states([{'q0'}])
    with pytest.raises(NotImplementedError):
        nfa.minimization_morphism()
    with pytest.raises(NotImplementedError):
        nfa.morphism_to(dfa)


# --------------------------------------------------------- merge_states (fusion)

def test_merging_equivalent_states_gives_the_projection_on_the_quotient():
    dfa = make_redundant_dfa()
    projection = dfa.merge_states([{'s0', 't0'}, {'s1'}, {'s2'}])
    quotient = projection.target
    assert len(quotient.states) == 3
    assert quotient.initial_state == frozenset({'s0', 't0'})
    assert projection('t0') == frozenset({'s0', 't0'})
    assert projection.is_surjective() is True
    assert projection.is_injective() is False
    assert projection.kernel() == {frozenset({'s0', 't0'}), frozenset({'s1'}), frozenset({'s2'})}
    assert same_language(dfa, quotient)
    assert dfa.states == {'s0', 't0', 's1', 's2'}  # l'original n'a pas changé


def test_merging_with_a_partition_that_is_not_a_congruence_is_rejected():
    dfa = make_redundant_dfa()
    with pytest.raises(ValueError):   # s0 et s1 se séparent sur b (t0 contre s2)
        dfa.merge_states([{'s0', 's1'}, {'t0'}, {'s2'}])
    with pytest.raises(ValueError):   # un état final avec un état non final
        dfa.merge_states([{'s0', 't0'}, {'s1', 's2'}])
    with pytest.raises(ValueError):   # blocs qui se chevauchent
        dfa.merge_states([{'s0', 't0'}, {'t0', 's1'}, {'s2'}])
    with pytest.raises(ValueError):   # un état manque
        dfa.merge_states([{'s0', 't0'}, {'s1'}])
    with pytest.raises(ValueError):   # bloc vide
        dfa.merge_states([{'s0', 't0'}, {'s1'}, {'s2'}, set()])


def test_merging_states_that_differ_on_the_existence_of_a_transition_is_rejected():
    dfa = ExtendedDFA(
        states={'p', 'q', 'r'},
        input_symbols={'a'},
        transitions={'p': {'a': 'r'}, 'q': {}, 'r': {}},
        initial_state='p',
        final_states={'r'},
        allow_partial=True,
    )
    with pytest.raises(ValueError):
        dfa.merge_states([{'p', 'q'}, {'r'}])


# ------------------------------------------------- minimization and morphism_to

def test_the_minimization_is_a_surjective_morphism_whose_kernel_is_the_classes():
    for dfa in (make_redundant_dfa(), make_minimal_dfa(), make_partial_a_dfa(),
                make_dfa_with_an_unreachable_state()):
        morphism = dfa.minimization_morphism()
        assert morphism.is_surjective() is True
        assert morphism.target.is_isomorphic(dfa.minimize()) is True
        assert morphism.target.is_minimal() is True
        assert morphism.kernel() == set(morphism.source.equivalence_classes())
        assert same_language(dfa, morphism.target)


def test_a_morphism_to_the_minimal_automaton_exists_and_not_the_other_way():
    redundant, minimal = make_redundant_dfa(), make_minimal_dfa()
    morphism = redundant.morphism_to(minimal)
    assert morphism is not None
    assert morphism.is_surjective() is True
    assert morphism('t0') == 's0'
    assert same_language(redundant, minimal)
    # Dans l'autre sens, s0 -b-> s0 imposerait phi(s0) = phi(s0), alors que dans
    # l'automate redondant s0 -b-> t0 avec t0 != s0 : aucun morphisme n'existe.
    assert minimal.morphism_to(redundant) is None


def test_morphism_to_finds_the_renaming_of_isomorphic_automata():
    morphism = make_minimal_dfa().morphism_to(make_renamed_minimal_dfa())
    assert morphism is not None
    assert morphism.is_isomorphism() is True
    assert morphism.mapping == {'s0': 'x', 's1': 'y', 's2': 'z'}


def test_morphism_to_ignores_unreachable_states_of_the_source():
    morphism = make_dfa_with_an_unreachable_state().morphism_to(make_minimal_dfa())
    assert morphism is not None
    assert morphism.source.states == {'s0', 's1', 's2'}
    assert morphism.is_isomorphism() is True


def test_morphism_to_returns_none_when_the_structure_cannot_be_preserved():
    minimal = make_minimal_dfa()
    # un DFA partiel n'a pas les mêmes transitions définies qu'un DFA complet
    assert make_partial_a_dfa().morphism_to(minimal) is None
    only_a = ExtendedDFA(
        states={'q'}, input_symbols={'a'}, transitions={'q': {'a': 'q'}},
        initial_state='q', final_states={'q'},
    )
    assert only_a.morphism_to(minimal) is None  # alphabets différents
    even_a = ExtendedDFA(
        states={'even', 'odd'}, input_symbols={'a', 'b'},
        transitions={'even': {'a': 'odd', 'b': 'even'}, 'odd': {'a': 'even', 'b': 'odd'}},
        initial_state='even', final_states={'even'},
    )
    assert minimal.morphism_to(even_a) is None  # finalité incompatible