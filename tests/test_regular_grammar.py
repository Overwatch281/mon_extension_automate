import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.grammar import ContextFreeGrammar, RegularGrammar
from tests.regex_helpers import all_words

EVEN_A = "S -> b S | a T | ε\nT -> b T | a S"
ENDS_WITH_AB = "S -> a S | b S | a A\nA -> b"
ABC = "S -> a b S | c"
UNITS_AND_EPSILON = "S -> A | b S\nA -> a A | ε"


def has_even_a(word):
    return word.count('a') % 2 == 0


def ends_with_ab(word):
    return word.endswith('ab')


def is_abc(word):
    return word.endswith('c') and word[:-1] == 'ab' * (len(word) // 2) and len(word) % 2 == 1


def is_b_star_a_star(word):
    return word == 'b' * word.count('b') + 'a' * word.count('a')


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


ALL_AUTOMATA = [
    make_even_a_dfa,
    make_ends_with_ab_nfa,
    make_epsilon_nfa,
    make_partial_a_dfa,
    make_empty_language_dfa,
]


# ------------------------------------------------------- the grammar itself

def test_a_regular_grammar_must_be_right_linear():
    grammar = RegularGrammar.from_text(EVEN_A)
    assert type(grammar) is RegularGrammar
    assert grammar.is_right_linear() is True
    with pytest.raises(ValueError):
        RegularGrammar.from_text("S -> a S b | ε")
    with pytest.raises(ValueError):
        RegularGrammar.from_text("S -> S a | a")


def test_the_derivation_of_a_right_linear_grammar_grows_on_the_right():
    grammar = RegularGrammar.from_text("S -> a S | b")
    assert grammar.leftmost_derivation('aab') == [
        ('S',), ('a', 'S'), ('a', 'a', 'S'), ('a', 'a', 'b'),
    ]


# ------------------------------------------------------ grammar -> automaton

def test_to_nfa_recognizes_the_language_of_the_grammar():
    for text, oracle in [
        (EVEN_A, has_even_a),
        (ENDS_WITH_AB, ends_with_ab),
        (ABC, is_abc),
        (UNITS_AND_EPSILON, is_b_star_a_star),
    ]:
        grammar = RegularGrammar.from_text(text)
        nfa = grammar.to_nfa()
        assert type(nfa) is ExtendedNFA
        for word in all_words(grammar.terminals, 6):
            assert nfa.accepts(word) == grammar.generates(word), (text, word)
            assert nfa.accepts(word) == oracle(word), (text, word)


def test_to_nfa_structure():
    nfa = RegularGrammar.from_text(ABC).to_nfa()
    # S -> a b S : un état intermédiaire S_1 ; S -> c : vers l'état final F
    assert nfa.states == {'S', 'S_1', 'F'}
    assert nfa.initial_state == 'S'
    assert nfa.final_states == {'F'}
    assert nfa.input_symbols == {'a', 'b', 'c'}


def test_to_nfa_picks_fresh_names_for_the_final_and_intermediate_states():
    grammar = RegularGrammar.from_text("F -> a b F_1 | c\nF_1 -> a")
    nfa = grammar.to_nfa()
    assert len(nfa.states) == 4  # F, F_1, l'état intermédiaire et l'état final
    for word in all_words('abc', 5):
        assert nfa.accepts(word) == grammar.generates(word)


# ------------------------------------------------------ automaton -> grammar

def test_to_grammar_writes_one_nonterminal_per_state():
    grammar = make_even_a_dfa().to_grammar()
    assert type(grammar) is RegularGrammar
    lines = str(grammar).splitlines()
    assert 'even -> a odd | b even | ε' in lines
    assert 'odd -> a even | b odd' in lines
    assert grammar.start == 'even'


def test_to_grammar_generates_the_language_of_the_automaton():
    for make in ALL_AUTOMATA:
        automaton = make()
        grammar = automaton.to_grammar()
        for word in all_words('ab', 5):
            assert grammar.generates(word) == automaton.accepts(word), (make.__name__, word)


def test_to_grammar_then_to_nfa_gives_back_an_equivalent_automaton():
    for make in ALL_AUTOMATA:
        automaton = make()
        rebuilt = automaton.to_grammar().to_nfa()
        assert rebuilt.language_equals(automaton) is True, make.__name__


def test_nonterminals_are_renamed_when_state_names_are_ambiguous():
    dfa = ExtendedDFA(
        states={'a', 'b'},
        input_symbols={'a', 'b'},
        transitions={'a': {'a': 'b', 'b': 'a'}, 'b': {'a': 'a', 'b': 'b'}},
        initial_state='a',
        final_states={'b'},
    )
    grammar = dfa.to_grammar()
    assert grammar.nonterminals == {'Q0', 'Q1'}
    for word in all_words('ab', 4):
        assert grammar.generates(word) == dfa.accepts(word)


def test_to_grammar_works_on_a_minimized_automaton_with_set_states():
    minimal = make_ends_with_ab_nfa().determinize().minimize()
    grammar = minimal.to_grammar()
    assert grammar.is_right_linear() is True
    for word in all_words('ab', 5):
        assert grammar.generates(word) == minimal.accepts(word)


def test_the_two_conversions_are_consistent_on_a_grammar():
    grammar = RegularGrammar.from_text(UNITS_AND_EPSILON)
    nfa = grammar.to_nfa()
    assert nfa.to_grammar().to_nfa().language_equals(nfa) is True
    assert isinstance(grammar, ContextFreeGrammar)