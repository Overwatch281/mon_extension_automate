import pytest
from automata.fa.nfa import NFA

from automata_extensions.regex import (
    Concat,
    Empty,
    Epsilon,
    Star,
    Symbol,
    Union,
    concat,
    empty,
    epsilon,
    parse_regex,
    star,
    symbol,
    union,
)
from tests.regex_helpers import all_words, reference_accepts

SAMPLE_EXPRESSIONS = [
    'a', 'ab', 'a|b', 'a*', '(a|b)*', 'a*b', '(ab)*', 'a?b', '(a|b)*abb',
    '(a|b)?b*', 'ε', '∅', 'a|ε', '(ab|b)*a', '((a|b)*b)*', 'a*b*a*',
    '(a*b*)*', 'ab|ab', '∅*', '(a|∅)b', 'a+b', '(a|b)+',
]


def a():
    return symbol('a')


def b():
    return symbol('b')


def c():
    return symbol('c')


# ------------------------------------------------------------ parser and printer

def test_parse_reads_the_usual_operators():
    assert parse_regex('ab') == concat(a(), b())
    assert parse_regex('a|b') == union(a(), b())
    assert parse_regex('a*') == star(a())
    assert parse_regex('a?') == union(epsilon(), a())
    assert parse_regex('a+') == concat(a(), star(a()))
    assert parse_regex('(a|b)*') == star(union(a(), b()))
    assert parse_regex('') == epsilon()
    assert parse_regex('()') == epsilon()
    assert parse_regex(' a | b ') == union(a(), b())
    assert parse_regex('ε') == epsilon()
    assert parse_regex('∅') == empty()


def test_printing_uses_the_minimum_of_parentheses():
    assert str(parse_regex('(a|b)*')) == '(a|b)*'
    assert str(parse_regex('(ab)*')) == '(ab)*'
    assert str(parse_regex('a*b')) == 'a*b'
    assert str(parse_regex('(a|b)c')) == '(a|b)c'
    assert str(parse_regex('b|a')) == 'a|b'  # opérandes triés
    assert str(parse_regex('a|ε')) == 'a?'
    assert str(parse_regex('(a|b)?c')) == '(a|b)?c'
    assert str(parse_regex('ε')) == 'ε'
    assert str(parse_regex('∅')) == '∅'


def test_printing_then_parsing_gives_back_the_same_expression():
    for text in SAMPLE_EXPRESSIONS:
        expression = parse_regex(text)
        assert parse_regex(str(expression)) == expression, text


def test_parser_rejects_malformed_expressions():
    for text in ['(', '(a', 'a)', ')', '*', '*a', '+a', '?', 'a|*', '(a|b']:
        with pytest.raises(ValueError):
            parse_regex(text)


def test_symbol_rejects_reserved_and_multi_character_symbols():
    for bad in ['|', '*', '(', 'ε', '∅', 'ab', '', ' ']:
        with pytest.raises(ValueError):
            Symbol(bad)


# ----------------------------------------------------- smart constructors, simplify

def test_smart_constructors_apply_the_simplification_rules():
    assert union(empty(), a()) == a()
    assert union(a(), a()) == a()
    assert union(a(), b()) == union(b(), a())
    assert union(union(a(), b()), c()) == union(a(), union(b(), c()))
    assert union(epsilon(), star(a())) == star(a())
    assert concat(epsilon(), a()) == a()
    assert concat(empty(), a()) == empty()
    assert concat(concat(a(), b()), c()) == concat(a(), concat(b(), c()))
    assert star(empty()) == epsilon()
    assert star(epsilon()) == epsilon()
    assert star(star(a())) == star(a())
    assert star(union(epsilon(), a())) == star(a())


def test_simplify_rebuilds_a_tree_assembled_by_hand():
    assert Union((a(), Union((a(), Empty())))).simplify() == a()
    assert Star(Star(a())).simplify() == star(a())
    assert Concat((Epsilon(), a(), b())).simplify() == concat(a(), b())


def test_expressions_are_hashable_and_compared_by_structure():
    assert len({parse_regex('a|b'), parse_regex('b|a'), union(a(), b())}) == 1
    assert parse_regex('ab') != parse_regex('ba')


def test_symbols_lists_the_symbols_of_the_expression():
    assert parse_regex('a(b|c)*').symbols() == {'a', 'b', 'c'}
    assert parse_regex('ε|∅').symbols() == set()


# ------------------------------------------------------ nullable and derivatives

def test_nullable():
    assert parse_regex('a*').nullable() is True
    assert parse_regex('(a|b)*').nullable() is True
    assert parse_regex('a?b?').nullable() is True
    assert parse_regex('ε').nullable() is True
    assert parse_regex('ab').nullable() is False
    assert parse_regex('a?b').nullable() is False
    assert parse_regex('∅').nullable() is False


def test_derivatives_of_simple_expressions():
    assert a().derivative('a') == epsilon()
    assert a().derivative('b') == empty()
    assert parse_regex('ab').derivative('a') == b()
    assert parse_regex('a*').derivative('a') == parse_regex('a*')
    assert parse_regex('a*b').derivative('a') == parse_regex('a*b')
    assert parse_regex('a*b').derivative('b') == epsilon()
    assert parse_regex('ab|ac').derivative('a') == parse_regex('b|c')
    assert parse_regex('(a|b)*').derivative('b') == parse_regex('(a|b)*')


def test_derivative_by_a_word():
    expression = parse_regex('abc')
    assert expression.derivative_word('ab') == c()
    assert expression.derivative_word('abc') == epsilon()
    assert expression.derivative_word('b') == empty()
    assert expression.derivative_word('') == expression


# ------------------------------------------------------------- matching

def test_matching_by_derivatives_agrees_with_the_definition():
    for text in SAMPLE_EXPRESSIONS:
        expression = parse_regex(text)
        for word in all_words('ab', 5):
            assert expression.accepts(word) == reference_accepts(expression, word), (text, word)


def test_reading_of_the_syntax_agrees_with_automata_lib():
    for text in ['a*b', '(a|b)*abb', 'a?b*', '(ab|b)*a', '(a|b)*', 'a(b|a)?b']:
        expression = parse_regex(text)
        library = NFA.from_regex(text, input_symbols={'a', 'b'})
        for word in all_words('ab', 5):
            assert expression.accepts(word) == library.accepts_input(word), (text, word)