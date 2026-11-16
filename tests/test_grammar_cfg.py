import pytest

from automata_extensions.grammar import ContextFreeGrammar
from tests.regex_helpers import all_words

ANBN = "S -> a S b | ε"
DYCK = "S -> S S | ( S ) | ε"
PALINDROMES = "S -> a S a | b S b | a | b | ε"
UNIT_CYCLE = "S -> A | a\nA -> S | b"
EXPRESSIONS = "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | n"


def is_anbn(word):
    half = len(word) // 2
    return len(word) % 2 == 0 and word == 'a' * half + 'b' * half


def is_balanced(word):
    depth = 0
    for char in word:
        depth += 1 if char == '(' else -1
        if depth < 0:
            return False
    return depth == 0


def is_palindrome(word):
    return word == word[::-1]


def check_leftmost_derivation(grammar, forms, word):
    """Independent check: every step rewrites the leftmost nonterminal."""
    assert forms[0] == (grammar.start,)
    assert forms[-1] == tuple(word)
    for before, after in zip(forms, forms[1:]):
        index = next(i for i, s in enumerate(before) if s in grammar.nonterminals)
        head, symbol, tail = before[:index], before[index], before[index + 1:]
        assert after[:index] == head
        right = after[index:len(after) - len(tail)]
        assert (symbol, right) in grammar.production_set
        assert after[len(after) - len(tail):] == tail


def check_rightmost_derivation(grammar, forms, word):
    """Independent check: every step rewrites the rightmost nonterminal."""
    assert forms[0] == (grammar.start,)
    assert forms[-1] == tuple(word)
    for before, after in zip(forms, forms[1:]):
        index = max(i for i, s in enumerate(before) if s in grammar.nonterminals)
        head, symbol, tail = before[:index], before[index], before[index + 1:]
        assert after[:index] == head
        right = after[index:len(after) - len(tail)]
        assert (symbol, right) in grammar.production_set
        assert after[len(after) - len(tail):] == tail


# ------------------------------------------------------- building a grammar

def test_default_symbols_come_from_the_productions():
    grammar = ContextFreeGrammar([('S', 'aSb'), ('S', '')], start='S')
    assert grammar.nonterminals == {'S'}
    assert grammar.terminals == {'a', 'b'}
    assert grammar.productions_of('S') == (('a', 'S', 'b'), ())
    assert grammar.start == 'S'


def test_grammar_rejects_inconsistent_definitions():
    with pytest.raises(ValueError):
        ContextFreeGrammar([('S', 'a')], start='T')                       # start inconnu
    with pytest.raises(ValueError):
        ContextFreeGrammar([('S', 'a')], start='S', terminals={'S', 'a'})  # S des deux côtés
    with pytest.raises(ValueError):
        ContextFreeGrammar([('S', 'ab')], start='S', terminals={'a'})      # b inconnu
    with pytest.raises(ValueError):
        ContextFreeGrammar([('a', 'S')], start='S', nonterminals={'S'}, terminals={'a'})  # a à gauche


def test_from_text_reads_rules_alternatives_and_comments():
    grammar = ContextFreeGrammar.from_text(
        "# commentaire\n"
        "S -> A B | ε\n"
        "A → a A | a\n"
        "B -> b\n"
    )
    assert grammar.start == 'S'
    assert grammar.nonterminals == {'S', 'A', 'B'}
    assert grammar.terminals == {'a', 'b'}
    assert grammar.productions_of('S') == (('A', 'B'), ())
    assert grammar.productions_of('A') == (('a', 'A'), ('a',))


def test_from_text_compact_mode_and_epsilon_spellings():
    compact = ContextFreeGrammar.from_text("S -> aSb | ε", compact=True)
    assert compact.productions_of('S') == (('a', 'S', 'b'), ())
    named = ContextFreeGrammar.from_text("S -> epsilon | x", start='S')
    assert named.productions_of('S') == ((), ('x',))


def test_from_text_rejects_malformed_text():
    for text in ["", "# rien", "S a b", "-> a"]:
        with pytest.raises(ValueError):
            ContextFreeGrammar.from_text(text)


def test_printing_then_reading_gives_back_the_same_grammar():
    for text in (ANBN, DYCK, PALINDROMES, UNIT_CYCLE, EXPRESSIONS):
        grammar = ContextFreeGrammar.from_text(text)
        again = ContextFreeGrammar.from_text(str(grammar))
        assert again.productions == grammar.productions


def test_is_right_linear():
    assert ContextFreeGrammar.from_text("S -> a S | b A | c\nA -> ε").is_right_linear() is True
    assert ContextFreeGrammar.from_text("S -> a b S | a b").is_right_linear() is True
    assert ContextFreeGrammar.from_text(ANBN).is_right_linear() is False
    assert ContextFreeGrammar.from_text("S -> S a | a").is_right_linear() is False


# ------------------------------------------------------------- generation

def test_anbn_grammar_generates_exactly_the_words_anbn():
    grammar = ContextFreeGrammar.from_text(ANBN)
    for word in all_words('ab', 8):
        assert grammar.generates(word) == is_anbn(word), word


def test_dyck_grammar_generates_exactly_the_balanced_words():
    grammar = ContextFreeGrammar.from_text(DYCK)  # ambiguë, récursive à gauche, avec ε
    for word in all_words('()', 8):
        assert grammar.generates(word) == is_balanced(word), word


def test_palindrome_grammar_generates_exactly_the_palindromes():
    grammar = ContextFreeGrammar.from_text(PALINDROMES)
    for word in all_words('ab', 7):
        assert grammar.generates(word) == is_palindrome(word), word


def test_a_cycle_of_unit_productions_does_not_loop_forever():
    grammar = ContextFreeGrammar.from_text(UNIT_CYCLE)
    assert grammar.generates('a') is True
    assert grammar.generates('b') is True
    assert grammar.generates('ab') is False
    assert grammar.generates('') is False


def test_words_with_unknown_symbols_are_not_generated():
    grammar = ContextFreeGrammar.from_text(ANBN)
    assert grammar.parse('abc') is None
    assert grammar.parse('x') is None


# ------------------------------------------------------ derivation trees

def test_every_tree_is_a_valid_derivation_of_the_word():
    for text, alphabet, oracle in [
        (ANBN, 'ab', is_anbn),
        (DYCK, '()', is_balanced),
        (PALINDROMES, 'ab', is_palindrome),
    ]:
        grammar = ContextFreeGrammar.from_text(text)
        for word in all_words(alphabet, 6):
            tree = grammar.parse(word)
            if oracle(word):
                assert tree is not None
                assert tree.text() == word
                assert tree.is_valid_for(grammar)
            else:
                assert tree is None


def test_the_empty_word_has_a_tree_made_of_one_epsilon_node():
    tree = ContextFreeGrammar.from_text(ANBN).parse('')
    assert str(tree) == 'S(ε)'
    assert tree.word() == ()


def test_expression_grammar_gives_the_precedence_of_the_operators():
    grammar = ContextFreeGrammar.from_text(EXPRESSIONS)
    tree = grammar.parse(['n', '+', 'n', '*', 'n'])
    assert tree is not None
    assert tree.is_valid_for(grammar)
    # E -> E + T : le produit est dans le second opérande de l'addition
    assert tree.productions()[0] == ('E', ('E', '+', 'T'))
    assert ('T', ('T', '*', 'F')) in tree.productions()
    assert grammar.generates(['n', '+', '+', 'n']) is False


def test_leftmost_and_rightmost_derivations_follow_the_definition():
    for text, words in [
        (ANBN, ['', 'ab', 'aabb']),
        (DYCK, ['()', '(())', '()()']),
        (PALINDROMES, ['aba', 'abba', 'b']),
    ]:
        grammar = ContextFreeGrammar.from_text(text)
        for word in words:
            check_leftmost_derivation(grammar, grammar.leftmost_derivation(word), word)
            check_rightmost_derivation(grammar, grammar.rightmost_derivation(word), word)
    assert ContextFreeGrammar.from_text(ANBN).leftmost_derivation('ba') is None
    assert ContextFreeGrammar.from_text(ANBN).rightmost_derivation('ba') is None