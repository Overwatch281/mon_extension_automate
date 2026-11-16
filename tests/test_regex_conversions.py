import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.regex import (
    EquationSystem,
    arden,
    concat,
    empty,
    epsilon,
    parse_regex,
    union,
)
from tests.regex_helpers import all_words

METHODS = ('elimination', 'arden')


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
        states={'q0', 'q1'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'a': 'q1', 'b': 'q0'},
            'q1': {'a': 'q0', 'b': 'q1'},
        },
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
    make_ends_with_ab_dfa,
    make_even_a_dfa,
    make_ends_with_ab_nfa,
    make_epsilon_nfa,
    make_partial_a_dfa,
    make_empty_language_dfa,
    make_all_words_dfa,
]


def rerooted(dfa, state):
    """The same DFA, but starting from `state`."""
    return ExtendedDFA(
        states=dfa.states,
        input_symbols=dfa.input_symbols,
        transitions=dfa.transitions,
        initial_state=state,
        final_states=dfa.final_states,
    )


# ---------------------------------------------------------- #53 and #54 to_regex

def test_to_regex_accepts_the_same_words_as_the_automaton():
    for make in ALL_AUTOMATA:
        automaton = make()
        for method in METHODS:
            expression = automaton.to_regex(method)
            for word in all_words('ab', 5):
                assert expression.accepts(word) == automaton.accepts(word), (make.__name__, method, word)


def test_to_regex_gives_back_an_equivalent_automaton():
    for make in ALL_AUTOMATA:
        automaton = make()
        for method in METHODS:
            expression = automaton.to_regex(method)
            rebuilt = expression.to_dfa(alphabet=automaton.input_symbols)
            assert rebuilt.language_equals(automaton) is True, (make.__name__, method)


def test_both_methods_give_equivalent_expressions():
    for make in ALL_AUTOMATA:
        automaton = make()
        alphabet = automaton.input_symbols
        first = automaton.to_regex('elimination').to_dfa(alphabet=alphabet)
        second = automaton.to_regex('arden').to_dfa(alphabet=alphabet)
        assert first.language_equals(second) is True, make.__name__


def test_to_regex_on_small_examples_computed_by_hand():
    loop = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    chain = make_partial_a_dfa()  # a, puis rien : langage {a}
    only_empty_word = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {}},
        initial_state='q0',
        final_states={'q0'},
        allow_partial=True,
    )
    for method in METHODS:
        assert loop.to_regex(method) == parse_regex('a*')
        assert chain.to_regex(method) == parse_regex('a')
        assert only_empty_word.to_regex(method) == epsilon()
        assert make_empty_language_dfa().to_regex(method) == empty()


def test_to_regex_works_on_a_minimized_automaton_with_set_states():
    minimal = make_ends_with_ab_nfa().determinize().minimize()
    for method in METHODS:
        expression = minimal.to_regex(method)
        for word in all_words('ab', 5):
            assert expression.accepts(word) == minimal.accepts(word)


def test_to_regex_order_and_method_validation():
    dfa = make_ends_with_ab_dfa()
    for method in METHODS:
        reversed_order = dfa.to_regex(method, order=['s2', 's1', 's0'])
        assert reversed_order.to_dfa(alphabet={'a', 'b'}).language_equals(dfa) is True
        with pytest.raises(ValueError):
            dfa.to_regex(method, order=['s0', 's1'])
        with pytest.raises(ValueError):
            dfa.to_regex(method, order=['s0', 's1', 's1'])
    with pytest.raises(ValueError):
        dfa.to_regex('magic')


# ----------------------------------------------------- #57 Arden, #58 equations

def test_arden_lemma_gives_the_star_of_the_coefficient_followed_by_the_constant():
    a, b = parse_regex('a'), parse_regex('b')
    assert arden(a, b) == parse_regex('a*b')
    assert arden(empty(), b) == b
    assert arden(epsilon(), b) == b
    assert arden(a, empty()) == empty()


def test_arden_solution_satisfies_the_equation():
    coefficient, constant = parse_regex('ab|b'), parse_regex('a')
    solution = arden(coefficient, constant)
    right_hand_side = union(concat(coefficient, solution), constant)
    alphabet = {'a', 'b'}
    assert right_hand_side.to_dfa(alphabet=alphabet).language_equals(
        solution.to_dfa(alphabet=alphabet)
    ) is True


def test_equation_system_is_written_state_by_state():
    system = EquationSystem.from_automaton(make_even_a_dfa())
    lines = str(system).splitlines()
    assert 'X_even = bX_even | aX_odd | ε' in lines
    assert 'X_odd = aX_even | bX_odd' in lines


def test_equation_system_solution_gives_the_language_of_each_state():
    dfa = make_ends_with_ab_dfa()
    solution = EquationSystem.from_automaton(dfa).solve()
    for state in dfa.states:
        expected = rerooted(dfa, state)
        for word in all_words('ab', 4):
            assert solution[state].accepts(word) == expected.accepts(word), (state, word)


def test_solving_does_not_modify_the_system_and_checks_the_order():
    system = EquationSystem.from_automaton(make_even_a_dfa())
    before = str(system)
    system.solve()
    assert str(system) == before
    with pytest.raises(ValueError):
        system.solve(order=['even'])