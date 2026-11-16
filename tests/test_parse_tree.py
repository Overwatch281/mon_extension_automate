import shutil

import pytest

from automata_extensions.grammar import ContextFreeGrammar, ParseTree

TWO_NONTERMINALS = "S -> A B\nA -> a\nB -> b"


def leaf(symbol):
    return ParseTree(symbol, (), True)


def sample_tree():
    """The tree S(A(a) B(b)) of the grammar S -> A B, A -> a, B -> b."""
    return ParseTree('S', (
        ParseTree('A', (leaf('a'),)),
        ParseTree('B', (leaf('b'),)),
    ))


def test_reading_a_tree():
    tree = sample_tree()
    assert tree.word() == ('a', 'b')
    assert tree.text() == 'ab'
    assert tree.height() == 2
    assert tree.size() == 5
    assert str(tree) == 'S(A(a) B(b))'
    assert leaf('a').height() == 0


def test_leftmost_and_rightmost_derivations_of_a_tree():
    tree = sample_tree()
    assert tree.leftmost_derivation() == [
        ('S',), ('A', 'B'), ('a', 'B'), ('a', 'b'),
    ]
    assert tree.rightmost_derivation() == [
        ('S',), ('A', 'B'), ('A', 'b'), ('a', 'b'),
    ]
    assert tree.productions() == [
        ('S', ('A', 'B')), ('A', ('a',)), ('B', ('b',)),
    ]
    assert tree.rightmost_productions() == [
        ('S', ('A', 'B')), ('B', ('b',)), ('A', ('a',)),
    ]


def test_a_tree_is_rebuilt_from_its_leftmost_derivation():
    grammar = ContextFreeGrammar.from_text("S -> a S b | ε")
    for word in ['', 'ab', 'aaabbb']:
        tree = grammar.parse(word)
        rebuilt = ParseTree.from_leftmost_derivation(grammar, tree.productions())
        assert rebuilt == tree


def test_from_leftmost_derivation_rejects_wrong_derivations():
    grammar = ContextFreeGrammar.from_text(TWO_NONTERMINALS)
    good = [('S', ('A', 'B')), ('A', ('a',)), ('B', ('b',))]
    assert ParseTree.from_leftmost_derivation(grammar, good).text() == 'ab'
    with pytest.raises(ValueError):   # B avant A : pas une dérivation gauche
        ParseTree.from_leftmost_derivation(
            grammar, [('S', ('A', 'B')), ('B', ('b',)), ('A', ('a',))])
    with pytest.raises(ValueError):   # trop courte
        ParseTree.from_leftmost_derivation(grammar, good[:2])
    with pytest.raises(ValueError):   # trop longue
        ParseTree.from_leftmost_derivation(grammar, good + [('A', ('a',))])
    with pytest.raises(ValueError):   # production inconnue
        ParseTree.from_leftmost_derivation(
            grammar, [('S', ('A', 'B')), ('A', ('b',)), ('B', ('b',))])


def test_is_valid_for_detects_a_tampered_tree():
    grammar = ContextFreeGrammar.from_text(TWO_NONTERMINALS)
    assert sample_tree().is_valid_for(grammar) is True
    wrong_rule = ParseTree('S', (leaf('a'),))                       # S -> a n'existe pas
    wrong_root = ParseTree('A', (leaf('a'),))                       # racine != axiome
    wrong_leaf = ParseTree('S', (
        ParseTree('A', (leaf('z'),)), ParseTree('B', (leaf('b'),))))  # z inconnu
    assert wrong_rule.is_valid_for(grammar) is False
    assert wrong_root.is_valid_for(grammar) is False
    assert wrong_leaf.is_valid_for(grammar) is False


def test_dot_description_of_a_tree():
    dot = sample_tree().to_dot()
    assert dot.startswith('digraph tree {')
    assert 'label="S"' in dot
    assert 'label="a", shape=box' in dot
    assert dot.count('->') == 4  # S->A, A->a, S->B, B->b

    epsilon_tree = ContextFreeGrammar.from_text("S -> ε").parse('')
    assert 'label="ε", shape=plaintext' in epsilon_tree.to_dot()


def test_save_rejects_an_unsupported_extension_and_writes_a_dot_file(tmp_path):
    with pytest.raises(ValueError):
        sample_tree().save(tmp_path / 'tree.jpg')
    written = sample_tree().save(tmp_path / 'tree.dot')
    assert written.read_text(encoding='utf-8').startswith('digraph tree {')


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz is not installed")
def test_tree_can_be_drawn_by_graphviz(tmp_path):
    tree = sample_tree()
    assert '<svg' in tree.to_svg()
    assert tree.save(tmp_path / 'tree.png').read_bytes().startswith(b'\x89PNG')
    assert tree.save(tmp_path / 'tree.pdf').read_bytes().startswith(b'%PDF')