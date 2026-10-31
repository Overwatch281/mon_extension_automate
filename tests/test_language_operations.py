import itertools

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def all_words(max_length):
    """Every word over {a, b} of length 0 to `max_length`."""
    for length in range(max_length + 1):
        for letters in itertools.product('ab', repeat=length):
            yield ''.join(letters)


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


def make_only_a_dfa():
    """DFA over the alphabet {a} only."""
    return ExtendedDFA(
        states={'q0'},
        input_symbols={'a'},
        transitions={'q0': {'a': 'q0'}},
        initial_state='q0',
        final_states={'q0'},
    )


def make_empty_word_only_dfa():
    """Partial DFA over {a, b} recognizing only the empty word."""
    return ExtendedDFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {}},
        initial_state='q0',
        final_states={'q0'},
        allow_partial=True,
    )


def in_concatenation(first, second, word):
    """Brute force: is `word` a concatenation of a word of each language?"""
    return any(
        first.accepts(word[:i]) and second.accepts(word[i:])
        for i in range(len(word) + 1)
    )


def in_star(automaton, word):
    """Brute force: is `word` a concatenation of words of the language?"""
    if word == '':
        return True
    return any(
        automaton.accepts(word[:i]) and in_star(automaton, word[i:])
        for i in range(1, len(word) + 1)
    )


# ------------------------------------------------ #42 #43 #44 boolean operations

def test_union_accepts_the_words_of_either_language():
    first, second = make_even_a_dfa(), make_ends_with_ab_nfa()
    union = first.union(second)
    for word in all_words(5):
        assert union.accepts(word) == (first.accepts(word) or second.accepts(word))


def test_intersection_accepts_the_words_of_both_languages():
    first, second = make_even_a_dfa(), make_ends_with_ab_nfa()
    inter = first.intersection(second)
    for word in all_words(5):
        assert inter.accepts(word) == (first.accepts(word) and second.accepts(word))


def test_difference_keeps_the_words_of_the_first_language_only():
    first, second = make_even_a_dfa(), make_ends_with_ab_nfa()
    diff = first.difference(second)
    for word in all_words(5):
        assert diff.accepts(word) == (first.accepts(word) and not second.accepts(word))


def test_boolean_operations_give_complete_deterministic_automata():
    result = make_even_a_dfa().union(make_ends_with_ab_nfa())
    assert type(result) is ExtendedDFA
    assert result.is_complete() is True


def test_boolean_identities_hold():
    first, second = make_even_a_dfa(), make_ends_with_ab_nfa()
    # La réunion est commutative
    assert first.union(second).language_equals(second.union(first)) is True
    # Loi de De Morgan : non (A ou B) = (non A) et (non B)
    left = first.union(second).complement()
    right = first.complement().intersection(second.complement())
    assert left.language_equals(right) is True
    # A \ B = A inter (non B)
    assert first.difference(second).language_equals(
        first.intersection(second.complement())
    ) is True


def test_operations_reject_different_alphabets_and_non_automata():
    dfa = make_even_a_dfa()
    only_a = make_only_a_dfa()
    for operation in (dfa.union, dfa.intersection, dfa.difference, dfa.concatenate):
        with pytest.raises(ValueError):
            operation(only_a)
        with pytest.raises(TypeError):
            operation(object())


# ----------------------------------------------------------- #45 concatenate

def test_concatenate_a_dfa_and_an_nfa():
    first, second = make_even_a_dfa(), make_ends_with_ab_nfa()
    result = first.concatenate(second)
    for word in all_words(5):
        assert result.accepts(word) == in_concatenation(first, second, word)


def test_concatenate_an_nfa_with_epsilon_transitions():
    first, second = make_epsilon_nfa(), make_ends_with_ab_nfa()
    result = first.concatenate(second)
    for word in all_words(5):
        assert result.accepts(word) == in_concatenation(first, second, word)


def test_concatenate_tags_the_states_and_links_them_with_epsilon():
    first, second = make_even_a_dfa(), make_ends_with_ab_nfa()
    result = first.concatenate(second)
    assert type(result) is ExtendedNFA
    assert result.initial_state == (0, 'even')
    assert result.final_states == {(1, 'q2')}
    assert result.states == {(0, 'even'), (0, 'odd'), (1, 'q0'), (1, 'q1'), (1, 'q2')}
    # le seul état final du premier automate relie le second par epsilon
    assert result.epsilon_closure((0, 'even')) == {(0, 'even'), (1, 'q0')}
    # les opérandes ne sont pas modifiés
    assert first.states == {'even', 'odd'}
    assert second.states == {'q0', 'q1', 'q2'}


def test_concatenate_with_the_empty_word_language_changes_nothing():
    dfa = make_even_a_dfa()
    only_empty_word = make_empty_word_only_dfa()
    assert dfa.concatenate(only_empty_word).language_equals(dfa) is True
    assert only_empty_word.concatenate(dfa).language_equals(dfa) is True


def test_concatenate_with_an_empty_language_gives_an_empty_language():
    dfa = make_even_a_dfa()
    empty = ExtendedDFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0', 'b': 'q0'}},
        initial_state='q0',
        final_states=set(),
    )
    assert dfa.concatenate(empty).is_empty() is True
    assert empty.concatenate(dfa).is_empty() is True


# ---------------------------------------------------------------- #46 star

def test_star_accepts_the_concatenations_of_words_of_the_language():
    for automaton in (make_ends_with_ab_nfa(), make_epsilon_nfa(), make_even_a_dfa()):
        star = automaton.star()
        for word in all_words(5):
            assert star.accepts(word) == in_star(automaton, word)


def test_star_always_accepts_the_empty_word():
    nfa = make_ends_with_ab_nfa()
    assert nfa.accepts('') is False
    assert nfa.star().accepts('') is True


def test_star_adds_a_fresh_initial_and_final_state():
    star = make_even_a_dfa().star()
    assert type(star) is ExtendedNFA
    assert star.initial_state == 'init'
    assert star.final_states == {'init'}
    assert star.states == {'even', 'odd', 'init'}

    taken = ExtendedDFA(
        states={'init'},
        input_symbols={'a'},
        transitions={'init': {'a': 'init'}},
        initial_state='init',
        final_states={'init'},
    )
    assert taken.star().initial_state == 'init1'


def test_star_of_the_empty_language_is_the_empty_word_language():
    empty = ExtendedDFA(
        states={'q0'},
        input_symbols={'a', 'b'},
        transitions={'q0': {'a': 'q0', 'b': 'q0'}},
        initial_state='q0',
        final_states=set(),
    )
    star = empty.star()
    assert star.accepts('') is True
    assert star.accepts('a') is False
    assert star.language_equals(make_empty_word_only_dfa()) is True


def test_star_is_idempotent_and_does_not_modify_the_original():
    nfa = make_ends_with_ab_nfa()
    star = nfa.star()
    assert star.star().language_equals(star) is True
    assert nfa.states == {'q0', 'q1', 'q2'}