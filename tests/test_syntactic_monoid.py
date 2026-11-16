import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from tests.regex_helpers import all_words


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


def make_a_star_dfa():
    """The language a* over {a, b}."""
    return ExtendedDFA(
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0', 'b': 'q1'}, 'q1': {'a': 'q1', 'b': 'q1'}},
        initial_state='q0',
        final_states={'q0'},
    )


def make_ends_with_ab_dfa():
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


def make_partial_a_dfa():
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
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0', 'b': 'q0'}},
        initial_state='q0',
        final_states=set(),
    )


def make_all_words_dfa():
    return ExtendedDFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0', 'b': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )


ALL_AUTOMATA = [
    make_even_a_dfa,
    make_a_star_dfa,
    make_ends_with_ab_dfa,
    make_epsilon_nfa,
    make_partial_a_dfa,
    make_empty_language_dfa,
    make_all_words_dfa,
]

CONTEXTS = list(all_words('ab', 3))  # assez long pour des automates minimaux de 4 états


def behaviour(automaton, word):
    """Brute force: how `word` behaves in every context x _ y."""
    return tuple(
        automaton.accepts(x + word + y) for x in CONTEXTS for y in CONTEXTS
    )


# ----------------------------------------------------------- known examples

def test_three_known_languages():
    even = make_even_a_dfa().syntactic_monoid()   # le groupe Z/2
    assert len(even) == 2
    assert even.elements() == ['', 'a']
    assert even.is_commutative() is True
    assert even.is_aperiodic() is False

    star = make_a_star_dfa().syntactic_monoid()   # 1 et un élément absorbant
    assert len(star) == 2
    assert star.elements() == ['', 'b']
    assert star.is_commutative() is True
    assert star.is_aperiodic() is True

    ends = make_ends_with_ab_dfa().syntactic_monoid()
    assert len(ends) == 5
    assert ends.elements() == ['', 'a', 'b', 'ab', 'bb']
    assert ends.is_commutative() is False
    assert ends.is_aperiodic() is True
    assert ends.accepting_elements() == {'ab'}


def test_the_empty_and_the_universal_languages_have_a_trivial_monoid():
    for make in (make_empty_language_dfa, make_all_words_dfa):
        monoid = make().syntactic_monoid()
        assert len(monoid) == 1
        assert monoid.elements() == ['']
        assert monoid.is_commutative() is True
        assert monoid.is_aperiodic() is True
    assert make_empty_language_dfa().syntactic_monoid().accepting_elements() == set()
    assert make_all_words_dfa().syntactic_monoid().accepting_elements() == {''}


# --------------------------------------------- the definition, by brute force

def test_two_words_are_the_same_element_exactly_when_they_behave_alike_in_every_context():
    for make in ALL_AUTOMATA:
        automaton = make()
        monoid = automaton.syntactic_monoid()
        words = list(all_words(automaton.input_symbols, 3))
        for first in words:
            for second in words:
                assert (monoid.element(first) == monoid.element(second)) == (
                    behaviour(automaton, first) == behaviour(automaton, second)
                ), (make.__name__, first, second)


def test_the_size_is_the_number_of_distinct_behaviours():
    for make in ALL_AUTOMATA:
        automaton = make()
        monoid = automaton.syntactic_monoid()
        behaviours = {behaviour(automaton, w) for w in all_words(automaton.input_symbols, 4)}
        assert len(monoid) == len(behaviours), make.__name__


# ------------------------------------------------------------ monoid structure

def test_the_product_is_the_concatenation_and_the_monoid_laws_hold():
    for make in ALL_AUTOMATA:
        monoid = make().syntactic_monoid()
        elements = monoid.elements()
        assert monoid.identity == ''
        for x in elements:
            assert monoid.element(x) == x             # chaque nom est son propre élément
            assert monoid.multiply('', x) == x        # élément neutre à gauche
            assert monoid.multiply(x, '') == x        # et à droite
            for y in elements:
                assert monoid.multiply(x, y) in elements   # stabilité
                for z in elements:
                    assert monoid.multiply(monoid.multiply(x, y), z) == monoid.multiply(
                        x, monoid.multiply(y, z)
                    ), (make.__name__, x, y, z)


def test_the_multiplication_table():
    monoid = make_even_a_dfa().syntactic_monoid()
    table = monoid.multiplication_table()
    assert table == {('', ''): '', ('', 'a'): 'a', ('a', ''): 'a', ('a', 'a'): ''}
    big = make_ends_with_ab_dfa().syntactic_monoid()
    assert len(big.multiplication_table()) == len(big) ** 2


def test_accepting_elements_are_the_words_of_the_language():
    for make in ALL_AUTOMATA:
        automaton = make()
        monoid = automaton.syntactic_monoid()
        accepting = monoid.accepting_elements()
        for word in all_words(automaton.input_symbols, 4):
            assert (monoid.element(word) in accepting) == automaton.accepts(word), (make.__name__, word)


def test_unknown_symbols_are_rejected():
    monoid = make_even_a_dfa().syntactic_monoid()
    with pytest.raises(ValueError):
        monoid.element('abc')
    with pytest.raises(ValueError):
        monoid.multiply('a', 'z')


def test_the_monoid_of_an_nfa_is_the_one_of_its_language():
    nfa = make_epsilon_nfa()                        # le langage a b*
    monoid = nfa.syntactic_monoid()
    assert monoid.is_commutative() is False         # ab et ba ne sont pas égaux
    assert monoid.is_aperiodic() is True
    same = nfa.determinize().minimize().syntactic_monoid()
    assert len(monoid) == len(same)