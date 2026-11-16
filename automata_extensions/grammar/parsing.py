"""Parsing with a context-free grammar: derivation trees and derivations."""

from automata_extensions.grammar.parse_tree import ParseTree


class ParsingMixin:
    """Mixin providing parse, generates and the derivations of a word."""

    def parse(self, word):
        """
        Find a derivation tree of a word, or None if it is not generated.

        The algorithm fills a table of the derivation trees of every
        nonterminal over every part (from position i to position j) of the
        word, from the shortest parts to the longest. For a given part,
        the table is completed repeatedly until nothing changes, which
        handles empty productions, unit productions (even cyclic ones) and
        left recursion. It works for any context-free grammar, ambiguous
        or not; when the word has several trees, one of them is returned.

        Parameters
        ----------
        word : str or sequence of str
            The word to derive. A string is read character by character.

        Returns
        -------
        ParseTree or None
            A derivation tree, or None.

        Complexity
        ----------
        Polynomial in the length n of the word: O(n^(k+1) * |P|) for
        right-hand sides of at most k symbols (pedagogical algorithm).

        References
        ----------
        Hopcroft, Motwani & Ullman, *Introduction to Automata Theory,
        Languages, and Computation*.
        """
        symbols = tuple(word)
        length = len(symbols)
        table = {}  # (nonterminal, i, j) -> ParseTree

        def tree_over(symbol, i, j):
            """A tree of `symbol` over symbols[i:j], if one is known."""
            if symbol in self.terminals:
                if j == i + 1 and symbols[i] == symbol:
                    return ParseTree(symbol, (), True)
                return None
            return table.get((symbol, i, j))

        def match(right, i, j):
            """Trees for the symbols of `right` covering symbols[i:j]."""
            if not right:
                return [] if i == j else None
            first, rest = right[0], right[1:]
            for middle in range(i, j + 1):
                tree = tree_over(first, i, middle)
                if tree is None:
                    continue
                others = match(rest, middle, j)
                if others is not None:
                    return [tree] + others
            return None

        for width in range(length + 1):
            for i in range(length - width + 1):
                j = i + width
                changed = True
                while changed:
                    changed = False
                    for rule in self.productions:
                        if (rule.left, i, j) in table:
                            continue
                        children = match(rule.right, i, j)
                        if children is not None:
                            table[(rule.left, i, j)] = ParseTree(rule.left, tuple(children))
                            changed = True

        return table.get((self.start, 0, length))

    def generates(self, word):
        """
        Test whether the grammar generates a word.

        Parameters
        ----------
        word : str or sequence of str
            The word to test.

        Returns
        -------
        bool
            True if the word has a derivation tree.

        Complexity
        ----------
        Same as `parse`.
        """
        return self.parse(word) is not None

    def leftmost_derivation(self, word):
        """
        Return a leftmost derivation of a word, or None.

        Returns
        -------
        list of tuple or None
            The sentential forms from the start symbol to the word, each
            step rewriting the leftmost nonterminal; None if the word is
            not generated.
        """
        tree = self.parse(word)
        return None if tree is None else tree.leftmost_derivation()

    def rightmost_derivation(self, word):
        """
        Return a rightmost derivation of a word, or None.

        Returns
        -------
        list of tuple or None
            The sentential forms from the start symbol to the word, each
            step rewriting the rightmost nonterminal; None if the word is
            not generated.
        """
        tree = self.parse(word)
        return None if tree is None else tree.rightmost_derivation()