from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from tests.regex_helpers import all_words


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


def make_third_symbol_from_the_end_is_a():
    """NFA with 4 states, whose minimal DFA has 8 states."""
    return ExtendedNFA(
        states={'0', '1', '2', '3'},
        input_symbols={'a', 'b'},
        transitions={
            '0': {'a': {'0', '1'}, 'b': {'0'}},
            '1': {'a': {'2'}, 'b': {'2'}},
            '2': {'a': {'3'}, 'b': {'3'}},
            '3': {},
        },
        initial_state='0',
        final_states={'3'},
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


def same_future(automaton, first, second, max_length=5):
    """Brute force: do `first` and `second` accept the same continuations?"""
    return all(
        automaton.accepts(first + word) == automaton.accepts(second + word)
        for word in all_words(automaton.input_symbols, max_length)
    )


# ----------------------------------------------- #59 Myhill-Nerode classes

def test_classes_of_two_known_languages():
    ends = make_ends_with_ab_dfa().myhill_nerode_classes()
    assert [c.representative for c in ends] == ['', 'a', 'ab']
    assert [c.accepting for c in ends] == [False, False, True]

    even = make_even_a_dfa().myhill_nerode_classes()
    assert [c.representative for c in even] == ['', 'a']
    assert [c.accepting for c in even] == [True, False]


def test_the_number_of_classes_is_the_size_of_the_minimal_dfa():
    for make in ALL_AUTOMATA:
        automaton = make()
        assert len(automaton.myhill_nerode_classes()) == len(
            automaton.determinize().minimize().states
        ), make.__name__


def test_two_words_are_equivalent_exactly_when_they_have_the_same_future():
    for make in ALL_AUTOMATA:
        automaton = make()
        for first in all_words(automaton.input_symbols, 3):
            for second in all_words(automaton.input_symbols, 3):
                assert automaton.nerode_equivalent(first, second) == same_future(
                    automaton, first, second
                ), (make.__name__, first, second)


def test_the_representative_of_each_class_is_a_shortest_word():
    for make in ALL_AUTOMATA:
        automaton = make()
        for current in automaton.myhill_nerode_classes():
            rep = current.representative
            for word in all_words(automaton.input_symbols, len(rep)):
                if len(word) < len(rep):
                    assert not automaton.nerode_equivalent(word, rep), (make.__name__, word, rep)


def test_the_quotient_of_a_class_accepts_the_continuations_of_its_words():
    for make in ALL_AUTOMATA:
        automaton = make()
        for current in automaton.myhill_nerode_classes():
            assert current.accepting == automaton.accepts(current.representative)
            for word in all_words(automaton.input_symbols, 4):
                assert current.quotient.accepts(word) == automaton.accepts(
                    current.representative + word
                ), (make.__name__, current.representative, word)


# ------------------------------------------------------ #60 residual automaton

def test_the_residual_automaton_recognizes_the_same_language():
    for make in ALL_AUTOMATA + [make_third_symbol_from_the_end_is_a]:
        automaton = make()
        residual = automaton.residual_automaton()
        assert type(residual) is ExtendedNFA
        assert residual.language_equals(automaton) is True, make.__name__


def test_every_state_of_the_residual_automaton_recognizes_its_own_residual():
    for make in ALL_AUTOMATA + [make_third_symbol_from_the_end_is_a]:
        automaton = make()
        residual = automaton.residual_automaton()
        residuals = {c.representative: c.quotient for c in automaton.myhill_nerode_classes()}

        # Les états sont nommés par les représentants (ε pour le mot vide),
        # sauf un éventuel état initial ajouté, nommé init, init_1...
        added = {s for s in residual.states if s != 'ε' and s not in residuals}
        assert all(name.startswith('init') for name in added), make.__name__

        for state in residual.states - added:
            word = '' if state == 'ε' else state
            rooted = ExtendedNFA(
                states=residual.states,
                input_symbols=residual.input_symbols,
                transitions=residual.transitions,
                initial_state=state,
                final_states=residual.final_states,
            )
            assert rooted.language_equals(residuals[word]) is True, (make.__name__, state)


def test_the_residual_automaton_can_be_much_smaller_than_the_minimal_dfa():
    automaton = make_third_symbol_from_the_end_is_a()
    assert len(automaton.determinize().minimize().states) == 8
    residual = automaton.residual_automaton()
    assert len(residual.states) == 4
    assert residual.is_deterministic() is False


def test_residual_automaton_of_a_dfa_that_is_already_minimal_keeps_its_size():
    residual = make_ends_with_ab_dfa().residual_automaton()
    assert len(residual.states) == 3
    assert residual.initial_state == 'ε'
    assert residual.final_states == {'ab'}


def test_residual_automaton_of_the_empty_and_the_universal_languages():
    empty = make_empty_language_dfa().residual_automaton()
    assert len(empty.states) == 1
    assert empty.is_empty() is True

    universal = make_all_words_dfa().residual_automaton()
    assert len(universal.states) == 1
    assert universal.accepts('') is True
    assert universal.accepts('abba') is True


def test_the_residual_automaton_does_not_modify_the_original():
    nfa = make_ends_with_ab_nfa()
    nfa.residual_automaton()
    nfa.myhill_nerode_classes()
    assert nfa.states == {'q0', 'q1', 'q2'}