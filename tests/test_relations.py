import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def make_even_a_dfa():
    """Complete DFA over {a, b} accepting an even number of 'a'."""
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


def make_ends_with_a_dfa():
    """Complete DFA over {a, b} accepting the words ending with 'a'."""
    return ExtendedDFA(
        states={'s0', 's1'},
        input_symbols={'a', 'b'},
        transitions={
            's0': {'a': 's1', 'b': 's0'},
            's1': {'a': 's1', 'b': 's0'},
        },
        initial_state='s0',
        final_states={'s1'},
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


def make_redundant_even_a_dfa():
    """Same language as make_even_a_dfa, but with a duplicated even state."""
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


SAMPLE_WORDS = ['', 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aab', 'abb', 'bab']


# ---------------------------------------------------------------- #23 product

def test_product_intersection():
    inter = make_even_a_dfa().product(make_ends_with_a_dfa(), lambda x, y: x and y)
    assert inter.accepts('aa') is True
    assert inter.accepts('baa') is True
    assert inter.accepts('a') is False    # nombre impair de 'a'
    assert inter.accepts('aab') is False  # ne finit pas par 'a'
    assert inter.accepts('') is False


def test_product_union():
    union = make_even_a_dfa().product(make_ends_with_a_dfa(), lambda x, y: x or y)
    assert union.accepts('a') is True     # finit par 'a'
    assert union.accepts('b') is True     # 0 'a' (pair)
    assert union.accepts('aab') is True
    assert union.accepts('ab') is False


def test_product_difference():
    diff = make_even_a_dfa().product(
        make_ends_with_a_dfa(), lambda x, y: x and not y
    )
    assert diff.accepts('') is True
    assert diff.accepts('aab') is True
    assert diff.accepts('aa') is False    # finit par 'a'


def test_product_initial_state_is_a_pair():
    inter = make_even_a_dfa().product(make_ends_with_a_dfa(), lambda x, y: x and y)
    assert inter.initial_state == ('even', 's0')


def test_product_only_builds_accessible_pairs():
    dfa = make_even_a_dfa()
    inter = dfa.product(dfa, lambda x, y: x and y)
    # Sur 4 couples possibles, seuls 2 sont accessibles
    assert inter.states == {('even', 'even'), ('odd', 'odd')}


def test_product_with_partial_automaton():
    union = make_partial_a_dfa().product(make_even_a_dfa(), lambda x, y: x or y)
    assert union.accepts('a') is True     # accepté par le DFA partiel
    assert union.accepts('aa') is True    # nombre pair de 'a'
    assert union.accepts('ab') is False


def test_product_rejects_different_alphabets():
    only_a = ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )
    with pytest.raises(ValueError):
        make_even_a_dfa().product(only_a, lambda x, y: x and y)


def test_product_determinizes_nfa_operands_first():
    nfa = make_ends_with_ab_nfa()
    dfa = make_even_a_dfa()

    inter = nfa.product(dfa, lambda x, y: x and y)
    assert type(inter) is ExtendedDFA
    for word in SAMPLE_WORDS:
        assert inter.accepts(word) == (nfa.accepts(word) and dfa.accepts(word))

    union = dfa.product(nfa, lambda x, y: x or y)
    for word in SAMPLE_WORDS:
        assert union.accepts(word) == (dfa.accepts(word) or nfa.accepts(word))


def test_product_does_not_modify_operands():
    first = make_partial_a_dfa()
    second = make_even_a_dfa()
    first.product(second, lambda x, y: x or y)
    assert first.states == {'q0', 'q1'}
    assert second.states == {'even', 'odd'}


# ------------------------------------------------------------ #24 inclusion

def test_language_subset_intersection_is_included_in_each_operand():
    even = make_even_a_dfa()
    ends_a = make_ends_with_a_dfa()
    inter = even.product(ends_a, lambda x, y: x and y)
    assert inter.language_subset(even) is True
    assert inter.language_subset(ends_a) is True
    assert even.language_subset(inter) is False  # le mot vide est dans even


def test_language_subset_is_reflexive():
    even = make_even_a_dfa()
    assert even.language_subset(even) is True


def test_language_subset_with_partial_automaton():
    partial = make_partial_a_dfa()  # {a}
    ends_a = make_ends_with_a_dfa()
    assert partial.language_subset(ends_a) is True
    assert ends_a.language_subset(partial) is False


# ------------------------------------------------------------- #25 egalite

def test_language_equals_itself_and_its_completion():
    partial = make_partial_a_dfa()
    assert partial.language_equals(partial) is True
    assert partial.language_equals(partial.complete()) is True


def test_language_equals_with_different_structure():
    assert make_even_a_dfa().language_equals(make_redundant_even_a_dfa()) is True


def test_language_equals_false_with_complement():
    even = make_even_a_dfa()
    assert even.language_equals(even.complement()) is False


def test_language_equals_double_complement():
    even = make_even_a_dfa()
    assert even.complement().complement().language_equals(even) is True