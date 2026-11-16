"""Context-free grammars.

A grammar has a set of nonterminals, a set of terminals, a start symbol and
productions ``A -> X1 X2 ... Xk`` (the right-hand side may be empty, which
is the production ``A -> epsilon``). Symbols are strings; a symbol that is
never on the left of a production is a terminal. Parsing is in
`parsing.py`.
"""

from collections import namedtuple

from automata_extensions.grammar.parsing import ParsingMixin
from automata_extensions.grammar.tree_export import EPSILON

Production = namedtuple("Production", ["left", "right"])


class ContextFreeGrammar(ParsingMixin):
    """
    An immutable context-free grammar.

    Parameters
    ----------
    productions : iterable of tuple
        Pairs (left, right). `left` is a nonterminal. `right` is a
        sequence of symbols (a tuple or a list, or a string whose
        characters are the symbols). An empty right-hand side is the
        empty word.
    start : str
        The start symbol.
    nonterminals : iterable of str, optional
        By default, the symbols found on the left of a production.
    terminals : iterable of str, optional
        By default, the other symbols found in the productions.

    Raises
    ------
    ValueError
        If the start symbol is not a nonterminal, if a symbol is both a
        terminal and a nonterminal, or if a production uses an unknown
        symbol.
    """

    def __init__(self, productions, start, nonterminals=None, terminals=None):
        rules = []
        for left, right in productions:
            rule = Production(left, tuple(right))
            if rule not in rules:
                rules.append(rule)

        if nonterminals is None:
            nonterminals = {rule.left for rule in rules}
        nonterminals = frozenset(nonterminals)

        used = {symbol for rule in rules for symbol in rule.right}
        if terminals is None:
            terminals = used - nonterminals
        terminals = frozenset(terminals)

        if start not in nonterminals:
            raise ValueError(f"the start symbol {start!r} is not a nonterminal")
        if nonterminals & terminals:
            raise ValueError(
                f"symbols both terminal and nonterminal: {sorted(nonterminals & terminals)}"
            )
        for rule in rules:
            if rule.left not in nonterminals:
                raise ValueError(f"the left-hand side {rule.left!r} is not a nonterminal")
            unknown = set(rule.right) - nonterminals - terminals
            if unknown:
                raise ValueError(f"unknown symbols in {rule}: {sorted(unknown)}")

        self.productions = tuple(rules)
        self.production_set = frozenset(rules)
        self.start = start
        self.nonterminals = nonterminals
        self.terminals = terminals

    @classmethod
    def from_text(cls, text, start=None, compact=False):
        """
        Read a grammar written as text.

        One rule per line, written ``A -> alternative | alternative``
        (the arrow can also be ``→``). The symbols of an alternative are
        separated by spaces; ``ε`` or ``epsilon`` alone is the empty
        word. With ``compact=True``, every character is a symbol instead.
        Empty lines and lines starting with ``#`` are ignored. The start
        symbol is the left-hand side of the first rule, unless given.

        Parameters
        ----------
        text : str
            The rules.
        start : str, optional
            The start symbol.
        compact : bool
            Whether every character of an alternative is a symbol.

        Returns
        -------
        ContextFreeGrammar
            The grammar.

        Raises
        ------
        ValueError
            If a rule has no arrow or no left-hand side, or if there is
            no rule at all.
        """
        productions = []
        first_left = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            arrow = "->" if "->" in line else "→"
            if arrow not in line:
                raise ValueError(f"missing arrow in the rule {line!r}")
            left, alternatives = line.split(arrow, 1)
            left = left.strip()
            if not left:
                raise ValueError(f"missing left-hand side in the rule {line!r}")
            if first_left is None:
                first_left = left
            for alternative in alternatives.split("|"):
                if compact:
                    symbols = tuple(char for char in alternative if not char.isspace())
                else:
                    symbols = tuple(alternative.split())
                if symbols in ((EPSILON,), ("epsilon",)):
                    symbols = ()
                productions.append((left, symbols))

        if not productions:
            raise ValueError("the grammar has no rule")
        return cls(productions, start if start is not None else first_left)

    def productions_of(self, nonterminal):
        """
        Return the right-hand sides of the productions of a nonterminal,
        in the order of the grammar.

        Complexity
        ----------
        O(number of productions)
        """
        return tuple(rule.right for rule in self.productions if rule.left == nonterminal)

    def is_right_linear(self):
        """
        Test whether the grammar is right-linear.

        A grammar is right-linear if every production is ``A -> w`` or
        ``A -> w B``, where w is a (possibly empty) sequence of terminals
        and B a nonterminal. These grammars generate exactly the regular
        languages.

        Returns
        -------
        bool
            True if every production is right-linear.

        Complexity
        ----------
        O(size of the grammar)
        """
        for rule in self.productions:
            body = rule.right[:-1] if rule.right and rule.right[-1] in self.nonterminals else rule.right
            if any(symbol not in self.terminals for symbol in body):
                return False
        return True

    def __str__(self):
        order = []
        for rule in self.productions:
            if rule.left not in order:
                order.append(rule.left)
        lines = []
        for nonterminal in order:
            alternatives = [
                " ".join(right) if right else EPSILON
                for right in self.productions_of(nonterminal)
            ]
            lines.append(f"{nonterminal} -> {' | '.join(alternatives)}")
        return "\n".join(lines)