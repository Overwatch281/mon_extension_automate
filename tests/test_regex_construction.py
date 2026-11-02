import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.regex import Regex, parse_regex
from tests.regex_helpers import all_words, reference_accepts

EXPRESSIONS = [
    'a', 'ab', 'a|b', 'a*', '(a|b)*', 'a*b', '(ab)*', 'a?b', '(a|b)*abb',
    '(a|b)?b*', 'ε', '∅', 'a|ε', '(ab|b)*a', '((a|b)*b)*', 'a*b*a*',
    '(a*b*)*', '∅*', '(a|∅)b', 'a+b',
]
ALPHABET = {'a', 'b'}


# ------------------------------------------------------------- #51 Thompson

def test_thompson_nfa_recognizes_the_language():
    for text in EXPRESSIONS:
        expression = parse_regex(text)
        nfa = expression.to_nfa(alphabet=ALPHABET)
        assert type(nfa) is ExtendedNFA
        for word in all_words(ALPHABET, 5):
            assert nfa.accepts(word) == reference_accepts(expression, word), (text, word)


def test_thompson_nfa_has_one_entry_and_one_exit():
    nfa = parse_regex('(a|b)*abb').to_nfa()
    (final_state,) = nfa.final_states
    assert nfa.transitions[final_state] == {}  # rien ne sort de l'état final
    for paths in nfa.transitions.values():     # rien n'entre dans l'état initial
        for destinations in paths.values():
            assert nfa.initial_state not in destinations


def test_thompson_nfa_sizes():
    assert len(parse_regex('a').to_nfa().states) == 2
    assert len(parse_regex('ab').to_nfa().states) == 4
    assert len(parse_regex('a|b').to_nfa().states) == 6
    assert len(parse_regex('a*').to_nfa().states) == 4


def test_the_alphabet_can_be_larger_but_not_smaller_than_the_symbols():
    nfa = parse_regex('a').to_nfa(alphabet={'a', 'b'})
    assert nfa.input_symbols == {'a', 'b'}
    assert nfa.accepts('a') is True
    assert nfa.accepts('b') is False
    with pytest.raises(ValueError):
        parse_regex('ab').to_nfa(alphabet={'a'})
    with pytest.raises(ValueError):
        parse_regex('ab').to_dfa(alphabet={'a'})


def test_regex_parse_is_available_on_the_class():
    assert Regex.parse('a|b') == parse_regex('a|b')


# --------------------------------------------------- derivative automaton (DFA)

def test_derivative_dfa_recognizes_the_language():
    for text in EXPRESSIONS:
        expression = parse_regex(text)
        dfa = expression.to_dfa(alphabet=ALPHABET)
        assert type(dfa) is ExtendedDFA
        for word in all_words(ALPHABET, 5):
            assert dfa.accepts(word) == reference_accepts(expression, word), (text, word)


def test_derivative_dfa_is_complete_and_its_states_are_derivatives():
    expression = parse_regex('(a|b)*abb')
    dfa = expression.to_dfa()
    assert dfa.is_complete() is True
    assert dfa.initial_state == expression
    assert dfa.transitions[expression]['a'] == expression.derivative('a')
    assert all(hasattr(state, 'nullable') for state in dfa.states)
    assert dfa.final_states == {state for state in dfa.states if state.nullable()}
    assert len(dfa.minimize().states) == 4  # l'automate minimal connu de (a|b)*abb


def test_derivative_dfa_and_thompson_nfa_agree():
    for text in EXPRESSIONS:
        expression = parse_regex(text)
        dfa = expression.to_dfa(alphabet=ALPHABET)
        nfa = expression.to_nfa(alphabet=ALPHABET)
        assert dfa.language_equals(nfa) is True, text


def test_derivative_dfa_terminates_on_nested_stars():
    expression = parse_regex('((a|b)*c)*')
    dfa = expression.to_dfa()
    assert len(dfa.states) < 20
    for word in all_words('abc', 4):
        assert dfa.accepts(word) == reference_accepts(expression, word)


def test_derivative_dfa_with_a_larger_alphabet_has_a_dead_state():
    dfa = parse_regex('a').to_dfa(alphabet={'a', 'b'})
    assert dfa.is_complete() is True
    assert dfa.accepts('a') is True
    assert dfa.accepts('b') is False
    assert dfa.accepts('ab') is False
    assert 'label="∅"' in dfa.dot()


def test_equivalent_expressions_give_equivalent_automata():
    first = parse_regex('(a|b)*').to_dfa()
    second = parse_regex('(a*b*)*').to_dfa()
    assert first.language_equals(second) is True
    assert parse_regex('a*').to_dfa(alphabet=ALPHABET).language_equals(
        parse_regex('aa*|ε').to_dfa(alphabet=ALPHABET)
    ) is True