"""Derivation trees (parse trees) of a grammar.

A tree shows how a word is derived from the start symbol of a grammar:
each internal node is a nonterminal rewritten by a production, its
children are the symbols of the right-hand side, and the leaves read from
left to right form the derived word. A nonterminal node without children
stands for the production A -> epsilon. The display and the export of a
tree are in `tree_export.py`.
"""

from dataclasses import dataclass

from automata_extensions.grammar.tree_export import TreeExportMixin


@dataclass(frozen=True)
class ParseTree(TreeExportMixin):
    """
    A node of a derivation tree.

    Attributes
    ----------
    symbol : str
        The terminal or the nonterminal written on the node.
    children : tuple of ParseTree
        The symbols of the right-hand side of the production used to
        rewrite this nonterminal (empty for a terminal, and for a
        nonterminal rewritten into the empty word).
    is_terminal : bool
        True for a leaf holding a terminal symbol.
    """

    symbol: str
    children: tuple = ()
    is_terminal: bool = False

    # ------------------------------------------------------------------
    # Reading the tree
    # ------------------------------------------------------------------

    def word(self):
        """
        Return the derived word: the terminals of the leaves, from left to
        right.

        Returns
        -------
        tuple of str
            The terminal symbols.

        Complexity
        ----------
        O(size of the tree)
        """
        if self.is_terminal:
            return (self.symbol,)
        return tuple(
            symbol for child in self.children for symbol in child.word()
        )

    def text(self):
        """Return the derived word as a string (symbols joined together)."""
        return "".join(self.word())

    def height(self):
        """
        Return the height of the tree: 0 for a terminal, and 1 more than
        the highest child for a nonterminal.

        Complexity
        ----------
        O(size of the tree)
        """
        if self.is_terminal:
            return 0
        return 1 + max((child.height() for child in self.children), default=0)

    def size(self):
        """
        Return the number of nodes of the tree.

        Complexity
        ----------
        O(size of the tree)
        """
        return 1 + sum(child.size() for child in self.children)

    def is_valid_for(self, grammar):
        """
        Test whether the tree is a derivation tree of a grammar.

        The root must be the start symbol, every nonterminal node must
        follow a production of the grammar, and every leaf must be a
        terminal of the grammar.

        Parameters
        ----------
        grammar : ContextFreeGrammar
            The grammar.

        Returns
        -------
        bool
            True if the tree is a derivation tree of the grammar.

        Complexity
        ----------
        O(size of the tree)
        """
        return self.symbol == grammar.start and self._follows(grammar)

    def _follows(self, grammar):
        """Check the nodes of the tree (but not the root symbol)."""
        if self.is_terminal:
            return self.symbol in grammar.terminals and not self.children
        right = tuple(child.symbol for child in self.children)
        if (self.symbol, right) not in grammar.production_set:
            return False
        return all(child._follows(grammar) for child in self.children)

    # ------------------------------------------------------------------
    # Derivations
    # ------------------------------------------------------------------

    def _productions(self, rightmost):
        """Productions of the nodes, in the order of a depth-first walk."""
        if self.is_terminal:
            return []
        result = [(self.symbol, tuple(child.symbol for child in self.children))]
        children = reversed(self.children) if rightmost else self.children
        for child in children:
            result.extend(child._productions(rightmost))
        return result

    def productions(self):
        """
        Return the productions of the tree in the order of a leftmost
        derivation (a depth-first walk, children from left to right).

        Returns
        -------
        list of tuple
            Pairs (left-hand side, tuple of right-hand side symbols).

        Complexity
        ----------
        O(size of the tree)
        """
        return self._productions(rightmost=False)

    def rightmost_productions(self):
        """
        Return the productions of the tree in the order of a rightmost
        derivation (a depth-first walk, children from right to left).

        Complexity
        ----------
        O(size of the tree)
        """
        return self._productions(rightmost=True)

    def _derivation(self, rightmost):
        """Sentential forms obtained by rewriting one nonterminal at a time."""
        frontier = [self]
        forms = [tuple(node.symbol for node in frontier)]
        while True:
            indexes = [
                index for index, node in enumerate(frontier)
                if not node.is_terminal
            ]
            if not indexes:
                return forms
            index = indexes[-1] if rightmost else indexes[0]
            frontier[index:index + 1] = list(frontier[index].children)
            forms.append(tuple(node.symbol for node in frontier))

    def leftmost_derivation(self):
        """
        Return the leftmost derivation described by the tree.

        At each step, the leftmost nonterminal of the sentential form is
        rewritten.

        Returns
        -------
        list of tuple
            The sentential forms, from the start symbol to the word.

        Complexity
        ----------
        O(size of the tree squared)
        """
        return self._derivation(rightmost=False)

    def rightmost_derivation(self):
        """
        Return the rightmost derivation described by the tree.

        At each step, the rightmost nonterminal of the sentential form is
        rewritten.

        Returns
        -------
        list of tuple
            The sentential forms, from the start symbol to the word.

        Complexity
        ----------
        O(size of the tree squared)
        """
        return self._derivation(rightmost=True)

    @staticmethod
    def from_leftmost_derivation(grammar, productions):
        """
        Build the derivation tree of a leftmost derivation (#56).

        The productions are given in the order in which they are applied,
        each one rewriting the leftmost nonterminal of the current
        sentential form, starting from the start symbol of the grammar.
        Such a derivation corresponds to a depth-first walk of the tree:
        the tree is built by expanding the nonterminals in that order.

        Parameters
        ----------
        grammar : ContextFreeGrammar
            The grammar.
        productions : iterable of tuple
            Pairs (left-hand side, right-hand side), in the order applied.

        Returns
        -------
        ParseTree
            The derivation tree.

        Raises
        ------
        ValueError
            If a production does not belong to the grammar, does not
            rewrite the leftmost nonterminal, or if the derivation is too
            short or too long to produce a word.

        Complexity
        ----------
        O(size of the tree)
        """
        remaining = iter(productions)

        def build(symbol):
            if symbol in grammar.terminals:
                return ParseTree(symbol, (), True)
            try:
                left, right = next(remaining)
            except StopIteration:
                raise ValueError(
                    "the derivation stops before every nonterminal is rewritten"
                ) from None
            right = tuple(right)
            if left != symbol:
                raise ValueError(
                    f"expected a production of {symbol!r}, got one of {left!r}"
                )
            if (left, right) not in grammar.production_set:
                raise ValueError(f"not a production of the grammar: {left} -> {right}")
            return ParseTree(symbol, tuple(build(child) for child in right))

        tree = build(grammar.start)
        if next(remaining, None) is not None:
            raise ValueError("the derivation has more productions than needed")
        return tree